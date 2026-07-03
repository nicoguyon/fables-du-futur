# GTA : LA DOUANE — Édition Spéciale Canal Saint-Martin
### Film 30 s · style lancement GTA VI · Été 2026 · Canicule

## Note d'intention
Un faux trailer de lancement de GTA VI, comme les vidéos IA virales sur X : key-art
ultra-léché, HUD de gameplay incrusté (minimap, texte de mission, étoiles de recherche),
caméra 3ᵉ personne, coucher de soleil saturé rose-orange… sauf que Vice City, c'est le
canal Saint-Martin en pleine canicule, et le protagoniste, c'est **La Douane** : un ado
à trottinette armé d'un pistolet à eau qui fait payer le passage 2 €.

**Personnage (stylisé, inspiré du phénomène du canal — pas de reproduction du vrai
visage, c'est un personnage de jeu vidéo)** : "LA DOUANE", ado ~14 ans, fine silhouette,
dégradé court, débardeur blanc, short de foot, claquettes-chaussettes, banane en
bandoulière, énorme pistolet à eau orange fluo. Sourire effronté de star de quartier.

**Décor** : Canal Saint-Martin, Paris 10ᵉ — passerelles vertes en fer, écluses, platanes,
façades haussmanniennes, péniche, foules d'apéro sur les quais. Chaleur écrasante, brume
de canicule, ciel dégradé rose/orange façon Vice City.

## Découpage — 6 plans × 5 s = 30 s

| # | Plan | Description | HUD / Texte à l'écran |
|---|------|-------------|----------------------|
| 1 | **Title card** | Key-art de couverture : La Douane pose façon jaquette GTA, pistolet à eau en travers, passerelle et canal derrière, brume de chaleur | Logo **GTA — LA DOUANE** (style logo GTA VI rose/orange), « ÉDITION SPÉCIALE CANAL SAINT-MARTIN », « ÉTÉ 2026 · CANICULE » |
| 2 | **Gameplay trottinette** | Caméra 3ᵉ personne : il file sur le quai de Valmy, une chaise de bistrot verte sanglée sur sa trottinette, cyclistes qui s'écartent | Minimap en bas à gauche, mission « LA DOUANE DU CANAL » en bas, compteur « 2,00 € » |
| 3 | **Le péage** | Cutscene : panneau carton « PÉAGE 2€ », cycliste en lycra à l'arrêt, La Douane le tient en joue au pistolet à eau | Popup « +2 € », minimap |
| 4 | **Recherché ★★★** | Il arrose deux policiers, jet d'eau en slow-mo dans la lumière dorée, pigeons qui s'envolent | 3 étoiles de recherche en haut à droite, minimap |
| 5 | **Le plongeon** | Plan large : saut périlleux depuis la passerelle dans le canal, la foule filme au smartphone, gerbe d'eau | Minimap, « MISSION ACCOMPLIE » discret |
| 6 | **Outro trône** | Assis en majesté sur la chaise de bistrot posée sur la trottinette, trempé, pistolet sur l'épaule, contre-jour coucher de soleil | « PROCHAINEMENT » + « ÉTÉ 2026 · CANICULE » |

## Pipeline (imposé)
- **Images de départ** : OpenAI **GPT Image 2** (`gpt-image-2`), 1536×1024, HUD et titres
  incrustés dans l'image (c'est la technique des faux gameplays viraux).
- **Vidéo** : **Seedance 2.0** `image-to-video` sur fal.ai, **4K**, 5 s par plan, 16:9.
- **Musique** : **API Suno** — rap français été/canicule, codes radio GTA.
- **Montage** : Remotion + FFmpeg, rendu final 30 s.
