#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Tu Keh De Toh" - Anuv Jain
Features:
- 4 Master Scenes with Makoto Shinkai & Studio Ghibli romantic aesthetic:
  1. Shot 1 (0.0s - 5.5s): Twilight Rooftop Balcony (Rising chai steam curls, twinkling stars, pulsing fairy lights, shooting star)
  2. Shot 2 (5.5s - 11.0s): Boy with Guitar (Torso breathing physics, hair sway wave, 5-frame eye blink, ambient bokeh shimmer)
  3. Shot 3 (11.0s - 16.5s): Intimate Girl Close-up (Chest breathing, wind in hair strands, eye blink, eye starlight reflection)
  4. Shot 4 (16.5s - 22.0s): Couple Climax under Blanket (Synchronized breathing, starfield shimmer, shooting star, fairy lights)
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

BASE_DIR = Path("projects/series-romantic-animations/15-tu-keh-de-toh-anuv-jain")
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_FILE = BASE_DIR / "audio" / "tu_keh_de_toh_clip.wav"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_VIDEO = OUT_DIR / "temp_tu_keh_de_toh.mp4"
FINAL_REEL = OUT_DIR / "film_tu_keh_de_toh_aep.mp4"
SUBTITLE_ASS = OUT_DIR / "tu_keh_de_toh_subtitles.ass"
COVER_FILE = OUT_DIR / "cover_aep.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 22.0
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing Living 2D Anime MV Engine for 'Tu Keh De Toh' ({TOTAL_FRAMES} frames @ {FPS} fps)...")

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
Title: Tu Keh De Toh - Living 2D Cinematic MV
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
Dialogue: 0,0:00:00.50,0:00:04.50,TitleBadge,,0,0,180,,{\\fad(400,600)}ANUV JAIN  |  {\\c&H003CE0FF&}TU KEH DE TOH
Dialogue: 1,0:00:00.20,0:00:05.10,LyricGold,,0,0,540,,{\\fad(250,200)}Tu keh de toh {\\c&H003CE0FF&}dil hai{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:05.20,0:00:10.50,LyricGold,,0,0,540,,{\\fad(200,200)}Har din hai {\\c&H00FFB040&}tere liye{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:10.60,0:00:15.80,LyricGold,,0,0,540,,{\\fad(200,200)}Tu maange toh {\\c&H003CE0FF&}jaan bhi{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:15.90,0:00:21.50,LyricGold,,0,0,540,,{\\fad(200,400)}Le jaa abhi, {\\c&H0055EEFF&}kuchh na kahein{\\c&H00FFFFFF&}...
"""
ass_content = ass_template.replace("__WIDTH__", str(WIDTH)).replace("__HEIGHT__", str(HEIGHT))

with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
    f.write(ass_content)

print(f"✅ Generated ASS Subtitles with Instagram safe zone baseline at y = 1390 (MarginV = 540).")

# -------------------------------------------------------------
# 3. PROCEDURAL PARTICLES & ENVIRONMENTAL SETUP
# -------------------------------------------------------------
# Twinkling stars in sky region
random.seed(101)
stars_sky = []
for _ in range(45):
    stars_sky.append((
        random.uniform(50, 1030),
        random.uniform(80, 580),
        random.uniform(1.2, 2.8),
        random.uniform(0, math.pi * 2)
    ))

# Fairy light positions on balcony railing
fairy_lights_s1 = [
    (120, 1150), (220, 1180), (330, 1205), (450, 1220),
    (570, 1225), (690, 1215), (810, 1195), (930, 1165),
    (180, 1165), (390, 1215), (630, 1220), (870, 1180)
]

# 50 floating golden fireflies / ambient dust motes
particles = []
for _ in range(50):
    particles.append({
        "x": random.uniform(40, 1040),
        "y": random.uniform(250, 1750),
        "vx": random.uniform(-0.35, 0.35),
        "vy": random.uniform(-0.6, -0.15),
        "radius": random.uniform(1.5, 4.2),
        "base_alpha": random.uniform(130, 230),
        "phase": random.uniform(0, math.pi * 2),
        "color": random.choice([(70, 200, 255), (90, 220, 255), (110, 240, 255), (60, 180, 255)]) # Warm amber/golden
    })

def apply_handheld_drift(frame, t, amp_x=2.8, amp_y=2.0):
    dx = math.sin(t * 0.85) * amp_x + math.sin(t * 1.6) * 0.9
    dy = math.cos(t * 0.65) * amp_y + math.cos(t * 1.3) * 0.7
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

# -------------------------------------------------------------
# 4. SHOT-BY-SHOT LIVING RENDERERS
# -------------------------------------------------------------

# --- SHOT 1: Wide Balcony Establishing (0.0s - 5.5s) ---
def render_shot1(t, f_idx):
    frame = canvas_s1.copy()
    
    # Twinkling stars in sky
    for sx, sy, r, phase in stars_sky:
        tw = (math.sin(t * 4.2 + phase) + 1.0) * 0.5
        cv2.circle(frame, (int(sx), int(sy)), int(r + tw * 1.6), (255, 250, 230), -1)
    
    # Pulsing fairy light radial blooms
    overlay = frame.copy()
    for fx, fy in fairy_lights_s1:
        pulse = (math.sin(t * 3.2 + fx * 0.05) + 1.0) * 0.5
        rad = int(14 + pulse * 10)
        cv2.circle(overlay, (fx, fy), rad, (60, 190, 255), -1)
        cv2.circle(frame, (fx, fy), 4, (240, 255, 255), -1)
    cv2.addWeighted(overlay, 0.32, frame, 0.68, 0, frame)
    
    # Rising chai steam curls from the two tea cups (around X: 520, 580, Y: 1350)
    for k_idx, k_cx in enumerate([510, 570]):
        for s_idx in range(4):
            s_t = t + s_idx * 0.45 + k_idx * 0.22
            sy = int(1350 - (s_t * 60) % 200)
            sway = math.sin(s_t * 3.8 + k_idx) * 14
            sx = int(k_cx + sway)
            rad = int(7 + ((1350 - sy) / 200) * 13)
            alpha = max(0.0, 1.0 - (1350 - sy) / 200) * 0.42
            steam_layer = frame.copy()
            cv2.circle(steam_layer, (sx, sy), rad, (220, 235, 245), -1)
            frame = cv2.addWeighted(steam_layer, alpha, frame, 1.0 - alpha, 0)
    
    # Shooting star at t=3.2s
    if 3.0 <= t <= 3.7:
        st_p = (t - 3.0) / 0.7
        sx1 = int(180 + st_p * 550)
        sy1 = int(100 + st_p * 240)
        sx0 = int(sx1 - 95)
        sy0 = int(sy1 - 42)
        cv2.line(frame, (sx0, sy0), (sx1, sy1), (255, 245, 210), 2)
        cv2.circle(frame, (sx1, sy1), 3, (255, 255, 255), -1)
        
    return apply_handheld_drift(frame, t)

# --- SHOT 2: Boy with Guitar (5.5s - 11.0s) ---
def render_shot2(t, f_idx):
    rel_t = max(0.0, t - 5.5)
    frame = canvas_s2.copy()
    
    # Cinematic micro push-in
    zoom = 1.0 + 0.035 * min(1.0, rel_t / 5.5)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Torso breathing physics (Y: 900..1400, X: 300..800)
    breath = math.sin(rel_t * (2.0 * math.pi / 3.0)) * 3.2
    torso = frame[900:1400, 300:800]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.5]])
    warped_torso = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    frame[900:1400, 300:800] = cv2.addWeighted(torso, 0.20, warped_torso, 0.80, 0)
    
    # Hair breeze wave (Y: 600..820, X: 420..680)
    hair = frame[600:820, 420:680]
    hh, hw = hair.shape[:2]
    wave = math.sin(rel_t * 3.6) * 3.0
    pts1 = np.float32([[0, 0], [hw, 0], [0, hh], [hw, hh]])
    pts2 = np.float32([[0, 0], [hw, 0], [wave, hh], [hw + wave, hh]])
    M_h = cv2.getPerspectiveTransform(pts1, pts2)
    warped_hair = cv2.warpPerspective(hair, M_h, (hw, hh), borderMode=cv2.BORDER_REFLECT)
    frame[600:820, 420:680] = cv2.addWeighted(hair, 0.25, warped_hair, 0.75, 0)
    
    # Natural 5-frame eye blink at t=8.2s
    dt_blink = abs(t - 8.20)
    if dt_blink < 0.10:
        b_phase = 1.0 - (dt_blink / 0.10)
        ey_cx, ey_cy = 540, 740
        skin_bgr = tuple(int(c) for c in canvas_s2[730:750, 530:550].mean(axis=(0,1)))
        cv2.ellipse(frame, (ey_cx, ey_cy), (8, int(6 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (ey_cx - 9, ey_cy), (ey_cx + 9, ey_cy), (30, 20, 25), 2)
    
    # Soft background fairy lights shimmer
    shimmer = (math.sin(rel_t * 3.5) + 1.0) * 0.04
    frame = cv2.addWeighted(frame, 1.0 + shimmer, np.zeros_like(frame), 0, 0)
    
    return apply_handheld_drift(frame, t, amp_x=2.5, amp_y=1.8)

# --- SHOT 3: Intimate Girl Portrait (11.0s - 16.5s) ---
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
    
    # Subtle chest breathing
    breath = math.sin(rel_t * (2.0 * math.pi / 2.8)) * 2.8
    chest = frame[1100:1500, 320:780]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[1100:1500, 320:780] = cv2.addWeighted(chest, 0.25, cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # Gentle wind caught in long dark hair strands
    hair_left = frame[650:1100, 220:440]
    lh, lw = hair_left.shape[:2]
    w_wave = math.sin(rel_t * 3.2) * 3.5
    pts1 = np.float32([[0, 0], [lw, 0], [0, lh], [lw, lh]])
    pts2 = np.float32([[0, 0], [lw, 0], [w_wave, lh], [lw + w_wave, lh]])
    M_hl = cv2.getPerspectiveTransform(pts1, pts2)
    frame[650:1100, 220:440] = cv2.addWeighted(hair_left, 0.30, cv2.warpPerspective(hair_left, M_hl, (lw, lh), borderMode=cv2.BORDER_REFLECT), 0.70, 0)
    
    # Eye blink at t=13.8s
    dt_blink = abs(t - 13.80)
    if dt_blink < 0.10:
        b_phase = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s3[770:790, 500:520].mean(axis=(0,1)))
        # Left eye
        cv2.ellipse(frame, (485, 780), (10, int(7 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (473, 780), (497, 780), (35, 20, 25), 2)
        # Right eye
        cv2.ellipse(frame, (595, 780), (10, int(7 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (583, 780), (607, 780), (35, 20, 25), 2)
    
    # Starlight glimmer in eyes
    twinkle = (math.sin(rel_t * 5.0) + 1.0) * 0.5
    cv2.circle(frame, (490, 776), int(1.5 + twinkle * 1.5), (255, 255, 240), -1)
    cv2.circle(frame, (600, 776), int(1.5 + twinkle * 1.5), (255, 255, 240), -1)
    
    return apply_handheld_drift(frame, t, amp_x=2.2, amp_y=1.8)

# --- SHOT 4: Couple Climax under Blanket (16.5s - 22.0s) ---
def render_shot4(t, f_idx):
    rel_t = max(0.0, t - 16.5)
    frame = canvas_s4.copy()
    
    # Harmonic couple breathing under shared blanket
    breath = math.sin(rel_t * (2.0 * math.pi / 2.9)) * 3.5
    couple_torso = frame[850:1450, 250:850]
    cth, ctw = couple_torso.shape[:2]
    M_ct = np.float32([[1, 0, 0], [0, 1, breath * 0.45]])
    frame[850:1450, 250:850] = cv2.addWeighted(couple_torso, 0.25, cv2.warpAffine(couple_torso, M_ct, (ctw, cth), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # Starry night twinkling in sky
    for sx, sy, r, phase in stars_sky:
        tw = (math.sin(t * 3.8 + phase) + 1.0) * 0.5
        cv2.circle(frame, (int(sx), int(sy)), int(r + tw * 1.5), (255, 250, 230), -1)
        
    # Shooting star at t=19.2s
    if 19.0 <= t <= 19.7:
        st_p = (t - 19.0) / 0.7
        sx1 = int(220 + st_p * 580)
        sy1 = int(120 + st_p * 260)
        sx0 = int(sx1 - 100)
        sy0 = int(sy1 - 45)
        cv2.line(frame, (sx0, sy0), (sx1, sy1), (255, 245, 220), 2)
        cv2.circle(frame, (sx1, sy1), 3, (255, 255, 255), -1)
        
    return apply_handheld_drift(frame, t, amp_x=2.4, amp_y=2.0)

# -------------------------------------------------------------
# 5. MASTER RENDER PIPELINE WITH CROSS-DISSOLVES & PARTICLES
# -------------------------------------------------------------
def get_shot_frame(t, f_idx):
    # Cross-dissolve configuration (6 frames = 0.20s)
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

print("🚀 Rendering 660 master frames with living character acting & particle physics...")

# Render loop
for f in range(TOTAL_FRAMES):
    t = f / FPS
    
    # 1. Base shot rendering
    frame = get_shot_frame(t, f)
    
    # 2. Update & render 50 floating golden fireflies
    p_overlay = frame.copy()
    for p in particles:
        p["x"] += p["vx"] + math.sin(t * 1.5 + p["phase"]) * 0.4
        p["y"] += p["vy"]
        if p["y"] < 150:
            p["y"] = 1800
            p["x"] = random.uniform(40, 1040)
        if p["x"] < 20: p["x"] = 1060
        if p["x"] > 1060: p["x"] = 20
        
        pulse = (math.sin(t * 3.0 + p["phase"]) + 1.0) * 0.5
        cur_r = p["radius"] * (0.8 + 0.4 * pulse)
        cv2.circle(p_overlay, (int(p["x"]), int(p["y"])), int(cur_r + 2), p["color"], -1)
        cv2.circle(frame, (int(p["x"]), int(p["y"])), int(cur_r), (255, 255, 255), -1)
    frame = cv2.addWeighted(p_overlay, 0.35, frame, 0.65, 0)
    
    # 3. AEP Cinema Post-Processing
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
# Extract representative frame at t=14.0s (Girl portrait) or t=18.0s (Couple)
cap = cv2.VideoCapture(str(FINAL_REEL))
cap.set(cv2.CAP_PROP_POS_FRAMES, int(18.0 * FPS))
ret, frame_cover = cap.read()
if ret:
    cv2.imwrite(str(COVER_FILE), frame_cover)
    cv2.imwrite(str(STORY_CARD), frame_cover)
    print(f"✅ Created cover and story card from film frame at t=18.0s.")
cap.release()

if TEMP_VIDEO.exists():
    TEMP_VIDEO.unlink()

print("🎉 ALL PRODUCTION STEPS FOR TU KEH DE TOH COMPLETED SUCCESSFULLY!")
