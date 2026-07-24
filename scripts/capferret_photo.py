#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envoie sur Telegram une image satellite récente de la zone Cap-Ferret / Saumos.

Usage :
    python3 scripts/capferret_photo.py --caption "Texte du message" [--date 2026-07-24]

- Image : NASA GIBS (WMS public, sans clé), couche VIIRS/MODIS vraie couleur
  + anomalies thermiques (points chauds des incendies), cadrée sur le bassin
  d'Arcachon et la presqu'île (lat 44.45–45.10, lon -1.45 – -0.70).
- Essaie la date du jour, puis la veille si l'image du jour n'est pas encore
  disponible (les passages satellites ont lieu en début d'après-midi).
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
from capferret_notify import load_local_secrets, log, telegram_chat_ids  # noqa: E402

GIBS_WMS = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"
BBOX = "44.45,-1.45,45.10,-0.70"  # lat_min,lon_min,lat_max,lon_max (WMS 1.3.0)
LAYER_SETS = [
    "VIIRS_SNPP_CorrectedReflectance_TrueColor,VIIRS_SNPP_Thermal_Anomalies_375m_All",
    "MODIS_Terra_CorrectedReflectance_TrueColor,MODIS_Terra_Thermal_Anomalies_All",
]


def fetch_satellite_image(date_str):
    """Renvoie (bytes_jpeg, description) ou (None, None)."""
    context = ssl.create_default_context()
    for layers in LAYER_SETS:
        url = (
            GIBS_WMS
            + "?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&CRS=EPSG:4326"
            + "&LAYERS=" + layers
            + "&BBOX=" + BBOX
            + "&WIDTH=900&HEIGHT=780&FORMAT=image/jpeg"
            + "&TIME=" + date_str
        )
        try:
            with urllib.request.urlopen(url, timeout=45, context=context) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type", "")
                if resp.status == 200 and "image" in ctype and len(data) > 20000:
                    sat = "VIIRS" if "VIIRS" in layers else "MODIS"
                    return data, "%s — %s" % (sat, date_str)
                log("GIBS %s %s : réponse non exploitable (%s, %d octets)"
                    % (layers.split(",")[0], date_str, ctype, len(data)))
        except (urllib.error.URLError, OSError) as exc:
            log("GIBS %s : erreur %s" % (date_str, exc))
    return None, None


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
    args = parser.parse_args(argv)

    load_local_secrets()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_ids = telegram_chat_ids(token)
    if not token or not chat_ids:
        log("Telegram non configuré — abandon.")
        return 1

    if args.date:
        dates = [args.date]
    else:
        today = datetime.date.today()
        dates = [str(today), str(today - datetime.timedelta(days=1))]

    image, desc = None, None
    if args.photo_url:
        image = fetch_url_image(args.photo_url)
        desc = None
    if image is None:
        for date_str in dates:
            image, desc = fetch_satellite_image(date_str)
            if image:
                break

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
