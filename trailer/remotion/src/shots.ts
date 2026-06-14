// Données du montage : 12 plans × 5 s (150 frames @30fps) = 1800 frames = 60 s.
// Le texte est le carton-titre affiché en surimpression sur le plan (vide = pas de carton).

export const FPS = 30;
export const SHOT_FRAMES = 150; // 5 s
export const WIDTH = 2560;
export const HEIGHT = 1097; // 21:9

export type Shot = {
  file: string; // dans public/clips/
  title?: string; // carton-titre en surimpression
  big?: boolean; // titre principal (gros)
};

export const SHOTS: Shot[] = [
  { file: "clips/shot01.mp4", title: "Julien avait une vie parfaite." },
  { file: "clips/shot02.mp4", title: "Une famille parfaite." },
  { file: "clips/shot03.mp4", title: "Jusqu'à cette chute." },
  { file: "clips/shot04.mp4", title: "Cette jambe n'était plus la sienne." },
  { file: "clips/shot05.mp4", title: "Il a tout essayé." },
  { file: "clips/shot06.mp4" },
  { file: "clips/shot07.mp4" },
  { file: "clips/shot08.mp4", title: "En vain." },
  { file: "clips/shot09.mp4", title: "Un homme s'obstinait à le réparer." },
  { file: "clips/shot10.mp4", title: "Alors il a trouvé une autre solution." },
  { file: "clips/shot11.mp4", title: "Il avait enfin gagné. Et tout perdu." },
  { file: "clips/shot12.mp4", title: "SIMPLE COMME UNE AMPUTATION", big: true },
];

export const DURATION = SHOTS.length * SHOT_FRAMES; // 1800
