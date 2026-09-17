import os
import math
import json
import urllib.request
import resvg_py
from PIL import Image
import subprocess

headers = {'User-Agent': 'Mozilla/5.0'}
url_min = "https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white/bahrain-1.svg"
req = urllib.request.Request(url_min, headers=headers)
with urllib.request.urlopen(req) as resp:
    svg_min = resp.read().decode('utf-8')

url_det = "https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/detailed/white/bahrain-1.svg"
req_det = urllib.request.Request(url_det, headers=headers)
with urllib.request.urlopen(req_det) as resp_det:
    svg_det = resp_det.read().decode('utf-8')

paths = svg_det.split('<path d="')
start_d = paths[2].split('"')[0]
out_start = subprocess.check_output(['node', '-e', f"""
const {{ svgPathProperties }} = require('./scratch/node_modules/svg-path-properties/dist/main.cjs');
const props = new svgPathProperties(`{start_d}`);
const pt = props.getPointAtLength(props.getTotalLength() / 2);
console.log(JSON.stringify([pt.x, pt.y]));
"""])
start_pt = json.loads(out_start)
print("Start point in SVG:", start_pt)

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

def compute_signed_area(pts):
    area = 0.0
    for i in range(len(pts)):
        p1 = pts[i]
        p2 = pts[(i + 1) % len(pts)]
        area += (p1[0] * p2[1] - p2[0] * p1[1])
    return area / 2.0

target_w, target_h = 1920, 1080
min_d_sq = float('inf')
start_idx = 0
for i, p in enumerate(pts):
    d_sq = (p[0] - start_pt[0])**2 + (p[1] - start_pt[1])**2
    if d_sq < min_d_sq:
        min_d_sq = d_sq
        start_idx = i

png_bytes = resvg_py.svg_to_bytes(svg_min)
img = Image.open(io := __import__('io').BytesIO(png_bytes))
bbox = img.getbbox()
cropped_w = bbox[2] - bbox[0]
cropped_h = bbox[3] - bbox[1]

scale = min((target_w * 0.72) / cropped_w, (target_h * 0.72) / cropped_h)
new_w = int(cropped_w * scale)
new_h = int(cropped_h * scale)
offset_x = (target_w - new_w) // 2
offset_y = (target_h - new_h) // 2

screen_pts = []
for x, y in pts:
    sx = offset_x + (x - bbox[0]) * scale
    sy = offset_y + (y - bbox[1]) * scale
    screen_pts.append((round(sx, 1), round(sy, 1)))

aligned_pts = [screen_pts[(start_idx + i) % len(screen_pts)] for i in range(len(screen_pts))]

area = compute_signed_area(aligned_pts)
print("Signed area:", area, "is_cw:", area > 0)
if area < 0: # counter-clockwise, invert to clockwise
    start_p = aligned_pts[0]
    aligned_pts = [start_p] + list(reversed(aligned_pts[1:]))

track_len = 0.0
for i in range(len(aligned_pts)):
    p1 = aligned_pts[i]
    p2 = aligned_pts[(i + 1) % len(aligned_pts)]
    track_len += math.hypot(p2[0] - p1[0], p2[1] - p1[1])

print(f"Bahrain 2024: {len(aligned_pts)} points, track length = {round(track_len)} px")
print(f"Start line: {aligned_pts[0]}")
