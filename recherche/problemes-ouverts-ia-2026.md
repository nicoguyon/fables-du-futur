# Faire avancer la science avec une IA — état des lieux & problèmes candidats (août 2026)

*Document de travail — Nico × Claude. Objectif : identifier 1 à 2 problèmes ouverts (maths / logique / physique computationnelle) où une contribution réelle et **vérifiable** est possible en 1–2 semaines.*

---

## 1. Ce qui s'est vraiment passé (2025–2026)

Le contexte dont tu parlais est réel, et il est même encore plus avancé que ce que tu as entendu :

- **Sébastien Bubeck (OpenAI)** a fait produire à GPT-5 Pro une **amélioration de borne dans un problème ouvert d'optimisation convexe** (de 1/L à 1.5/L), preuve vérifiée à la main. Il a aussi montré que GPT-5 est « surhumain en recherche bibliographique » : le problème d'Erdős #339, listé ouvert, était en fait résolu depuis 20 ans.
- **erdosproblems.com** (site de Thomas Bloom, poussé par Terence Tao) : ~1217 problèmes, ~46 % résolus. Depuis fin 2025, des dizaines de problèmes ont été résolus ou faits avancer **avec des modèles du commerce** (GPT-5.x, Gemini, Claude, Aristotle de Harmonic, AlphaProof). Le wiki officiel [AI contributions to Erdős problems](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) documente qui a fait quoi, avec quel modèle, et comment c'est vérifié (Lean + relecture humaine).
- **DeepMind AlphaEvolve** : un agent « évolutionnaire » qui fait écrire des programmes de recherche par un LLM et garde les meilleurs. Résultats : nouveau record du **kissing number en dimension 11** (593 sphères), amélioration de **5 bornes inférieures de nombres de Ramsey**, amélioration de la constante θ des ensembles sommes/différences (1.14465 → 1.1584, ensuite encore battue par des humains). Le dépôt public [alphaevolve_repository_of_problems](https://github.com/google-deepmind/alphaevolve_repository_of_problems) contient **67 problèmes avec le code de vérification** — reproductible dans un simple Colab.
- **Terence Tao** défend une vision de « big mathematics » : des humains + IA qui collaborent à grande échelle, les humains gardant la partie créative et le contrôle qualité (conférence ICM 2026, « Mathematics in the age of AI »).

**La leçon clé** : les contributions qui tiennent la route ont toutes un point commun — un **vérificateur indépendant** (un script qui checke un certificat, une preuve Lean, ou un mathématicien qui relit). C'est ça notre boussole.

---

## 2. Où NOUS pouvons réellement contribuer

Trois familles, classées par rapport chance-de-réussite / vérifiabilité :

### Famille A — Records de constructions (vérification automatique, zéro risque d'erreur)
Le principe : on ne cherche pas une *preuve*, on cherche un *objet* (un coloriage, un ensemble de points, une configuration) qui bat le record connu. Un script de 50 lignes vérifie l'objet. **On ne peut pas se tromper.**

| # | Problème | Ce qu'on cherche | Vérification | Concurrence |
|---|----------|------------------|--------------|-------------|
| A1 | **Bornes inférieures de nombres de Ramsey** (petits cas, ex. R(3,k), R(4,k), Ramsey de livres/roues) | Un coloriage de graphe sans la structure interdite | Script en secondes | Forte mais des amateurs ont récemment amélioré R(3,13)→61, R(3,18)→100 |
| A2 | **Problèmes du dépôt AlphaEvolve** où le record n'a PAS été amélioré | Une construction qui bat le score du notebook | Le code de vérif est fourni par DeepMind | Moyenne — le terrain de jeu idéal |
| A3 | **Kissing numbers / empilements de sphères** en petites dimensions | Configuration de points sur la sphère | Vérif des distances par script | Forte sur les cas connus |
| A4 | **Ensembles de Sidon, ensembles sommes/différences, autocorrélation** (très « Erdős ») | Un ensemble d'entiers avec la bonne propriété | Script trivial | Moyenne |
| A5 | **Nombres de van der Waerden / Schur** (bornes inférieures) | Un coloriage de {1..n} sans progression monochrome | Script trivial | Faible sur les cas exotiques |

### Famille B — Contributions « secondaires » officielles au projet Erdős (accessibles, reconnues)
- **B1. Chasse bibliographique** : prendre des problèmes listés « ouverts » sur erdosproblems.com et chercher en profondeur s'ils ont déjà été résolus (c'est exactement le coup du #339 de Bubeck). Chaque trouvaille validée est une vraie contribution à la base, créditée sur le site.
- **B2. Formalisation Lean** : le projet [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) de DeepMind veut formaliser *tous* les problèmes d'Erdős ouverts. Contribuer une formalisation est vérifiable par le compilateur Lean lui-même, et c'est une contribution citée.
- **B3. Liaison erdosproblems ↔ OEIS** : projet crowdsourcé en cours, barrière d'entrée basse.

### Famille C — Physique / STEM computationnel (ton envie « mécanique / électronique »)
Plus dur à vérifier sans labo, mais il existe des records numériques vérifiables :
- **C1. Problème de Thomson** (électrons sur une sphère, minimum d'énergie) — records numériques publiés, vérification = calcul d'énergie.
- **C2. Chorégraphies du problème à N corps** (nouvelles orbites périodiques) — vérification par intégration numérique de haute précision.
- **C3. Structures optimales** (codes correcteurs, packings de codes) — tables de records publiques (codetables.de), vérification automatique.

### À éviter (pour être honnête)
- Riemann, Collatz, P≠NP : aucune chance exploitable, même avec beaucoup de calcul.
- Le canapé mobile (moving sofa) : résolu fin 2024 par Jineon Baek.
- Une « vraie » preuve de théorème entièrement nouvelle : possible mais rare ; les labos frontière y mettent des moyens énormes. Notre niche réaliste, c'est A + B.

---

## 3. Recommandation : les 2 pistes à lancer

1. **Piste principale (A2 + A4/A5)** : choisir 2–3 problèmes du dépôt AlphaEvolve (ou de type Erdős combinatoire) avec vérificateur fourni, reproduire le record actuel, puis lancer une boucle de recherche type AlphaEvolve (Claude écrit et fait évoluer des heuristiques, on calcule, on vérifie). Résultat espéré : battre un record documenté → contribution publiable immédiatement (le certificat parle de lui-même).
2. **Piste parallèle (B1)** : chasse bibliographique sur ~20 problèmes Erdős « ouverts » peu regardés. Coût faible, et chaque trouvaille est une contribution officielle créditée.

## 4. Protocole (anti-erreur, avec GPT-5 en second avis)

1. **Sélection** : ne retenir un problème que s'il a (a) un vérificateur automatisable en < 100 lignes, (b) un record actuel documenté et daté, (c) un espace de recherche attaquable sans méga-GPU.
2. **Baseline obligatoire** : reproduire et vérifier le record connu. Si on n'y arrive pas → on change de problème.
3. **Boucle de recherche** : Claude génère des constructions/heuristiques, exécute, garde les meilleures (style évolutionnaire). Journal de bord committé dans ce repo.
4. **Croisement GPT-5** : Nico soumet à GPT-5 Pro (a) le problème pour des idées de constructions alternatives, (b) la recherche bibliographique (son point fort démontré), (c) toute preuve candidate pour tentative de réfutation. Règle d'or : **aucun résultat accepté sans vérification par un script indépendant** (écrit séparément, idéalement par l'autre modèle) — jamais juste parce que les deux IA sont d'accord.
5. **Publication** : record battu → certificat + script dans un repo public + soumission à la base concernée (erdosproblems.com via GitHub, tables de records, arXiv note si pertinent), avec mention transparente de l'assistance IA.

---

## Sources principales
- [Wiki « AI contributions to Erdős problems » (Tao)](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems)
- [erdosproblems.com](https://www.erdosproblems.com/)
- [Dépôt des 67 problèmes AlphaEvolve](https://github.com/google-deepmind/alphaevolve_repository_of_problems) et [« Mathematical exploration and discovery at scale » (Tao et al.)](https://terrytao.wordpress.com/2025/11/05/mathematical-exploration-and-discovery-at-scale/)
- [Bubeck : GPT-5 Pro améliore une borne en optimisation convexe](https://x.com/SebastienBubeck/status/1958198661139009862) · [GPT-5 « résout » Erdős #339 par bibliographie](https://x.com/SebastienBubeck/status/1977181716457701775)
- [Quanta : « Why the Legendary Erdős Problems Are Falling to AI »](https://www.quantamagazine.org/why-the-legendary-erdos-problems-are-falling-to-ai-20260803/)
- [Quanta : « How Terry Tao Became an Evangelist for AI in Math »](https://www.quantamagazine.org/how-terry-tao-became-an-evangelist-for-ai-in-math-20260608/)
- [Certificats vérifiés SAT+CAS pour R(3,8) et R(3,9)](https://arxiv.org/pdf/2502.06055)
- [formal-conjectures (DeepMind) — formaliser tous les problèmes d'Erdős](https://github.com/google-deepmind/formal-conjectures/milestone/1)
