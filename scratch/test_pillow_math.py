import math
from PIL import Image
import numpy as np

# Test Pillow's rotate transform
w, h = 500, 500
angle = -90 # Pillow parameter

img = Image.new("RGBA", (w, h), (0,0,0,0))
# Let's see rotated size
rot = img.rotate(angle, expand=True)
rot_w, rot_h = rot.size
print(f"Original size: {w}x{h}, Rotated size: {rot_w}x{rot_h}")

# In Pillow, rotate(angle, expand=True) rotates around (w/2, h/2) counter-clockwise by angle
# With y down, counter-clockwise rotation by angle rad:
# x_rel = x - cx
# y_rel = y - cy
# x_rot = x_rel * cos(a) + y_rel * sin(a)
# y_rot = -x_rel * sin(a) + y_rel * cos(a)
# Then translated to center of rot image: + rot_w/2, + rot_h/2
