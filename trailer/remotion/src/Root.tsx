import { Composition, staticFile } from "remotion";
import { Trailer } from "./Trailer";
import { DURATION, FPS, WIDTH, HEIGHT } from "./shots";
import {
  JeuNewYork,
  NY_DURATION,
  NY_FPS,
  NY_W,
  NY_H,
} from "./JeuNewYork";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Trailer"
        component={Trailer}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{
          music: staticFile("audio/music.mp3"),
          voice: staticFile("audio/voix.mp3"),
        }}
      />
      <Composition
        id="JeuNewYork"
        component={JeuNewYork}
        durationInFrames={NY_DURATION}
        fps={NY_FPS}
        width={NY_W}
        height={NY_H}
      />
    </>
  );
};
