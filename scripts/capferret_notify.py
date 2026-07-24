#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Notifications de la veille incendie Cap-Ferret (Telegram + e-mail via Resend).

Usage :
    python3 scripts/capferret_notify.py --kind digest|urgent|info \
        [--subject "Objet personnalisé"] [--summary "Texte court"]

- Lit data/capferret-live.json (le contrat JSON est décrit dans
  scripts/CAPFERRET-MONITORING.md).
- Telegram : envoyé pour tous les kinds, si TELEGRAM_BOT_TOKEN et
  TELEGRAM_CHAT_ID sont définis. Sinon, simple log et on continue.
- E-mail (API Resend) : envoyé pour --kind digest et urgent uniquement,
  si RESEND_API_KEY et RESEND_FROM_DEFAULT sont définis.

Stdlib uniquement, aucune dépendance à installer.
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO_ROOT, "data", "capferret-live.json")
SECRETS_PATH = os.path.join(REPO_ROOT, ".capferret-secrets.env")


def load_local_secrets():
    """Charge .capferret-secrets.env (KEY=VALUE, hors git) dans os.environ
    pour les clés absentes de l'environnement (TELEGRAM_BOT_TOKEN, etc.)."""
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip('"').strip("'")
                if key and value and not os.environ.get(key):
                    os.environ[key] = value
    except OSError:
        pass


load_local_secrets()
PAGE_URL = "https://fables.comptoiria.com/cap-ferret-aout-2026.html"
EMAIL_TO = "nicolas@comptoiria.com"

LEVEL_EMOJI = {"good": "🟢", "warning": "🟡", "serious": "🟠", "critical": "🔴"}
LEVEL_COLOR = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}
STAT_LABELS = [
    ("hectares", "Hectares parcourus"),
    ("evacues", "Personnes évacuées"),
    ("pompiers", "Pompiers mobilisés"),
    ("statut_feu", "Statut du feu"),
]


def log(msg):
    print("[capferret-notify] %s" % msg)


def load_data():
    """Charge data/capferret-live.json ; renvoie None si illisible."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        log("ERREUR : fichier introuvable : %s" % DATA_PATH)
    except (json.JSONDecodeError, OSError) as exc:
        log("ERREUR : impossible de lire %s (%s)" % (DATA_PATH, exc))
    return None


def http_post_json(url, payload, headers=None):
    """POST JSON ; renvoie (status, corps) ou (None, message d'erreur)."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=30, context=context) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return exc.code, detail
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, str(exc)


def html_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ---------------------------------------------------------------- Telegram

def send_telegram(data, summary):
    """Envoie le message compact Telegram. True = OK, False = échec réel."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        log("Telegram non configuré (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID absents) — étape ignorée.")
        return True

    level = data.get("level", "warning")
    emoji = LEVEL_EMOJI.get(level, "🟡")
    stats = data.get("stats", {}) or {}
    lines = [
        "%s <b>Cap-Ferret — %s</b>" % (emoji, html_escape(data.get("level_label", "situation en cours"))),
        "",
        html_escape(summary or data.get("headline", "")),
        "",
        "🔥 %s ha · 👥 %s évacués · 🚒 %s pompiers · état : %s" % (
            html_escape(stats.get("hectares", "?")),
            html_escape(stats.get("evacues", "?")),
            html_escape(stats.get("pompiers", "?")),
            html_escape(stats.get("statut_feu", "?")),
        ),
        "📊 Séjour possible %s %% · dégradé %s %% · annulé %s %%" % (
            data.get("prob_ok", "?"),
            data.get("prob_degraded", "?"),
            data.get("prob_cancelled", "?"),
        ),
        "🕐 %s" % html_escape(data.get("updated_label", "")),
        "",
        '<a href="%s">Voir le dashboard complet</a>' % PAGE_URL,
    ]
    payload = {
        "chat_id": chat_id,
        "text": "\n".join(lines),
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    status, detail = http_post_json(
        "https://api.telegram.org/bot%s/sendMessage" % token, payload
    )
    if status == 200:
        log("Telegram : message envoyé.")
        return True
    log("Telegram : échec (statut=%s, détail=%s)" % (status, detail))
    return False


# ------------------------------------------------------------------ E-mail

def build_email_html(data, summary):
    """Corps HTML de l'e-mail : une colonne claire, CSS inline uniquement."""
    level = data.get("level", "warning")
    color = LEVEL_COLOR.get(level, LEVEL_COLOR["warning"])
    emoji = LEVEL_EMOJI.get(level, "🟡")
    stats = data.get("stats", {}) or {}

    stat_rows = "".join(
        '<tr>'
        '<td style="padding:8px 12px;border-bottom:1px solid #eceae4;color:#52514e;'
        'font-size:13px;">%s</td>'
        '<td style="padding:8px 12px;border-bottom:1px solid #eceae4;color:#0b0b0b;'
        'font-size:14px;font-weight:700;text-align:right;white-space:nowrap;">%s</td>'
        '</tr>' % (label, html_escape(stats.get(key, "—")))
        for key, label in STAT_LABELS
    )

    probs = [
        (data.get("prob_ok", 0), "#0ca30c", "possible"),
        (data.get("prob_degraded", 0), "#ec835a", "dégradé"),
        (data.get("prob_cancelled", 0), "#d03b3b", "annulé"),
    ]
    total = sum(max(int(p or 0), 0) for p, _c, _l in probs) or 1
    prob_cells = "".join(
        '<td width="%d%%" style="background:%s;color:#ffffff;font-size:12px;'
        'font-weight:700;text-align:center;padding:9px 2px;">%s %s%%</td>'
        % (round(max(int(p or 0), 0) * 100 / total), c, l, p)
        for p, c, l in probs
        if int(p or 0) > 0
    )

    journal = (data.get("journal") or [])[:3]
    journal_html = "".join(
        '<tr><td style="padding:10px 0;border-bottom:1px solid #eceae4;">'
        '<div style="font-size:11px;font-weight:700;letter-spacing:.08em;'
        'text-transform:uppercase;color:#898781;">'
        '<span style="color:%s;">&#9679;</span>&nbsp; %s</div>'
        '<div style="font-size:13.5px;color:#52514e;line-height:1.55;margin-top:3px;">%s</div>'
        '</td></tr>'
        % (
            LEVEL_COLOR.get(entry.get("level", "warning"), "#fab219"),
            html_escape(entry.get("time_label", "")),
            html_escape(entry.get("text", "")),
        )
        for entry in journal
    )

    return """\
<div style="margin:0;padding:24px 12px;background:#f9f9f7;font-family:Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;">
  <table role="presentation" cellpadding="0" cellspacing="0" width="100%%" style="max-width:560px;margin:0 auto;background:#fcfcfb;border:1px solid #e5e3dc;border-radius:14px;overflow:hidden;">
    <tr>
      <td style="background:%(color)s;padding:18px 24px;">
        <div style="color:#ffffff;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.85;">Veille automatique Cap-Ferret</div>
        <div style="color:#ffffff;font-size:19px;font-weight:800;margin-top:4px;">%(emoji)s %(level_label)s</div>
      </td>
    </tr>
    <tr>
      <td style="padding:22px 24px 6px;">
        <p style="margin:0;font-size:15.5px;font-weight:600;color:#0b0b0b;line-height:1.5;">%(headline)s</p>
        <p style="margin:8px 0 0;font-size:12.5px;color:#898781;">Dernière vérification : %(updated_label)s · %(next_check)s</p>
      </td>
    </tr>
    <tr>
      <td style="padding:16px 24px 0;">
        <table role="presentation" cellpadding="0" cellspacing="0" width="100%%" style="border:1px solid #eceae4;border-radius:10px;border-collapse:separate;overflow:hidden;">%(stat_rows)s</table>
      </td>
    </tr>
    <tr>
      <td style="padding:20px 24px 0;">
        <div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#898781;margin-bottom:8px;">Probabilités pour vos dates</div>
        <table role="presentation" cellpadding="0" cellspacing="2" width="100%%" style="border-collapse:separate;border-radius:8px;overflow:hidden;"><tr>%(prob_cells)s</tr></table>
      </td>
    </tr>
    <tr>
      <td style="padding:20px 24px 0;">
        <div style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#898781;">Journal de situation</div>
        <table role="presentation" cellpadding="0" cellspacing="0" width="100%%">%(journal)s</table>
      </td>
    </tr>
    <tr>
      <td style="padding:24px;text-align:center;">
        <a href="%(page_url)s" style="display:inline-block;background:#2a78d6;color:#ffffff;font-size:14.5px;font-weight:700;text-decoration:none;padding:13px 28px;border-radius:10px;">Voir le dashboard complet</a>
      </td>
    </tr>
    <tr>
      <td style="padding:0 24px 22px;text-align:center;">
        <p style="margin:0;font-size:11.5px;color:#898781;line-height:1.6;">Veille automatique Cap-Ferret · répondre STOP pour ajuster la fréquence</p>
      </td>
    </tr>
  </table>
</div>
""" % {
        "color": color,
        "emoji": emoji,
        "level_label": html_escape(data.get("level_label", "Situation en cours")),
        "headline": html_escape(summary or data.get("headline", "")),
        "updated_label": html_escape(data.get("updated_label", "—")),
        "next_check": html_escape(data.get("next_check_label", "")),
        "stat_rows": stat_rows,
        "prob_cells": prob_cells,
        "journal": journal_html,
        "page_url": PAGE_URL,
    }


AGENTMAIL_INBOX = "nico-fireflies@agentmail.to"


def send_email(data, subject, summary):
    """Envoie l'e-mail : AgentMail en priorité, Resend en secours.

    (api.resend.com est bloqué par la politique de sortie de certains
    environnements ; AgentMail est la voie fiable ici.)
    True = OK ou non configuré, False = échec.
    """
    level = data.get("level", "warning")
    if not subject:
        subject = "%s Cap-Ferret — %s" % (
            LEVEL_EMOJI.get(level, "🟡"),
            data.get("level_label", "point de situation"),
        )
    html = build_email_html(data, summary)

    agentmail_key = os.environ.get("AGENTMAIL_API_KEY", "").strip()
    if agentmail_key:
        status, detail = http_post_json(
            "https://api.agentmail.to/v0/inboxes/%s/messages/send" % AGENTMAIL_INBOX,
            {
                "to": [EMAIL_TO],
                "subject": subject,
                "html": html,
                "text": "%s — %s\n%s" % (
                    data.get("level_label", ""),
                    summary or data.get("headline", ""),
                    PAGE_URL,
                ),
            },
            headers={"Authorization": "Bearer %s" % agentmail_key},
        )
        if status in (200, 201):
            log("E-mail (AgentMail) : envoyé à %s (objet : %s)." % (EMAIL_TO, subject))
            return True
        log("E-mail (AgentMail) : échec (statut=%s, détail=%s) — tentative Resend." % (status, detail))

    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    sender = os.environ.get("RESEND_FROM_DEFAULT", "").strip()
    if not resend_key or not sender:
        if not agentmail_key:
            log("E-mail non configuré (ni AGENTMAIL_API_KEY ni RESEND_API_KEY) — étape ignorée.")
            return True
        return False

    status, detail = http_post_json(
        "https://api.resend.com/emails",
        {"from": sender, "to": [EMAIL_TO], "subject": subject, "html": html},
        headers={"Authorization": "Bearer %s" % resend_key},
    )
    if status in (200, 201):
        log("E-mail (Resend) : envoyé à %s (objet : %s)." % (EMAIL_TO, subject))
        return True
    log("E-mail (Resend) : échec (statut=%s, détail=%s)" % (status, detail))
    return False


# -------------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Notifications de la veille incendie Cap-Ferret (Telegram + e-mail Resend)."
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=["digest", "urgent", "info"],
        help="digest/urgent = Telegram + e-mail ; info = Telegram seul.",
    )
    parser.add_argument("--subject", default="", help="Objet de l'e-mail (facultatif).")
    parser.add_argument(
        "--summary", default="", help="Texte court remplaçant la headline (facultatif)."
    )
    args = parser.parse_args(argv)

    data = load_data()
    if data is None:
        return 2

    ok = send_telegram(data, args.summary)

    if args.kind in ("digest", "urgent"):
        ok = send_email(data, args.subject, args.summary) and ok
    else:
        log("Kind « info » : pas d'e-mail, Telegram uniquement.")

    if ok:
        log("Terminé sans erreur.")
        return 0
    log("Terminé avec au moins un échec d'envoi.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
