// Test script for de Casteljau subdivision on transition
function splitBezier(p0, p1, p2, p3, t) {
  const q0 = { x: p0.x, y: p0.y };
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
  return { q0, q1, q2, q3 };
}

const p0 = { x: 100, y: 50 };
const p1 = { x: 150, y: 50 };
const p2 = { x: 150, y: 150 };
const p3 = { x: 200, y: 150 };

console.log('t=0:', splitBezier(p0, p1, p2, p3, 0));
console.log('t=0.5:', splitBezier(p0, p1, p2, p3, 0.5));
console.log('t=1:', splitBezier(p0, p1, p2, p3, 1.0));
