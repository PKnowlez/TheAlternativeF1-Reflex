// Simulation script to verify power_rankings_chart.js math with sample F1 data
const sampleData = {
  season: 2026,
  races: ["Preseason", "Final Preseason"],
  teams: [
    {
      name: "Cadillac",
      short_name: "CAD",
      color: "#D9B464",
      icon: "https://example.com/cad.png",
      rankings: [{ race: "Preseason", rank: 1 }, { race: "Final Preseason", rank: 3 }]
    },
    {
      name: "Haas",
      short_name: "HAS",
      color: "#ED1B24",
      icon: "https://example.com/has.png",
      rankings: [{ race: "Preseason", rank: 2 }, { race: "Final Preseason", rank: 1 }]
    },
    {
      name: "McLaren",
      short_name: "MCL",
      color: "#FF8000",
      icon: "https://example.com/mcl.png",
      rankings: [{ race: "Preseason", rank: 3 }, { race: "Final Preseason", rank: 2 }]
    }
  ]
};

function splitBezier(p0, p1, p2, p3, t) {
  const q1 = { x: (1 - t) * p0.x + t * p1.x, y: (1 - t) * p0.y + t * p1.y };
  const r0 = { x: (1 - t) * p1.x + t * p2.x, y: (1 - t) * p1.y + t * p2.y };
  const q2 = { x: (1 - t) * q1.x + t * r0.x, y: (1 - t) * q1.y + t * r0.y };
  const r1 = { x: (1 - t) * p2.x + t * p3.x, y: (1 - t) * p2.y + t * p3.y };
  const r2 = { x: (1 - t) * r0.x + t * r1.x, y: (1 - t) * r0.y + t * r1.y };
  const q3 = { x: (1 - t) * q2.x + t * r2.x, y: (1 - t) * q2.y + t * r2.y };
  return { q1, q2, q3 };
}

const M = sampleData.races.length;
const K = 2 * M - 1;
console.log(`M = ${M}, K = ${K} steps, total duration = ${K}s at 1x`);

// Check layout
const marginL = 80;
const marginR = 150;
const stepW = 200;
const usableW = K * stepW;
const viewW = marginL + usableW + marginR;
console.log(`viewW = ${viewW}`);

// Test progressive path generation for progress from 0.0 to 1.0 in steps of 0.2
[0.0, 0.25, 0.333, 0.5, 0.666, 0.8, 1.0].forEach(p => {
  const u = p * K;
  const s = Math.min(K - 1, Math.floor(u));
  const f = p >= 1.0 ? 1.0 : Math.min(1.0, Math.max(0.0, u - s));
  console.log(`p=${p.toFixed(3)} -> u=${u.toFixed(2)}, interval=${s} (${s % 2 === 0 ? 'Plateau ' + (s/2) : 'Transition ' + Math.floor(s/2) + '->' + (Math.floor(s/2)+1)}), fraction=${f.toFixed(2)}`);
});
