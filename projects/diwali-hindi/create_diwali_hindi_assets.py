#!/usr/bin/env python3
import math
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

BASE_DIR = Path("/home/pratik/stickman-video-director")
SRC_DIR = BASE_DIR / "projects" / "diwali-special" / "assets"
OUT_DIR = BASE_DIR / "projects" / "diwali-hindi" / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 768, 1376

# Load reference base
base_ayodhya = Image.open(SRC_DIR / "scene-1.jpg").convert("RGBA")
base_ayodhya = base_ayodhya.resize((W, H), Image.Resampling.LANCZOS)

def add_glow(base_img, cx, cy, radius, color, max_alpha=200):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    steps = 25
    r_col, g_col, b_col = color
    for i in range(steps, 0, -1):
        cur_r = int(radius * (i / steps))
        alpha = int(max_alpha * (1.0 - (i / steps)) ** 1.8)
        draw.ellipse([cx - cur_r, cy - cur_r, cx + cur_r, cy + cur_r], fill=(r_col, g_col, b_col, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 10))
    return Image.alpha_composite(base_img, glow)

def draw_stickman(draw, head_cx, head_cy, head_r=22, pose="sit", is_old=False, is_rama=False):
    # Head
    head_fill = (255, 235, 170) if is_rama else (240, 240, 245)
    line_col = (20, 20, 25)
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=head_fill, outline=line_col, width=4)

    if is_rama:
        # Golden Mukut (crown)
        pts = [
            (head_cx - 16, head_cy - head_r + 2),
            (head_cx - 20, head_cy - head_r - 28),
            (head_cx - 8, head_cy - head_r - 18),
            (head_cx, head_cy - head_r - 38), # central peak
            (head_cx + 8, head_cy - head_r - 18),
            (head_cx + 20, head_cy - head_r - 28),
            (head_cx + 16, head_cy - head_r + 2)
        ]
        draw.polygon(pts, fill=(255, 205, 30), outline=(180, 130, 10))
        # Tilak
        draw.line([head_cx, head_cy - 12, head_cx, head_cy - 2], fill=(220, 40, 30), width=3)
        draw.point((head_cx, head_cy + 1), fill=(255, 215, 0))
    elif is_old:
        # Old potter white hair & beard
        draw.arc([head_cx - head_r - 4, head_cy - head_r, head_cx + head_r + 4, head_cy + head_r + 4], start=30, end=150, fill=(230, 230, 230), width=6)
        # Gentle closed/smiling eyes
        draw.arc([head_cx - 12, head_cy - 6, head_cx - 4, head_cy + 2], start=200, end=340, fill=line_col, width=3)
        draw.arc([head_cx + 4, head_cy - 6, head_cx + 12, head_cy + 2], start=200, end=340, fill=line_col, width=3)

    # Body
    neck_y = head_cy + head_r
    pelvis_y = neck_y + 85
    draw.line([head_cx, neck_y, head_cx, pelvis_y], fill=line_col, width=7)

    if is_rama:
        # Pitambara yellow sash
        draw.polygon([
            (head_cx - 18, neck_y + 15),
            (head_cx + 22, pelvis_y - 15),
            (head_cx + 28, pelvis_y + 25),
            (head_cx - 12, neck_y + 40)
        ], fill=(255, 195, 20, 220), outline=(210, 150, 10))

    if pose == "sit":
        # Potter seated cross legged
        draw.line([head_cx, pelvis_y, head_cx - 55, pelvis_y + 40], fill=line_col, width=6)
        draw.line([head_cx - 55, pelvis_y + 40, head_cx + 45, pelvis_y + 45], fill=line_col, width=6)
        # Arms shaping wheel / resting
        draw.line([head_cx, neck_y + 20, head_cx + 45, neck_y + 60], fill=line_col, width=6)
        draw.line([head_cx + 45, neck_y + 60, head_cx + 80, neck_y + 75], fill=line_col, width=6)
    elif pose == "kneel_left":
        # Potter kneeling facing right
        draw.line([head_cx, pelvis_y, head_cx - 30, pelvis_y + 50], fill=line_col, width=6)
        draw.line([head_cx - 30, pelvis_y + 50, head_cx + 20, pelvis_y + 80], fill=line_col, width=6)
        # Arms cupping diya forward
        draw.line([head_cx, neck_y + 20, head_cx + 45, neck_y + 50], fill=line_col, width=6)
        draw.line([head_cx + 45, neck_y + 50, head_cx + 90, neck_y + 45], fill=line_col, width=6)
    elif pose == "kneel_right":
        # Rama gently kneeling facing left
        draw.line([head_cx, pelvis_y, head_cx + 40, pelvis_y + 55], fill=line_col, width=7)
        draw.line([head_cx + 40, pelvis_y + 55, head_cx - 10, pelvis_y + 85], fill=line_col, width=7)
        # Arms extending forward gently touching diya
        draw.line([head_cx, neck_y + 20, head_cx - 45, neck_y + 48], fill=line_col, width=7)
        draw.line([head_cx - 45, neck_y + 48, head_cx - 90, neck_y + 45], fill=line_col, width=7)
    elif pose == "stand_hold":
        # Potter standing holding unlit diya
        draw.line([head_cx, pelvis_y, head_cx - 20, pelvis_y + 110], fill=line_col, width=6)
        draw.line([head_cx, pelvis_y, head_cx + 20, pelvis_y + 110], fill=line_col, width=6)
        # Arms cupping chest level
        draw.line([head_cx, neck_y + 20, head_cx + 35, neck_y + 55], fill=line_col, width=6)
        draw.line([head_cx + 35, neck_y + 55, head_cx + 60, neck_y + 40], fill=line_col, width=6)

def draw_earthen_diya(draw, cx, cy, scale=1.0, is_lit=False):
    # Traditional terracotta earthen diya
    w = int(32 * scale)
    h = int(14 * scale)
    # Clay bowl (burnt terracotta orange)
    draw.chord([cx - w, cy - h, cx + w, cy + h], 0, 180, fill=(185, 85, 40), outline=(120, 50, 20), width=int(2*scale))
    # Diya rim
    draw.ellipse([cx - w, cy - int(4*scale), cx + w, cy + int(4*scale)], fill=(205, 105, 50), outline=(135, 60, 25), width=int(2*scale))
    wick_x, wick_y = cx, cy - int(4*scale)
    draw.line([wick_x, wick_y, wick_x, wick_y - int(8*scale)], fill=(40, 30, 20), width=int(2*scale))
    return wick_x, wick_y - int(8*scale)

def draw_flame(draw, wx, wy, scale=1.0):
    fw = int(14 * scale)
    fh = int(28 * scale)
    # Outer orange flame
    draw.polygon([(wx - fw, wy + 2), (wx, wy - fh), (wx + fw, wy + 2), (wx, wy + int(6*scale))], fill=(255, 120, 20, 230))
    # Middle gold flame
    draw.polygon([(wx - int(fw*0.65), wy), (wx, wy - int(fh*0.8)), (wx + int(fw*0.65), wy), (wx, wy + int(4*scale))], fill=(255, 215, 30, 255))
    # Inner white hot core
    draw.polygon([(wx - int(fw*0.35), wy), (wx, wy - int(fh*0.45)), (wx + int(fw*0.35), wy)], fill=(255, 255, 235, 255))

# ========================================================
# 1. SCENE 1: The Old Potter in his rustic earthen workshop
# ========================================================
s1 = base_ayodhya.copy()
# Darken background to emphasize quiet midnight hour
dark_overlay = Image.new("RGBA", (W, H), (10, 12, 25, 140))
s1 = Image.alpha_composite(s1, dark_overlay)

# Add earthen hut architecture elements in foreground
draw1 = ImageDraw.Draw(s1)
# Wooden pillar on left
draw1.rectangle([40, 0, 140, H], fill=(25, 18, 14, 255))
draw1.line([140, 0, 140, H], fill=(45, 32, 22), width=3)
# Earthen floor
draw1.polygon([(0, 880), (W, 880), (W, H), (0, H)], fill=(32, 24, 18, 255))
draw1.line([(0, 880), (W, 880)], fill=(55, 42, 30), width=4)

# Potter's wheel (stone circular disc in perspective)
wheel_cx, wheel_cy = 440, 1020
draw1.ellipse([wheel_cx - 120, wheel_cy - 35, wheel_cx + 120, wheel_cy + 35], fill=(70, 65, 60), outline=(40, 38, 35), width=5)
draw1.ellipse([wheel_cx - 110, wheel_cy - 30, wheel_cx + 110, wheel_cy + 30], fill=(85, 80, 75))
draw1.ellipse([wheel_cx - 20, wheel_cy - 7, wheel_cx + 20, wheel_cy + 7], fill=(40, 38, 35))

# Potter stickman seated on an earthen mat
draw_stickman(draw1, head_cx=280, head_cy=880, head_r=26, pose="sit", is_old=True)

# Row of unlit clay diyas on a wooden board
for i, dx in enumerate(range(180, 620, 75)):
    draw_earthen_diya(draw1, dx, 1140, scale=1.4, is_lit=False)

# One single unlit diya on the potter wheel
draw_earthen_diya(draw1, wheel_cx, wheel_cy - 12, scale=1.5, is_lit=False)

# Subtle warm lantern hanging from pillar on far left
s1 = add_glow(s1, 90, 420, 160, (255, 160, 40), max_alpha=120)
draw1 = ImageDraw.Draw(s1)
draw1.rectangle([75, 400, 105, 440], fill=(255, 200, 60), outline=(50, 30, 10), width=3)
draw1.line([90, 320, 90, 400], fill=(60, 40, 20), width=3)

s1.convert("RGB").save(OUT_DIR / "scene-1.jpg", quality=95)
print("✅ Scene 1 Generated (The Potter's Workshop)")

# ========================================================
# 2. SCENE 2: The Contrast - Golden Palaces vs Humble Diya
# ========================================================
s2 = base_ayodhya.copy()
# Enhance the golden palace radiance in distance
s2 = add_glow(s2, 420, 480, 360, (255, 190, 40), max_alpha=160)
s2 = add_glow(s2, 580, 380, 280, (255, 170, 30), max_alpha=140)

draw2 = ImageDraw.Draw(s2)
# Distant golden palace silhouettes and hundreds of tiny glittering lamps
for _ in range(120):
    rx = random.randint(180, 740)
    ry = random.randint(460, 780)
    rad = random.randint(2, 5)
    draw2.ellipse([rx - rad, ry - rad, rx + rad, ry + rad], fill=(255, 230, 120, 230))

# Humble dark foreground balcony / doorway on left
draw2.polygon([(0, 600), (320, 680), (320, H), (0, H)], fill=(20, 18, 24, 255))
draw2.line([(320, 680), (320, H)], fill=(40, 35, 45), width=4)

# Old Potter standing in profile, gently cradling a humble unlit earthen diya
draw_stickman(draw2, head_cx=220, head_cy=840, head_r=26, pose="stand_hold", is_old=True)
# Cupped hands holding the fragile clay diya
draw_earthen_diya(draw2, 280, 930, scale=1.5, is_lit=False)

s2.convert("RGB").save(OUT_DIR / "scene-2.jpg", quality=95)
print("✅ Scene 2 Generated (The Golden Palaces vs Humble Diya)")

# ========================================================
# 3. SCENE 3: Prabhu Shri Ram's Arrival & Lighting the Diya
# ========================================================
s3 = base_ayodhya.copy()
# Divine Golden Glow centered between Rama and the Potter
s3 = add_glow(s3, 400, 860, 420, (255, 215, 60), max_alpha=210)
s3 = add_glow(s3, 520, 780, 300, (255, 180, 40), max_alpha=180)

draw3 = ImageDraw.Draw(s3)
# Ground plane
draw3.polygon([(0, 920), (W, 920), (W, H), (0, H)], fill=(28, 22, 18, 255))

# Left: Old Potter kneeling in humility
draw_stickman(draw3, head_cx=240, head_cy=860, head_r=24, pose="kneel_left", is_old=True)

# Right: Prabhu Shri Ram kneeling lovingly
draw_stickman(draw3, head_cx=530, head_cy=840, head_r=26, pose="kneel_right", is_rama=True)

# Divine Diya held between their meeting hands at (385, 915)
diya_cx, diya_cy = 385, 915
wx, wy = draw_earthen_diya(draw3, diya_cx, diya_cy, scale=1.8, is_lit=True)
draw_flame(draw3, wx, wy, scale=1.8)

# Floating divine golden sparkles
for _ in range(80):
    sx = int(diya_cx + random.gauss(0, 110))
    sy = int(wy - random.uniform(10, 240))
    if 0 <= sx < W and 0 <= sy < H:
        srad = random.randint(2, 6)
        draw3.ellipse([sx - srad, sy - srad, sx + srad, sy + srad], fill=(255, 245, 140, 240))

s3.convert("RGB").save(OUT_DIR / "scene-3.jpg", quality=95)
print("✅ Scene 3 Generated (Prabhu Shri Ram Lights the Potter's Diya)")

# ========================================================
# 4. SCENE 4: The Grand Celebration - Ocean of Diyas & Fireworks
# ========================================================
s4 = base_ayodhya.copy()
# Grand festive illumination
s4 = add_glow(s4, W // 2, 400, 480, (255, 170, 30), max_alpha=180)
s4 = add_glow(s4, W // 2, 1080, 450, (255, 195, 45), max_alpha=190)

draw4 = ImageDraw.Draw(s4)

# Millions of golden diyas across the ghats
for _ in range(250):
    gx = random.randint(30, W - 30)
    gy = random.randint(720, H - 40)
    sz = random.uniform(0.5, 1.2)
    dwx, dwy = draw_earthen_diya(draw4, gx, gy, scale=sz, is_lit=True)
    draw_flame(draw4, dwx, dwy, scale=sz)

# Fireworks in the night sky (bursts in gold, ruby, and emerald)
def draw_firework_burst(draw, cx, cy, radius, color, num_sparks=36):
    for i in range(num_sparks):
        angle = (2 * math.pi / num_sparks) * i + random.uniform(-0.08, 0.08)
        dist = radius * random.uniform(0.65, 1.0)
        ex = int(cx + dist * math.cos(angle))
        ey = int(cy + dist * math.sin(angle))
        # Draw particle trail
        draw.line([(cx + int(dist*0.45*math.cos(angle)), cy + int(dist*0.45*math.sin(angle))), (ex, ey)], fill=color, width=random.randint(2, 4))
        draw.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 255, 255, 255))

draw_firework_burst(draw4, 220, 240, 110, (255, 215, 0)) # Gold
draw_firework_burst(draw4, 560, 200, 125, (255, 80, 120)) # Ruby Pink
draw_firework_burst(draw4, 380, 360, 95, (80, 240, 140)) # Emerald Green
draw_firework_burst(draw4, 640, 340, 80, (255, 180, 40)) # Amber

# Rising sky lanterns
for lx, ly, lrad in [(140, 440, 14), (280, 480, 18), (490, 420, 22), (620, 490, 16), (360, 560, 15)]:
    draw4.polygon([(lx - lrad, ly + lrad), (lx - int(lrad*0.8), ly - lrad), (lx + int(lrad*0.8), ly - lrad), (lx + lrad, ly + lrad)], fill=(255, 190, 40, 240), outline=(220, 120, 10))
    draw4.ellipse([lx - int(lrad*0.5), ly + lrad - 3, lx + int(lrad*0.5), ly + lrad + 3], fill=(255, 255, 220))

s4.convert("RGB").save(OUT_DIR / "scene-4.jpg", quality=95)
print("✅ Scene 4 Generated (Grand Finale Celebration)")

