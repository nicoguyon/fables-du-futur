#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Poste un point de situation sur X (Twitter), avec image optionnelle.

Usage :
    python3 scripts/capferret_xpost.py --text "Point de situation…" [--image chemin.jpg]

Clés requises (variables d'environnement ou .capferret-secrets.env) :
    X_API_KEY, X_API_SECRET          (consumer keys de l'app X)
    X_ACCESS_TOKEN, X_ACCESS_SECRET  (jetons du compte qui poste)

- Texte : POST https://api.x.com/2/tweets (JSON), auth OAuth 1.0a user context.
- Image : upload préalable via https://upload.twitter.com/1.1/media/upload.json
  (multipart), puis attachée au tweet.
Stdlib uniquement. Sans clés : log clair + code retour 1, jamais d'exception.
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capferret_notify import load_local_secrets, log  # noqa: E402


def pct(value):
    """Percent-encode RFC 3986 strict (OAuth exige ~ non encodé)."""
    return urllib.parse.quote(str(value), safe="~")


def oauth_header(method, url, creds, extra_params=None):
    """Construit l'en-tête Authorization OAuth 1.0a (signature HMAC-SHA1)."""
    api_key, api_secret, access_token, access_secret = creds
    oauth = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }
    all_params = dict(oauth)
    all_params.update(extra_params or {})
    param_str = "&".join(
        "%s=%s" % (pct(k), pct(all_params[k])) for k in sorted(all_params)
    )
    base = "&".join([method.upper(), pct(url), pct(param_str)])
    key = ("%s&%s" % (pct(api_secret), pct(access_secret))).encode()
    sig = base64.b64encode(hmac.new(key, base.encode(), hashlib.sha1).digest()).decode()
    oauth["oauth_signature"] = sig
    return "OAuth " + ", ".join(
        '%s="%s"' % (pct(k), pct(oauth[k])) for k in sorted(oauth)
    )


def upload_media(image_path, creds):
    """Upload l'image (v1.1 media/upload, multipart). Renvoie media_id ou None."""
    try:
        with open(image_path, "rb") as fh:
            payload = fh.read()
    except OSError as exc:
        log("xpost : image illisible (%s)" % exc)
        return None

    url = "https://upload.twitter.com/1.1/media/upload.json"
    boundary = uuid.uuid4().hex
    body = b"".join([
        ("--%s\r\nContent-Disposition: form-data; name=\"media\"; "
         "filename=\"situation.jpg\"\r\nContent-Type: application/octet-stream\r\n\r\n"
         % boundary).encode(),
        payload,
        ("\r\n--%s--\r\n" % boundary).encode(),
    ])
    req = urllib.request.Request(url, data=body, method="POST")
    # Les champs multipart ne participent pas à la signature OAuth.
    req.add_header("Authorization", oauth_header("POST", url, creds))
    req.add_header("Content-Type", "multipart/form-data; boundary=%s" % boundary)
    try:
        with urllib.request.urlopen(req, timeout=60,
                                    context=ssl.create_default_context()) as resp:
            data = json.load(resp)
            media_id = data.get("media_id_string")
            if media_id:
                log("xpost : image uploadée (media_id %s)." % media_id)
            return media_id
    except urllib.error.HTTPError as exc:
        log("xpost media/upload : HTTP %s — %s" % (exc.code, exc.read()[:200]))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log("xpost media/upload : erreur %s" % exc)
    return None


def post_tweet(text, media_id, creds):
    """POST /2/tweets. Renvoie l'id du tweet ou None."""
    url = "https://api.x.com/2/tweets"
    payload = {"text": text}
    if media_id:
        payload["media"] = {"media_ids": [media_id]}
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", oauth_header("POST", url, creds))
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30,
                                    context=ssl.create_default_context()) as resp:
            data = json.load(resp)
            return (data.get("data") or {}).get("id")
    except urllib.error.HTTPError as exc:
        log("xpost /2/tweets : HTTP %s — %s" % (exc.code, exc.read()[:300]))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        log("xpost /2/tweets : erreur %s" % exc)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Point de situation → X.")
    parser.add_argument("--text", required=True, help="Texte du post (≤ 280 caractères).")
    parser.add_argument("--image", default="", help="Chemin d'une image jpeg/png à joindre.")
    args = parser.parse_args(argv)

    load_local_secrets()
    creds = tuple(
        os.environ.get(k, "").strip()
        for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")
    )
    if not all(creds):
        log("xpost : clés X absentes (X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN / "
            "X_ACCESS_SECRET) — publication ignorée.")
        return 1

    if len(args.text) > 280:
        log("xpost : texte tronqué à 280 caractères.")
        args.text = args.text[:277] + "…"

    media_id = upload_media(args.image, creds) if args.image else None
    tweet_id = post_tweet(args.text, media_id, creds)
    if tweet_id:
        log("xpost : publié — https://x.com/i/status/%s" % tweet_id)
        return 0
    log("xpost : échec de publication.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
