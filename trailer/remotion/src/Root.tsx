import { Composition, staticFile } from "remotion";
import { Trailer } from "./Trailer";
import { DURATION, FPS, WIDTH, HEIGHT } from "./shots";

export const RemotionRoot: React.FC = () => {
  return (
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
  );
};
