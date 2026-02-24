#!/usr/bin/env python3
"""Generate a sassy sci-fi robot avatar for Magi"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import random

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# --- Background gradient: deep space dark blue-purple ---
bg = Image.new("RGBA", (SIZE, SIZE))
bg_draw = ImageDraw.Draw(bg)
for y in range(SIZE):
    r = int(4 + (y / SIZE) * 12)
    g = int(0 + (y / SIZE) * 4)
    b = int(20 + (y / SIZE) * 30)
    bg_draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# Subtle star field
random.seed(42)
for _ in range(80):
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)
    brightness = random.randint(80, 200)
    r2 = random.randint(1, 2)
    bg_draw.ellipse([x-r2, y-r2, x+r2, y+r2], fill=(brightness, brightness, brightness+30, 200))

img = bg.copy()
draw = ImageDraw.Draw(img)

CX, CY = SIZE // 2, SIZE // 2

# --- Hexagonal frame / outer ring ---
def hex_points(cx, cy, r, rotation=0):
    pts = []
    for i in range(6):
        angle = math.radians(60 * i + rotation)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts

# Outer glow ring
glow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow_layer)
hex_outer = hex_points(CX, CY, 230, 30)
for offset in range(12, 0, -2):
    alpha = int(30 + offset * 8)
    glow_draw.polygon(hex_outer, outline=(0, 200+offset*5, 255, alpha))

# Apply glow blur
glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))
img = Image.alpha_composite(img, glow_layer)
draw = ImageDraw.Draw(img)

# Main hex border
hex_pts = hex_points(CX, CY, 228, 30)
draw.polygon(hex_pts, outline=(0, 220, 255, 255))
draw.polygon(hex_points(CX, CY, 224, 30), outline=(0, 180, 220, 180))

# Inner hex (robot face area) - dark metal background
inner_hex = hex_points(CX, CY, 210, 30)
# Dark metallic gradient fill via manual draw
metal_img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
metal_draw = ImageDraw.Draw(metal_img)
for y in range(SIZE):
    t = y / SIZE
    r = int(20 + t * 15)
    g = int(22 + t * 18)
    b = int(32 + t * 20)
    metal_draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# Mask metal to hex shape
mask = Image.new("L", (SIZE, SIZE), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.polygon(inner_hex, fill=255)
metal_img.putalpha(mask)
img = Image.alpha_composite(img, metal_img)
draw = ImageDraw.Draw(img)

# Hex inner border
draw.polygon(inner_hex, outline=(30, 120, 180, 200))

# --- Robot face ---
# Head: rounded rectangle
HEAD_W, HEAD_H = 200, 160
HEAD_X = CX - HEAD_W // 2
HEAD_Y = CY - HEAD_H // 2 + 10
RADIUS = 25

def rounded_rect(draw, x, y, w, h, r, fill=None, outline=None, width=2):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=width)

# Shadow behind head
shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.rounded_rectangle([HEAD_X-3, HEAD_Y+3, HEAD_X+HEAD_W+3, HEAD_Y+HEAD_H+3], radius=RADIUS, fill=(0, 0, 0, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(img, shadow)
draw = ImageDraw.Draw(img)

# Head body - dark metallic
rounded_rect(draw, HEAD_X, HEAD_Y, HEAD_W, HEAD_H, RADIUS, 
             fill=(28, 32, 45), outline=(60, 160, 200, 200), width=2)

# Subtle panel lines on head
draw.line([(HEAD_X+20, HEAD_Y+HEAD_H//2), (HEAD_X+HEAD_W-20, HEAD_Y+HEAD_H//2)], 
          fill=(50, 100, 140, 80), width=1)

# --- Eyes: glowing cyan ---
EYE_Y = HEAD_Y + HEAD_H // 2 - 20
EYE_OFFSET = 40
EYE_W, EYE_H = 50, 22

def draw_eye(base_img, base_draw, cx, cy, w, h):
    """Draw a glowing angular robot eye"""
    # Glow behind eye
    glow_e = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_e)
    for g in range(20, 0, -2):
        a = int(15 * g)
        gd.ellipse([cx - w//2 - g*2, cy - h//2 - g, cx + w//2 + g*2, cy + h//2 + g], 
                   fill=(0, 230, 255, a))
    glow_e = glow_e.filter(ImageFilter.GaussianBlur(5))
    result_img = Image.alpha_composite(base_img, glow_e)
    d = ImageDraw.Draw(result_img)
    
    # Eye socket (dark)
    d.rounded_rectangle([cx-w//2-2, cy-h//2-2, cx+w//2+2, cy+h//2+2], radius=3,
                         fill=(10, 15, 25))
    # Eye iris - bright cyan
    d.rounded_rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], radius=3,
                         fill=(0, 200, 240, 255), outline=(100, 240, 255, 255), width=1)
    # Pupil - thin vertical slit (snarky!)
    pupil_w = 6
    d.rounded_rectangle([cx-pupil_w//2, cy-h//2+3, cx+pupil_w//2, cy+h//2-3], radius=2,
                         fill=(0, 20, 40, 255))
    # Highlight
    d.ellipse([cx-w//4-3, cy-h//2+4, cx-w//4+3, cy-h//2+8], fill=(200, 255, 255, 220))
    return result_img, d

img, draw = draw_eye(img, draw, CX - EYE_OFFSET, EYE_Y, EYE_W, EYE_H)
img, draw = draw_eye(img, draw, CX + EYE_OFFSET, EYE_Y, EYE_W, EYE_H)

# --- Raised eyebrow plates (angular/sharp = snarky!) ---
# Left brow - angled up on inner side
brow_y_inner = EYE_Y - EYE_H // 2 - 16
brow_y_outer = EYE_Y - EYE_H // 2 - 8
# Left brow
draw.polygon([
    (CX - EYE_OFFSET - EYE_W//2 - 4, brow_y_outer),
    (CX - EYE_OFFSET + EYE_W//2 + 4, brow_y_inner),
    (CX - EYE_OFFSET + EYE_W//2 + 4, brow_y_inner + 6),
    (CX - EYE_OFFSET - EYE_W//2 - 4, brow_y_outer + 6),
], fill=(0, 180, 220, 220))

# Right brow - mirror
draw.polygon([
    (CX + EYE_OFFSET - EYE_W//2 - 4, brow_y_inner),
    (CX + EYE_OFFSET + EYE_W//2 + 4, brow_y_outer),
    (CX + EYE_OFFSET + EYE_W//2 + 4, brow_y_outer + 6),
    (CX + EYE_OFFSET - EYE_W//2 - 4, brow_y_inner + 6),
], fill=(0, 180, 220, 220))

# --- Nose: small rectangular ridge ---
NOSE_Y = EYE_Y + EYE_H // 2 + 12
draw.rounded_rectangle([CX - 8, NOSE_Y, CX + 8, NOSE_Y + 14], radius=3, 
                        fill=(40, 50, 65), outline=(60, 120, 160, 150))

# --- Mouth: snarky smirk (asymmetric) ---
MOUTH_Y = HEAD_Y + HEAD_H - 38
MOUTH_W = 80
# Slightly raised on the right = smirk
pts_mouth = [
    (CX - MOUTH_W//2, MOUTH_Y + 8),
    (CX - MOUTH_W//4, MOUTH_Y + 4),
    (CX, MOUTH_Y + 2),
    (CX + MOUTH_W//4, MOUTH_Y),
    (CX + MOUTH_W//2, MOUTH_Y - 2),
]
# Draw as thick line
for i in range(len(pts_mouth) - 1):
    draw.line([pts_mouth[i], pts_mouth[i+1]], fill=(0, 200, 240, 230), width=4)

# Mouth grill lines
for i in range(5):
    gx = CX - MOUTH_W//2 + 12 + i * 14
    gy_top = MOUTH_Y - 10
    gy_bot = MOUTH_Y + 12
    alpha = 120
    draw.line([(gx, gy_top), (gx, gy_bot)], fill=(0, 160, 200, alpha), width=2)

# Mouth border box
draw.rounded_rectangle([CX - MOUTH_W//2 - 5, MOUTH_Y - 12, CX + MOUTH_W//2 + 5, MOUTH_Y + 12],
                        radius=5, outline=(50, 140, 180, 160), width=1)

# --- Antenna: snarky little spike on top ---
ANT_BASE_X = CX + 30
ANT_BASE_Y = HEAD_Y - 2
ANT_TOP_Y = HEAD_Y - 45
# Antenna stick
draw.line([(ANT_BASE_X, ANT_BASE_Y), (ANT_BASE_X - 10, ANT_TOP_Y)], 
          fill=(60, 160, 200, 200), width=3)
# Antenna tip glow
ant_glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
ant_draw = ImageDraw.Draw(ant_glow)
for g in range(15, 0, -3):
    a = int(20 * g)
    ant_draw.ellipse([ANT_BASE_X-10-g, ANT_TOP_Y-g, ANT_BASE_X-10+g, ANT_TOP_Y+g], 
                     fill=(255, 80, 80, a))
ant_glow = ant_glow.filter(ImageFilter.GaussianBlur(4))
img = Image.alpha_composite(img, ant_glow)
draw = ImageDraw.Draw(img)
draw.ellipse([ANT_BASE_X-14, ANT_TOP_Y-6, ANT_BASE_X-6, ANT_TOP_Y+4], fill=(255, 100, 80, 255))
# Small left antenna
draw.line([(CX - 20, HEAD_Y - 2), (CX - 25, HEAD_Y - 25)], fill=(60, 160, 200, 160), width=2)
draw.ellipse([CX-28, HEAD_Y-30, CX-22, HEAD_Y-24], fill=(0, 200, 240, 200))

# --- Ear panels (side augments) ---
EAR_W, EAR_H = 18, 55
EAR_Y = HEAD_Y + 30
# Left ear
draw.rounded_rectangle([HEAD_X - EAR_W - 2, EAR_Y, HEAD_X - 2, EAR_Y + EAR_H], 
                        radius=6, fill=(25, 35, 50), outline=(50, 130, 170, 200), width=2)
# Ear detail lines
for i in range(3):
    ey = EAR_Y + 12 + i * 14
    draw.line([(HEAD_X - EAR_W + 3, ey), (HEAD_X - 6, ey)], fill=(0, 160, 200, 150), width=1)

# Right ear
draw.rounded_rectangle([HEAD_X + HEAD_W + 2, EAR_Y, HEAD_X + HEAD_W + EAR_W + 2, EAR_Y + EAR_H],
                        radius=6, fill=(25, 35, 50), outline=(50, 130, 170, 200), width=2)
for i in range(3):
    ey = EAR_Y + 12 + i * 14
    draw.line([(HEAD_X + HEAD_W + 6, ey), (HEAD_X + HEAD_W + EAR_W - 3, ey)], fill=(0, 160, 200, 150), width=1)

# --- Neck/collar area ---
NECK_W = 60
NECK_Y = HEAD_Y + HEAD_H - 5
draw.rounded_rectangle([CX - NECK_W//2, NECK_Y, CX + NECK_W//2, NECK_Y + 30],
                        radius=4, fill=(22, 28, 40), outline=(40, 100, 140, 180), width=2)
# Collar glow strip
draw.rounded_rectangle([CX - NECK_W//2 + 5, NECK_Y + 4, CX + NECK_W//2 - 5, NECK_Y + 10],
                        radius=2, fill=(0, 180, 220, 180))

# --- Circuitry marks on face (techy detail) ---
# Small corner brackets on head
corner_size = 14
corners = [
    (HEAD_X + 8, HEAD_Y + 8),      # TL
    (HEAD_X + HEAD_W - 8, HEAD_Y + 8),  # TR
    (HEAD_X + 8, HEAD_Y + HEAD_H - 8),  # BL
    (HEAD_X + HEAD_W - 8, HEAD_Y + HEAD_H - 8),  # BR
]
for (cx2, cy2) in corners:
    draw.line([(cx2 - corner_size//2, cy2), (cx2, cy2), (cx2, cy2 - corner_size//2)], 
              fill=(0, 200, 240, 120), width=1)

# HUD-style corner decorations on the hex frame
for i, (hx, hy) in enumerate(hex_points(CX, CY, 195, 30)):
    draw.ellipse([hx-4, hy-4, hx+4, hy+4], fill=(0, 180, 220, 180))

# --- Small bottom text plate: M-4G1 (robot designation) ---
text_y = CY + 130
draw.rounded_rectangle([CX - 45, text_y, CX + 45, text_y + 22], radius=4,
                        fill=(15, 20, 32), outline=(0, 160, 200, 200), width=1)
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", 14)
except:
    font = ImageFont.load_default()
draw.text((CX, text_y + 4), "M-4G1", fill=(0, 220, 255, 255), font=font, anchor="mm")

# --- Final overall subtle scanline effect ---
scan_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
scan_draw = ImageDraw.Draw(scan_layer)
for y in range(0, SIZE, 4):
    scan_draw.line([(0, y), (SIZE, y)], fill=(0, 0, 0, 15))
img = Image.alpha_composite(img, scan_layer)

# --- Flatten to RGB and save ---
final = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
final.paste(img, mask=img.split()[3])
final.save("/Users/eric/clawd-magi/assets/magi-avatar.png", "PNG")
print("Avatar generated successfully!")
print(f"Size: {final.size}")
