"""Generate a CPSL app icon: a cycling/analytics emblem on a racing-gradient disc."""
from PIL import Image, ImageDraw
import math

S = 512
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ── Background disc with racing gradient (diagonal) ──
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
c1 = (37, 99, 235)   # electric blue
c2 = (168, 85, 247)  # violet
c3 = (16, 185, 129)  # emerald
for y in range(S):
    t = y / S
    if t < 0.5:
        col = lerp(c1, c2, t * 2)
    else:
        col = lerp(c2, c3, (t - 0.5) * 2)
    d.line([(0, y), (S, y)], fill=col + (255,))

# subtle vignette
vig = Image.new("L", (S, S), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([20, 20, S - 20, S - 20], fill=255)
mask = Image.new("L", (S, S), 0)
md = ImageDraw.Draw(mask)
md.ellipse([8, 8, S - 8, S - 8], fill=255)
img.putalpha(mask)
# darken corners
corner = Image.new("RGBA", (S, S), (0, 0, 0, 0))
cd = ImageDraw.Draw(corner)
cd.ellipse([0, 0, S, S], fill=(0, 0, 0, 60))
img = Image.alpha_composite(img, corner)

# ── Cycling wheel (top-left) ──
cx, cy, r = 175, 175, 78
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 235), width=10)
d.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], outline=(255, 255, 255, 180), width=6)
for i in range(12):
    a = math.radians(i * 30)
    x1, y1 = cx + math.cos(a) * (r // 3), cy + math.sin(a) * (r // 3)
    x2, y2 = cx + math.cos(a) * r, cy + math.sin(a) * r
    d.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 160), width=3)

# ── Analytics line chart (bottom-right) ──
px, py, pw, ph = 250, 250, 210, 190
pts = [(px + i * pw / 5, py + ph - (40 + 120 * (0.3 + 0.7 * abs(math.sin(i * 1.1))))) for i in range(6)]
d.line(pts, fill=(255, 255, 255, 240), width=7, joint="curve")
for (x, y) in pts:
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255, 255))

# ── Lightning bolt accent (center) ──
def bolt(cx0, cy0, s, col):
    pts = [(cx0, cy0 - s), (cx0 - s * 0.55, cy0 + s * 0.1), (cx0 - s * 0.1, cy0 + s * 0.1),
           (cx0 - s * 0.2, cy0 + s), (cx0 + s * 0.6, cy0 - s * 0.15), (cx0 + s * 0.1, cy0 - s * 0.15)]
    d.polygon(pts, fill=col)
bolt(256, 256, 46, (255, 221, 64, 255))

img.save("assets/icon_new.png")
print("saved assets/icon_new.png")

# Build .ico from multiple sizes
sizes = [16, 24, 32, 48, 64, 128, 256, 512]
frames = [img.resize((s, s), Image.LANCZOS) for s in sizes]
img.save("assets/icon.ico", sizes=[(s, s) for s in sizes])
print("saved assets/icon.ico")

# macOS icns placeholder (copy png at 512)
img.save("assets/icon_512x512.png")
print("done")
