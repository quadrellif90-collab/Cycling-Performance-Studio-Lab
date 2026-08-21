"""Generate PNG icons for the CPSL intervals.icu browser extension."""
from PIL import Image, ImageDraw

def make(size, path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # rounded racing gradient-ish disc
    d.ellipse([2, 2, size-2, size-2], fill=(15, 23, 42, 255))
    d.ellipse([int(size*0.12), int(size*0.12), int(size*0.88), int(size*0.88)], fill=(30, 41, 59, 255))
    # lightning bolt (CPSL mark)
    cx, cy = size//2, size//2
    bolt = [
        (cx+int(size*0.10), int(size*0.20)),
        (cx-int(size*0.14), cy+int(size*0.06)),
        (cx+int(size*0.02), cy+int(size*0.06)),
        (cx-int(size*0.10), int(size*0.80)),
        (cx+int(size*0.16), cy-int(size*0.04)),
        (cx+int(size*0.0), cy-int(size*0.04)),
    ]
    d.polygon(bolt, fill=(56, 189, 248, 255))
    img.save(path)
    print("wrote", path)

import os
os.makedirs("extensions/icu-cpsl/icons", exist_ok=True)
for s in (16, 48, 128):
    make(s, f"extensions/icu-cpsl/icons/icon-{s}.png")
