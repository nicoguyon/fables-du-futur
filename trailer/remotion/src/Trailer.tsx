import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { SHOTS, SHOT_FRAMES, DURATION } from "./shots";

const FONT =
  "'Helvetica Neue', 'Arial Narrow', Helvetica, Arial, sans-serif";

// Un plan : vidéo + léger Ken Burns + carton-titre en surimpression.
const ShotView: React.FC<{
  file: string;
  title?: string;
  big?: boolean;
}> = ({ file, title, big }) => {
  const frame = useCurrentFrame();
  // Ken Burns très léger pour donner de la vie au plan.
  const scale = interpolate(frame, [0, SHOT_FRAMES], [1.03, 1.09], {
    extrapolateRight: "clamp",
  });
  // Apparition / disparition du carton.
  const titleOpacity = interpolate(
    frame,
    [10, 28, SHOT_FRAMES - 22, SHOT_FRAMES - 6],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <AbsoluteFill style={{ transform: `scale(${scale})` }}>
        <OffthreadVideo
          src={staticFile(file)}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>

      {/* vignette cinéma */}
      <AbsoluteFill
        style={{
          boxShadow: "inset 0 0 350px 80px rgba(0,0,0,0.55)",
          pointerEvents: "none",
        }}
      />

      {title ? (
        <AbsoluteFill
          style={{
            justifyContent: big ? "center" : "flex-end",
            alignItems: "center",
            paddingBottom: big ? 0 : 90,
            opacity: titleOpacity,
          }}
        >
          <div
            style={{
              fontFamily: FONT,
              color: "white",
              textAlign: "center",
              textTransform: "uppercase",
              fontWeight: big ? 800 : 500,
              fontSize: big ? 96 : 40,
              letterSpacing: big ? 8 : 4,
              lineHeight: 1.15,
              textShadow: "0 2px 30px rgba(0,0,0,0.8)",
              maxWidth: "80%",
            }}
          >
            {title}
            {big ? (
              <div
                style={{
                  fontSize: 30,
                  fontWeight: 400,
                  letterSpacing: 6,
                  marginTop: 28,
                  opacity: 0.85,
                }}
              >
                un film d'Alexandre — prochainement
              </div>
            ) : null}
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};

export const Trailer: React.FC<{ music: string; voice: string }> = ({
  music,
  voice,
}) => {
  const frame = useCurrentFrame();
  // Fondu d'ouverture et de fermeture global.
  const fade = interpolate(
    frame,
    [0, 18, DURATION - 30, DURATION],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <AbsoluteFill style={{ opacity: fade }}>
        {SHOTS.map((shot, i) => (
          <Sequence
            key={shot.file}
            from={i * SHOT_FRAMES}
            durationInFrames={SHOT_FRAMES}
          >
            <ShotView file={shot.file} title={shot.title} big={shot.big} />
          </Sequence>
        ))}
      </AbsoluteFill>

      {/* Bande son : musique (lit) + voix off par-dessus */}
      {music ? <Audio src={music} volume={0.55} /> : null}
      {voice ? <Audio src={voice} volume={1} /> : null}
    </AbsoluteFill>
  );
};
