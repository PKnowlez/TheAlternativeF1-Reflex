function splitBezier(p0, p1, p2, p3, t) {
  const q1 = {
    x: (1 - t) * p0.x + t * p1.x,
    y: (1 - t) * p0.y + t * p1.y
  };
  const r0 = {
    x: (1 - t) * p1.x + t * p2.x,
    y: (1 - t) * p1.y + t * p2.y
  };
  const q2 = {
    x: (1 - t) * q1.x + t * r0.x,
    y: (1 - t) * q1.y + t * r0.y
  };
  const r1 = {
    x: (1 - t) * p2.x + t * p3.x,
    y: (1 - t) * p2.y + t * p3.y
  };
  const r2 = {
    x: (1 - t) * r0.x + t * r1.x,
    y: (1 - t) * r0.y + t * r1.y
  };
  const q3 = {
    x: (1 - t) * q2.x + t * r2.x,
    y: (1 - t) * q2.y + t * r2.y
  };
  return { q1, q2, q3 };
}

const plateaus = [
  { startX: 65, endX: 185, midX: 125 },
  { startX: 305, endX: 425, midX: 365 }
];

const team = {
  racePoints: [
    { y: 76, rank: 1 },
    { y: 144, rank: 2 }
  ]
};

const K = 3;
[0.0, 0.33, 0.5, 0.66, 1.0].forEach(p => {
  const u = p * K;
  const s = Math.min(K - 1, Math.floor(u));
  const f = p >= 1.0 ? 1.0 : Math.min(1.0, Math.max(0.0, u - s));

  const pathCommands = [];
  let currX = plateaus[0].startX;
  let currY = team.racePoints[0].y;

  for (let i = 0; i <= s; i++) {
    if (i % 2 === 0) {
      const j = i / 2;
      const plat = plateaus[j];
      const y = team.racePoints[j].y;

      if (i === 0) {
        pathCommands.push(`M ${plat.startX.toFixed(1)} ${y.toFixed(1)}`);
      }

      if (i < s) {
        pathCommands.push(`L ${plat.endX.toFixed(1)} ${y.toFixed(1)}`);
        currX = plat.endX;
        currY = y;
      } else {
        currX = plat.startX + f * (plat.endX - plat.startX);
        currY = y;
        pathCommands.push(`L ${currX.toFixed(1)} ${currY.toFixed(1)}`);
      }
    } else {
      const j = Math.floor(i / 2);
      const platCurr = plateaus[j];
      const platNext = plateaus[j + 1];
      const y0 = team.racePoints[j].y;
      const y1 = team.racePoints[j + 1].y;

      const p0 = { x: platCurr.endX, y: y0 };
      const p3 = { x: platNext.startX, y: y1 };
      const cx = (p0.x + p3.x) / 2;
      const p1 = { x: cx, y: y0 };
      const p2 = { x: cx, y: y1 };

      if (i < s) {
        pathCommands.push(
          `C ${p1.x.toFixed(1)} ${p1.y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}, ${p3.x.toFixed(1)} ${p3.y.toFixed(1)}`
        );
        currX = p3.x;
        currY = p3.y;
      } else {
        const { q1, q2, q3 } = splitBezier(p0, p1, p2, p3, f);
        currX = q3.x;
        currY = q3.y;
        pathCommands.push(
          `C ${q1.x.toFixed(1)} ${q1.y.toFixed(1)}, ${q2.x.toFixed(1)} ${q2.y.toFixed(1)}, ${q3.x.toFixed(1)} ${q3.y.toFixed(1)}`
        );
      }
    }
  }
  console.log(`p=${p.toFixed(2)}: ${pathCommands.join(' ')}`);
});
