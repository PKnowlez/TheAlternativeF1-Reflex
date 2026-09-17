import urllib.request
import re
import math
from PIL import Image, ImageDraw
import resvg_py
import io

# Let's inspect the SVG for silverstone-8
url_det = "https://raw.githubusercontent.com/julesr0y/f1-circuits-svg/main/circuits/detailed/white/silverstone-8.svg"
req = urllib.request.Request(url_det, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    svg_data = resp.read().decode('utf-8')

# Extract the 3 paths
paths = re.findall(r'<path d="([^"]+)"', svg_data)
print(f"Found {len(paths)} paths in silverstone-8.svg")
# Path 0: track
# Path 1: start line
# Path 2: direction arrow
