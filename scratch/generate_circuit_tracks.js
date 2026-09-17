const fs = require('fs');
const path = require('path');
const https = require('https');
const { svgPathProperties } = require(path.join(__dirname, 'node_modules', 'svg-path-properties', 'dist', 'main.cjs'));

const raceToLayout = {
  'Abu Dhabi': { lid: 'yas-marina-2', angle: 99, direction: 'counter-clockwise' },
  'Australia': { lid: 'melbourne-2', angle: -46, direction: 'clockwise' },
  'Austria': { lid: 'spielberg-3', angle: -31, direction: 'clockwise' },
  'Austria Reverse': { lid: 'spielberg-3', angle: -31, direction: 'clockwise' },
  'Austria Sprint': { lid: 'spielberg-3', angle: -31, direction: 'clockwise' },
  'Bahrain': { lid: 'bahrain-3', angle: 0, direction: 'clockwise' },
  'Bahrain Sprint': { lid: 'bahrain-3', angle: 0, direction: 'clockwise' },
  'Baku': { lid: 'baku-1', angle: 73, direction: 'counter-clockwise' },
  'Brazil': { lid: 'interlagos-2', angle: 90, direction: 'counter-clockwise' },
  'Brazil Sprint': { lid: 'interlagos-2', angle: 90, direction: 'counter-clockwise' },
  'COTA': { lid: 'austin-1', angle: 30, direction: 'counter-clockwise' },
  'COTA Sprint': { lid: 'austin-1', angle: 30, direction: 'counter-clockwise' },
  'Canada': { lid: 'montreal-6', angle: -55, direction: 'clockwise' },
  'China': { lid: 'shanghai-1', angle: 24, direction: 'clockwise' },
  'China Sprint': { lid: 'shanghai-1', angle: 24, direction: 'clockwise' },
  'France': { lid: 'paul-ricard-3', angle: 0, direction: 'clockwise' },
  'Germany': { lid: 'hockenheimring-4', angle: 0, direction: 'clockwise' },
  'Hungary': { lid: 'hungaroring-3', angle: 52, direction: 'clockwise' },
  'Imola': { lid: 'imola-3', angle: 0, direction: 'counter-clockwise' },
  'Jeddah': { lid: 'jeddah-1', angle: 0, direction: 'counter-clockwise' },
  'Las Vegas': { lid: 'las-vegas-1', angle: 0, direction: 'counter-clockwise' },
  'Mexico': { lid: 'mexico-city-3', angle: -8, direction: 'clockwise' },
  'Miami': { lid: 'miami-1', angle: -18, direction: 'counter-clockwise' },
  'Miami Sprint': { lid: 'miami-1', angle: -18, direction: 'counter-clockwise' },
  'Monaco': { lid: 'monaco-6', angle: 45, direction: 'clockwise' },
  'Monza': { lid: 'monza-7', angle: -95, direction: 'clockwise' },
  'Mugello': { lid: 'mugello-1', angle: 0, direction: 'clockwise' },
  'Nurburgring': { lid: 'nurburgring-4', angle: 0, direction: 'clockwise' },
  'Portugal': { lid: 'portimao-1', angle: 0, direction: 'clockwise' },
  'Qatar': { lid: 'lusail-1', angle: 0, direction: 'clockwise' },
  'Russia': { lid: 'sochi-1', angle: 0, direction: 'clockwise' },
  'Saudi Arabia': { lid: 'jeddah-1', angle: 0, direction: 'counter-clockwise' },
  'Silverstone': { lid: 'silverstone-8', angle: 90, direction: 'clockwise' },
  'Silverstone Sprint': { lid: 'silverstone-8', angle: 90, direction: 'clockwise' },
  'Singapore': { lid: 'marina-bay-4', angle: 0, direction: 'counter-clockwise' },
  'Singapore Sprint': { lid: 'marina-bay-4', angle: 0, direction: 'counter-clockwise' },
  'Spa': { lid: 'spa-francorchamps-4', angle: -100, direction: 'clockwise' },
  'Spa Sprint': { lid: 'spa-francorchamps-4', angle: -100, direction: 'clockwise' },
  'Spain': { lid: 'catalunya-6', angle: 32, direction: 'clockwise' },
  'Suzuka': { lid: 'suzuka-2', angle: 0, direction: 'clockwise' },
  'Turkey': { lid: 'istanbul-1', angle: 0, direction: 'counter-clockwise' },
  'Zandvoort': { lid: 'zandvoort-5', angle: 0, direction: 'clockwise' },
  'Zandvoort Sprint': { lid: 'zandvoort-5', angle: 0, direction: 'clockwise' },
};

function fetchText(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

function rotatePoint(x, y, angleDeg, cx = 250, cy = 250) {
  if (angleDeg === 0) return { x, y };
  const rad = (-angleDeg * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  const dx = x - cx;
  const dy = y - cy;
  return {
    x: cx + dx * cos - dy * sin,
    y: cy + dx * sin + dy * cos,
  };
}

// Compute signed polygon area to determine winding order (clockwise vs counter-clockwise)
function computeSignedArea(pts) {
  let area = 0;
  for (let i = 0; i < pts.length; i++) {
    const p1 = pts[i];
    const p2 = pts[(i + 1) % pts.length];
    area += (p1.x * p2.y - p2.x * p1.y);
  }
  return area / 2;
}

async function main() {
  const uniqueLids = [...new Set(Object.values(raceToLayout).map(v => v.lid))];
  console.log(`Processing ${uniqueLids.length} unique layouts for ${Object.keys(raceToLayout).length} races...`);

  // 1. Fetch SVGs
  const svgDataCache = {};
  for (const lid of uniqueLids) {
    const minUrl = `https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white/${lid}.svg`;
    try {
      const minText = await fetchText(minUrl);
      const match = minText.match(/<path\s+d="([^"]+)"/);
      if (!match) throw new Error(`No path d in ${lid}`);
      const pathD = match[1];

      // Try fetching detailed SVG to get start line coordinates
      let startPoint = null;
      try {
        const detUrl = `https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/detailed/white/${lid}.svg`;
        const detText = await fetchText(detUrl);
        const paths = [...detText.matchAll(/<path\s+d="([^"]+)"/g)];
        if (paths.length >= 2) {
          const startLineD = paths[1][1];
          const startProps = new svgPathProperties(startLineD);
          const pStart = startProps.getPointAtLength(startProps.getTotalLength() / 2);
          startPoint = { x: pStart.x, y: pStart.y };
        }
      } catch (e) {
        // Fallback: start at beginning of minimal path
      }

      svgDataCache[lid] = { pathD, startPoint };
    } catch (e) {
      console.error(`Error loading ${lid}: ${e.message}`);
    }
  }

  const NUM_SAMPLES = 800;
  const TARGET_W = 1920;
  const TARGET_H = 1080;
  const finalTracks = {};

  for (const [raceName, info] of Object.entries(raceToLayout)) {
    const { lid, angle, direction } = info;
    const svgItem = svgDataCache[lid];
    if (!svgItem) continue;

    const props = new svgPathProperties(svgItem.pathD);
    const totalLen = props.getTotalLength();

    // Sample points along the SVG path
    const rawPoints = [];
    for (let i = 0; i < NUM_SAMPLES; i++) {
      const dist = (i / NUM_SAMPLES) * totalLen;
      const pt = props.getPointAtLength(dist);
      rawPoints.push({ x: pt.x, y: pt.y });
    }

    // Find start point on the path
    let startIdx = 0;
    if (svgItem.startPoint) {
      let minDistSq = Infinity;
      for (let i = 0; i < rawPoints.length; i++) {
        const dx = rawPoints[i].x - svgItem.startPoint.x;
        const dy = rawPoints[i].y - svgItem.startPoint.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < minDistSq) {
          minDistSq = distSq;
          startIdx = i;
        }
      }
    }

    // Rotate all raw points around (250, 250)
    const rotated = rawPoints.map(p => rotatePoint(p.x, p.y, angle));

    // Calculate bounding box in rotated space
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const p of rotated) {
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }

    const bboxW = maxX - minX;
    const bboxH = maxY - minY;

    // Scale to ~72% of canvas (matching generate_all_white_outlines.py)
    const scale = Math.min((TARGET_W * 0.72) / bboxW, (TARGET_H * 0.72) / bboxH);
    const newW = bboxW * scale;
    const newH = bboxH * scale;
    const offsetX = (TARGET_W - newW) / 2;
    const offsetY = (TARGET_H - newH) / 2;

    // Transform points to 1920x1080 canvas coordinates
    const canvasPoints = rotated.map(p => ({
      x: Math.round((offsetX + (p.x - minX) * scale) * 10) / 10,
      y: Math.round((offsetY + (p.y - minY) * scale) * 10) / 10,
    }));

    // Rotate point array so startIdx is index 0
    let alignedPoints = [];
    for (let i = 0; i < NUM_SAMPLES; i++) {
      alignedPoints.push(canvasPoints[(startIdx + i) % NUM_SAMPLES]);
    }

    // Check winding direction: SVG y is inverted (down is positive)
    // In screen coords, positive signed area means clockwise, negative means counter-clockwise
    const signedArea = computeSignedArea(alignedPoints);
    const isCurrentlyClockwise = signedArea > 0;
    const targetClockwise = (direction === 'clockwise');

    if (isCurrentlyClockwise !== targetClockwise) {
      // Reverse array starting from index 0
      const startP = alignedPoints[0];
      const rest = alignedPoints.slice(1).reverse();
      alignedPoints = [startP, ...rest];
    }

    // Calculate total track perimeter in screen pixels for speed and spacing calculations
    let trackLengthPx = 0;
    for (let i = 0; i < alignedPoints.length; i++) {
      const p1 = alignedPoints[i];
      const p2 = alignedPoints[(i + 1) % alignedPoints.length];
      const d = Math.hypot(p2.x - p1.x, p2.y - p1.y);
      trackLengthPx += d;
    }

    finalTracks[raceName] = {
      layout_id: lid,
      direction: direction,
      f1_orientation: angle,
      track_length_px: Math.round(trackLengthPx),
      start_line: alignedPoints[0],
      points: alignedPoints.map(p => [p.x, p.y]),
    };
    console.log(`[OK] ${raceName} (${lid}): ${alignedPoints.length} pts, len=${Math.round(trackLengthPx)}px, dir=${direction}`);
  }

  const outPath = path.join(__dirname, '..', 'assets', 'circuit_tracks.json');
  fs.writeFileSync(outPath, JSON.stringify(finalTracks, null, 2), 'utf-8');
  console.log(`\nSuccessfully saved ${Object.keys(finalTracks).length} tracks to ${outPath}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
