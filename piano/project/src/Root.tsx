import {Composition} from 'remotion';
import {Promo, Song, Visualizer} from './Visualizer';
import primiPassi from '../public/primi-passi/notes.json';
import sonatinaGShort from '../public/sonatina-g-short/notes.json';
import requiemShort from '../public/requiem-short/notes.json';
import moonlight3Short from '../public/moonlight3-short/notes.json';
import interstellarShort from '../public/interstellar-short/notes.json';
import rondoLive from '../public/rondo-live/notes.json';
import {LiveSong, SplitVisualizer} from './SplitVisualizer';

const FPS = 30;
const PROMO_BANNER = {bannerName: 'Научись играть это', bannerTagline: 'Piano Lab · ссылка в профиле'};
const OUTRO: [string, string] = ['Подпишись', 'чтобы не пропустить следующую мелодию'];

const SONGS: {id: string; dir: string; song: Song; promo?: Promo}[] = [
  {id: 'PrimiPassi', dir: 'primi-passi', song: primiPassi as Song},
  {
    id: 'SonatinaGShort',
    dir: 'sonatina-g-short',
    song: sonatinaGShort as Song,
    promo: {...PROMO_BANNER, hook: 'Бетховен, которого реально выучить', outro: OUTRO},
  },
  {
    id: 'RequiemShort',
    dir: 'requiem-short',
    song: requiemShort as Song,
    promo: {...PROMO_BANNER, hook: 'Узнаешь с первых нот?', outro: OUTRO},
  },
  {id: 'Moonlight3Short', dir: 'moonlight3-short', song: moonlight3Short as Song},
  {
    id: 'InterstellarShort',
    dir: 'interstellar-short',
    song: interstellarShort as Song,
    promo: {...PROMO_BANNER, hook: 'Тема из «Интерстеллара», от которой мурашки', outro: OUTRO},
  },
];

export const Root: React.FC = () => (
  <>
    {SONGS.map(({id, dir, song, promo}) => (
      <Composition
        key={id}
        id={id}
        component={Visualizer}
        durationInFrames={Math.ceil(song.duration * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{song, audio: `${dir}/audio.wav`, promo}}
      />
    ))}
    <Composition
      id="RondoLive"
      component={SplitVisualizer}
      durationInFrames={Math.ceil(rondoLive.duration * FPS)}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{song: rondoLive as LiveSong, dir: 'rondo-live'}}
    />
  </>
);
