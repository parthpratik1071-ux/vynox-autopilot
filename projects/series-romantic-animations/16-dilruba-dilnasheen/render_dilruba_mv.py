#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Dilruba Dilnasheen" - Rito Riba
Features:
- 4 Master Scenes with Makoto Shinkai & Studio Ghibli romantic aesthetic:
  1. Shot 1 (0.0s - 5.5s): Blooming Courtyard Garden (Swaying jasmine vines, drifting rose petals, lantern blooms, lavender twilight)
  2. Shot 2 (5.5s - 11.0s): Boy by Floral Archway (Torso breathing physics, hair breeze wave, 5-frame eye blink, floating petals)
  3. Shot 3 (11.0s - 16.5s): Intimate Girl "Dilruba" Portrait (Chest breathing, wind in dark glossy hair, starlight eye twinkle, eye blink)
  4. Shot 4 (16.5s - 22.0s): Couple Climax under Night Sky (Synchronized breathing, starfield shimmer, shooting star, swirling rose petals)
- Procedural falling rose & jasmine petals with rotational drift physics
- 50 floating golden fireflies & ambient light motes drifting with Brownian motion
- Smooth 6-frame cross-dissolve transitions between shots
- Handheld 6-DOF camera micro-drift on every frame
- AEP Cinema Grade Stack: Deep Glow bloom + Rainbow Prism flare + 35mm grain
- Master ASS Subtitles strictly at Instagram safe-zone baseline y = 1390 (MarginV = 540)
"""

import math
import os
import random
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath("scripts"))
from aep_cinema_engine import (
    generate_rainbow_prism_flare,
    apply_deep_glow,
    apply_cinema_grade,
    add_film_grain,
    render_cinema_single_caption
)

BASE_DIR = Path("projects/series-romantic-animations/16-dilruba-dilnasheen")
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_FILE = BASE_DIR / "audio" / "dilruba_clip.wav"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_VIDEO = OUT_DIR / "temp_dilruba.mp4"
FINAL_REEL = OUT_DIR / "film_dilruba_aep.mp4"
SUBTITLE_ASS = OUT_DIR / "dilruba_subtitles.ass"
COVER_FILE = OUT_DIR / "cover_aep.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 22.0
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing Living 2D Anime MV Engine for 'Dilruba Dilnasheen' ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# -------------------------------------------------------------
# 1. LOAD & PREPARE 4 CANVASES (1080x1920) in NATIVE BGR
# -------------------------------------------------------------
def load_canvas(path):
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {path}")
    ih, iw = img.shape[:2]
    scale = max(WIDTH / iw, HEIGHT / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    return resized[oy:oy + HEIGHT, ox:ox + WIDTH].copy()

canvas_s1 = load_canvas(ASSETS_DIR / "scene-1.jpg")
canvas_s2 = load_canvas(ASSETS_DIR / "scene-2.jpg")
canvas_s3 = load_canvas(ASSETS_DIR / "scene-3.jpg")
canvas_s4 = load_canvas(ASSETS_DIR / "scene-4.jpg")

print("✅ Loaded all 4 scene canvases in native BGR.")

# -------------------------------------------------------------
# 2. WRITE MASTER ASS SUBTITLES (Safe Zone: MarginV=540, baseline y=1390)
# -------------------------------------------------------------
ass_template = """[Script Info]
Title: Dilruba Dilnasheen - Living 2D Cinematic MV
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: __WIDTH__
PlayResY: __HEIGHT__

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleBadge,Lato,38,&H00FFFFFF,&H000000FF,&H90000000,&H60000000,-1,0,0,0,100,100,2,0,1,2.0,1.0,8,60,60,180,1
Style: LyricGold,Lato,62,&H00FFFFFF,&H000000FF,&H90050810,&H80000000,-1,0,0,0,100,100,1,0,1,3.5,2.0,2,80,80,540,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:04.50,TitleBadge,,0,0,180,,{\\fad(400,600)}RITO RIBA  |  {\\c&H003CE0FF&}DILRUBA DILNASHEEN
Dialogue: 1,0:00:00.20,0:00:05.10,LyricGold,,0,0,540,,{\\fad(250,200)}Dilruba {\\c&H003CE0FF&}dil-nasheen{\\c&H00FFFFFF&}, ba-khuda tu haseen...
Dialogue: 1,0:00:05.20,0:00:10.50,LyricGold,,0,0,540,,{\\fad(200,200)}Tere jaisi {\\c&H00FFB040&}hoor na koi{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:10.60,0:00:15.80,LyricGold,,0,0,540,,{\\fad(200,200)}Tum mile {\\c&H003CE0FF&}gul khile{\\c&H00FFFFFF&}, gul khile jo tum mile...
Dialogue: 1,0:00:15.90,0:00:21.50,LyricGold,,0,0,540,,{\\fad(200,400)}Gulzar zindagi {\\c&H0055EEFF&}yeh ho gayi, dilruba{\\c&H00FFFFFF&}...
"""
ass_content = ass_template.replace("__WIDTH__", str(WIDTH)).replace("__HEIGHT__", str(HEIGHT))

with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
    f.write(ass_content)

print(f"✅ Generated ASS Subtitles with Instagram safe zone baseline at y = 1390 (MarginV = 540).")

# -------------------------------------------------------------
# 3. PROCEDURAL PARTICLES: PETALS & FIREFLIES SETUP
# -------------------------------------------------------------
random.seed(303)

# 30 Drifting flower petals (rose pink & jasmine ivory)
petals = []
for _ in range(30):
    petals.append({
        "x": random.uniform(20, 1060),
        "y": random.uniform(-100, 1850),
        "vx": random.uniform(0.4, 1.2),
        "vy": random.uniform(1.0, 2.5),
        "size": random.uniform(8.0, 18.0),
        "angle": random.uniform(0, 360),
        "rot_speed": random.uniform(-3.5, 3.5),
        "color": random.choice([
            (170, 150, 245), # Soft rose pink in BGR
            (190, 170, 255), # Light blush pink
            (235, 245, 255), # Jasmine ivory white
            (160, 130, 230)  # Peach rose
        ])
    })

# 50 floating golden fireflies / ambient light motes
fireflies = []
for _ in range(50):
    fireflies.append({
        "x": random.uniform(40, 1040),
        "y": random.uniform(250, 1750),
        "vx": random.uniform(-0.35, 0.35),
        "vy": random.uniform(-0.6, -0.15),
        "radius": random.uniform(1.5, 4.2),
        "base_alpha": random.uniform(130, 230),
        "phase": random.uniform(0, math.pi * 2),
        "color": random.choice([(70, 200, 255), (90, 220, 255), (110, 240, 255), (60, 180, 255)])
    })

# Twinkling stars in sky
stars_sky = []
for _ in range(40):
    stars_sky.append((
        random.uniform(50, 1030),
        random.uniform(80, 500),
        random.uniform(1.2, 2.6),
        random.uniform(0, math.pi * 2)
    ))

def apply_handheld_drift(frame, t, amp_x=2.6, amp_y=2.0):
    dx = math.sin(t * 0.82) * amp_x + math.sin(t * 1.55) * 0.85
    dy = math.cos(t * 0.62) * amp_y + math.cos(t * 1.25) * 0.70
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

# -------------------------------------------------------------
# 4. SHOT-BY-SHOT LIVING RENDERERS
# -------------------------------------------------------------

# --- SHOT 1: Blooming Courtyard Garden (0.0s - 5.5s) ---
def render_shot1(t, f_idx):
    frame = canvas_s1.copy()
    
    # Twinkling stars in twilight sky
    for sx, sy, r, phase in stars_sky:
        tw = (math.sin(t * 4.0 + phase) + 1.0) * 0.5
        cv2.circle(frame, (int(sx), int(sy)), int(r + tw * 1.5), (255, 250, 235), -1)
    
    # Climbing jasmine vines gentle breeze sway (X: 0..400, Y: 300..1200)
    vine_region = frame[300:1200, 0:400]
    vh, vw = vine_region.shape[:2]
    v_wave = math.sin(t * 2.8) * 3.5
    pts1 = np.float32([[0, 0], [vw, 0], [0, vh], [vw, vh]])
    pts2 = np.float32([[0, 0], [vw, 0], [v_wave, vh], [vw + v_wave, vh]])
    M_v = cv2.getPerspectiveTransform(pts1, pts2)
    frame[300:1200, 0:400] = cv2.addWeighted(vine_region, 0.25, cv2.warpPerspective(vine_region, M_v, (vw, vh), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # Lantern warm pulsing glow (X: 450, Y: 920 and X: 750, Y: 950)
    overlay = frame.copy()
    for lx, ly in [(450, 920), (750, 950)]:
        pulse = (math.sin(t * 3.0 + lx * 0.05) + 1.0) * 0.5
        rad = int(22 + pulse * 12)
        cv2.circle(overlay, (lx, ly), rad, (80, 210, 255), -1)
        cv2.circle(frame, (lx, ly), 5, (240, 255, 255), -1)
    cv2.addWeighted(overlay, 0.28, frame, 0.72, 0, frame)
    
    # Shooting star at t=3.0s
    if 2.8 <= t <= 3.5:
        st_p = (t - 2.8) / 0.7
        sx1 = int(180 + st_p * 540)
        sy1 = int(100 + st_p * 230)
        sx0 = int(sx1 - 90)
        sy0 = int(sy1 - 40)
        cv2.line(frame, (sx0, sy0), (sx1, sy1), (255, 245, 215), 2)
        cv2.circle(frame, (sx1, sy1), 3, (255, 255, 255), -1)
        
    return apply_handheld_drift(frame, t)

# --- SHOT 2: Boy Character by Floral Archway (5.5s - 11.0s) ---
def render_shot2(t, f_idx):
    rel_t = max(0.0, t - 5.5)
    frame = canvas_s2.copy()
    
    # Cinematic push-in
    zoom = 1.0 + 0.035 * min(1.0, rel_t / 5.5)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Torso breathing physics
    breath = math.sin(rel_t * (2.0 * math.pi / 2.9)) * 3.2
    torso = frame[850:1400, 320:820]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.48]])
    frame[850:1400, 320:820] = cv2.addWeighted(torso, 0.20, cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT), 0.80, 0)
    
    # Soft hair breeze wave
    hair = frame[550:800, 420:700]
    hh, hw = hair.shape[:2]
    wave = math.sin(rel_t * 3.4) * 3.2
    pts1 = np.float32([[0, 0], [hw, 0], [0, hh], [hw, hh]])
    pts2 = np.float32([[0, 0], [hw, 0], [wave, hh], [hw + wave, hh]])
    M_h = cv2.getPerspectiveTransform(pts1, pts2)
    frame[550:800, 420:700] = cv2.addWeighted(hair, 0.25, cv2.warpPerspective(hair, M_h, (hw, hh), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # 5-frame natural eye blink at t=8.2s
    dt_blink = abs(t - 8.20)
    if dt_blink < 0.10:
        b_phase = 1.0 - (dt_blink / 0.10)
        ey_cx, ey_cy = 555, 735
        skin_bgr = tuple(int(c) for c in canvas_s2[720:740, 545:565].mean(axis=(0,1)))
        cv2.ellipse(frame, (ey_cx, ey_cy), (8, int(6 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (ey_cx - 9, ey_cy), (ey_cx + 9, ey_cy), (30, 20, 25), 2)
    
    return apply_handheld_drift(frame, t, amp_x=2.4, amp_y=1.8)

# --- SHOT 3: Intimate Girl "Dilruba" Portrait (11.0s - 16.5s) ---
def render_shot3(t, f_idx):
    rel_t = max(0.0, t - 11.0)
    frame = canvas_s3.copy()
    
    # Cinematic push-in
    zoom = 1.0 + 0.04 * min(1.0, rel_t / 5.5)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Chest breathing physics
    breath = math.sin(rel_t * (2.0 * math.pi / 2.7)) * 2.8
    chest = frame[1050:1500, 300:780]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.42]])
    frame[1050:1500, 300:780] = cv2.addWeighted(chest, 0.22, cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT), 0.78, 0)
    
    # Wind in dark glossy hair strands
    hair = frame[600:1150, 200:460]
    hh, hw = hair.shape[:2]
    w_wave = math.sin(rel_t * 3.2) * 3.6
    pts1 = np.float32([[0, 0], [hw, 0], [0, hh], [hw, hh]])
    pts2 = np.float32([[0, 0], [hw, 0], [w_wave, hh], [hw + w_wave, hh]])
    M_h = cv2.getPerspectiveTransform(pts1, pts2)
    frame[600:1150, 200:460] = cv2.addWeighted(hair, 0.28, cv2.warpPerspective(hair, M_h, (hw, hh), borderMode=cv2.BORDER_REFLECT), 0.72, 0)
    
    # Silver jhumka earring subtle micro-swing pendulum physics (X: 380, Y: 820)
    swing = math.sin(rel_t * 4.0) * 2.5
    jhumka = frame[800:870, 360:410]
    jh, jw = jhumka.shape[:2]
    M_j = np.float32([[1, 0, swing], [0, 1, 0]])
    frame[800:870, 360:410] = cv2.addWeighted(jhumka, 0.30, cv2.warpAffine(jhumka, M_j, (jw, jh), borderMode=cv2.BORDER_REFLECT), 0.70, 0)
    
    # Eye blink at t=13.6s
    dt_blink = abs(t - 13.60)
    if dt_blink < 0.10:
        b_phase = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s3[770:790, 520:540].mean(axis=(0,1)))
        # Left eye
        cv2.ellipse(frame, (485, 765), (10, int(7 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (473, 765), (497, 765), (35, 20, 25), 2)
        # Right eye
        cv2.ellipse(frame, (595, 765), (10, int(7 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (583, 765), (607, 765), (35, 20, 25), 2)
    
    # Starlight twinkle in eyes
    twinkle = (math.sin(rel_t * 5.2) + 1.0) * 0.5
    cv2.circle(frame, (490, 762), int(1.5 + twinkle * 1.5), (255, 255, 245), -1)
    cv2.circle(frame, (600, 762), int(1.5 + twinkle * 1.5), (255, 255, 245), -1)
    
    return apply_handheld_drift(frame, t, amp_x=2.2, amp_y=1.8)

# --- SHOT 4: Couple Climax under Night Sky (16.5s - 22.0s) ---
def render_shot4(t, f_idx):
    rel_t = max(0.0, t - 16.5)
    frame = canvas_s4.copy()
    
    # Synchronized couple breathing
    breath = math.sin(rel_t * (2.0 * math.pi / 2.8)) * 3.4
    couple_torso = frame[850:1450, 250:850]
    cth, ctw = couple_torso.shape[:2]
    M_ct = np.float32([[1, 0, 0], [0, 1, breath * 0.42]])
    frame[850:1450, 250:850] = cv2.addWeighted(couple_torso, 0.25, cv2.warpAffine(couple_torso, M_ct, (ctw, cth), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # Starry night twinkling
    for sx, sy, r, phase in stars_sky:
        tw = (math.sin(t * 3.9 + phase) + 1.0) * 0.5
        cv2.circle(frame, (int(sx), int(sy)), int(r + tw * 1.5), (255, 250, 230), -1)
        
    # Shooting star at t=19.4s
    if 19.1 <= t <= 19.8:
        st_p = (t - 19.1) / 0.7
        sx1 = int(220 + st_p * 580)
        sy1 = int(110 + st_p * 250)
        sx0 = int(sx1 - 95)
        sy0 = int(sy1 - 42)
        cv2.line(frame, (sx0, sy0), (sx1, sy1), (255, 245, 220), 2)
        cv2.circle(frame, (sx1, sy1), 3, (255, 255, 255), -1)
        
    return apply_handheld_drift(frame, t, amp_x=2.5, amp_y=2.0)

# -------------------------------------------------------------
# 5. MASTER RENDER PIPELINE WITH CROSS-DISSOLVES & PETALS
# -------------------------------------------------------------
def get_shot_frame(t, f_idx):
    DISSOLVE_DUR = 0.20
    
    if t < 5.50 - DISSOLVE_DUR:
        return render_shot1(t, f_idx)
    elif t < 5.50:
        alpha = (t - (5.50 - DISSOLVE_DUR)) / DISSOLVE_DUR
        f1 = render_shot1(t, f_idx)
        f2 = render_shot2(t, f_idx)
        return cv2.addWeighted(f1, 1.0 - alpha, f2, alpha, 0)
    elif t < 11.00 - DISSOLVE_DUR:
        return render_shot2(t, f_idx)
    elif t < 11.00:
        alpha = (t - (11.00 - DISSOLVE_DUR)) / DISSOLVE_DUR
        f2 = render_shot2(t, f_idx)
        f3 = render_shot3(t, f_idx)
        return cv2.addWeighted(f2, 1.0 - alpha, f3, alpha, 0)
    elif t < 16.50 - DISSOLVE_DUR:
        return render_shot3(t, f_idx)
    elif t < 16.50:
        alpha = (t - (16.50 - DISSOLVE_DUR)) / DISSOLVE_DUR
        f3 = render_shot3(t, f_idx)
        f4 = render_shot4(t, f_idx)
        return cv2.addWeighted(f3, 1.0 - alpha, f4, alpha, 0)
    else:
        return render_shot4(t, f_idx)

# Precompute flare overlay
flare_overlay = generate_rainbow_prism_flare(WIDTH, HEIGHT, intensity=0.35, blur_radius=28)
flare_norm = flare_overlay.astype(np.float32) / 255.0

# Open Video Writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(str(TEMP_VIDEO), fourcc, FPS, (WIDTH, HEIGHT))

print("🚀 Rendering 660 master frames with living character acting, petals & fireflies...")

# Render loop
for f in range(TOTAL_FRAMES):
    t = f / FPS
    
    # 1. Base shot rendering
    frame = get_shot_frame(t, f)
    
    # 2. Render drifting flower petals
    petal_overlay = frame.copy()
    for p in petals:
        p["x"] += p["vx"] + math.sin(t * 2.0 + p["y"] * 0.01) * 0.8
        p["y"] += p["vy"]
        p["angle"] += p["rot_speed"]
        if p["y"] > 1950:
            p["y"] = -50
            p["x"] = random.uniform(20, 1060)
        if p["x"] > 1100: p["x"] = -20
        
        # Draw tilted petal ellipse
        center = (int(p["x"]), int(p["y"]))
        axes = (int(p["size"]), int(p["size"] * 0.55))
        cv2.ellipse(petal_overlay, center, axes, p["angle"], 0, 360, p["color"], -1)
    cv2.addWeighted(petal_overlay, 0.40, frame, 0.60, 0, frame)
    
    # 3. Render 50 floating golden fireflies
    ff_overlay = frame.copy()
    for ff in fireflies:
        ff["x"] += ff["vx"] + math.sin(t * 1.5 + ff["phase"]) * 0.4
        ff["y"] += ff["vy"]
        if ff["y"] < 150:
            ff["y"] = 1800
            ff["x"] = random.uniform(40, 1040)
        if ff["x"] < 20: ff["x"] = 1060
        if ff["x"] > 1060: ff["x"] = 20
        
        pulse = (math.sin(t * 3.0 + ff["phase"]) + 1.0) * 0.5
        cur_r = ff["radius"] * (0.8 + 0.4 * pulse)
        cv2.circle(ff_overlay, (int(ff["x"]), int(ff["y"])), int(cur_r + 2), ff["color"], -1)
        cv2.circle(frame, (int(ff["x"]), int(ff["y"])), int(cur_r), (255, 255, 255), -1)
    frame = cv2.addWeighted(ff_overlay, 0.35, frame, 0.65, 0)
    
    # 4. AEP Cinema Post-Processing
    glow = apply_deep_glow(frame, threshold=180, bloom_factor=0.50, tint=(0.95, 1.05, 1.15))
    g_norm = glow.astype(np.float32) / 255.0
    flared = np.clip((1.0 - (1.0 - g_norm) * (1.0 - flare_norm)) * 255.0, 0, 255).astype(np.uint8)
    graded = apply_cinema_grade(flared, lift=10, contrast=1.10, warm_highlight=1.06, cool_shadow=1.03)
    grained = add_film_grain(graded, intensity=2.8, seed=f)
    
    writer.write(grained)
    if f % 90 == 0 or f == TOTAL_FRAMES - 1:
        print(f"  Frame {f}/{TOTAL_FRAMES} (t = {t:.2f}s) completed.")

writer.release()
print(f"✅ Master frames rendered to {TEMP_VIDEO}.")

# -------------------------------------------------------------
# 6. FFMPEG AUDIO MUX & ASS SUBTITLE INJECTION
# -------------------------------------------------------------
print("🎬 Multiplexing audio and burning ASS subtitles in safe zone...")

cmd = [
    "ffmpeg", "-y",
    "-i", str(TEMP_VIDEO),
    "-i", str(AUDIO_FILE),
    "-vf", f"subtitles={SUBTITLE_ASS}:fontsdir=/usr/share/fonts",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    str(FINAL_REEL)
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print(f"FFmpeg error: {res.stderr}")
    sys.exit(1)

print(f"✅ Final living reel rendered cleanly: {FINAL_REEL} ({FINAL_REEL.stat().st_size / (1024*1024):.2f} MB)")

# -------------------------------------------------------------
# 7. GENERATE COVER AND STORY CARD
# -------------------------------------------------------------
cap = cv2.VideoCapture(str(FINAL_REEL))
cap.set(cv2.CAP_PROP_POS_FRAMES, int(14.0 * FPS)) # Girl portrait at t=14s
ret, frame_cover = cap.read()
if ret:
    cv2.imwrite(str(COVER_FILE), frame_cover)
    cv2.imwrite(str(STORY_CARD), frame_cover)
    print(f"✅ Created cover and story card from film frame at t=14.0s.")
cap.release()

if TEMP_VIDEO.exists():
    TEMP_VIDEO.unlink()

print("🎉 ALL PRODUCTION STEPS FOR DILRUBA DILNASHEEN COMPLETED SUCCESSFULLY!")
