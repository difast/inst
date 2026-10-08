import {
  AbsoluteFill,
  Audio,
  continueRender,
  delayRender,
  Img,
  interpolate,
  OffthreadVideo,
  random,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {Song} from './Visualizer';

// Three bands: mood photo on top, falling notes in the middle, the real keyboard
// (live video) below. The notes column is laid out from the video's own key
// geometry, so every note lands on the key that is actually struck. Colours follow
// the photo: candle amber, warm cream, deep brown-black.
export type LiveSong = Song & {geometry: {x0: number; ww: number; firstWhite: number; height: number}};
export type LivePromo = {hook: string; outro: [string, string]};

const PHOTO_H = 660;
const KB_TOP = 1056; // top edge of the keys; the strip ends ~1500, above the Reels caption
const SPEED = 260; // px per second
const NOTE: [string, string] = ['#ffe0a6', '#e08a2e'];
const GLOW = '#ff9b3d';
const FONT = 'Cormorant Garamond';

const font = new FontFace(FONT, `url(${staticFile('fonts/Cormorant.ttf')})`, {weight: '300 700'});
const fontHandle = delayRender('font');
font
  .load()
  .then(() => {
    document.fonts.add(font);
    continueRender(fontHandle);
  })
  .catch(() => continueRender(fontHandle));

const isBlack = (m: number) => [1, 3, 6, 8, 10].includes(m % 12);

const keyRect = (m: number, g: LiveSong['geometry']) => {
  let wi = 0;
  for (let k = g.firstWhite; k < (isBlack(m) ? m + 1 : m); k++) if (!isBlack(k)) wi++;
  if (!isBlack(m)) return {x: g.x0 + wi * g.ww, w: g.ww, black: false};
  const bw = g.ww * 0.62;
  return {x: g.x0 + wi * g.ww - bw / 2, w: bw, black: true};
};

const ctaText: React.CSSProperties = {
  fontFamily: FONT,
  fontWeight: 600,
  color: '#fff3df',
  lineHeight: 1.1,
  textAlign: 'center',
  textShadow: `0 0 24px rgba(255,155,61,0.55), 0 4px 18px rgba(0,0,0,0.95)`,
};

export const SplitVisualizer: React.FC<{song: LiveSong; dir: string; promo?: LivePromo}> = ({song, dir, promo}) => {
  const {notes, geometry} = song;
  const frame = useCurrentFrame();
  const {fps, width, height, durationInFrames} = useVideoConfig();
  const t = frame / fps;
  const kbBottom = KB_TOP + geometry.height;
  const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
  const hookOpacity = interpolate(t, [0.2, 0.6, 2.6, 3.0], [0, 1, 1, 0], clamp);
  const outroStart = durationInFrames / fps - 3;
  const outroOpacity = interpolate(t, [outroStart, outroStart + 0.5], [0, 1], clamp);

  return (
    <AbsoluteFill style={{background: 'linear-gradient(#0d0805, #150b06 55%, #080504)'}}>
      <Audio src={staticFile(`${dir}/audio.wav`)} />

      {/* top: mood photo, melting into the notes area */}
      <Img src={staticFile(`${dir}/photo.jpg`)} style={{position: 'absolute', top: 0, left: 0, width, height: PHOTO_H}} />
      <div
        style={{
          position: 'absolute',
          top: PHOTO_H - 200,
          left: 0,
          width,
          height: 200,
          background: 'linear-gradient(rgba(13,8,5,0), #0f0905)',
        }}
      />

      {/* middle: falling notes with a soft candle-like glow behind them */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: PHOTO_H,
          width,
          height: KB_TOP - PHOTO_H,
          background: 'radial-gradient(ellipse 60% 90% at 50% 100%, rgba(255,140,50,0.10), rgba(0,0,0,0))',
        }}
      />
      <AbsoluteFill
        style={{
          maskImage: `linear-gradient(transparent ${PHOTO_H - 60}px, #000 ${PHOTO_H + 80}px)`,
          WebkitMaskImage: `linear-gradient(transparent ${PHOTO_H - 60}px, #000 ${PHOTO_H + 80}px)`,
        }}
      >
        {notes.map((n, i) => {
          const k = keyRect(n.midi, geometry);
          const bottom = KB_TOP - (n.start - t) * SPEED;
          const h = Math.max(n.dur * SPEED, 14);
          const top = bottom - h;
          if (top > KB_TOP || bottom < 0) return null;
          const pad = k.black ? 2 : 6;
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: k.x + pad,
                width: k.w - pad * 2,
                top,
                height: Math.min(h, KB_TOP - top),
                borderRadius: 10,
                background: `linear-gradient(${NOTE[0]}, ${NOTE[1]})`,
                boxShadow: `0 0 22px ${GLOW}, inset 0 0 0 1px rgba(255,240,215,0.45)`,
              }}
            />
          );
        })}

        {notes.map((n, i) => {
          const age = t - n.start;
          if (age < 0 || age > 0.7) return null;
          const k = keyRect(n.midi, geometry);
          return Array.from({length: 7}).map((_, j) => {
            const dx = (random(`x${i}-${j}`) - 0.5) * 80;
            const vy = 140 + random(`y${i}-${j}`) * 240;
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
                  background: '#ffe6b8',
                  opacity: 1 - age / 0.7,
                  boxShadow: `0 0 8px ${GLOW}`,
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
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: KB_TOP - 5,
          width,
          height: 5,
          background: 'linear-gradient(#3a1d08, #ffc27a)',
          boxShadow: `0 0 22px ${GLOW}`,
        }}
      />
      {/* soft vignette on the strip edges so the cropped keyboard sits in the frame */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: KB_TOP,
          width,
          height: geometry.height,
          background:
            'linear-gradient(90deg, rgba(8,5,4,0.45), rgba(8,5,4,0) 10%, rgba(8,5,4,0) 90%, rgba(8,5,4,0.45)), linear-gradient(rgba(0,0,0,0) 85%, rgba(8,5,4,0.35))',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: kbBottom,
          width,
          height: height - kbBottom,
          background: 'linear-gradient(#0c0705, #050302)',
        }}
      />

      {/* CTA: hook over the photo, outro over the notes area */}
      {promo ? (
        <>
          <div
            style={{
              position: 'absolute',
              left: 60,
              right: 60,
              top: PHOTO_H - 230,
              opacity: hookOpacity,
              transform: `translateY(${interpolate(t, [0.2, 0.8], [14, 0], clamp)}px)`,
            }}
          >
            <div style={{...ctaText, fontSize: 80, whiteSpace: 'pre-line'}}>{promo.hook}</div>
          </div>
          <div
            style={{
              position: 'absolute',
              left: 60,
              right: 60,
              top: PHOTO_H - 120,
              height: KB_TOP - PHOTO_H + 120,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              opacity: outroOpacity,
            }}
          >
            <div style={{...ctaText, fontSize: 96}}>{promo.outro[0]}</div>
            <div style={{...ctaText, fontSize: 44, fontWeight: 500, marginTop: 14, color: '#f3d3a6', letterSpacing: 1}}>
              {promo.outro[1]}
            </div>
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};
