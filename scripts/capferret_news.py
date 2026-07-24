#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Veille presse — incendie Cap-Ferret : articles récents + photos édito.

Usage :
    python3 scripts/capferret_news.py [--hours 4] [--max 12] [--photos]

- Interroge Google News RSS (sans clé) sur plusieurs requêtes, dédoublonne,
  trie par fraîcheur : titre | source | heure FR | lien.
- --photos : ouvre les articles les plus récents et extrait leur image
  éditoriale (balise og:image) → candidates pour les pulses (à créditer
  « photo : <source> »).
- Les sites qui bloquent (403/paywall) sont ignorés silencieusement.

Croisement : un fait n'est considéré solide que s'il apparaît dans ≥ 2 sources
indépendantes ou 1 source officielle (préfecture/SDIS). Ce script fournit la
matière ; le croisement reste un jugement du cycle de veille.
Stdlib uniquement.
"""

import argparse
import datetime
import email.utils
import html
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

QUERIES = [
    "incendie gironde cap-ferret",
    "incendie Saumos évacuation",
    "feu Lège-Cap-Ferret bassin d'Arcachon",
]
UA = {"User-Agent": "Mozilla/5.0 (compatible; capferret-veille/1.0)"}


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, OSError, ValueError):
        return ""


def rss_items(query):
    url = ("https://news.google.com/rss/search?q=%s&hl=fr&gl=FR&ceid=FR:fr"
           % urllib.parse.quote(query))
    xml = fetch(url)
    items = []
    for m in re.finditer(r"<item>(.*?)</item>", xml, re.S):
        block = m.group(1)
        def tag(name):
            t = re.search(r"<%s>(.*?)</%s>" % (name, name), block, re.S)
            return html.unescape(t.group(1).strip()) if t else ""
        title = re.sub(r"<!\[CDATA\[|\]\]>", "", tag("title"))
        link = re.sub(r"<!\[CDATA\[|\]\]>", "", tag("link"))
        source = re.search(r"<source[^>]*>(.*?)</source>", block, re.S)
        source = html.unescape(source.group(1).strip()) if source else "?"
        try:
            dt = email.utils.parsedate_to_datetime(tag("pubDate"))
        except (TypeError, ValueError):
            dt = None
        items.append((dt, title, source, link))
    return items


def og_image(article_url):
    """Extrait og:image (photo éditoriale) d'un article. '' si indisponible."""
    page = fetch(article_url)
    for pattern in (
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
    ):
        m = re.search(pattern, page, re.I)
        if m:
            return html.unescape(m.group(1))
    return ""


def main(argv=None):
    parser = argparse.ArgumentParser(description="Veille presse Cap-Ferret.")
    parser.add_argument("--hours", type=int, default=4,
                        help="Fenêtre de fraîcheur en heures (défaut 4).")
    parser.add_argument("--max", type=int, default=12,
                        help="Nombre max d'articles listés (défaut 12).")
    parser.add_argument("--photos", action="store_true",
                        help="Extraire aussi les photos éditoriales (og:image).")
    args = parser.parse_args(argv)

    cutoff = (datetime.datetime.now(datetime.timezone.utc)
              - datetime.timedelta(hours=args.hours))
    seen_titles, rows = set(), []
    for q in QUERIES:
        for dt, title, source, link in rss_items(q):
            key = title[:80].lower()
            if key in seen_titles:
                continue
            seen_titles.add(key)
            if dt and dt < cutoff:
                continue
            rows.append((dt or datetime.datetime.now(datetime.timezone.utc),
                         title, source, link))
    rows.sort(key=lambda r: r[0], reverse=True)
    rows = rows[:args.max]

    if not rows:
        print("(aucun article frais sur %d h)" % args.hours)
        return 0

    fr = datetime.timezone(datetime.timedelta(hours=2))
    for dt, title, source, link in rows:
        print("[%s FR] %s — %s" % (dt.astimezone(fr).strftime("%H:%M"), source, title))
        print("        %s" % link)
        if args.photos:
            img = og_image(link)
            if img:
                print("        📸 %s (crédit : %s)" % (img, source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
