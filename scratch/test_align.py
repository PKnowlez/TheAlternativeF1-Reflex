import math
import json
import urllib.request
import resvg_py
from PIL import Image
import numpy as np

# Let's test on Silverstone
lid = 'silverstone-8'
angle = 90 # F1 orientation

# 1. Fetch SVG
url = f"https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/minimal/white/{lid}.svg"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    svg_data = resp.read().decode('utf-8')

png_bytes = resvg_py.svg_to_bytes(svg_data)
img = Image.open(io := __import__('io').BytesIO(png_bytes))

# Rotate by -angle exactly like generate_all_white_outlines.py
rotated = img.rotate(-angle, expand=True, resample=Image.Resampling.BICUBIC)
bbox = rotated.getbbox() # (left, top, right, bottom)
cropped = rotated.crop(bbox)

target_w, target_h = 1920, 1080
scale = min((target_w * 0.72) / cropped.width, (target_h * 0.72) / cropped.height)
new_w = int(cropped.width * scale)
new_h = int(cropped.height * scale)
offset_x = (target_w - new_w) // 2
offset_y = (target_h - new_h) // 2

print("Rotated size:", rotated.size)
print("Bbox:", bbox)
print("Cropped size:", cropped.size)
print("Scale:", scale, "Offset:", offset_x, offset_y)

# Pillow rotate transform math:
# Let rad = math.radians(-angle)
# Pillow rotates around (img.width/2, img.height/2)
cx_in, cy_in = img.width / 2, img.height / 2
cx_out, cy_out = rotated.width / 2, rotated.height / 2
rad = math.radians(-angle)
cos_a = math.cos(rad)
sin_a = math.sin(rad)

def transform_point(x, y):
    dx = x - cx_in
    dy = y - cy_in
    # In Pillow coordinate system (y down, rotation is counter-clockwise for positive, clockwise for negative):
    # For positive rotation theta (CCW in standard, CW in y-down):
    # x' = dx * cos - dy * sin
    # y' = dx * sin + dy * cos
    # Wait, in Pillow, positive angle rotates image counter-clockwise.
    # A point on the image rotates counter-clockwise.
    # In screen coordinates (y down), CCW rotation by theta:
    # x_rot = dx * cos(theta) + dy * sin(theta)
    # y_rot = -dx * sin(theta) + dy * cos(theta)
    # Let's test both signs:
    x_rot = dx * cos_a + dy * sin_a
    y_rot = -dx * sin_a + dy * cos_a
    
    rx = x_rot + cx_out
    ry = y_rot + cy_out
    
    # Now crop & scale
    sx = offset_x + (rx - bbox[0]) * scale
    sy = offset_y + (ry - bbox[1]) * scale
    return sx, sy

# Let's test with the actual track image!
track_img = Image.open('assets/TrackMaps/Silverstone.jpg').convert('L')
arr = np.array(track_img)
white_y, white_x = np.where(arr > 150)
white_coords = np.column_stack((white_x, white_y))

# Let's load the raw sampled points from scratch/raw_silverstone.json if available
