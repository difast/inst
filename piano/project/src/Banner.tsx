import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// Piano Lab promo banner, styled after the piano-lab.ru favicon.
const PURPLE_LIGHT = '#6265f0';
const PURPLE_DARK = '#4338ca';
const KEY_BLACK = '#1c1917';

const Logo: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 512 512">
    <defs>
      <linearGradient id="pl-bg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor={PURPLE_LIGHT} />
        <stop offset="1" stopColor={PURPLE_DARK} />
      </linearGradient>
    </defs>
    <rect width="512" height="512" rx="110" fill="url(#pl-bg)" />
    <rect x="88" y="148" width="336" height="216" rx="28" fill="#fff" />
    {[155, 222, 289, 356].map((x) => (
      <rect key={x} x={x - 1.5} y="190" width="3" height="174" fill="#d4d4d4" />
    ))}
    {[136, 203, 337].map((x) => (
      <rect key={x} x={x} y="148" width="40" height="132" rx="8" fill={KEY_BLACK} />
    ))}
  </svg>
);

export const Banner: React.FC<{top: number; name: string; site: string; tagline?: string}> = ({
  top,
  name,
  site,
  tagline,
}) => {
  const frame = useCurrentFrame();
  const {fps, width} = useVideoConfig();

  const enter = spring({frame: frame - 12, fps, config: {damping: 14, stiffness: 120}});
  // a short "pop" every 6 seconds to catch the eye
  const cycle = frame % (fps * 6);
  const pop = interpolate(cycle, [0, 6, 14], [1, 1.06, 1], {extrapolateRight: 'clamp'});
  // light sweep across the banner right after each pop
  const sweep = interpolate(cycle, [0, 24], [-0.4, 1.4], {extrapolateRight: 'clamp'});
  const glow = interpolate(Math.sin((frame / fps) * Math.PI), [-1, 1], [0.35, 0.7]);

  const w = 600;
  const h = 116;

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: (width - w) / 2,
        width: w,
        height: h,
        transform: `translateY(${(1 - enter) * 60}px) scale(${(0.9 + enter * 0.1) * pop})`,
        opacity: enter,
      }}
    >
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          borderRadius: h / 2,
          overflow: 'hidden',
          background: `linear-gradient(120deg, ${PURPLE_LIGHT}, ${PURPLE_DARK})`,
          boxShadow: `0 0 40px rgba(98,101,240,${glow}), inset 0 0 0 2px rgba(255,255,255,0.18)`,
          display: 'flex',
          alignItems: 'center',
          padding: '0 34px 0 14px',
          gap: 22,
          fontFamily: 'Helvetica, Arial, sans-serif',
        }}
      >
        <div style={{width: 88, height: 88, borderRadius: 44, overflow: 'hidden', flexShrink: 0, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <Logo size={88} />
        </div>
        <div style={{flex: 1, color: '#fff', lineHeight: 1.05}}>
          <div style={{fontSize: 44, fontWeight: 700}}>{name}</div>
          <div style={{fontSize: 30, opacity: 0.9, marginTop: 6}}>{tagline ?? `Учись играть на ${site}`}</div>
        </div>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: `${sweep * 100}%`,
            width: 120,
            height: '100%',
            background: 'linear-gradient(100deg, transparent, rgba(255,255,255,0.35), transparent)',
            transform: 'skewX(-20deg)',
          }}
        />
      </div>
    </div>
  );
};
