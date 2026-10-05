const isBlack = (m: number) => [1, 3, 6, 8, 10].includes(m % 12);

export type Key = {midi: number; black: boolean; x: number; w: number};

export const layout = (width: number, low: number, high: number): Key[] => {
  const whites = [];
  for (let m = low; m <= high; m++) if (!isBlack(m)) whites.push(m);
  const ww = width / whites.length;
  const keys: Key[] = [];
  let wi = 0;
  for (let m = low; m <= high; m++) {
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
