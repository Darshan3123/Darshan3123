"""
Prepare the avatar/photo for clean ASCII conversion:
  1. isolate the subject (transparent/white background)
  2. bilateral-smooth away noise while keeping drawn lines sharp
  3. stretch tones so skin lands near bright and hair/lines stay dark
  4. darken the line work (difference-of-gaussians ridges) -- eyes, pupils, beard, smile
  5. composite onto white and crop square around the subject

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.

    python scripts/prep_photo.py [input.png] [output.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

LINE_WEIGHT = 0.65     # how hard drawn lines are pushed toward black

# 1. Load image and cut out background
img_bgr = cv2.imread(INP)
if img_bgr is None:
    raise FileNotFoundError(f"Could not load image: {INP}")

h, w = img_bgr.shape[:2]

# Use floodFill from corners to cleanly isolate uniform background
mask = np.zeros((h + 2, w + 2), np.uint8)
# floodfill from all 4 corners
for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
    cv2.floodFill(
        img_bgr.copy(),
        mask,
        seed,
        (0, 0, 0),
        (10, 10, 10),
        (10, 10, 10),
        cv2.FLOODFILL_MASK_ONLY | (255 << 8),
    )

bg_mask = mask[1:-1, 1:-1]
alpha = 255 - bg_mask

# If corners weren't background or rembg is available and needed, we can also refine
gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

# 2. Smooth texture, keep edges
smooth = gray.copy()
for _ in range(3):
    smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

# 3. Tone stretch over the subject only
subject_pixels = smooth[alpha > 128]
if len(subject_pixels) == 0:
    subject_pixels = smooth

lo, hi = np.percentile(subject_pixels, [2, 92])
if hi <= lo:
    hi = lo + 1.0
tone = np.clip((smooth.astype(np.float32) - lo) / (hi - lo), 0, 1)

# 4. Dark-on-light ridges -> darken lines (hair, eyes, beard contours)
fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
coarse = cv2.GaussianBlur(smooth, (0, 0), 6).astype(np.float32)
lines = np.clip((coarse - fine) / 40.0, 0, 1)
out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255.0

# 5. Composite onto pure white with slight feathering
mask_feather = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
out = out * mask_feather + 255.0 * (1.0 - mask_feather)

# Crop square around the subject
ys, xs = np.where(alpha > 20)
if len(xs) > 0 and len(ys) > 0:
    side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
    cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
else:
    side = max(h, w)
    cx, cy = w // 2, h // 2

canvas = np.full((side, side), 255, np.uint8)
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])

dx0, dy0 = sx0 - x0, sy0 - y0
dx1, dy1 = dx0 + (sx1 - sx0), dy0 + (sy1 - sy0)
canvas[dy0:dy1, dx0:dx1] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
