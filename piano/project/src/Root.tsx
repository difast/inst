import {Composition} from 'remotion';
import {Visualizer} from './Visualizer';
import song from '../public/notes.json';

export const Root: React.FC = () => (
  <Composition
    id="PrimiPassi"
    component={Visualizer}
    durationInFrames={30 * 30}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{
      notes: song.notes,
      composer: 'Fabrizio Paterlini',
      title: 'Primi Passi',
      audio: 'audio.wav',
    }}
  />
);
