#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envoie sur Telegram une image satellite récente de la zone Cap-Ferret / Saumos.

Usage :
    python3 scripts/capferret_photo.py --caption "Texte" [--date AAAA-MM-JJ] [--style fresh|day] [--photo-url URL]

- Image : API snapshot NASA Worldview (publique, sans clé) — vraie couleur +
  anomalies thermiques + traits de côte, cadrée sur le bassin d'Arcachon et la
  presqu'île. Sélection automatique du meilleur passage parmi 5 satellites
  (VIIRS NOAA-21/NOAA-20/Suomi-NPP ~12h30-13h30, MODIS Aqua ~13h30,
  MODIS Terra ~10h30), sur aujourd'hui puis la veille.
- --style fresh (défaut) : détections les plus récentes, y compris les points
  chauds de la nuit sur fond noir ; --style day : plus belle image de jour
  (panache de fumée visible).
- Envoi : Telegram sendPhoto en multipart (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID,
  lus dans l'environnement ou .capferret-secrets.env comme capferret_notify).
Stdlib uniquement.
"""

import argparse
import datetime
import os
import ssl
import sys
import urllib.error
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capferret_notify import load_local_secrets, log, mark_blocked, telegram_chat_ids  # noqa: E402

WORLDVIEW = "https://wvs.earthdata.nasa.gov/api/v1/snapshot"
BBOX = "44.45,-1.45,45.10,-0.70"  # lat_min,lon_min,lat_max,lon_max (EPSG:4326)
# Passages quotidiens approximatifs (heure locale) : Terra ~10h30, NOAA-20 ~12h30,
# SNPP/NOAA-21/Aqua ~13h30. On interroge tous les satellites et on garde le meilleur.
SATELLITES = [
    ("VIIRS_NOAA21_CorrectedReflectance_TrueColor,VIIRS_NOAA21_Thermal_Anomalies_375m_All", "VIIRS NOAA-21"),
    ("VIIRS_NOAA20_CorrectedReflectance_TrueColor,VIIRS_NOAA20_Thermal_Anomalies_375m_All", "VIIRS NOAA-20"),
    ("VIIRS_SNPP_CorrectedReflectance_TrueColor,VIIRS_SNPP_Thermal_Anomalies_375m_All", "VIIRS Suomi-NPP"),
    ("MODIS_Aqua_CorrectedReflectance_TrueColor,MODIS_Aqua_Thermal_Anomalies_All", "MODIS Aqua"),
    ("MODIS_Terra_CorrectedReflectance_TrueColor,MODIS_Terra_Thermal_Anomalies_All", "MODIS Terra"),
]
HOTSPOT_MIN = 15000   # en dessous : snapshot vide (ni image de jour ni points chauds)
DAYLIGHT_MIN = 30000  # au-dessus : vraie image de jour exploitable


def fetch_snapshot(layers, date_str):
    """Un snapshot Worldview (couche vraie couleur + points chauds + côtes)."""
    url = (
        WORLDVIEW
        + "?REQUEST=GetSnapshot&CRS=EPSG:4326&FORMAT=image/jpeg"
        + "&WIDTH=1000&HEIGHT=870&BBOX=" + BBOX
        + "&LAYERS=" + layers + ",Coastlines_15m"
        + "&TIME=" + date_str
    )
    try:
        with urllib.request.urlopen(url, timeout=45,
                                    context=ssl.create_default_context()) as resp:
            data = resp.read()
            if resp.status == 200 and "image" in resp.headers.get("Content-Type", ""):
                return data
    except (urllib.error.URLError, OSError) as exc:
        log("Worldview %s %s : erreur %s" % (layers.split(",")[0], date_str, exc))
    return None


def fetch_satellite_image(date_str=None, style="fresh"):
    """Sélectionne la meilleure image parmi tous les satellites sur 2 jours.

    style « fresh » : priorité aux détections les plus récentes (points chauds
    de la nuit inclus, sur fond noir) ; style « day » : priorité à la plus
    belle image de jour (panache de fumée visible). Renvoie (bytes, desc).
    """
    today = datetime.date.today()
    dates = [date_str] if date_str else [str(today), str(today - datetime.timedelta(days=1))]

    candidates = []  # (date, nom_satellite, taille, bytes)
    for d in dates:
        for layers, name in SATELLITES:
            data = fetch_snapshot(layers, d)
            if data and len(data) >= HOTSPOT_MIN:
                candidates.append((d, name, len(data), data))
        # style fresh : si le jour le plus récent a déjà du contenu, inutile
        # d'interroger la veille sauf pour trouver une image de jour.
        if style == "fresh" and candidates and any(c[0] == d for c in candidates):
            daylight = [c for c in candidates if c[2] >= DAYLIGHT_MIN]
            if daylight:
                break

    if not candidates:
        return None, None

    freshest_day = candidates[0][0]
    fresh_best = max((c for c in candidates if c[0] == freshest_day), key=lambda c: c[2])
    day_candidates = [c for c in candidates if c[2] >= DAYLIGHT_MIN]
    day_best = max(day_candidates, key=lambda c: c[2]) if day_candidates else None

    if style == "day" and day_best:
        chosen, kind = day_best, "dernier passage de jour"
    elif fresh_best[2] >= DAYLIGHT_MIN:
        chosen, kind = fresh_best, "image de jour la plus récente"
    elif style == "fresh" or day_best is None:
        chosen, kind = fresh_best, "points chauds les plus récents"
    else:
        chosen, kind = day_best, "dernier passage de jour"

    d, name, _size, data = chosen
    return data, "%s — %s (%s)" % (name, d, kind)


def send_photo(token, chat_id, image, caption):
    """sendPhoto en multipart/form-data. True si OK."""
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in (("chat_id", chat_id), ("caption", caption[:1024]),
                        ("parse_mode", "HTML")):
        parts.append(
            ("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
             % (boundary, name, value)).encode("utf-8")
        )
    parts.append(
        ("--%s\r\nContent-Disposition: form-data; name=\"photo\"; "
         "filename=\"satellite.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n"
         % boundary).encode("utf-8")
    )
    parts.append(image)
    parts.append(("\r\n--%s--\r\n" % boundary).encode("utf-8"))
    body = b"".join(parts)

    req = urllib.request.Request(
        "https://api.telegram.org/bot%s/sendPhoto" % token,
        data=body,
        method="POST",
    )
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=context) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            mark_blocked(chat_id)
        else:
            log("sendPhoto : erreur HTTP %s" % exc.code)
        return False
    except (urllib.error.URLError, OSError) as exc:
        log("sendPhoto : erreur %s" % exc)
        return False


def fetch_url_image(url):
    """Télécharge une image quelconque (jpeg/png). Renvoie bytes ou None."""
    context = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "capferret-veille/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45, context=context) as resp:
            data = resp.read()
            if resp.status == 200 and "image" in resp.headers.get("Content-Type", "") \
                    and len(data) > 10000:
                return data
            log("fetch_url_image : réponse non exploitable (%s, %d octets)"
                % (resp.headers.get("Content-Type", ""), len(data)))
    except (urllib.error.URLError, OSError) as exc:
        log("fetch_url_image : erreur %s" % exc)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Photo satellite (ou autre image) → Telegram.")
    parser.add_argument("--caption", required=True, help="Légende du message.")
    parser.add_argument("--date", default="", help="Date AAAA-MM-JJ (défaut : aujourd'hui puis la veille).")
    parser.add_argument("--photo-url", default="",
                        help="URL d'une image à envoyer à la place du satellite "
                             "(ex. photo Wikimedia Commons d'une destination plan B).")
    parser.add_argument("--style", default="fresh", choices=["fresh", "day"],
                        help="fresh = détections les plus récentes (défaut) ; "
                             "day = plus belle image de jour (panache visible).")
    parser.add_argument("--photo-file", default="",
                        help="Chemin local d'une image à envoyer (ex. carte de "
                             "situation générée par scripts/render_card.mjs).")
    args = parser.parse_args(argv)

    load_local_secrets()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_ids = telegram_chat_ids(token)
    if not token or not chat_ids:
        log("Telegram non configuré — abandon.")
        return 1

    image, desc = None, None
    if args.photo_file:
        try:
            with open(args.photo_file, "rb") as fh:
                image = fh.read()
        except OSError as exc:
            log("photo-file illisible (%s) — repli satellite." % exc)
    if image is None and args.photo_url:
        image = fetch_url_image(args.photo_url)
    if image is None:
        image, desc = fetch_satellite_image(args.date or None, style=args.style)

    rc = 0
    if image:
        caption = args.caption
        if desc:
            caption += "\n🛰 Image satellite NASA %s" % desc
        for chat_id in chat_ids:
            if send_photo(token, chat_id, image, caption):
                log("Photo satellite envoyée à %s (%s)." % (chat_id, desc))
            else:
                rc = 1
        return rc

    log("Aucune image satellite disponible — envoi du texte seul via sendMessage.")
    import json as _json
    import urllib.request as _r
    for chat_id in chat_ids:
        body = _json.dumps({"chat_id": chat_id, "text": args.caption,
                            "parse_mode": "HTML"}).encode("utf-8")
        req = _r.Request("https://api.telegram.org/bot%s/sendMessage" % token,
                         data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with _r.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
                if resp.status != 200:
                    rc = 1
        except (urllib.error.URLError, OSError) as exc:
            log("sendMessage %s : erreur %s" % (chat_id, exc))
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
