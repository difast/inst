import {Composition} from 'remotion';
import {Song, Visualizer} from './Visualizer';
import primiPassi from '../public/primi-passi/notes.json';
import sonatinaGShort from '../public/sonatina-g-short/notes.json';
import requiemShort from '../public/requiem-short/notes.json';
import moonlight3Short from '../public/moonlight3-short/notes.json';
import interstellarShort from '../public/interstellar-short/notes.json';

const FPS = 30;
const SONGS: {id: string; dir: string; song: Song}[] = [
  {id: 'PrimiPassi', dir: 'primi-passi', song: primiPassi as Song},
  {id: 'SonatinaGShort', dir: 'sonatina-g-short', song: sonatinaGShort as Song},
  {id: 'RequiemShort', dir: 'requiem-short', song: requiemShort as Song},
  {id: 'Moonlight3Short', dir: 'moonlight3-short', song: moonlight3Short as Song},
  {id: 'InterstellarShort', dir: 'interstellar-short', song: interstellarShort as Song},
];

export const Root: React.FC = () => (
  <>
    {SONGS.map(({id, dir, song}) => (
      <Composition
        key={id}
        id={id}
        component={Visualizer}
        durationInFrames={Math.ceil(song.duration * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{song, audio: `${dir}/audio.wav`}}
      />
    ))}
  </>
);
