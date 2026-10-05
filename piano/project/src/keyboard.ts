export const LOW = 48; // C3
export const HIGH = 96; // C7

const isBlack = (m: number) => [1, 3, 6, 8, 10].includes(m % 12);

export type Key = {midi: number; black: boolean; x: number; w: number};

export const layout = (width: number): Key[] => {
  const whites = [];
  for (let m = LOW; m <= HIGH; m++) if (!isBlack(m)) whites.push(m);
  const ww = width / whites.length;
  const keys: Key[] = [];
  let wi = 0;
  for (let m = LOW; m <= HIGH; m++) {
    if (isBlack(m)) {
      const bw = ww * 0.58;
      keys.push({midi: m, black: true, x: wi * ww - bw / 2, w: bw});
    } else {
      keys.push({midi: m, black: false, x: wi * ww, w: ww});
      wi++;
    }
  }
  return keys;
};
