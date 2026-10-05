import {Composition} from 'remotion';
import {Song, Visualizer} from './Visualizer';
import primiPassi from '../public/primi-passi/notes.json';
import sonatinaG from '../public/sonatina-g/notes.json';
import sonatinaGShort from '../public/sonatina-g-short/notes.json';
import requiem from '../public/requiem/notes.json';
import requiemShort from '../public/requiem-short/notes.json';

const FPS = 30;
const SONGS: {id: string; dir: string; song: Song}[] = [
  {id: 'PrimiPassi', dir: 'primi-passi', song: primiPassi as Song},
  {id: 'SonatinaG', dir: 'sonatina-g', song: sonatinaG as Song},
  {id: 'SonatinaGShort', dir: 'sonatina-g-short', song: sonatinaGShort as Song},
  {id: 'Requiem', dir: 'requiem', song: requiem as Song},
  {id: 'RequiemShort', dir: 'requiem-short', song: requiemShort as Song},
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
