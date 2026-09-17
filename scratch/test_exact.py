import math
import json
import urllib.request
import resvg_py
from PIL import Image
import numpy as np

# 1. Load Silverstone minimal SVG
lid = 'silverstone-8'
f1_orientation = 90
pillow_angle = -f1_orientation

url = f"https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white/{lid}.svg"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    svg_data = resp.read().decode('utf-8')

png_bytes = resvg_py.svg_to_bytes(svg_data)
img = Image.open(__import__('io').BytesIO(png_bytes))
rotated = img.rotate(pillow_angle, expand=True, resample=Image.Resampling.BICUBIC)
bbox = rotated.getbbox() # (left, top, right, bottom)
cropped_w = bbox[2] - bbox[0]
cropped_h = bbox[3] - bbox[1]

target_w, target_h = 1920, 1080
scale = min((target_w * 0.72) / cropped_w, (target_h * 0.72) / cropped_h)
new_w = int(cropped_w * scale)
new_h = int(cropped_h * scale)
offset_x = (target_w - new_w) // 2
offset_y = (target_h - new_h) // 2

rot_w, rot_h = rotated.size
rad = math.radians(pillow_angle)
cos_a = math.cos(rad)
sin_a = math.sin(rad)

# Load points from Node.js sampled points or let's sample via node
# Let's run node to get raw 500x500 points for silverstone
import subprocess
out = subprocess.check_output(['node', '-e', f"""
const {{ svgPathProperties }} = require('./scratch/node_modules/svg-path-properties/dist/main.cjs');
const props = new svgPathProperties(`{svg_data.split('<path d="')[1].split('"')[0]}`);
const len = props.getTotalLength();
const pts = [];
for (let i = 0; i < 800; i++) {{
  const pt = props.getPointAtLength((i / 800) * len);
  pts.push([pt.x, pt.y]);
}}
console.log(JSON.stringify(pts));
"""])
raw_pts = json.loads(out)

# Transform each raw point
screen_pts = []
for x, y in raw_pts:
    dx = x - 250
    dy = y - 250
    x_rot = dx * cos_a + dy * sin_a + rot_w / 2
    y_rot = -dx * sin_a + dy * cos_a + rot_h / 2
    sx = offset_x + (x_rot - bbox[0]) * scale
    sy = offset_y + (y_rot - bbox[1]) * scale
    screen_pts.append((sx, sy))

# Test against actual white line in assets/TrackMaps/Silverstone.jpg!
track_img = Image.open('assets/TrackMaps/Silverstone.jpg').convert('L')
arr = np.array(track_img)
white_y, white_x = np.where(arr > 150)
white_coords = np.column_stack((white_x, white_y))

dists = []
for p in screen_pts[::10]:
    d = np.min(np.hypot(white_coords[:, 0] - p[0], white_coords[:, 1] - p[1]))
    dists.append(d)

print(f"MEAN DISTANCE: {np.mean(dists):.2f} pixels! (MAX: {np.max(dists):.2f}px)")
