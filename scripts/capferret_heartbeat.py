#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Battement de cœur de la veille Cap-Ferret : un cycle d'envoi déterministe.

Appelé toutes les 15 min par une boucle de fond. Sans analyse LLM : compose
les messages depuis data/capferret-live.json (l'analyse riche reste faite par
les cycles interactifs qui mettent le JSON à jour).

- Telegram : à chaque appel, image en alternance carte de situation ↔
  satellite NASA (compteur dans /tmp/capferret-hb-state.json).
- X (via Late) : un appel sur deux (≈ toutes les 30 min), texte horodaté
  (unicité garantie par l'heure), image satellite publique du moment.
"""

import datetime
import json
import os
import subprocess
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capferret_notify import LEVEL_EMOJI, load_data, load_local_secrets, log  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = "/tmp/capferret-hb-state.json"
CARD_PATH = "/tmp/capferret-card.png"
PAGE_URL = "https://fables.comptoiria.com/cap-ferret-aout-2026.html"
LATE_X_ACCOUNT = "69a8b75bdc8cab9432b8bf60"
PW_MODULES = ("/tmp/claude-0/-home-user-fables-du-futur/"
              "b65dadee-d9c0-5614-8d62-c158e9939883/scratchpad")


def now_fr():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))


def load_state():
    try:
        return json.load(open(STATE_PATH))
    except (OSError, ValueError):
        return {"n": 0}


def save_state(state):
    json.dump(state, open(STATE_PATH, "w"))


def render_card():
    env = dict(os.environ, PW_MODULES=PW_MODULES)
    try:
        subprocess.run(["node", os.path.join(REPO_ROOT, "scripts", "render_card.mjs"),
                        CARD_PATH], env=env, timeout=120, check=True,
                       capture_output=True)
        return True
    except Exception as exc:  # noqa: BLE001 — le repli satellite suffit
        log("heartbeat : rendu carte impossible (%s)" % exc)
        return False


def telegram_caption(d, hhmm):
    return (
        "%s <b>Point automatique de %s</b>\n"
        "%s\n"
        "📊 Séjour début août : possible %s %% · dégradé %s %% · annulé %s %%\n"
        "🕐 Dernière analyse complète : %s — prochain battement dans 15 min\n"
        "🔗 %s"
        % (
            LEVEL_EMOJI.get(d.get("level"), "🔴"), hhmm,
            d.get("headline", ""),
            d.get("prob_ok", "?"), d.get("prob_degraded", "?"), d.get("prob_cancelled", "?"),
            d.get("updated_label", "?"),
            PAGE_URL,
        )
    )


def x_text(d, hhmm):
    return (
        "%s Point de %s — incendie Cap-Ferret. %s ha parcourus, %s personnes évacuées, "
        "%s pompiers engagés. Estimation séjour début août : %s %% de risque d'annulation. "
        "Soutien aux secours et aux habitants. Suivi gratuit toutes les 15 min : t.me/Capfeuretbot"
        % (
            LEVEL_EMOJI.get(d.get("level"), "🔴"), hhmm,
            d.get("stats", {}).get("hectares", "?"),
            d.get("stats", {}).get("evacues", "?"),
            d.get("stats", {}).get("pompiers", "?"),
            d.get("prob_cancelled", "?"),
        )
    )


def post_x(d, hhmm):
    key = os.environ.get("LATE_API_KEY", "").strip()
    if not key:
        log("heartbeat : LATE_API_KEY absente, pas de post X.")
        return
    sat_url = ("https://wvs.earthdata.nasa.gov/api/v1/snapshot?REQUEST=GetSnapshot"
               "&CRS=EPSG:4326&FORMAT=image/jpeg&WIDTH=1000&HEIGHT=870"
               "&BBOX=44.45,-1.45,45.10,-0.70"
               "&LAYERS=VIIRS_NOAA20_CorrectedReflectance_TrueColor,"
               "VIIRS_NOAA20_Thermal_Anomalies_375m_All,Coastlines_15m"
               "&TIME=" + str(datetime.date.today()))
    payload = {
        "content": x_text(d, hhmm)[:280],
        "publishNow": True,
        "platforms": [{"platform": "twitter", "accountId": LATE_X_ACCOUNT}],
        "mediaItems": [{"type": "image", "url": sat_url}],
    }
    req = urllib.request.Request("https://getlate.dev/api/v1/posts",
                                 data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            log("heartbeat : post X créé (HTTP %s)." % resp.status)
    except Exception as exc:  # noqa: BLE001 — un échec X ne bloque pas Telegram
        log("heartbeat : post X échoué (%s)." % exc)


def notify_new_subscribers(state):
    """Prévient Nico sur Telegram quand le compteur d'abonnés progresse."""
    from capferret_notify import BLOCKED_PATH, SUBSCRIBERS_PATH, _read_id_set, refresh_subscribers
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return
    subs = refresh_subscribers(token) - _read_id_set(BLOCKED_PATH)
    known = set(state.get("known_subs") or [])
    new = sorted(subs - known)
    if known and new:
        msg = ("👥 Veille Cap-Ferret : +%d abonné(s). Total : %d actifs."
               % (len(new), len(subs)))
        body = json.dumps({"chat_id": "632685614", "text": msg}).encode()
        req = urllib.request.Request(
            "https://api.telegram.org/bot%s/sendMessage" % token,
            data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            urllib.request.urlopen(req, timeout=20)
            log("heartbeat : %d nouvel(aux) abonné(s) signalé(s) à Nico." % len(new))
        except Exception as exc:  # noqa: BLE001
            log("heartbeat : notification abonnés échouée (%s)." % exc)
    state["known_subs"] = sorted(subs)


def main():
    load_local_secrets()
    d = load_data()
    if d is None:
        return 1
    state = load_state()
    state["n"] = state.get("n", 0) + 1
    notify_new_subscribers(state)
    hhmm = now_fr().strftime("%Hh%M")

    args = ["--caption", telegram_caption(d, hhmm)]
    if state["n"] % 2 == 0 and render_card():
        args += ["--photo-file", CARD_PATH]
    rc = subprocess.call(
        [sys.executable, os.path.join(REPO_ROOT, "scripts", "capferret_photo.py")] + args
    )

    if state["n"] % 2 == 1:
        post_x(d, hhmm)

    save_state(state)
    return rc


if __name__ == "__main__":
    sys.exit(main())
