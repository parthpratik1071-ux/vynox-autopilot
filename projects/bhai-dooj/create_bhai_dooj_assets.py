#!/usr/bin/env python3
"""
Generate 4 cinematic 2D stickman scenes for Bhai Dooj Special Reel (Yamraj & Yamuna)
Resolution: 768x1376 (9:16 vertical)
"""

import math
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

OUT_DIR = Path("/home/pratik/stickman-video-director/projects/bhai-dooj/assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 768, 1376

def add_glow(base_img, cx, cy, radius, color, max_alpha=200):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    steps = 22
    r_col, g_col, b_col = color
    for i in range(steps, 0, -1):
        cur_r = int(radius * (i / steps))
        alpha = int(max_alpha * (1.0 - (i / steps)) ** 1.8)
        draw.ellipse([cx - cur_r, cy - cur_r, cx + cur_r, cy + cur_r], fill=(r_col, g_col, b_col, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 10))
    return Image.alpha_composite(base_img, glow)

def draw_yamraj(draw, cx, cy, scale=1.0, pose="imposing"):
    # Yamraj: Majestic stickman with golden crown, dark blue/indigo body, mace/noose
    head_r = int(28 * scale)
    line_col = (20, 25, 40)
    
    # Head (subtle indigo/midnight tone)
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=(45, 55, 80), outline=line_col, width=int(4 * scale))
    
    # Golden Crown (Mukut)
    crown_w = int(24 * scale)
    draw.polygon([
        (cx - crown_w, cy - head_r),
        (cx - int(crown_w * 0.7), cy - head_r - int(25 * scale)),
        (cx, cy - head_r - int(40 * scale)),
        (cx + int(crown_w * 0.7), cy - head_r - int(25 * scale)),
        (cx + crown_w, cy - head_r)
    ], fill=(255, 200, 40), outline=(180, 130, 20), width=int(3 * scale))
    # Crown ruby jewel
    draw.ellipse([cx - 4, cy - head_r - int(22 * scale), cx + 4, cy - head_r - int(14 * scale)], fill=(220, 30, 30))

    # Eyes & Tilak
    draw.line([cx - int(12 * scale), cy - 4, cx - 2, cy], fill=(255, 230, 120), width=int(3 * scale))
    draw.line([cx + 2, cy, cx + int(12 * scale), cy - 4], fill=(255, 230, 120), width=int(3 * scale))
    draw.line([cx, cy - int(14 * scale), cx, cy - 2], fill=(255, 70, 40), width=int(3 * scale))

    # Body
    neck_y = cy + head_r
    pelvis_y = neck_y + int(85 * scale)
    draw.line([cx, neck_y, cx, pelvis_y], fill=line_col, width=int(8 * scale))

    # Royal crimson sash
    draw.polygon([
        (cx - int(18 * scale), neck_y + int(30 * scale)),
        (cx + int(24 * scale), pelvis_y - int(10 * scale)),
        (cx + int(28 * scale), pelvis_y + int(25 * scale)),
        (cx - int(14 * scale), neck_y + int(50 * scale))
    ], fill=(180, 35, 45), outline=(130, 20, 30), width=int(3 * scale))

    if pose == "imposing":
        # Left hand holding the noose (पाश)
        draw.line([cx, neck_y + int(20 * scale), cx - int(40 * scale), neck_y + int(45 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx - int(40 * scale), neck_y + int(45 * scale), cx - int(55 * scale), neck_y + int(90 * scale)], fill=line_col, width=int(6 * scale))
        # Golden glowing noose
        draw.ellipse([cx - int(75 * scale), neck_y + int(80 * scale), cx - int(35 * scale), neck_y + int(130 * scale)], outline=(255, 215, 50), width=int(4 * scale))
        # Right hand holding Gada (mace)
        draw.line([cx, neck_y + int(20 * scale), cx + int(45 * scale), neck_y + int(40 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx + int(45 * scale), neck_y + int(40 * scale), cx + int(60 * scale), neck_y - int(30 * scale)], fill=(230, 180, 40), width=int(6 * scale))
        draw.ellipse([cx + int(45 * scale), neck_y - int(60 * scale), cx + int(75 * scale), neck_y - int(25 * scale)], fill=(255, 200, 30), outline=(180, 130, 20), width=int(3 * scale))
        # Legs
        draw.line([cx, pelvis_y, cx - int(25 * scale), pelvis_y + int(80 * scale)], fill=line_col, width=int(7 * scale))
        draw.line([cx, pelvis_y, cx + int(25 * scale), pelvis_y + int(80 * scale)], fill=line_col, width=int(7 * scale))
    elif pose == "bowing":
        # Hands resting respectfully / accepting tilak
        draw.line([cx, neck_y + int(20 * scale), cx - int(25 * scale), neck_y + int(50 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx - int(25 * scale), neck_y + int(50 * scale), cx - int(10 * scale), neck_y + int(75 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, neck_y + int(20 * scale), cx + int(25 * scale), neck_y + int(50 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx + int(25 * scale), neck_y + int(50 * scale), cx + int(10 * scale), neck_y + int(75 * scale)], fill=line_col, width=int(6 * scale))
        # Legs
        draw.line([cx, pelvis_y, cx - int(20 * scale), pelvis_y + int(80 * scale)], fill=line_col, width=int(7 * scale))
        draw.line([cx, pelvis_y, cx + int(20 * scale), pelvis_y + int(80 * scale)], fill=line_col, width=int(7 * scale))
    elif pose == "blessing":
        # Right hand raised in Abhaya Mudra (protection blessing)
        draw.line([cx, neck_y + int(20 * scale), cx + int(35 * scale), neck_y + int(20 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx + int(35 * scale), neck_y + int(20 * scale), cx + int(45 * scale), cy], fill=line_col, width=int(6 * scale))
        # Palm facing forward with golden aura
        draw.ellipse([cx + int(40 * scale), cy - int(12 * scale), cx + int(55 * scale), cy + int(4 * scale)], fill=(255, 220, 80))
        # Left hand resting gracefully
        draw.line([cx, neck_y + int(20 * scale), cx - int(30 * scale), neck_y + int(55 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx - int(30 * scale), neck_y + int(55 * scale), cx - int(20 * scale), neck_y + int(80 * scale)], fill=line_col, width=int(6 * scale))
        # Legs
        draw.line([cx, pelvis_y, cx - int(20 * scale), pelvis_y + int(80 * scale)], fill=line_col, width=int(7 * scale))
        draw.line([cx, pelvis_y, cx + int(20 * scale), pelvis_y + int(80 * scale)], fill=line_col, width=int(7 * scale))

def draw_yamuna(draw, cx, cy, scale=1.0, pose="holding_thaal"):
    # Goddess Yamuna: Stickwoman with flowing yellow/orange sari, tiara, graceful posture
    head_r = int(22 * scale)
    line_col = (20, 25, 40)
    
    # Head
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=(255, 240, 225), outline=line_col, width=int(3.5 * scale))
    # Golden Tiara / Bindi
    draw.arc([cx - head_r, cy - head_r - 2, cx + head_r, cy - head_r + 10], start=180, end=360, fill=(255, 215, 0), width=int(3 * scale))
    draw.point((cx, cy - int(5 * scale)), fill=(230, 30, 40))
    # Long flowing hair braid
    draw.arc([cx - head_r - 5, cy, cx - head_r + 15, cy + int(50 * scale)], start=90, end=270, fill=(40, 30, 20), width=int(5 * scale))

    # Body
    neck_y = cy + head_r
    pelvis_y = neck_y + int(75 * scale)
    draw.line([cx, neck_y, cx, pelvis_y], fill=line_col, width=int(6 * scale))

    # Festive Saffron & Gold Sari Dupatta
    draw.polygon([
        (cx - int(20 * scale), neck_y + int(25 * scale)),
        (cx + int(28 * scale), pelvis_y),
        (cx + int(35 * scale), pelvis_y + int(45 * scale)),
        (cx - int(15 * scale), neck_y + int(60 * scale))
    ], fill=(255, 160, 40), outline=(210, 110, 20), width=int(3 * scale))

    if pose == "holding_thaal":
        # Both hands holding golden Puja Thaal
        draw.line([cx, neck_y + int(20 * scale), cx - int(25 * scale), neck_y + int(45 * scale)], fill=line_col, width=int(5 * scale))
        draw.line([cx - int(25 * scale), neck_y + int(45 * scale), cx - int(45 * scale), neck_y + int(40 * scale)], fill=line_col, width=int(5 * scale))
        draw.line([cx, neck_y + int(20 * scale), cx - int(10 * scale), neck_y + int(50 * scale)], fill=line_col, width=int(5 * scale))
        # Golden Puja Thaal (held towards left)
        thaal_x, thaal_y = cx - int(45 * scale), neck_y + int(42 * scale)
        draw.ellipse([thaal_x - int(25 * scale), thaal_y - int(8 * scale), thaal_x + int(25 * scale), thaal_y + int(8 * scale)], fill=(255, 215, 50), outline=(190, 140, 20), width=int(2.5 * scale))
        # Diya on thaal
        draw.polygon([(thaal_x - 6, thaal_y - 2), (thaal_x + 6, thaal_y - 2), (thaal_x, thaal_y + 4)], fill=(180, 70, 30))
        draw.ellipse([thaal_x - 3, thaal_y - 12, thaal_x + 3, thaal_y - 4], fill=(255, 170, 30))
        # Red kumkum bowl
        draw.ellipse([thaal_x + 10, thaal_y - 4, thaal_x + 18, thaal_y + 2], fill=(220, 20, 40))
        # Legs
        draw.line([cx, pelvis_y, cx - int(16 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(5.5 * scale))
        draw.line([cx, pelvis_y, cx + int(16 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(5.5 * scale))
    elif pose == "applying_tilak":
        # Right hand reaching forward to apply tilak to brother
        draw.line([cx, neck_y + int(20 * scale), cx - int(35 * scale), neck_y + int(15 * scale)], fill=line_col, width=int(5 * scale))
        draw.line([cx - int(35 * scale), neck_y + int(15 * scale), cx - int(75 * scale), neck_y - int(10 * scale)], fill=line_col, width=int(5 * scale))
        # Finger with glowing red vermilion
        draw.ellipse([cx - int(78 * scale), neck_y - int(14 * scale), cx - int(70 * scale), neck_y - int(6 * scale)], fill=(255, 30, 50))
        # Left hand holding thaal
        draw.line([cx, neck_y + int(20 * scale), cx - int(15 * scale), neck_y + int(50 * scale)], fill=line_col, width=int(5 * scale))
        thaal_x, thaal_y = cx - int(25 * scale), neck_y + int(52 * scale)
        draw.ellipse([thaal_x - int(20 * scale), thaal_y - int(6 * scale), thaal_x + int(20 * scale), thaal_y + int(6 * scale)], fill=(255, 215, 50), outline=(190, 140, 20), width=int(2 * scale))
        # Legs
        draw.line([cx, pelvis_y, cx - int(16 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(5.5 * scale))
        draw.line([cx, pelvis_y, cx + int(16 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(5.5 * scale))

def render_scene_1():
    print("🎨 Rendering Scene 1: Yamraj lowers his dread weapon / Lord of Death...")
    img = Image.new("RGBA", (W, H), (14, 10, 24, 255))
    draw = ImageDraw.Draw(img)

    # Dark stormy clouds and crimson-purple lightning
    for y in range(0, int(H * 0.65), 15):
        alpha = int(120 * (1.0 - y / (H * 0.65)))
        draw.rectangle([0, y, W, y + 15], fill=(30 + y // 30, 15, 45 + y // 25, alpha))

    # Ominous glowing dark moon / solar eclipse
    draw.ellipse([W // 2 - 90, 140, W // 2 + 90, 320], fill=(20, 15, 30), outline=(180, 80, 60), width=4)
    img = add_glow(img, W // 2, 230, 140, (220, 90, 50), max_alpha=120)
    draw = ImageDraw.Draw(img)

    # Rocky crags of Yamaloka
    ground_y = int(H * 0.68)
    draw.polygon([
        (0, ground_y + 40),
        (W // 3, ground_y - 20),
        (2 * W // 3, ground_y + 10),
        (W, ground_y - 30),
        (W, H),
        (0, H)
    ], fill=(28, 25, 35), outline=(65, 55, 75), width=3)

    # Fearsome Yamraj standing majestically lowering his noose
    draw_yamraj(draw, W // 2, ground_y - 40, scale=1.35, pose="imposing")
    img = add_glow(img, W // 2 - 75, ground_y + 60, 90, (255, 215, 60), max_alpha=160)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-1.jpg", quality=95)

def render_scene_2():
    print("🎨 Rendering Scene 2: Goddess Yamuna greets Yamraj by the holy river...")
    img = Image.new("RGBA", (W, H), (20, 25, 45, 255))
    draw = ImageDraw.Draw(img)

    # Warm dawn sky over sacred river
    for y in range(0, int(H * 0.55), 10):
        t = y / (H * 0.55)
        r = int(255 * (1 - t) + 40 * t)
        g = int(170 * (1 - t) + 60 * t)
        b = int(90 * (1 - t) + 110 * t)
        draw.rectangle([0, y, W, y + 10], fill=(r, g, b, 255))

    # Rising golden sun
    draw.ellipse([W // 2 - 75, 120, W // 2 + 75, 270], fill=(255, 220, 100))
    img = add_glow(img, W // 2, 195, 150, (255, 200, 80), max_alpha=180)
    draw = ImageDraw.Draw(img)

    # Holy Yamuna river waters
    water_y = int(H * 0.55)
    draw.polygon([(0, water_y), (W, water_y - 15), (W, int(H * 0.70)), (0, int(H * 0.70))], fill=(35, 95, 160), outline=(80, 150, 220), width=2)
    # Sacred lotus blossoms in river
    for lx, ly in [(120, water_y + 45), (320, water_y + 80), (620, water_y + 35)]:
        draw.ellipse([lx - 15, ly - 8, lx + 15, ly + 8], fill=(255, 120, 170), outline=(220, 60, 120), width=2)

    # Riverside marble ghat / terrace
    ghat_y = int(H * 0.68)
    draw.polygon([(0, ghat_y), (W, ghat_y), (W, H), (0, H)], fill=(225, 215, 195), outline=(160, 140, 120), width=3)

    # Yamraj standing humbly on left
    draw_yamraj(draw, 240, ghat_y - 15, scale=1.15, pose="bowing")

    # Sister Yamuna holding puja thaal on right facing him
    draw_yamuna(draw, 520, ghat_y - 5, scale=1.1, pose="holding_thaal")
    img = add_glow(img, 470, ghat_y + 35, 75, (255, 200, 50), max_alpha=180)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-2.jpg", quality=95)

def render_scene_3():
    print("🎨 Rendering Scene 3: The Sacred Tilak of Protection & Immortality...")
    img = Image.new("RGBA", (W, H), (15, 20, 38, 255))
    draw = ImageDraw.Draw(img)

    # Divine radiance background
    img = add_glow(img, W // 2, int(H * 0.45), 260, (255, 215, 70), max_alpha=150)
    img = add_glow(img, W // 2, int(H * 0.45), 140, (255, 255, 200), max_alpha=200)
    draw = ImageDraw.Draw(img)

    ground_y = int(H * 0.68)
    draw.rectangle([0, ground_y, W, H], fill=(235, 225, 210), outline=(170, 150, 130), width=3)

    # Close-up interaction: Sister Yamuna applies tilak to Yamraj's forehead
    yamraj_x, yamraj_y = 280, ground_y - 30
    yamuna_x, yamuna_y = 520, ground_y - 30

    draw_yamraj(draw, yamraj_x, yamraj_y, scale=1.25, pose="bowing")
    draw_yamuna(draw, yamuna_x, yamuna_y, scale=1.2, pose="applying_tilak")

    # Glowing red & gold Tilak on Yamraj's forehead
    tilak_x, tilak_y = yamraj_x, yamraj_y - 35
    draw.line([tilak_x, tilak_y - 18, tilak_x, tilak_y], fill=(255, 30, 40), width=4)
    draw.point((tilak_x, tilak_y + 4), fill=(255, 215, 0))
    img = add_glow(img, tilak_x, tilak_y - 8, 80, (255, 60, 60), max_alpha=230)
    img = add_glow(img, tilak_x, tilak_y - 8, 140, (255, 220, 50), max_alpha=180)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-3.jpg", quality=95)

def render_scene_4():
    print("🎨 Rendering Scene 4: Yamraj grants the Eternal Boon / Joyous Bhai Dooj...")
    img = Image.new("RGBA", (W, H), (18, 15, 32, 255))
    draw = ImageDraw.Draw(img)

    # Golden showered festive background with hanging marigolds & diyas
    img = add_glow(img, W // 2, 280, 240, (255, 190, 60), max_alpha=160)
    draw = ImageDraw.Draw(img)

    # Hanging festive toran / marigold garlands
    for x in range(40, W - 20, 45):
        draw.line([x, 0, x, 75], fill=(80, 140, 50), width=2)
        draw.ellipse([x - 12, 65, x + 12, 89], fill=(255, 160, 20), outline=(210, 100, 10), width=2)

    ground_y = int(H * 0.68)
    draw.rectangle([0, ground_y, W, H], fill=(240, 230, 215), outline=(180, 160, 140), width=3)

    # Lit diyas along the floor
    for dx in [80, 180, 280, 480, 580, 680]:
        draw.ellipse([dx - 18, ground_y + 60, dx + 18, ground_y + 76], fill=(190, 85, 30))
        draw.ellipse([dx - 5, ground_y + 45, dx + 5, ground_y + 62], fill=(255, 210, 50))
        img = add_glow(img, dx, ground_y + 52, 45, (255, 180, 40), max_alpha=160)
    draw = ImageDraw.Draw(img)

    # Yamraj blessing with Abhaya Mudra on right, Yamuna with folded hands on left
    draw_yamraj(draw, 490, ground_y - 25, scale=1.25, pose="blessing")
    draw_yamuna(draw, 240, ground_y - 20, scale=1.15, pose="holding_thaal")

    # Divine protection shield / blessing aura radiating over them
    img = add_glow(img, 545, ground_y - 120, 110, (255, 230, 80), max_alpha=220)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-4.jpg", quality=95)

if __name__ == "__main__":
    render_scene_1()
    render_scene_2()
    render_scene_3()
    render_scene_4()
    print("✅ All 4 Bhai Dooj scenes rendered successfully!")
