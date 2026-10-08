import {AbsoluteFill, Audio, Img, OffthreadVideo, random, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Song} from './Visualizer';

// Three bands: mood photo on top, falling notes in the middle, the real keyboard
// (live video) below. The notes column is laid out from the video's own key
// geometry, so every note lands on the key that is actually struck.
export type LiveSong = Song & {geometry: {x0: number; ww: number; firstWhite: number; height: number}};

const PHOTO_H = 620;
const KB_TOP = 1393; // top edge of the keys in the video band
const SPEED = 320; // px per second
const COLOR: [string, string] = ['#7fdcff', '#1f9bff'];

const isBlack = (m: number) => [1, 3, 6, 8, 10].includes(m % 12);

const keyRect = (m: number, g: LiveSong['geometry']) => {
  let wi = 0;
  for (let k = g.firstWhite; k < (isBlack(m) ? m + 1 : m); k++) if (!isBlack(k)) wi++;
  if (!isBlack(m)) return {x: g.x0 + wi * g.ww, w: g.ww, black: false};
  const bw = g.ww * 0.62;
  return {x: g.x0 + wi * g.ww - bw / 2, w: bw, black: true};
};

export const SplitVisualizer: React.FC<{song: LiveSong; dir: string}> = ({song, dir}) => {
  const {notes, geometry} = song;
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const t = frame / fps;
  const active = notes.filter((n) => t >= n.start && t < n.start + n.dur);

  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Audio src={staticFile(`${dir}/audio.wav`)} />

      {/* top: mood photo, melting into the dark notes area */}
      <Img src={staticFile(`${dir}/photo.jpg`)} style={{position: 'absolute', top: 0, left: 0, width, height: PHOTO_H}} />
      <div
        style={{
          position: 'absolute',
          top: PHOTO_H - 160,
          left: 0,
          width,
          height: 160,
          background: 'linear-gradient(rgba(0,0,0,0), #000)',
        }}
      />

      {/* middle: falling notes */}
      <AbsoluteFill
        style={{
          maskImage: `linear-gradient(transparent ${PHOTO_H - 40}px, #000 ${PHOTO_H + 120}px)`,
          WebkitMaskImage: `linear-gradient(transparent ${PHOTO_H - 40}px, #000 ${PHOTO_H + 120}px)`,
        }}
      >
        {notes.map((n, i) => {
          const k = keyRect(n.midi, geometry);
          const bottom = KB_TOP - (n.start - t) * SPEED;
          const h = Math.max(n.dur * SPEED, 14);
          const top = bottom - h;
          if (top > KB_TOP || bottom < 0) return null;
          const pad = k.black ? 1 : 3;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: k.x + pad,
                width: k.w - pad * 2,
                top,
                height: Math.min(h, KB_TOP - top),
                borderRadius: 7,
                background: `linear-gradient(${COLOR[0]}, ${COLOR[1]})`,
                boxShadow: `0 0 18px ${COLOR[1]}, inset 0 0 0 1px rgba(255,255,255,0.35)`,
              }}
            />
          );
        })}

        {/* sparks at the hit line */}
        {notes.map((n, i) => {
          const age = t - n.start;
          if (age < 0 || age > 0.7) return null;
          const k = keyRect(n.midi, geometry);
          return Array.from({length: 7}).map((_, j) => {
            const dx = (random(`x${i}-${j}`) - 0.5) * 70;
            const vy = 140 + random(`y${i}-${j}`) * 260;
            const s = 2 + random(`s${i}-${j}`) * 4;
            return (
              <div
                key={`${i}-${j}`}
                style={{
                  position: 'absolute',
                  left: k.x + k.w / 2 + dx * age * 2.2,
                  top: KB_TOP - vy * age + 160 * age * age,
                  width: s,
                  height: s,
                  borderRadius: s,
                  background: '#bdf0ff',
                  opacity: 1 - age / 0.7,
                  boxShadow: `0 0 8px ${COLOR[1]}`,
                }}
              />
            );
          });
        })}
      </AbsoluteFill>

      {/* bottom: the real keyboard */}
      <OffthreadVideo
        src={staticFile(`${dir}/keys.mp4`)}
        muted
        style={{position: 'absolute', top: KB_TOP, left: 0, width, height: geometry.height}}
      />
      {/* pressed keys light up on the video */}
      {active.map((n, i) => {
        const k = keyRect(n.midi, geometry);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: k.x + 1,
              width: k.w - 2,
              top: KB_TOP,
              height: k.black ? geometry.height * 0.6 : geometry.height,
              background: `linear-gradient(${COLOR[0]}, rgba(31,155,255,0.15))`,
              mixBlendMode: 'screen',
              opacity: 0.7,
              boxShadow: `0 0 26px ${COLOR[1]}`,
            }}
          />
        );
      })}
      {/* glow line where notes meet the keys */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: KB_TOP - 5,
          width,
          height: 5,
          background: 'linear-gradient(#0b2a3d, #5fe3ff)',
          boxShadow: '0 0 22px #2fb8ff',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: KB_TOP + geometry.height,
          width,
          height: height - KB_TOP - geometry.height,
          background: 'linear-gradient(#050505, #000)',
        }}
      />
    </AbsoluteFill>
  );
};
