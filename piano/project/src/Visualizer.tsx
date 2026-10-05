import {AbsoluteFill, Audio, interpolate, random, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {layout} from './keyboard';
import {Banner} from './Banner';

type Note = {midi: number; start: number; dur: number; hand: string; vel: number};

export type Song = {
  composer: string;
  title: string;
  duration: number;
  keyboard: number[];
  sections: {start: number; label: string}[];
  notes: Note[];
};

// keyboard and banner sit above the Reels caption/UI zone (bottom ~400px)
const KB_TOP = 1120;
const WHITE_H = 230;
const BLACK_H = 146;
const SPEED = 430; // px per second
const COLORS: Record<string, [string, string]> = {
  R: ['#7fdcff', '#1f9bff'],
  L: ['#6f8dff', '#3048ff'],
};

export const Visualizer: React.FC<{song: Song; audio: string}> = ({song, audio}) => {
  const {notes, composer, title, sections, keyboard} = song;
  const frame = useCurrentFrame();
  const {fps, width, durationInFrames} = useVideoConfig();
  const t = frame / fps;
  const keys = layout(width, keyboard[0], keyboard[1]);
  const section = [...sections].reverse().find((sec) => t >= sec.start - 0.5);
  const sectionOpacity = section
    ? interpolate(t, [section.start - 0.5, section.start + 0.3], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
    : 0;
  const byMidi = new Map(keys.map((k) => [k.midi, k]));
  const active = new Map<number, string>();
  for (const n of notes) if (t >= n.start && t < n.start + n.dur) active.set(n.midi, n.hand);

  const titleOpacity = interpolate(frame, [5, 30, durationInFrames - 20, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{background: 'linear-gradient(#000 0%, #03060c 70%, #000 100%)'}}>
      <Audio src={staticFile(audio)} />

      <AbsoluteFill
        style={{
          maskImage: 'linear-gradient(transparent 0px, transparent 370px, #000 540px)',
          WebkitMaskImage: 'linear-gradient(transparent 0px, transparent 370px, #000 540px)',
        }}
      >
      {/* octave guide lines */}
      {keys
        .filter((k) => k.midi % 12 === 0)
        .map((k) => (
          <div key={k.midi} style={{position: 'absolute', left: k.x, top: 0, width: 1, height: KB_TOP, background: '#0d1624'}} />
        ))}

      {/* falling notes */}
      {notes.map((n, i) => {
        const k = byMidi.get(n.midi);
        if (!k) return null;
        const bottom = KB_TOP - (n.start - t) * SPEED;
        const h = Math.max(n.dur * SPEED, 14);
        const top = bottom - h;
        if (top > KB_TOP || bottom < 0) return null;
        const [c1, c2] = COLORS[n.hand];
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
              background: `linear-gradient(${c1}, ${c2})`,
              boxShadow: `0 0 18px ${c2}, inset 0 0 0 1px rgba(255,255,255,0.35)`,
            }}
          />
        );
      })}

      {/* sparks at the hit line */}
      {notes.map((n, i) => {
        const k = byMidi.get(n.midi);
        const age = t - n.start;
        if (!k || age < 0 || age > 0.7) return null;
        return Array.from({length: 7}).map((_, j) => {
          const dx = (random(`x${i}-${j}`) - 0.5) * 70;
          const vy = 140 + random(`y${i}-${j}`) * 260;
          const x = k.x + k.w / 2 + dx * age * 2.2;
          const y = KB_TOP - vy * age + 160 * age * age;
          const o = 1 - age / 0.7;
          const s = 2 + random(`s${i}-${j}`) * 4;
          return (
            <div
              key={`${i}-${j}`}
              style={{
                position: 'absolute',
                left: x,
                top: y,
                width: s,
                height: s,
                borderRadius: s,
                background: '#bdf0ff',
                opacity: o,
                boxShadow: `0 0 8px ${COLORS[n.hand][1]}`,
              }}
            />
          );
        });
      })}

      </AbsoluteFill>

      {/* glow strip above the keys */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: KB_TOP - 7,
          width,
          height: 7,
          background: 'linear-gradient(#0b2a3d, #5fe3ff)',
          boxShadow: '0 0 22px #2fb8ff',
        }}
      />

      {/* keyboard */}
      {keys
        .filter((k) => !k.black)
        .map((k) => {
          const hand = active.get(k.midi);
          return (
            <div
              key={k.midi}
              style={{
                position: 'absolute',
                left: k.x,
                top: KB_TOP,
                width: k.w - 1.5,
                height: WHITE_H,
                borderRadius: '0 0 6px 6px',
                background: hand
                  ? `linear-gradient(${COLORS[hand][0]}, ${COLORS[hand][1]})`
                  : 'linear-gradient(#d9dde2, #ffffff 18%, #f3f4f6)',
                boxShadow: hand ? `0 0 30px ${COLORS[hand][1]}` : 'inset 0 -6px 0 #c9ccd2',
              }}
            />
          );
        })}
      {keys
        .filter((k) => k.black)
        .map((k) => {
          const hand = active.get(k.midi);
          return (
            <div
              key={k.midi}
              style={{
                position: 'absolute',
                left: k.x,
                top: KB_TOP,
                width: k.w,
                height: BLACK_H,
                borderRadius: '0 0 4px 4px',
                background: hand
                  ? `linear-gradient(${COLORS[hand][0]}, ${COLORS[hand][1]})`
                  : 'linear-gradient(#000, #2a2d33 85%, #444850)',
                boxShadow: hand ? `0 0 24px ${COLORS[hand][1]}` : '0 3px 4px rgba(0,0,0,0.6)',
              }}
            />
          );
        })}

      <Banner top={KB_TOP + WHITE_H + 36} name="Piano Lab" site="piano-lab.ru" />

      {/* title */}
      <div
        style={{
          position: 'absolute',
          top: 190,
          width,
          textAlign: 'center',
          color: '#fff',
          fontFamily: 'Helvetica, Arial, sans-serif',
          opacity: titleOpacity,
          textShadow: '0 0 20px rgba(80,180,255,0.6)',
        }}
      >
        <div style={{fontSize: 40, letterSpacing: 6, color: '#9fd8ff', textTransform: 'uppercase'}}>{composer}</div>
        <div style={{fontSize: 92, fontWeight: 300, marginTop: 6}}>{title}</div>
        {section ? (
          <div style={{fontSize: 38, marginTop: 4, color: '#cfe9ff', opacity: sectionOpacity, fontStyle: 'italic'}}>
            {section.label}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
