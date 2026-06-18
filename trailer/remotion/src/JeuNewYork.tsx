/**
 * NEW YORK — le jeu vidéo · teaser 15 s (450 frames @ 30fps, 1920×1080)
 * Rendu 100 % par code (SVG + React), sans API externe.
 * Personnages : Yosh (pond un champignon), Mara (comme Mario, plus grand & rapide),
 * Pirates (bras-canon). Monde : Manhattan 2027, grand soleil, taxis/vélos/piétons,
 * tornades et gratte-ciel qui s'effondrent. Règles de vie affichées dans le HUD.
 */
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Easing,
  random,
} from "remotion";

export const NY_FPS = 30;
export const NY_W = 1920;
export const NY_H = 1080;
export const NY_DURATION = 450; // 15 s

const FONT = "'Arial Black', 'Helvetica Neue', Arial, sans-serif";

/* ------------------------------------------------------------------ *
 *  DÉCOR
 * ------------------------------------------------------------------ */

const Sun: React.FC<{ x?: number; y?: number }> = ({ x = 1640, y = 180 }) => {
  const frame = useCurrentFrame();
  const rot = frame * 0.4;
  return (
    <g transform={`translate(${x} ${y})`}>
      <g transform={`rotate(${rot})`} opacity={0.85}>
        {Array.from({ length: 12 }).map((_, i) => (
          <rect
            key={i}
            x={-6}
            y={-150}
            width={12}
            height={48}
            rx={6}
            fill="#ffe27a"
            transform={`rotate(${i * 30})`}
          />
        ))}
      </g>
      <circle r={92} fill="#ffd23f" />
      <circle r={92} fill="#fff27a" opacity={0.5} />
    </g>
  );
};

const Cloud: React.FC<{ x: number; y: number; s: number; speed: number }> = ({
  x,
  y,
  s,
  speed,
}) => {
  const frame = useCurrentFrame();
  const cx = ((x + frame * speed) % (NY_W + 400)) - 200;
  return (
    <g transform={`translate(${cx} ${y}) scale(${s})`} fill="#ffffff" opacity={0.9}>
      <ellipse cx={0} cy={0} rx={70} ry={42} />
      <ellipse cx={60} cy={10} rx={55} ry={34} />
      <ellipse cx={-55} cy={12} rx={48} ry={30} />
    </g>
  );
};

const Building: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  fill: string;
  win: string;
  seed: number;
}> = ({ x, y, w, h, fill, win, seed }) => {
  const cols = Math.max(2, Math.floor(w / 26));
  const rows = Math.max(3, Math.floor(h / 34));
  const cells: React.ReactNode[] = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const on = random(`${seed}-${r}-${c}`) > 0.45;
      cells.push(
        <rect
          key={`${r}-${c}`}
          x={x + 9 + c * (w / cols)}
          y={y + 14 + r * (h / rows)}
          width={Math.max(6, w / cols - 9)}
          height={Math.max(8, h / rows - 12)}
          fill={on ? win : "#27324a"}
          opacity={on ? 0.95 : 0.5}
          rx={1.5}
        />
      );
    }
  }
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} fill={fill} rx={3} />
      <rect x={x} y={y} width={w} height={10} fill="#ffffff" opacity={0.12} />
      {cells}
    </g>
  );
};

// Skyline déterministe, en bandes de parallaxe.
const Skyline: React.FC<{
  baseY: number;
  count: number;
  fill: string;
  win: string;
  minH: number;
  maxH: number;
  seedKey: string;
  scroll: number;
}> = ({ baseY, count, fill, win, minH, maxH, seedKey, scroll }) => {
  const frame = useCurrentFrame();
  const dx = -((frame * scroll) % 260);
  const items: React.ReactNode[] = [];
  let x = -260 + dx;
  for (let i = 0; i < count + 2; i++) {
    const r1 = random(`${seedKey}-w-${i}`);
    const r2 = random(`${seedKey}-h-${i}`);
    const w = 120 + r1 * 110;
    const h = minH + r2 * (maxH - minH);
    items.push(
      <Building
        key={i}
        x={x}
        y={baseY - h}
        w={w}
        h={h}
        fill={fill}
        win={win}
        seed={1000 * i + seedKey.length}
      />
    );
    x += w + 18 + random(`${seedKey}-g-${i}`) * 26;
  }
  return <g>{items}</g>;
};

const Street: React.FC = () => (
  <g>
    <rect x={0} y={NY_H - 150} width={NY_W} height={36} fill="#b9b2a6" />
    <rect x={0} y={NY_H - 114} width={NY_W} height={114} fill="#3a3f4a" />
    <rect x={0} y={NY_H - 150} width={NY_W} height={5} fill="#d8d2c6" />
  </g>
);

const LaneDashes: React.FC = () => {
  const frame = useCurrentFrame();
  const dx = -((frame * 14) % 200);
  return (
    <g>
      {Array.from({ length: 14 }).map((_, i) => (
        <rect
          key={i}
          x={dx + i * 200}
          y={NY_H - 60}
          width={110}
          height={10}
          rx={5}
          fill="#ffd23f"
        />
      ))}
    </g>
  );
};

const Taxi: React.FC<{ x: number; flip?: boolean; scale?: number }> = ({
  x,
  flip,
  scale = 1,
}) => (
  <g transform={`translate(${x} ${NY_H - 150}) scale(${flip ? -scale : scale} ${scale})`}>
    <rect x={-90} y={-66} width={180} height={52} rx={14} fill="#ffd21f" />
    <rect x={-58} y={-92} width={108} height={34} rx={12} fill="#ffd21f" />
    <rect x={-50} y={-86} width={44} height={26} rx={6} fill="#bfe9ff" />
    <rect x={2} y={-86} width={44} height={26} rx={6} fill="#bfe9ff" />
    <rect x={-90} y={-40} width={180} height={12} fill="#111" />
    <g fill="#111">
      <rect x={-78} y={-46} width={14} height={10} />
      <rect x={-50} y={-46} width={14} height={10} />
      <rect x={-22} y={-46} width={14} height={10} />
    </g>
    <circle cx={-52} cy={-8} r={20} fill="#1a1a1a" />
    <circle cx={-52} cy={-8} r={9} fill="#777" />
    <circle cx={54} cy={-8} r={20} fill="#1a1a1a" />
    <circle cx={54} cy={-8} r={9} fill="#777" />
    <text x={0} y={-44} fontSize={16} fontFamily={FONT} fill="#111" textAnchor="middle">
      TAXI
    </text>
  </g>
);

const Bike: React.FC<{ x: number; scale?: number }> = ({ x, scale = 1 }) => {
  const frame = useCurrentFrame();
  return (
    <g transform={`translate(${x} ${NY_H - 150}) scale(${scale})`}>
      <circle cx={-24} cy={-10} r={18} fill="none" stroke="#222" strokeWidth={4} />
      <circle cx={24} cy={-10} r={18} fill="none" stroke="#222" strokeWidth={4} />
      <path d="M-24,-10 L0,-34 L24,-10 M0,-34 L6,-44" stroke="#e63946" strokeWidth={4} fill="none" />
      <circle cx={0} cy={-44} r={3} fill="#e63946" />
      <g transform={`translate(0 -46)`}>
        <circle cx={4} cy={-22} r={8} fill="#f1c27d" />
        <rect x={-4} y={-16} width={14} height={20} rx={4} fill="#3b82f6" transform={`rotate(${Math.sin(frame / 4) * 4})`} />
      </g>
    </g>
  );
};

const Pedestrian: React.FC<{ x: number; color: string; phase: number }> = ({
  x,
  color,
  phase,
}) => {
  const frame = useCurrentFrame();
  const swing = Math.sin((frame + phase) / 5) * 8;
  return (
    <g transform={`translate(${x} ${NY_H - 150})`}>
      <circle cx={0} cy={-44} r={8} fill="#f1c27d" />
      <rect x={-7} y={-38} width={14} height={22} rx={5} fill={color} />
      <line x1={-3} y1={-16} x2={-3 - swing / 3} y2={0} stroke="#333" strokeWidth={4} />
      <line x1={3} y1={-16} x2={3 + swing / 3} y2={0} stroke="#333" strokeWidth={4} />
    </g>
  );
};

const Shopfronts: React.FC = () => {
  const names = ["DELI", "PIZZA", "COFFEE", "BAGELS", "BOOKS", "DINER", "SUBWAY"];
  const colors = ["#e63946", "#2a9d8f", "#e76f51", "#457b9d", "#9d4edd", "#f4a261", "#06d6a0"];
  return (
    <g>
      {names.map((n, i) => (
        <g key={n} transform={`translate(${40 + i * 280} ${NY_H - 150})`}>
          <rect x={0} y={-86} width={250} height={86} fill="#2b2b33" />
          <rect x={0} y={-86} width={250} height={26} fill={colors[i]} />
          <text x={125} y={-66} fontSize={18} fontFamily={FONT} fill="#fff" textAnchor="middle">
            {n}
          </text>
          <rect x={16} y={-52} width={96} height={48} rx={3} fill="#9fe3ff" opacity={0.8} />
          <rect x={138} y={-52} width={96} height={48} rx={3} fill="#9fe3ff" opacity={0.8} />
          <rect x={104} y={-56} width={6} height={56} fill={colors[i]} />
        </g>
      ))}
    </g>
  );
};

const CityBackground: React.FC<{ withSun?: boolean }> = ({ withSun = true }) => (
  <AbsoluteFill>
    <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`}>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#36b8ff" />
          <stop offset="55%" stopColor="#8fd8ff" />
          <stop offset="100%" stopColor="#d7f1ff" />
        </linearGradient>
      </defs>
      <rect width={NY_W} height={NY_H} fill="url(#sky)" />
      {withSun && <Sun />}
      <Cloud x={200} y={150} s={1} speed={0.25} />
      <Cloud x={900} y={90} s={0.7} speed={0.18} />
      <Cloud x={1400} y={220} s={1.1} speed={0.3} />
      <Skyline baseY={NY_H - 150} count={9} fill="#7e9bc4" win="#cfe2ff" minH={220} maxH={420} seedKey="far" scroll={0.5} />
      <Skyline baseY={NY_H - 150} count={7} fill="#4f6fa6" win="#ffe9a8" minH={320} maxH={620} seedKey="mid" scroll={1.1} />
      <Street />
      <LaneDashes />
    </svg>
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ *
 *  PERSONNAGES
 * ------------------------------------------------------------------ */

const Champignon: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <g transform={`scale(${s})`}>
    <rect x={-12} y={-2} width={24} height={26} rx={8} fill="#ffe9c7" />
    <ellipse cx={0} cy={0} rx={28} ry={20} fill="#e63946" />
    <circle cx={-12} cy={-4} r={5} fill="#fff" />
    <circle cx={10} cy={-6} r={6} fill="#fff" />
    <circle cx={2} cy={6} r={4} fill="#fff" />
    <circle cx={-6} cy={8} r={2.5} fill="#222" />
    <circle cx={8} cy={8} r={2.5} fill="#222" />
  </g>
);

// YOSH — petit dinosaure vert (comme Yoshi)
const Yosh: React.FC<{ bob?: number }> = ({ bob = 0 }) => {
  const frame = useCurrentFrame();
  const b = Math.sin(frame / 6) * 6 + bob;
  return (
    <g transform={`translate(0 ${b})`}>
      {/* bottines */}
      <ellipse cx={-26} cy={86} rx={22} ry={12} fill="#ff8c1a" />
      <ellipse cx={28} cy={86} rx={22} ry={12} fill="#ff8c1a" />
      {/* queue */}
      <path d="M40,40 q40,-6 30,40" stroke="#3fbf3f" strokeWidth={18} fill="none" strokeLinecap="round" />
      {/* corps */}
      <ellipse cx={0} cy={36} rx={48} ry={52} fill="#3fbf3f" />
      <ellipse cx={0} cy={52} rx={30} ry={34} fill="#fdf6e3" />
      {/* dos à pics rouges */}
      {[-18, 0, 18].map((dx, i) => (
        <path key={i} d={`M${dx - 8},-6 L${dx},-26 L${dx + 8},-6 Z`} fill="#e63946" />
      ))}
      {/* bras */}
      <ellipse cx={-44} cy={34} rx={12} ry={18} fill="#3fbf3f" />
      <ellipse cx={44} cy={34} rx={12} ry={18} fill="#3fbf3f" />
      {/* tête */}
      <ellipse cx={4} cy={-26} rx={40} ry={36} fill="#3fbf3f" />
      <ellipse cx={34} cy={-18} rx={22} ry={14} fill="#3fbf3f" />
      {/* yeux */}
      <ellipse cx={-2} cy={-44} rx={16} ry={20} fill="#fff" />
      <circle cx={2} cy={-40} r={7} fill="#222" />
      {/* nez */}
      <circle cx={50} cy={-14} r={4} fill="#1f7a1f" />
      <circle cx={42} cy={-14} r={4} fill="#1f7a1f" />
    </g>
  );
};

// MARA — plombier rouge (comme Mario, plus grand)
const Mara: React.FC<{ run?: boolean }> = ({ run }) => {
  const frame = useCurrentFrame();
  const swing = run ? Math.sin(frame / 2.2) * 14 : Math.sin(frame / 8) * 4;
  return (
    <g>
      {/* jambes / chaussures */}
      <g transform={`rotate(${swing} 0 60)`}>
        <rect x={-22} y={60} width={18} height={34} rx={6} fill="#2b6fd6" />
        <ellipse cx={-18} cy={98} rx={20} ry={10} fill="#5a3a1a" />
      </g>
      <g transform={`rotate(${-swing} 0 60)`}>
        <rect x={6} y={60} width={18} height={34} rx={6} fill="#2b6fd6" />
        <ellipse cx={16} cy={98} rx={20} ry={10} fill="#5a3a1a" />
      </g>
      {/* corps : chemise rouge + salopette bleue */}
      <rect x={-30} y={-2} width={60} height={70} rx={16} fill="#e63946" />
      <rect x={-28} y={26} width={56} height={42} rx={12} fill="#2b6fd6" />
      <circle cx={-12} cy={36} r={5} fill="#ffd23f" />
      <circle cx={12} cy={36} r={5} fill="#ffd23f" />
      {/* bras / gants blancs */}
      <g transform={`rotate(${-swing} -28 8)`}>
        <rect x={-46} y={4} width={16} height={34} rx={8} fill="#e63946" />
        <circle cx={-38} cy={42} r={12} fill="#fff" />
      </g>
      <g transform={`rotate(${swing} 28 8)`}>
        <rect x={30} y={4} width={16} height={34} rx={8} fill="#e63946" />
        <circle cx={38} cy={42} r={12} fill="#fff" />
      </g>
      {/* tête */}
      <circle cx={0} cy={-30} r={28} fill="#f1c27d" />
      {/* nez */}
      <circle cx={0} cy={-22} r={9} fill="#f1c27d" stroke="#d9a86a" strokeWidth={1} />
      {/* moustache */}
      <path d="M-18,-16 q18,12 0,0 q-18,12 0,0 M2,-16 q-18,12 0,0 q18,12 0,0" fill="#5a3a1a" />
      <ellipse cx={-13} cy={-13} rx={12} ry={6} fill="#5a3a1a" />
      <ellipse cx={13} cy={-13} rx={12} ry={6} fill="#5a3a1a" />
      {/* yeux */}
      <circle cx={-12} cy={-32} r={4} fill="#222" />
      <circle cx={12} cy={-32} r={4} fill="#222" />
      {/* casquette */}
      <path d="M-30,-44 a30,26 0 0 1 60,0 Z" fill="#e63946" />
      <ellipse cx={16} cy={-44} rx={28} ry={9} fill="#e63946" />
      <circle cx={0} cy={-50} r={11} fill="#fff" />
      <text x={0} y={-46} fontSize={13} fontFamily={FONT} fill="#e63946" textAnchor="middle">
        M
      </text>
    </g>
  );
};

// PIRATES — bras-canon
const Pirates: React.FC<{ firing?: boolean }> = ({ firing }) => {
  const frame = useCurrentFrame();
  const recoil = firing ? Math.max(0, Math.sin(frame / 3)) * 8 : 0;
  return (
    <g>
      {/* jambes */}
      <rect x={-22} y={56} width={18} height={40} rx={6} fill="#3a2e23" />
      <rect x={6} y={56} width={18} height={40} rx={6} fill="#3a2e23" />
      <ellipse cx={-14} cy={98} rx={18} ry={9} fill="#1c1206" />
      <ellipse cx={16} cy={98} rx={18} ry={9} fill="#1c1206" />
      {/* manteau */}
      <rect x={-30} y={-4} width={60} height={66} rx={14} fill="#6b3e8e" />
      <rect x={-6} y={-4} width={12} height={62} fill="#ffd23f" />
      <rect x={-30} y={36} width={60} height={12} fill="#3a2356" />
      {/* bras normal gauche */}
      <rect x={-46} y={4} width={16} height={30} rx={8} fill="#6b3e8e" />
      <circle cx={-38} cy={36} r={10} fill="#f1c27d" />
      {/* bras-canon droit */}
      <g transform={`translate(${-recoil} 0)`}>
        <rect x={28} y={14} width={26} height={22} rx={6} fill="#444" />
        <rect x={50} y={10} width={46} height={30} rx={8} fill="#2b2b2b" />
        <ellipse cx={96} cy={25} rx={8} ry={16} fill="#111" />
        <circle cx={62} cy={25} r={5} fill="#777" />
      </g>
      {/* tête */}
      <circle cx={0} cy={-28} r={26} fill="#f1c27d" />
      {/* barbe */}
      <path d="M-22,-22 q22,40 44,0 q-6,18 -22,18 q-16,0 -22,-18Z" fill="#3a2e23" />
      {/* cache-œil */}
      <rect x={-18} y={-36} width={16} height={12} rx={3} fill="#111" />
      <line x1={-20} y1={-40} x2={22} y2={-30} stroke="#111" strokeWidth={3} />
      <circle cx={10} cy={-30} r={4} fill="#222" />
      {/* chapeau tricorne + tête de mort */}
      <path d="M-34,-44 q34,-34 68,0 q-34,-12 -68,0Z" fill="#241a12" />
      <ellipse cx={0} cy={-44} rx={40} ry={10} fill="#241a12" />
      <circle cx={0} cy={-56} r={8} fill="#f4f1e8" />
      <circle cx={-3} cy={-57} r={1.6} fill="#241a12" />
      <circle cx={3} cy={-57} r={1.6} fill="#241a12" />
    </g>
  );
};

/* ------------------------------------------------------------------ *
 *  EFFETS
 * ------------------------------------------------------------------ */

const Tornado: React.FC<{ cx: number }> = ({ cx }) => {
  const frame = useCurrentFrame();
  const rings = 9;
  return (
    <g>
      {Array.from({ length: rings }).map((_, i) => {
        const t = i / rings;
        const ry = 14 + t * 26;
        const rx = 30 + t * 160;
        const y = NY_H - 150 - i * 95;
        const wob = Math.sin(frame / 6 + i) * (20 + i * 6);
        return (
          <ellipse
            key={i}
            cx={cx + wob}
            cy={y}
            rx={rx / 2}
            ry={ry}
            fill="#6b7280"
            opacity={0.35 + t * 0.35}
          />
        );
      })}
      {Array.from({ length: 10 }).map((_, i) => {
        const a = frame / 4 + i;
        return (
          <rect
            key={`d${i}`}
            x={cx + Math.cos(a) * (60 + i * 8) - 4}
            y={NY_H - 300 - ((frame * 3 + i * 60) % 500)}
            width={10}
            height={6}
            fill="#9aa3af"
          />
        );
      })}
    </g>
  );
};

const Boat: React.FC<{ x: number }> = ({ x }) => {
  const frame = useCurrentFrame();
  const rock = Math.sin(frame / 7) * 3;
  return (
    <g transform={`translate(${x} ${NY_H - 120}) rotate(${rock})`}>
      <path d="M-90,0 L90,0 L62,46 L-62,46 Z" fill="#8a5a2b" />
      <rect x={-90} y={-6} width={180} height={10} rx={4} fill="#b5793c" />
      <rect x={-4} y={-110} width={8} height={108} fill="#5a3a1a" />
      <path d="M4,-104 L70,-50 L4,-50 Z" fill="#f4f1e8" />
      <path d="M-4,-104 L-66,-58 L-4,-58 Z" fill="#e63946" />
    </g>
  );
};

const Waves: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <g>
      <rect x={0} y={NY_H - 80} width={NY_W} height={80} fill="#2a8fd6" />
      {Array.from({ length: 24 }).map((_, i) => (
        <ellipse
          key={i}
          cx={(i * 90 + frame * 4) % NY_W}
          cy={NY_H - 70 + Math.sin(frame / 8 + i) * 4}
          rx={36}
          ry={8}
          fill="#7ec8ff"
          opacity={0.6}
        />
      ))}
    </g>
  );
};

/* ------------------------------------------------------------------ *
 *  HUD
 * ------------------------------------------------------------------ */

const Heart: React.FC<{ x: number; filled: boolean }> = ({ x, filled }) => (
  <path
    transform={`translate(${x} 0) scale(1.3)`}
    d="M0,6 C0,2 -4,-1 -8,1 C-13,4 -12,11 0,20 C12,11 13,4 8,1 C4,-1 0,2 0,6 Z"
    fill={filled ? "#ff3b53" : "#5a2530"}
    stroke="#2a0d12"
    strokeWidth={1.5}
  />
);

const Hud: React.FC<{ hp: number; maxHp?: number }> = ({ hp, maxHp = 5 }) => {
  return (
    <g transform={`translate(50 50)`}>
      <rect x={-16} y={-12} width={260} height={56} rx={14} fill="#000" opacity={0.35} />
      <text x={-4} y={26} fontSize={26} fontFamily={FONT} fill="#fff">
        VIE
      </text>
      <g transform="translate(64 8)">
        {Array.from({ length: maxHp }).map((_, i) => (
          <Heart key={i} x={i * 44} filled={i < hp} />
        ))}
      </g>
    </g>
  );
};

// Popup auto-géré sur un frame relatif (`from`) — rendu en <g>, à placer dans un <svg>.
const Popup: React.FC<{
  text: string;
  color: string;
  x: number;
  y: number;
  from: number;
}> = ({ text, color, x, y, from }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame() - from;
  if (frame < 0 || frame > 40) return null;
  const s = spring({ frame, fps, config: { damping: 9, mass: 0.6 } });
  const up = interpolate(frame, [0, 30], [0, -40], { extrapolateRight: "clamp" });
  const op = interpolate(frame, [0, 6, 24, 34], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <g transform={`translate(${x} ${y + up}) scale(${0.6 + s * 0.6})`} opacity={op}>
      <text
        fontFamily={FONT}
        fontSize={72}
        fill={color}
        stroke="#fff"
        strokeWidth={5}
        paintOrder="stroke"
        textAnchor="middle"
      >
        {text}
      </text>
    </g>
  );
};

/* ------------------------------------------------------------------ *
 *  CARTONS
 * ------------------------------------------------------------------ */

const Card: React.FC<{
  text: string;
  sub?: string;
  big?: boolean;
  appearAt?: number;
}> = ({ text, sub, big, appearAt = 6 }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [appearAt, appearAt + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [appearAt, appearAt + 16], [24, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        justifyContent: big ? "center" : "flex-end",
        alignItems: "center",
        paddingBottom: big ? 0 : 200,
      }}
    >
      <div style={{ opacity: op, transform: `translateY(${y}px)`, textAlign: "center" }}>
        <div
          style={{
            fontFamily: FONT,
            color: "#fff",
            fontSize: big ? 150 : 60,
            fontWeight: 900,
            letterSpacing: big ? 6 : 2,
            textShadow: "0 6px 0 #1b2a4a, 0 10px 30px rgba(0,0,0,.5)",
            WebkitTextStroke: big ? "3px #1b2a4a" : "2px #1b2a4a",
            textTransform: "uppercase",
          }}
        >
          {text}
        </div>
        {sub && (
          <div
            style={{
              fontFamily: FONT,
              color: "#ffd23f",
              fontSize: big ? 46 : 32,
              marginTop: 14,
              letterSpacing: 4,
              textShadow: "0 3px 0 #1b2a4a",
            }}
          >
            {sub}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

const NameTag: React.FC<{ name: string; desc: string; x: number; appearAt: number }> = ({
  name,
  desc,
  x,
  appearAt,
}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [appearAt, appearAt + 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <g transform={`translate(${x} ${NY_H - 250})`} opacity={op}>
      <rect x={-110} y={0} width={220} height={70} rx={12} fill="#1b2a4a" opacity={0.9} />
      <text x={0} y={34} fontSize={34} fontFamily={FONT} fill="#ffd23f" textAnchor="middle">
        {name}
      </text>
      <text x={0} y={58} fontSize={18} fontFamily={FONT} fill="#fff" textAnchor="middle">
        {desc}
      </text>
    </g>
  );
};

/* ------------------------------------------------------------------ *
 *  SCÈNES
 * ------------------------------------------------------------------ */

// S1 — la ville
const SceneCity: React.FC = () => {
  const frame = useCurrentFrame();
  const taxi = -200 + frame * 16;
  return (
    <AbsoluteFill>
      <CityBackground />
      <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
        <Shopfronts />
        <Pedestrian x={300} color="#e63946" phase={0} />
        <Pedestrian x={520} color="#2a9d8f" phase={12} />
        <Pedestrian x={1500} color="#9d4edd" phase={6} />
        <Pedestrian x={1680} color="#f4a261" phase={20} />
        <Bike x={1000 - frame * 4} scale={1} />
        <Taxi x={taxi} scale={1.1} />
        <Taxi x={1700 - frame * 10} flip scale={0.9} />
      </svg>
      <Card text="NEW YORK" sub="2027" />
    </AbsoluteFill>
  );
};

// S2 — les héros
const SceneHeroes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const maraX = interpolate(frame, [0, 40], [-200, 470], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const yoshPop = spring({ frame: frame - 30, fps, config: { damping: 10 } });
  const pirPop = spring({ frame: frame - 50, fps, config: { damping: 10 } });
  const champShow = frame > 60;
  return (
    <AbsoluteFill>
      <CityBackground />
      <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
        {/* traînée de vitesse de Mara */}
        {frame < 42 &&
          Array.from({ length: 6 }).map((_, i) => (
            <rect
              key={i}
              x={maraX - 120 - i * 60}
              y={NY_H - 250 + i * 8}
              width={70}
              height={8}
              rx={4}
              fill="#fff"
              opacity={0.5 - i * 0.07}
            />
          ))}
        <g transform={`translate(${maraX} ${NY_H - 240})`}>
          <Mara run={frame < 42} />
        </g>
        <g transform={`translate(960 ${NY_H - 230}) scale(${0.2 + yoshPop * 0.9})`}>
          <Yosh />
        </g>
        {champShow && (
          <g transform={`translate(1040 ${NY_H - 175})`}>
            <Champignon s={1.4} />
          </g>
        )}
        <g transform={`translate(1480 ${NY_H - 240}) scale(${0.2 + pirPop * 0.95})`}>
          <Pirates firing={false} />
        </g>
      </svg>
      <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
        <NameTag name="MARA" desc="très rapide" x={460} appearAt={14} />
        <NameTag name="YOSH" desc="pond un champignon" x={960} appearAt={40} />
        <NameTag name="PIRATES" desc="bras-canon" x={1470} appearAt={58} />
      </svg>
    </AbsoluteFill>
  );
};

// S3 — les dangers
const SceneDanger: React.FC = () => {
  const frame = useCurrentFrame();
  // taxi fonce sur Mara entre 8 et 30
  const taxiX = interpolate(frame, [0, 28], [2100, 720], {
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });
  const hitCar = frame >= 28 && frame < 50;
  // boulet de canon entre 55 et 78
  const ballX = interpolate(frame, [52, 80], [1500, 760], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const hitBall = frame >= 78;
  const hp = frame < 50 ? 5 : frame < 80 ? 3 : 0;
  const shake = (hitCar && frame < 36) || (hitBall && frame < 88) ? Math.sin(frame * 3) * 8 : 0;
  return (
    <AbsoluteFill>
      <CityBackground />
      <svg
        width={NY_W}
        height={NY_H}
        viewBox={`0 0 ${NY_W} ${NY_H}`}
        style={{ position: "absolute", transform: `translateX(${shake}px)` }}
      >
        {/* héros (Mara) qui se fait toucher */}
        <g transform={`translate(700 ${NY_H - 240}) rotate(${hitCar ? 8 : 0})`}>
          <Mara />
        </g>
        {/* Pirates qui tire le boulet, à droite */}
        {frame > 40 && (
          <g transform={`translate(1500 ${NY_H - 240})`}>
            <Pirates firing />
          </g>
        )}
        {frame >= 52 && !hitBall && <circle cx={ballX} cy={NY_H - 210} r={22} fill="#1a1a1a" />}
        {frame >= 52 && !hitBall && (
          <circle cx={ballX + 30} cy={NY_H - 210} r={14} fill="#888" opacity={0.5} />
        )}
        <Taxi x={taxiX} flip scale={1.15} />
        {(hitCar || (hitBall && frame < 90)) && (
          <text
            x={760}
            y={NY_H - 260}
            fontSize={90}
            fontFamily={FONT}
            fill="#ffd23f"
            textAnchor="middle"
          >
            ✶
          </text>
        )}
      </svg>
      <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
        <Hud hp={hp} />
        <Popup text="−2 ❤" color="#ff3b53" x={760} y={NY_H - 320} from={30} />
        <Popup text="−3 ❤" color="#ff3b53" x={780} y={NY_H - 320} from={80} />
      </svg>
    </AbsoluteFill>
  );
};

// S4 — tornade, effondrement, bateau
const SceneChaos: React.FC = () => {
  const frame = useCurrentFrame();
  // 0-45 tornade + effondrement ; 45-90 bateau + boost
  const collapse = interpolate(frame, [10, 44], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const boatPhase = frame >= 48;
  const boatX = interpolate(frame, [48, 90], [-260, 1100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <AbsoluteFill>
      {!boatPhase ? (
        <>
          <CityBackground withSun />
          <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
            {/* gratte-ciel qui s'effondre */}
            <g
              transform={`translate(560 ${NY_H - 150}) rotate(${collapse * 22}) translate(0 ${collapse * 60})`}
              opacity={1 - collapse * 0.15}
            >
              <Building x={-70} y={-560} w={150} h={560} fill="#4f6fa6" win="#ffe9a8" seed={777} />
            </g>
            {/* blocs de débris */}
            {collapse > 0.3 &&
              Array.from({ length: 10 }).map((_, i) => (
                <rect
                  key={i}
                  x={520 + i * 30 + Math.sin(frame + i) * 20}
                  y={NY_H - 150 - collapse * (200 + i * 30)}
                  width={26}
                  height={26}
                  fill="#3c5688"
                  transform={`rotate(${frame * 4 + i * 30} ${530 + i * 30} ${NY_H - 250})`}
                />
              ))}
            <Tornado cx={1300} />
            {/* héros qui fuit */}
            <g transform={`translate(${interpolate(frame, [0, 44], [900, 1500])} ${NY_H - 240})`}>
              <Mara run />
            </g>
          </svg>
          <Card text="évite les effondrements" appearAt={4} />
        </>
      ) : (
        <>
          <AbsoluteFill>
            <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`}>
              <defs>
                <linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#36b8ff" />
                  <stop offset="100%" stopColor="#bfeaff" />
                </linearGradient>
              </defs>
              <rect width={NY_W} height={NY_H} fill="url(#sky2)" />
              <Sun x={300} y={170} />
              <Skyline baseY={NY_H - 80} count={8} fill="#4f6fa6" win="#ffe9a8" minH={260} maxH={520} seedKey="harbor" scroll={0.6} />
              <Waves />
              <Boat x={boatX} />
              {/* sillage / vitesse */}
              {Array.from({ length: 5 }).map((_, i) => (
                <rect key={i} x={boatX - 130 - i * 70} y={NY_H - 110 + i * 6} width={80} height={9} rx={4} fill="#fff" opacity={0.6 - i * 0.1} />
              ))}
            </svg>
          </AbsoluteFill>
          <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
            <Popup text="+7 km" color="#06d6a0" x={960} y={300} from={52} />
          </svg>
        </>
      )}
    </AbsoluteFill>
  );
};

// S5 — logo final
const SceneLogo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 8, mass: 0.7 } });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1733" }}>
      <svg width={NY_W} height={NY_H} viewBox={`0 0 ${NY_W} ${NY_H}`} style={{ position: "absolute" }}>
        <rect width={NY_W} height={NY_H} fill="#0b1733" />
        <Sun x={960} y={420} />
        <Skyline baseY={NY_H} count={10} fill="#16234a" win="#ffd23f" minH={300} maxH={640} seedKey="logo" scroll={0.4} />
        <g opacity={0.25}>
          <Skyline baseY={NY_H} count={8} fill="#0f1a38" win="#ffe9a8" minH={200} maxH={420} seedKey="logo2" scroll={0.2} />
        </g>
      </svg>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div style={{ transform: `scale(${0.5 + pop * 0.5})`, textAlign: "center" }}>
          <div
            style={{
              fontFamily: FONT,
              fontSize: 190,
              fontWeight: 900,
              color: "#ffd23f",
              letterSpacing: 4,
              WebkitTextStroke: "5px #e63946",
              textShadow: "0 10px 0 #7a1620, 0 20px 40px rgba(0,0,0,.6)",
            }}
          >
            NEW YORK
          </div>
          <div
            style={{
              fontFamily: FONT,
              fontSize: 44,
              color: "#fff",
              letterSpacing: 10,
              marginTop: 6,
            }}
          >
            LE JEU VIDÉO · 2027
          </div>
          <div
            style={{
              fontFamily: FONT,
              fontSize: 30,
              color: "#9fe3ff",
              letterSpacing: 8,
              marginTop: 22,
              opacity: interpolate(frame, [24, 40], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}
          >
            BIENTÔT
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ *
 *  MONTAGE
 * ------------------------------------------------------------------ */

const Vignette: React.FC = () => (
  <AbsoluteFill style={{ boxShadow: "inset 0 0 300px 60px rgba(0,0,0,0.45)", pointerEvents: "none" }} />
);

export const JeuNewYork: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [NY_DURATION - 16, NY_DURATION], [1, 0], {
    extrapolateLeft: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", opacity: Math.min(fadeIn, fadeOut) }}>
      <Sequence from={0} durationInFrames={105}>
        <SceneCity />
      </Sequence>
      <Sequence from={105} durationInFrames={105}>
        <SceneHeroes />
      </Sequence>
      <Sequence from={210} durationInFrames={90}>
        <SceneDanger />
      </Sequence>
      <Sequence from={300} durationInFrames={90}>
        <SceneChaos />
      </Sequence>
      <Sequence from={390} durationInFrames={60}>
        <SceneLogo />
      </Sequence>
      <Vignette />
    </AbsoluteFill>
  );
};
