# Veille automatique Cap-Ferret — runbook

Runbook pour les sessions automatiques qui mettent à jour la page
`cap-ferret-aout-2026.html` (servie sur https://fables.comptoiria.com/cap-ferret-aout-2026.html)
toutes les 3 heures, entre 7h et 22h heure française.

## 1. Le contrat JSON : `data/capferret-live.json`

C'est l'API entre la page (dashboard live), le script de notification et la
routine. Tous les champs sont obligatoires.

```json
{
  "updated": "2026-07-24T09:30:00Z",
  "updated_label": "vendredi 24 juillet, 11h30",
  "level": "critical",
  "level_label": "Feu actif — presqu'île évacuée",
  "headline": "L'incendie de Saumos dépasse 10 000 ha ; évacuation totale de la presqu'île ordonnée, feu toujours virulent.",
  "prob_ok": 35,
  "prob_degraded": 30,
  "prob_cancelled": 35,
  "stats": { "hectares": "10 000+", "evacues": "40 000", "pompiers": "800+", "statut_feu": "actif, non maîtrisé" },
  "journal": [
    { "time": "2026-07-24T08:00:00Z", "time_label": "ven. 24/07, 10h00", "level": "critical", "text": "…" }
  ],
  "next_check_label": "prochaine vérification vers 14h00"
}
```

Règles :

- `level` ∈ `good` | `warning` | `serious` | `critical` (idem pour le `level`
  de chaque entrée du journal).
- `updated` et `time` en UTC (ISO 8601, suffixe `Z`) ; `updated_label` et
  `time_label` en heure française, en français.
- `prob_ok` + `prob_degraded` + `prob_cancelled` = 100 (entiers).
- `journal` : ordre antichronologique (le plus récent en premier). Ajouter une
  entrée à chaque évolution notable ; ne jamais réécrire l'historique, sauf
  correction factuelle.
- `next_check_label` : prochaine passe de la routine (« prochaine vérification
  vers 14h00 » ; le soir : « prochaine vérification demain vers 7h00 »).

## 2. Procédure de mise à jour (à chaque passe)

1. **Recherche web** : points de situation de la préfecture de la Gironde,
   ICI/France Bleu Gironde, France 3 Nouvelle-Aquitaine, feuxdeforet.fr,
   Météo-France (météo des forêts). Chercher : surface parcourue, évacuations
   (ordres ou levées), feu « fixé » / « maîtrisé » / « éteint », reprises,
   météo à venir.
2. **Mettre à jour `data/capferret-live.json`** (contrat ci-dessus) : niveau,
   headline, stats, probabilités, nouvelle entrée de journal si évolution.
3. Si les chiffres clés de la page statique deviennent faux (tuiles de la
   section « Ce qui se passe en ce moment », graphiques, verdict), les mettre
   à jour aussi dans `cap-ferret-aout-2026.html`.
4. **Commit + push** sur la branche `claude/cap-ferret-vacation-fire-risk-94u72s`
   (jamais sur `main`) :
   ```bash
   git add data/capferret-live.json cap-ferret-aout-2026.html
   git commit -m "Veille Cap-Ferret : point de situation du <date/heure>"
   git push origin claude/cap-ferret-vacation-fire-risk-94u72s
   ```
5. **Redéployer** depuis la racine du repo :
   ```bash
   vercel --prod --yes --token "$VERCEL_TOKEN"
   ```
   Si `.vercel/project.json` manque, le recréer d'abord :
   ```bash
   mkdir -p .vercel && cat > .vercel/project.json <<'EOF'
   {"projectId":"prj_xlhhny18IWIlGhbG9CpkeMTb6LCj","orgId":"team_Go7sLeDrEMzn9KdyzZkVwD9X"}
   EOF
   ```
6. **Notifier** selon la politique ci-dessous (script `scripts/capferret_notify.py`).

## 3. Politique de notification

Le script : `python3 scripts/capferret_notify.py --kind digest|urgent|info
[--subject "…"] [--summary "…"]` (stdlib uniquement ; lit le JSON, log et
continue proprement si une clé d'API manque).

- **Telegram** (`--kind info` suffit) : à **chaque changement** notable —
  nouvelle entrée de journal, évolution des stats ou des probabilités.
- **E-mail** (`--kind digest` ou `--kind urgent`) :
  - **Digests** : deux par jour, aux passes de **7h** et de **19h** heure
    française (`--kind digest`).
  - **Urgences**, immédiatement (`--kind urgent` + `--subject` explicite) :
    - feu déclaré **fixé** ou **maîtrisé** ;
    - **levée** ou **extension** d'un ordre d'évacuation ;
    - **reprise** du feu ;
    - toute **bascule de `level`** (dans un sens ou dans l'autre).
- Destinataire e-mail : nicolas@comptoiria.com, via l'API **AgentMail**
  (`AGENTMAIL_API_KEY`, boîte d'envoi `nico-fireflies@agentmail.to`), avec
  Resend en secours (`RESEND_API_KEY`, `RESEND_FROM_DEFAULT`). Attention :
  `api.resend.com` est bloqué par la politique de sortie de l'environnement
  Claude Code — AgentMail est la voie qui fonctionne, testée le 24/07/2026.

## 4. Activer Telegram

1. Créer un bot : parler à [@BotFather](https://t.me/BotFather) sur Telegram,
   commande `/newbot`, choisir un nom et un identifiant → BotFather donne le
   **token** (forme `123456789:AAH…`).
2. Récupérer le chat_id : envoyer un message quelconque au bot depuis son
   compte, puis :
   ```bash
   curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates" | python3 -m json.tool
   ```
   → le `chat.id` de l'update est le **chat_id**.
3. Définir `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` dans les variables
   d'environnement de l'environnement Claude Code (paramètres de
   l'environnement sur claude.ai/code).
4. Tant que ces variables sont absentes, le script logge « Telegram non
   configuré » et continue sans erreur : rien d'autre à faire.

## 6. Sources X / Twitter (prioritaires pour le temps réel)

X est souvent en avance de 1 à 3 h sur la presse pour cette crise. À chaque
cycle, lancer des recherches web ciblées (les posts X ressortent bien via la
recherche web classique) :

- **Comptes officiels** : `@PrefAquitaine33` (préfète — points de situation,
  ordres d'évacuation, routes), `@SDIS33` (pompiers de la Gironde),
  `@SecCivileFrance`, `@Interieur_Gouv`, `@VigiMeteoFrance`, mairie
  `Lège-Cap-Ferret`.
- **Requêtes types** :
  - `x.com PrefAquitaine33 incendie Saumos Cap-Ferret point de situation`
  - `x.com SDIS33 OR SecCivileFrance Gironde feu`
  - `twitter "Lège-Cap-Ferret" OR #Saumos évacuation OR réouverture OR fixé`
- Toujours **recouper avec le communiqué préfectoral** avant de qualifier un
  événement de majeur ; les posts officiels de @PrefAquitaine33 valent
  communiqué (les citer dans le journal avec leur URL x.com).

## 7. Publication automatique sur X (via Late)

La publication passe par l'API Late (getlate.dev) — la clé `LATE_API_KEY` est
dans l'environnement, le compte X connecté est « Nicolas Guyon - e/acc »
(accountId `69a8b75bdc8cab9432b8bf60`). Un point toutes les 3 h (cycles UTC
5/8/11/14/17/20), ≤ 280 caractères (une URL compte 23), terminé par « Suivi en
continu : t.me/Capfeuretbot » + lien dashboard, avec image satellite :

```bash
curl -s -X POST "https://getlate.dev/api/v1/posts" \
  -H "Authorization: Bearer $LATE_API_KEY" -H "Content-Type: application/json" \
  -d '{"content":"<texte>","publishNow":true,
       "platforms":[{"platform":"twitter","accountId":"69a8b75bdc8cab9432b8bf60"}],
       "mediaItems":[{"type":"image","url":"<URL image publique>"}]}'
```

Pour l'image : réutiliser l'URL snapshot NASA Worldview du moment (publique),
ou un asset poussé dans `social/capferret/` (servi sur
https://fables.comptoiria.com/social/capferret/…). Vérifier ensuite
`GET /api/v1/posts/<id>` → `status: published`. L'ancien script
`capferret_xpost.py` (API X directe) reste en secours si Late est indisponible.

## 8. Veille X temps réel (Apify)

`python3 scripts/capferret_x_live.py [--minutes 45] [--max 25] [--officiels]`
interroge X en TEMPS RÉEL via l'acteur Apify
`kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest`
(`APIFY_TOKEN` dans l'environnement). Sort un digest antichronologique
horodaté (heure française). À chaque cycle : lancer d'abord `--officiels
--minutes 90` (préfète/SDIS/Sécurité civile = source faisant foi), puis sans
option pour le bruit ambiant (témoins, médias). C'est CE canal qui a détecté
l'extension des évacuations à Arès/Andernos/Le Temple/Saumos 11 minutes après
le post de la préfète, avant toute reprise presse. Coût : pay-per-result
(~0,2 $/1 000 tweets) — rester sur des maxItems raisonnables (15-25).
