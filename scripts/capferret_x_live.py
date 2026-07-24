#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veille X (Twitter) temps réel via Apify — incendie Cap-Ferret.

Usage :
    python3 scripts/capferret_x_live.py [--minutes 45] [--max 25] [--officiels]

Sort un digest texte antichronologique des tweets récents :
- recherche « Latest » sur l'incendie (incendie gironde, Cap-Ferret, Saumos) ;
- --officiels : uniquement les comptes officiels (préfète, SDIS, Sécurité
  civile, mairie), à recouper en priorité.

Acteur : kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest
(pay-per-result). Clé : APIFY_TOKEN (env ou .capferret-secrets.env).
Stdlib uniquement.
"""

import argparse
import datetime
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capferret_notify import load_local_secrets, log  # noqa: E402

ACTOR = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
SEARCH_QUERIES = [
    "incendie gironde",
    "\"Cap-Ferret\" OR \"Lège-Cap-Ferret\" OR Saumos feu OR incendie OR évacuation",
]
OFFICIAL_QUERY = ("from:PrefAquitaine33 OR from:SDIS33 OR from:SecCivileFrance "
                  "OR from:Interieur_Gouv OR from:VigiMeteoFrance")


def run_actor(token, query, max_items):
    url = ("https://api.apify.com/v2/acts/%s/run-sync-get-dataset-items"
           "?token=%s&timeout=120" % (ACTOR, token))
    payload = {"searchTerms": [query], "queryType": "Latest", "maxItems": max_items}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=170,
                                    context=ssl.create_default_context()) as resp:
            return json.load(resp)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log("Apify : erreur %s" % exc)
        return []


def parse_created(s):
    # format : "Fri Jul 24 13:31:39 +0000 2026"
    try:
        return datetime.datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
    except (ValueError, TypeError):
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Veille X live via Apify.")
    parser.add_argument("--minutes", type=int, default=45,
                        help="Fenêtre de fraîcheur en minutes (défaut 45).")
    parser.add_argument("--max", type=int, default=25,
                        help="Tweets max par requête (défaut 25).")
    parser.add_argument("--officiels", action="store_true",
                        help="Uniquement les comptes officiels.")
    parser.add_argument("--images", action="store_true",
                        help="Uniquement les tweets contenant des photos "
                             "(ajoute filter:images à la recherche, liste les URLs des médias).")
    args = parser.parse_args(argv)

    load_local_secrets()
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        log("APIFY_TOKEN absent — veille X live indisponible.")
        return 1

    queries = [OFFICIAL_QUERY] if args.officiels else list(SEARCH_QUERIES)
    if args.images:
        queries = [q + " filter:images" for q in queries]
    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(minutes=args.minutes))

    seen, rows = set(), []
    for q in queries:
        for t in run_actor(token, q, args.max):
            if not isinstance(t, dict) or not t.get("text"):
                continue
            if "From KaitoEasyAPI" in t["text"]:  # bourrage publicitaire de l'acteur
                continue
            tid = t.get("id") or t.get("url")
            if tid in seen:
                continue
            seen.add(tid)
            created = parse_created(t.get("createdAt"))
            if created and created < cutoff:
                continue
            media_urls = [m.get("media_url_https") or m.get("url") or ""
                          for m in ((t.get("extendedEntities") or {}).get("media") or [])
                          if m.get("type") == "photo"]
            if args.images and not media_urls:
                continue
            author = (t.get("author") or {})
            rows.append((
                created or datetime.datetime.now(datetime.timezone.utc),
                author.get("userName") or "?",
                bool(author.get("isVerified") or author.get("isBlueVerified")),
                (t.get("text") or "").replace("\n", " ").strip(),
                t.get("url") or "",
                media_urls,
            ))

    rows.sort(key=lambda r: r[0], reverse=True)
    if not rows:
        print("(aucun tweet frais sur la fenêtre de %d min)" % args.minutes)
        return 0
    for created, user, verified, text, url, media_urls in rows:
        hhmm = created.astimezone(datetime.timezone(datetime.timedelta(hours=2))).strftime("%H:%M")
        badge = "✔" if verified else " "
        print("[%s FR]%s @%-20s %s  %s" % (hhmm, badge, user, text[:240], url))
        for mu in media_urls:
            print("        📸 %s" % mu)
    return 0


if __name__ == "__main__":
    sys.exit(main())
