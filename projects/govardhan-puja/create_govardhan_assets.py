#!/usr/bin/env python3
"""
Generate 4 cinematic 2D stickman scenes for Govardhan Puja Special Reel
Resolution: 768x1376 (9:16 vertical)
"""

import math
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

OUT_DIR = Path("/home/pratik/stickman-video-director/projects/govardhan-puja/assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 768, 1376

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

def draw_hut(draw, x, y, w, h):
    # Mud hut wall
    draw.rectangle([x, y, x + w, y + h], fill=(160, 110, 70), outline=(90, 60, 35), width=3)
    # Door
    dw, dh = w // 3, int(h * 0.6)
    draw.rectangle([x + w//3, y + h - dh, x + w//3 + dw, y + h], fill=(70, 45, 25))
    # Thatch roof
    draw.polygon([
        (x - 15, y),
        (x + w // 2, y - int(h * 0.7)),
        (x + w + 15, y)
    ], fill=(210, 170, 80), outline=(130, 95, 30), width=4)

def draw_krishna(draw, cx, cy, lifting=True):
    # Head (Divine subtle blue-cyan fill)
    head_r = 26
    line_col = (15, 20, 30)
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=(210, 240, 255), outline=line_col, width=4)

    # Peacock feather on head
    # Stem
    draw.line([cx + 6, cy - head_r, cx + 18, cy - head_r - 35], fill=(30, 140, 60), width=3)
    # Feather eye
    draw.ellipse([cx + 12, cy - head_r - 42, cx + 28, cy - head_r - 26], fill=(20, 160, 80), outline=(10, 100, 50), width=2)
    draw.ellipse([cx + 16, cy - head_r - 38, cx + 24, cy - head_r - 30], fill=(20, 80, 200))
    draw.ellipse([cx + 18, cy - head_r - 36, cx + 22, cy - head_r - 32], fill=(255, 215, 0))

    # Tilak
    draw.line([cx, cy - 14, cx, cy - 2], fill=(230, 180, 20), width=3)
    draw.point((cx, cy + 2), fill=(220, 30, 30))

    # Smiling eyes
    draw.arc([cx - 14, cy - 8, cx - 4, cy + 2], start=20, end=160, fill=line_col, width=3)
    draw.arc([cx + 4, cy - 8, cx + 14, cy + 2], start=20, end=160, fill=line_col, width=3)

    # Body
    neck_y = cy + head_r
    pelvis_y = neck_y + 90
    draw.line([cx, neck_y, cx, pelvis_y], fill=line_col, width=7)

    # Pitambara yellow dhoti
    draw.polygon([
        (cx - 20, neck_y + 30),
        (cx + 25, pelvis_y - 10),
        (cx + 32, pelvis_y + 35),
        (cx - 15, neck_y + 55)
    ], fill=(255, 210, 30), outline=(190, 140, 10), width=3)

    if lifting:
        # Left arm raised high holding the mountain on little finger
        draw.line([cx, neck_y + 20, cx - 40, neck_y - 25], fill=line_col, width=6)
        draw.line([cx - 40, neck_y - 25, cx - 60, neck_y - 95], fill=line_col, width=6)
        # Pointing little finger up
        draw.line([cx - 60, neck_y - 95, cx - 62, neck_y - 120], fill=line_col, width=4)

        # Right arm gently resting on hip or holding flute
        draw.line([cx, neck_y + 25, cx + 35, neck_y + 50], fill=line_col, width=6)
        draw.line([cx + 35, neck_y + 50, cx + 20, neck_y + 80], fill=line_col, width=6)
        # Golden Flute
        draw.line([cx - 10, neck_y + 65, cx + 55, neck_y + 45], fill=(255, 190, 30), width=4)

        # Legs (relaxed stance)
        draw.line([cx, pelvis_y, cx - 25, pelvis_y + 70], fill=line_col, width=6)
        draw.line([cx, pelvis_y, cx + 20, pelvis_y + 70], fill=line_col, width=6)
    else:
        # Playing flute pose
        draw.line([cx, neck_y + 20, cx - 25, neck_y + 40], fill=line_col, width=6)
        draw.line([cx - 25, neck_y + 40, cx - 5, cy + 12], fill=line_col, width=6)
        draw.line([cx, neck_y + 20, cx + 25, neck_y + 40], fill=line_col, width=6)
        draw.line([cx + 25, neck_y + 40, cx + 15, cy + 12], fill=line_col, width=6)
        # Flute
        draw.line([cx - 30, cy + 14, cx + 45, cy + 8], fill=(255, 200, 30), width=4)
        # Crossed legs
        draw.line([cx, pelvis_y, cx - 15, pelvis_y + 70], fill=line_col, width=6)
        draw.line([cx, pelvis_y, cx + 25, pelvis_y + 35], fill=line_col, width=6)
        draw.line([cx + 25, pelvis_y + 35, cx - 10, pelvis_y + 70], fill=line_col, width=6)

def draw_villager(draw, cx, cy, pose="worried"):
    head_r = 18
    line_col = (30, 35, 45)
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=(245, 240, 230), outline=line_col, width=3)
    neck_y = cy + head_r
    pelvis_y = neck_y + 65
    draw.line([cx, neck_y, cx, pelvis_y], fill=line_col, width=5)

    if pose == "worried":
        # Hands on head / pointing up
        draw.line([cx, neck_y + 15, cx - 25, neck_y - 10], fill=line_col, width=4)
        draw.line([cx - 25, neck_y - 10, cx - 15, cy - head_r], fill=line_col, width=4)
        draw.line([cx, neck_y + 15, cx + 30, neck_y - 15], fill=line_col, width=4)
        # Legs running
        draw.line([cx, pelvis_y, cx - 20, pelvis_y + 55], fill=line_col, width=5)
        draw.line([cx, pelvis_y, cx + 25, pelvis_y + 45], fill=line_col, width=5)
    elif pose == "folded_hands":
        # Namaste / folded hands looking up at mountain
        draw.line([cx, neck_y + 15, cx - 12, neck_y + 35], fill=line_col, width=4)
        draw.line([cx, neck_y + 15, cx + 12, neck_y + 35], fill=line_col, width=4)
        draw.line([cx - 12, neck_y + 35, cx, neck_y + 25], fill=line_col, width=4)
        draw.line([cx + 12, neck_y + 35, cx, neck_y + 25], fill=line_col, width=4)
        # Legs standing
        draw.line([cx, pelvis_y, cx - 12, pelvis_y + 55], fill=line_col, width=5)
        draw.line([cx, pelvis_y, cx + 12, pelvis_y + 55], fill=line_col, width=5)
    elif pose == "joyful":
        # Both arms raised high celebrating
        draw.line([cx, neck_y + 15, cx - 28, neck_y - 25], fill=line_col, width=4)
        draw.line([cx, neck_y + 15, cx + 28, neck_y - 25], fill=line_col, width=4)
        # Dancing legs
        draw.line([cx, pelvis_y, cx - 18, pelvis_y + 50], fill=line_col, width=5)
        draw.line([cx, pelvis_y, cx + 15, pelvis_y + 35], fill=line_col, width=5)
        draw.line([cx + 15, pelvis_y + 35, cx + 28, pelvis_y + 55], fill=line_col, width=5)

# ==========================================
# SCENE 1: Gathering storm over Gokul
# ==========================================
print("🎨 Rendering Scene 1: Storm clouds over Gokul...")
s1 = Image.new("RGBA", (W, H), (20, 25, 40))
draw1 = ImageDraw.Draw(s1)

# Dark ominous gradient sky
for y in range(int(H * 0.7)):
    ratio = y / (H * 0.7)
    r = int(15 + 25 * ratio)
    g = int(20 + 35 * ratio)
    b = int(35 + 50 * ratio)
    draw1.line([(0, y), (W, y)], fill=(r, g, b))

# Mountain silhouettes in background
draw1.polygon([(0, 650), (250, 480), (520, 680), (0, 750)], fill=(35, 45, 60))
draw1.polygon([(280, 680), (550, 460), (W, 620), (W, 750), (280, 750)], fill=(28, 38, 52))

# Gokul ground
draw1.rectangle([0, int(H * 0.65), W, H], fill=(55, 65, 45))

# Dark storm clouds
for cx, cy, cr in [(150, 160, 180), (380, 130, 220), (620, 180, 200), (280, 260, 190), (500, 270, 210)]:
    draw1.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(12, 16, 28, 220))

# Lightning flash in sky
s1 = add_glow(s1, 460, 280, 180, (230, 240, 255), max_alpha=180)
draw1 = ImageDraw.Draw(s1)
# Lightning bolt
bolt = [(450, 100), (465, 220), (435, 235), (475, 360), (455, 380), (490, 510)]
for i in range(len(bolt) - 1):
    draw1.line([bolt[i], bolt[i+1]], fill=(255, 255, 255), width=5)
    draw1.line([bolt[i], bolt[i+1]], fill=(180, 220, 255), width=9)

# Village huts
draw_hut(draw1, 80, 850, 160, 140)
draw_hut(draw1, 520, 840, 170, 150)

# Worried villagers looking at the sky
draw_villager(draw1, 300, 960, pose="worried")
draw_villager(draw1, 380, 980, pose="worried")
draw_villager(draw1, 460, 950, pose="worried")
s1.convert("RGB").save(OUT_DIR / "scene-1.jpg", quality=95)

# ==========================================
# SCENE 2: Torrential downpour & rising flood
# ==========================================
print("🎨 Rendering Scene 2: Torrential rain & floods...")
s2 = Image.new("RGBA", (W, H), (15, 20, 32))
draw2 = ImageDraw.Draw(s2)

# Deep stormy sky
for y in range(H):
    r = int(10 + 20 * (y / H))
    g = int(18 + 30 * (y / H))
    b = int(30 + 45 * (y / H))
    draw2.line([(0, y), (W, y)], fill=(r, g, b))

# Swirling cloud masses
for cx, cy, cr in [(120, 100, 220), (360, 90, 260), (640, 120, 240), (240, 220, 230), (530, 240, 250)]:
    draw2.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(8, 12, 22, 230))

# Massive fork lightning
s2 = add_glow(s2, 260, 320, 220, (200, 230, 255), max_alpha=210)
draw2 = ImageDraw.Draw(s2)
fork1 = [(260, 80), (280, 210), (250, 230), (300, 370), (275, 395), (310, 550)]
for i in range(len(fork1) - 1):
    draw2.line([fork1[i], fork1[i+1]], fill=(255, 255, 255), width=6)
    draw2.line([fork1[i], fork1[i+1]], fill=(160, 210, 255), width=10)

# Heavy slanted rain streaks
random.seed(42)
for _ in range(850):
    rx = random.randint(-50, W + 50)
    ry = random.randint(0, H - 100)
    rlen = random.randint(35, 75)
    draw2.line([(rx, ry), (rx - 15, ry + rlen)], fill=(180, 210, 245, 140), width=2)

# Flood water rising
draw2.rectangle([0, 1050, W, H], fill=(40, 65, 85, 220))
# Water surface waves
for x in range(0, W, 40):
    draw2.arc([x, 1040, x + 40, 1065], start=0, end=180, fill=(160, 200, 230), width=3)

# Half-submerged huts
draw_hut(draw2, 60, 940, 150, 130)
draw_hut(draw2, 540, 930, 160, 140)

# Panicking stickmen running through water
draw_villager(draw2, 250, 980, pose="worried")
draw_villager(draw2, 380, 970, pose="worried")
draw_villager(draw2, 480, 990, pose="worried")
s2.convert("RGB").save(OUT_DIR / "scene-2.jpg", quality=95)

# ==========================================
# SCENE 3: Krishna lifting Mount Govardhan
# ==========================================
print("🎨 Rendering Scene 3: Krishna lifts Govardhan Mountain on his little finger...")
s3 = Image.new("RGBA", (W, H), (20, 25, 45))
draw3 = ImageDraw.Draw(s3)

# Storm sky outside, but golden divine light emanating from Krishna
for y in range(H):
    r = int(15 + 40 * (y / H))
    g = int(22 + 45 * (y / H))
    b = int(38 + 55 * (y / H))
    draw3.line([(0, y), (W, y)], fill=(r, g, b))

# Rain streaming down on the sides only, hitting the mountain roof
random.seed(99)
for _ in range(400):
    rx = random.choice([random.randint(0, 180), random.randint(W - 180, W)])
    ry = random.randint(0, H)
    rlen = random.randint(30, 60)
    draw3.line([(rx, ry), (rx - 10, ry + rlen)], fill=(160, 195, 235, 120), width=2)

# MOUNT GOVARDHAN (Massive sacred rock umbrella lifted high)
mountain_pts = [
    (30, 520),
    (110, 420),
    (220, 340),
    (360, 300),
    (520, 330),
    (660, 410),
    (740, 500),
    (680, 540),
    (480, 530),
    (300, 535),
    (100, 545)
]
draw3.polygon(mountain_pts, fill=(55, 95, 60), outline=(30, 60, 35), width=5)
# Mountain foliage / trees / rocks on the slopes
for tx, ty in [(180, 380), (320, 330), (450, 340), (580, 410)]:
    draw3.ellipse([tx - 25, ty - 25, tx + 25, ty + 25], fill=(75, 130, 75))

# Massive Divine Golden Aura from Krishna's lifting hand & heart
s3 = add_glow(s3, 380, 780, 360, (255, 220, 110), max_alpha=200)
s3 = add_glow(s3, 320, 540, 240, (255, 240, 180), max_alpha=240) # finger contact point glow
draw3 = ImageDraw.Draw(s3)

# Little Krishna in the center lifting the mountain with left hand
draw_krishna(draw3, 380, 760, lifting=True)

# Safe dry ground under the mountain
draw3.rectangle([0, 980, W, H], fill=(95, 115, 75))

# Grateful villagers sheltering safely beneath the mountain umbrella
draw_villager(draw3, 160, 890, pose="folded_hands")
draw_villager(draw3, 240, 900, pose="folded_hands")
draw_villager(draw3, 520, 895, pose="folded_hands")
draw_villager(draw3, 610, 910, pose="folded_hands")

# Sacred Cow / Calf stickman silhouette under shelter
cow_x, cow_y = 480, 930
draw3.ellipse([cow_x - 30, cow_y - 15, cow_x + 30, cow_y + 15], fill=(230, 225, 215), outline=(50, 50, 60), width=3) # body
draw3.ellipse([cow_x - 42, cow_y - 25, cow_x - 22, cow_y - 5], fill=(230, 225, 215), outline=(50, 50, 60), width=3) # head
draw3.line([cow_x - 20, cow_y + 12, cow_x - 20, cow_y + 40], fill=(50, 50, 60), width=4) # legs
draw3.line([cow_x + 20, cow_y + 12, cow_x + 20, cow_y + 40], fill=(50, 50, 60), width=4)

s3.convert("RGB").save(OUT_DIR / "scene-3.jpg", quality=95)

# ==========================================
# SCENE 4: Golden victory, clear skies, celebration
# ==========================================
print("🎨 Rendering Scene 4: Golden victory, rainbow, joyful Govardhan celebration...")
s4 = Image.new("RGBA", (W, H), (245, 235, 210))
draw4 = ImageDraw.Draw(s4)

# Radiant golden morning sky
for y in range(int(H * 0.7)):
    ratio = y / (H * 0.7)
    r = int(255 - 15 * ratio)
    g = int(210 + 25 * ratio)
    b = int(140 + 70 * ratio)
    draw4.line([(0, y), (W, y)], fill=(r, g, b))

# Golden Sun shining brightly
s4 = add_glow(s4, 384, 250, 320, (255, 215, 60), max_alpha=220)
draw4 = ImageDraw.Draw(s4)

# Rainbow arcing across clear morning sky
for i, col in enumerate([
    (240, 80, 80, 90),
    (250, 160, 60, 90),
    (250, 220, 60, 90),
    (80, 190, 100, 90),
    (70, 160, 230, 90),
    (140, 90, 210, 90)
]):
    r_val = 460 - i * 12
    draw4.arc([384 - r_val, 320 - r_val, 384 + r_val, 320 + r_val], start=190, end=350, fill=col, width=12)

# Lush green Govardhan mountain resting peacefully in the background
draw4.polygon([(40, 640), (220, 480), (384, 430), (560, 490), (730, 640), (0, 720)], fill=(80, 145, 80), outline=(45, 90, 45), width=4)

# Lush blooming meadow ground
draw4.rectangle([0, int(H * 0.65), W, H], fill=(110, 160, 85))

# Krishna playing the flute happily in the center
draw_krishna(draw4, 384, 820, lifting=False)

# Joyful villagers dancing with arms raised in celebration
draw_villager(draw4, 150, 940, pose="joyful")
draw_villager(draw4, 260, 950, pose="joyful")
draw_villager(draw4, 510, 945, pose="joyful")
draw_villager(draw4, 620, 935, pose="joyful")

# Flower petals raining down
random.seed(123)
for _ in range(120):
    fx = random.randint(40, W - 40)
    fy = random.randint(150, H - 150)
    p_col = random.choice([(255, 120, 150), (255, 210, 50), (255, 165, 40)])
    draw4.ellipse([fx - 6, fy - 6, fx + 6, fy + 6], fill=p_col)

s4.convert("RGB").save(OUT_DIR / "scene-4.jpg", quality=95)
print("✅ All 4 Govardhan Puja scenes rendered successfully to", OUT_DIR)
