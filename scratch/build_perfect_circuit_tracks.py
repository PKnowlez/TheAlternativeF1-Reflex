import os
import math
import json
import urllib.request
import resvg_py
from PIL import Image
import numpy as np
import subprocess

race_to_layout = {
    'Abu Dhabi': ('yas-marina-2', 99, 'counter-clockwise'),
    'Australia': ('melbourne-2', -46, 'clockwise'),
    'Austria': ('spielberg-3', -31, 'clockwise'),
    'Austria Reverse': ('spielberg-3', -31, 'clockwise'),
    'Austria Sprint': ('spielberg-3', -31, 'clockwise'),
    'Bahrain': ('bahrain-1', 0, 'clockwise'),
    'Bahrain Sprint': ('bahrain-1', 0, 'clockwise'),
    'Baku': ('baku-1', 73, 'counter-clockwise'),
    'Brazil': ('interlagos-2', 90, 'counter-clockwise'),
    'Brazil Sprint': ('interlagos-2', 90, 'counter-clockwise'),
    'COTA': ('austin-1', 30, 'counter-clockwise'),
    'COTA Sprint': ('austin-1', 30, 'counter-clockwise'),
    'Canada': ('montreal-6', -55, 'clockwise'),
    'China': ('shanghai-1', 24, 'clockwise'),
    'China Sprint': ('shanghai-1', 24, 'clockwise'),
    'France': ('paul-ricard-3', 0, 'clockwise'),
    'Germany': ('hockenheimring-4', 0, 'clockwise'),
    'Hungary': ('hungaroring-3', 52, 'clockwise'),
    'Imola': ('imola-3', 0, 'counter-clockwise'),
    'Jeddah': ('jeddah-1', 0, 'counter-clockwise'),
    'Las Vegas': ('las-vegas-1', 0, 'counter-clockwise'),
    'Mexico': ('mexico-city-3', -8, 'clockwise'),
    'Miami': ('miami-1', -18, 'counter-clockwise'),
    'Miami Sprint': ('miami-1', -18, 'counter-clockwise'),
    'Monaco': ('monaco-6', 45, 'clockwise'),
    'Monza': ('monza-7', -95, 'clockwise'),
    'Mugello': ('mugello-1', 0, 'clockwise'),
    'Nurburgring': ('nurburgring-4', 0, 'clockwise'),
    'Portugal': ('portimao-1', 0, 'clockwise'),
    'Qatar': ('lusail-1', 0, 'clockwise'),
    'Russia': ('sochi-1', 0, 'clockwise'),
    'Saudi Arabia': ('jeddah-1', 0, 'counter-clockwise'),
    'Silverstone': ('silverstone-8', 90, 'clockwise'),
    'Silverstone Sprint': ('silverstone-8', 90, 'clockwise'),
    'Singapore': ('marina-bay-4', 0, 'counter-clockwise'),
    'Singapore Sprint': ('marina-bay-4', 0, 'counter-clockwise'),
    'Spa': ('spa-francorchamps-4', -100, 'clockwise'),
    'Spa Sprint': ('spa-francorchamps-4', -100, 'clockwise'),
    'Spain': ('catalunya-6', 32, 'clockwise'),
    'Suzuka': ('suzuka-2', 0, 'clockwise'),
    'Turkey': ('istanbul-1', 0, 'counter-clockwise'),
    'Zandvoort': ('zandvoort-5', 0, 'clockwise'),
    'Zandvoort Sprint': ('zandvoort-5', 0, 'clockwise'),
}

headers = {'User-Agent': 'Mozilla/5.0'}
unique_lids = sorted(list(set(v[0] for v in race_to_layout.values())))
print(f"Sampling {len(unique_lids)} unique circuit layouts...")

# 1. Fetch SVGs and sample 800 points for each unique layout
raw_sampled_data = {}
for lid in unique_lids:
    url_min = f"https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white/{lid}.svg"
    req = urllib.request.Request(url_min, headers=headers)
    with urllib.request.urlopen(req) as resp:
        svg_min = resp.read().decode('utf-8')
    
    # Try start line from detailed
    start_pt = None
    try:
        url_det = f"https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/detailed/white/{lid}.svg"
        req_det = urllib.request.Request(url_det, headers=headers)
        with urllib.request.urlopen(req_det) as resp_det:
            svg_det = resp_det.read().decode('utf-8')
        paths = svg_det.split('<path d="')
        if len(paths) >= 3:
            # Second path is start line
            start_d = paths[2].split('"')[0]
            out_start = subprocess.check_output(['node', '-e', f"""
            const {{ svgPathProperties }} = require('./scratch/node_modules/svg-path-properties/dist/main.cjs');
            const props = new svgPathProperties(`{start_d}`);
            const pt = props.getPointAtLength(props.getTotalLength() / 2);
            console.log(JSON.stringify([pt.x, pt.y]));
            """])
            start_pt = json.loads(out_start)
    except Exception:
        pass
    
    # Sample minimal path
    main_d = svg_min.split('<path d="')[1].split('"')[0]
    out_pts = subprocess.check_output(['node', '-e', f"""
    const {{ svgPathProperties }} = require('./scratch/node_modules/svg-path-properties/dist/main.cjs');
    const props = new svgPathProperties(`{main_d}`);
    const len = props.getTotalLength();
    const pts = [];
    for (let i = 0; i < 800; i++) {{
      const pt = props.getPointAtLength((i / 800) * len);
      pts.push([pt.x, pt.y]);
    }}
    console.log(JSON.stringify(pts));
    """])
    pts = json.loads(out_pts)
    raw_sampled_data[lid] = {
        'svg_data': svg_min,
        'points': pts,
        'start_pt': start_pt
    }

def compute_signed_area(pts):
    area = 0.0
    for i in range(len(pts)):
        p1 = pts[i]
        p2 = pts[(i + 1) % len(pts)]
        area += (p1[0] * p2[1] - p2[0] * p1[1])
    return area / 2.0

final_tracks = {}
target_w, target_h = 1920, 1080

for race_name, (lid, f1_angle, target_direction) in race_to_layout.items():
    lid_info = raw_sampled_data[lid]
    raw_pts = lid_info['points']
    start_pt = lid_info['start_pt']
    
    # Find start line index in raw_pts
    start_idx = 0
    if start_pt is not None:
        min_d_sq = float('inf')
        for i, p in enumerate(raw_pts):
            d_sq = (p[0] - start_pt[0])**2 + (p[1] - start_pt[1])**2
            if d_sq < min_d_sq:
                min_d_sq = d_sq
                start_idx = i

    # Render rotated image to get exact Pillow bounding box
    pillow_angle = -f1_angle
    png_bytes = resvg_py.svg_to_bytes(lid_info['svg_data'])
    img = Image.open(io := __import__('io').BytesIO(png_bytes))
    if pillow_angle != 0:
        rotated = img.rotate(pillow_angle, expand=True, resample=Image.Resampling.BICUBIC)
    else:
        rotated = img
    
    bbox = rotated.getbbox()
    cropped_w = bbox[2] - bbox[0]
    cropped_h = bbox[3] - bbox[1]
    
    scale = min((target_w * 0.72) / cropped_w, (target_h * 0.72) / cropped_h)
    new_w = int(cropped_w * scale)
    new_h = int(cropped_h * scale)
    offset_x = (target_w - new_w) // 2
    offset_y = (target_h - new_h) // 2
    
    rot_w, rot_h = rotated.size
    rad = math.radians(pillow_angle)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    
    screen_pts = []
    for x, y in raw_pts:
        dx = x - 250
        dy = y - 250
        x_rot = dx * cos_a + dy * sin_a + rot_w / 2
        y_rot = -dx * sin_a + dy * cos_a + rot_h / 2
        sx = offset_x + (x_rot - bbox[0]) * scale
        sy = offset_y + (y_rot - bbox[1]) * scale
        screen_pts.append((round(sx, 1), round(sy, 1)))
        
    # Rotate array so start_idx is index 0
    aligned_pts = [screen_pts[(start_idx + i) % len(screen_pts)] for i in range(len(screen_pts))]
    
    # Check winding direction
    area = compute_signed_area(aligned_pts)
    is_cw = area > 0
    should_be_cw = (target_direction == 'clockwise')
    
    if is_cw != should_be_cw:
        start_p = aligned_pts[0]
        aligned_pts = [start_p] + list(reversed(aligned_pts[1:]))
        
    track_len = 0.0
    for i in range(len(aligned_pts)):
        p1 = aligned_pts[i]
        p2 = aligned_pts[(i + 1) % len(aligned_pts)]
        track_len += math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        
    final_tracks[race_name] = {
        'layout_id': lid,
        'direction': target_direction,
        'f1_orientation': f1_angle,
        'track_length_px': round(track_len),
        'start_line': aligned_pts[0],
        'points': aligned_pts,
    }
    print(f"[OK] {race_name}: {len(aligned_pts)} pts, length={round(track_len)}px, dir={target_direction}")

out_path = os.path.join("assets", "circuit_tracks.json")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(final_tracks, f)

print(f"\nSaved all 43 tracks to {out_path} ({os.path.getsize(out_path)} bytes)")
