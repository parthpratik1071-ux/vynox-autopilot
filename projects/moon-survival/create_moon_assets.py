#!/usr/bin/env python3
"""
Generate 4 cinematic 2D stickman scenes for Moon Survival Reel (Bhai Dooj Space Special)
Resolution: 768x1376 (9:16 vertical)
"""

import math
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pathlib import Path

OUT_DIR = Path("/home/pratik/stickman-video-director/projects/moon-survival/assets")
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

def draw_stars(draw, count=250):
    random.seed(42)
    for _ in range(count):
        sx = random.randint(0, W)
        sy = random.randint(0, int(H * 0.7))
        brightness = random.randint(140, 255)
        r = random.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(brightness, brightness, brightness))

def draw_earth(draw, cx, cy, radius):
    # Glowing blue planet Earth
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(20, 90, 190), outline=(60, 160, 255), width=3)
    # Continents
    draw.ellipse([cx - radius//2, cy - radius//3, cx, cy + radius//4], fill=(40, 150, 70))
    draw.ellipse([cx + 10, cy - radius//2, cx + radius//2, cy], fill=(50, 160, 80))
    # Clouds swirl
    draw.arc([cx - radius + 10, cy - radius + 20, cx + radius - 10, cy + radius - 20], start=30, end=140, fill=(240, 245, 255), width=8)

def draw_lunar_ground(draw, horizon_y):
    # Lunar surface dark grey with craters
    draw.polygon([
        (0, horizon_y),
        (W // 4, horizon_y - 25),
        (W // 2, horizon_y - 10),
        (3 * W // 4, horizon_y - 35),
        (W, horizon_y - 15),
        (W, H),
        (0, H)
    ], fill=(45, 48, 55), outline=(70, 75, 85), width=3)

    # Craters
    craters = [
        (120, horizon_y + 120, 80, 25),
        (450, horizon_y + 200, 160, 45),
        (650, horizon_y + 90, 90, 30),
        (250, horizon_y + 350, 220, 60),
    ]
    for cx, cy, rx, ry in craters:
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(32, 35, 40), outline=(65, 70, 80), width=2)

def draw_astronaut(draw, cx, cy, is_female=False, pose="standing", scale=1.0):
    # Astronaut stickman with space helmet and backpack
    line_col = (235, 240, 250)
    helmet_r = int(24 * scale)
    
    # Life support backpack
    bp_w = int(26 * scale)
    bp_h = int(55 * scale)
    draw.rectangle([cx - int(32 * scale), cy - int(10 * scale), cx - int(6 * scale), cy + bp_h], fill=(70, 75, 85), outline=(130, 140, 155), width=2)
    # Oxygen indicator light on pack
    light_col = (0, 255, 120) if not is_female else (0, 200, 255)
    draw.ellipse([cx - int(24 * scale), cy, cx - int(14 * scale), cy + int(10 * scale)], fill=light_col)

    # Helmet
    draw.ellipse([cx - helmet_r, cy - helmet_r, cx + helmet_r, cy + helmet_r], fill=(30, 35, 45), outline=line_col, width=int(4 * scale))
    # Visor reflection
    draw.arc([cx - helmet_r + 4, cy - helmet_r + 4, cx + helmet_r - 4, cy + helmet_r - 4], start=210, end=330, fill=(255, 200, 50), width=int(4 * scale))

    # Body
    neck_y = cy + helmet_r
    pelvis_y = neck_y + int(70 * scale)
    draw.line([cx, neck_y, cx, pelvis_y], fill=line_col, width=int(7 * scale))

    # Suit belt
    draw.line([cx - int(15 * scale), pelvis_y - int(10 * scale), cx + int(15 * scale), pelvis_y - int(10 * scale)], fill=(180, 50, 50), width=int(4 * scale))

    if pose == "standing":
        # Arms
        draw.line([cx, neck_y + int(15 * scale), cx - int(30 * scale), neck_y + int(45 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, neck_y + int(15 * scale), cx + int(30 * scale), neck_y + int(45 * scale)], fill=line_col, width=int(6 * scale))
        # Legs
        draw.line([cx, pelvis_y, cx - int(20 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, pelvis_y, cx + int(20 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(6 * scale))
    elif pose == "salute":
        # Right hand saluting/thumbs up
        draw.line([cx, neck_y + int(15 * scale), cx - int(25 * scale), neck_y + int(50 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, neck_y + int(15 * scale), cx + int(25 * scale), neck_y], fill=line_col, width=int(6 * scale))
        draw.line([cx + int(25 * scale), neck_y, cx + int(32 * scale), cy - int(5 * scale)], fill=line_col, width=int(6 * scale))
        # Legs
        draw.line([cx, pelvis_y, cx - int(18 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, pelvis_y, cx + int(18 * scale), pelvis_y + int(70 * scale)], fill=line_col, width=int(6 * scale))
    elif pose == "kneeling":
        # Left arm reaching to lock tank
        draw.line([cx, neck_y + int(15 * scale), cx + int(35 * scale), neck_y + int(25 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, neck_y + int(15 * scale), cx - int(20 * scale), neck_y + int(45 * scale)], fill=line_col, width=int(6 * scale))
        # Kneeling legs
        draw.line([cx, pelvis_y, cx - int(25 * scale), pelvis_y + int(35 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx - int(25 * scale), pelvis_y + int(35 * scale), cx, pelvis_y + int(60 * scale)], fill=line_col, width=int(6 * scale))
        draw.line([cx, pelvis_y, cx + int(25 * scale), pelvis_y + int(50 * scale)], fill=line_col, width=int(6 * scale))

def render_scene_1():
    print("🎨 Rendering Scene 1: Lunar crash site & Earth in deep cosmos...")
    img = Image.new("RGBA", (W, H), (6, 8, 16, 255))
    draw = ImageDraw.Draw(img)

    draw_stars(draw, count=280)
    draw_earth(draw, W - 140, 180, 95)
    img = add_glow(img, W - 140, 180, 150, (60, 170, 255), max_alpha=120)
    draw = ImageDraw.Draw(img)

    horizon_y = int(H * 0.62)
    draw_lunar_ground(draw, horizon_y)

    # Crashed lunar rover (smoking)
    # Rover chassis
    rx, ry = 120, horizon_y + 40
    draw.polygon([(rx, ry + 80), (rx + 220, ry + 40), (rx + 200, ry + 120), (rx - 20, ry + 140)], fill=(75, 80, 95), outline=(130, 140, 160), width=4)
    # Broken cockpit dome
    draw.arc([rx + 40, ry + 10, rx + 160, ry + 90], start=180, end=360, fill=(100, 200, 255), width=4)
    # Sparks / fire warning beacon
    draw.ellipse([rx + 80, ry + 20, rx + 100, ry + 40], fill=(255, 60, 40))
    img = add_glow(img, rx + 90, ry + 30, 70, (255, 70, 30), max_alpha=180)
    draw = ImageDraw.Draw(img)

    # Brother & Sister astronauts facing crashed rover
    draw_astronaut(draw, 480, horizon_y + 110, is_female=False, pose="standing", scale=1.1)
    draw_astronaut(draw, 580, horizon_y + 130, is_female=True, pose="standing", scale=0.95)

    # Subtle vignette
    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-1.jpg", quality=95)

def render_scene_2():
    print("🎨 Rendering Scene 2: Critical Alarm HUD & Only 1 O2 Tank...")
    img = Image.new("RGBA", (W, H), (12, 12, 20, 255))
    draw = ImageDraw.Draw(img)

    draw_stars(draw, count=150)
    horizon_y = int(H * 0.68)
    draw_lunar_ground(draw, horizon_y)

    # Red warning holographic banner overlay
    alert_box = [60, 180, W - 60, 380]
    draw.rounded_rectangle(alert_box, radius=16, fill=(40, 8, 12, 220), outline=(255, 50, 60), width=4)

    # Alert warning text & icons
    # Flashing warning icon
    draw.polygon([(W // 2, 210), (W // 2 - 35, 275), (W // 2 + 35, 275)], fill=(255, 50, 50), outline=(255, 230, 200), width=3)
    draw.line([W // 2, 235, W // 2, 255], fill=(255, 255, 255), width=4)
    draw.point((W // 2, 265), fill=(255, 255, 255))

    # Alert message text (Holographic font style lines)
    draw.text((W // 2, 305), "CRITICAL OXYGEN FAILURE", fill=(255, 70, 70), anchor="mm")
    draw.text((W // 2, 340), "TIME REMAINING: 10 MINUTES | TANKS LEFT: 1", fill=(255, 220, 80), anchor="mm")

    # Center focus: The single glowing Cyan O2 Tank floating / resting between them
    tank_x, tank_y = W // 2, int(H * 0.58)
    draw.rounded_rectangle([tank_x - 30, tank_y - 80, tank_x + 30, tank_y + 80], radius=15, fill=(40, 180, 230), outline=(220, 255, 255), width=4)
    draw.rectangle([tank_x - 15, tank_y - 100, tank_x + 15, tank_y - 80], fill=(200, 210, 220))
    # Valve gauge
    draw.ellipse([tank_x - 10, tank_y - 40, tank_x + 10, tank_y - 20], fill=(0, 255, 120))

    img = add_glow(img, tank_x, tank_y, 140, (0, 210, 255), max_alpha=210)
    draw = ImageDraw.Draw(img)

    # Astronauts on each side looking at the tank
    draw_astronaut(draw, 190, horizon_y + 90, is_female=False, pose="standing", scale=1.15)
    draw_astronaut(draw, 580, horizon_y + 100, is_female=True, pose="standing", scale=1.0)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-2.jpg", quality=95)

def render_scene_3():
    print("🎨 Rendering Scene 3: Brother locks the last O2 tank into his sister's suit...")
    img = Image.new("RGBA", (W, H), (10, 12, 22, 255))
    draw = ImageDraw.Draw(img)

    draw_stars(draw, count=220)
    draw_earth(draw, 140, 200, 80)
    img = add_glow(img, 140, 200, 130, (50, 160, 255), max_alpha=100)
    draw = ImageDraw.Draw(img)

    horizon_y = int(H * 0.65)
    draw_lunar_ground(draw, horizon_y)

    # Emotional Golden & Cyan bond glow connecting brother and sister
    sister_x, sister_y = 480, horizon_y + 80
    brother_x, brother_y = 290, horizon_y + 80

    # Brother kneeling down tenderly
    draw_astronaut(draw, brother_x, brother_y, is_female=False, pose="kneeling", scale=1.2)
    # Sister standing, touched, hands gently raised
    draw_astronaut(draw, sister_x, sister_y, is_female=True, pose="standing", scale=1.05)

    # Golden emotional bond aura around the cylinder being inserted into sister's suit
    mid_x, mid_y = int((brother_x + sister_x) / 2) + 15, brother_y + 45
    draw.rounded_rectangle([mid_x - 22, mid_y - 50, mid_x + 22, mid_y + 50], radius=12, fill=(0, 220, 255), outline=(255, 240, 150), width=3)
    img = add_glow(img, mid_x, mid_y, 160, (255, 215, 60), max_alpha=190)
    img = add_glow(img, mid_x, mid_y, 90, (0, 240, 255), max_alpha=220)
    draw = ImageDraw.Draw(img)

    # Brother's helmet visor reflecting her reflection
    draw.arc([brother_x - 18, brother_y - 18, brother_x + 18, brother_y + 18], start=210, end=330, fill=(255, 230, 80), width=5)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-3.jpg", quality=95)

def render_scene_4():
    print("🎨 Rendering Scene 4: The Heroic Salute on the Lunar Ridge...")
    img = Image.new("RGBA", (W, H), (8, 10, 18, 255))
    draw = ImageDraw.Draw(img)

    draw_stars(draw, count=320)
    # Earth shining brightly above like a blue marble of hope
    draw_earth(draw, W // 2, 230, 120)
    img = add_glow(img, W // 2, 230, 220, (70, 180, 255), max_alpha=140)
    draw = ImageDraw.Draw(img)

    # Elevated lunar ridge
    ridge_y = int(H * 0.65)
    draw.polygon([
        (0, ridge_y + 80),
        (W // 2, ridge_y),
        (W, ridge_y + 60),
        (W, H),
        (0, H)
    ], fill=(40, 44, 52), outline=(75, 82, 95), width=4)

    # Brother standing on the summit alone in brave silhouette with golden halo
    bx, by = W // 2, ridge_y - 20
    draw_astronaut(draw, bx, by, is_female=False, pose="salute", scale=1.3)
    img = add_glow(img, bx, by, 180, (255, 210, 70), max_alpha=160)
    draw = ImageDraw.Draw(img)

    # Rescue pod lights flashing far in the distance taking sister home safely
    pod_x, pod_y = 620, int(H * 0.42)
    draw.ellipse([pod_x - 18, pod_y - 10, pod_x + 18, pod_y + 10], fill=(220, 240, 255), outline=(100, 200, 255), width=2)
    # Ion engine trail
    draw.polygon([(pod_x - 15, pod_y), (pod_x - 90, pod_y + 25), (pod_x - 25, pod_y + 8)], fill=(0, 220, 255, 180))
    img = add_glow(img, pod_x, pod_y, 80, (0, 220, 255), max_alpha=200)

    img = img.convert("RGB")
    img.save(OUT_DIR / "scene-4.jpg", quality=95)

if __name__ == "__main__":
    render_scene_1()
    render_scene_2()
    render_scene_3()
    render_scene_4()
    print("✅ All 4 Moon Survival scenes rendered successfully!")
