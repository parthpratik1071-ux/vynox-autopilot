#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Alag Aasmaan" - Anuv Jain
Features:
- 4 Distinct Cinematic Shots timed to lyrics:
  1. Shot 1 (0.0s - 6.0s): Girl on rooftop under moon (Breathing, 5-frame eye blink, hair sway, twinkling stars, fairy lights)
  2. Shot 2 (6.0s - 12.0s): Boy miles away under same sky (Push-in, torso breathing, eye blink, city highway bokeh)
  3. Shot 3 (12.0s - 18.0s): Celestial stardust connection (Shooting star, cosmic glow, rotational drift)
  4. Shot 4 (18.0s - 24.0s): Emotional close-up (Dual eye blink, smiling micro-acting, golden starlight rim lighting, fireflies)
- Smooth 6-frame cinematic cross-dissolves
- Lato-Bold synced subtitles in Instagram safe zone (MarginV=540)
"""

import math
import random
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

PROJECT_DIR = Path("projects/series-romantic-animations/05-alag-aasmaan-anuv-jain")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "alag_clip.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_alag_aasmaan_romantic.mp4"
SUBTITLE_ASS = OUT_DIR / "alag_subtitles.ass"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 24.00
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing Alag Aasmaan Living 2D Anime MV ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# 1. LOAD & PREPARE 4 CANVASES (1080x1920) in NATIVE BGR
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

# 2. WRITE MASTER ASS SUBTITLES
ass_template = """[Script Info]
Title: Alag Aasmaan - Living 2D Cinematic MV
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: __WIDTH__
PlayResY: __HEIGHT__

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TitleBadge,Lato,38,&H00FFFFFF,&H000000FF,&H90000000,&H60000000,-1,0,0,0,100,100,2,0,1,2.0,1.0,8,60,60,180,1
Style: LyricGold,Lato,60,&H00FFFFFF,&H000000FF,&H90050810,&H80000000,-1,0,0,0,100,100,1,0,1,3.5,2.0,2,80,80,540,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:04.80,TitleBadge,,0,0,180,,{\\fad(350,450)}ANUV JAIN  |  {\\c&H003CE0FF&}ALAG AASMAAN
Dialogue: 1,0:00:00.50,0:00:03.80,LyricGold,,0,0,540,,{\\fad(200,200)}Dil ko mere {\\c&H003CE0FF&}ye hai pata{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:03.80,0:00:07.50,LyricGold,,0,0,540,,{\\fad(200,200)}Ke milon ka ye {\\c&H00FFB040&}faasla hai{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:07.50,0:00:11.50,LyricGold,,0,0,540,,{\\fad(200,200)}{\\c&H003CE0FF&}Alag aasmaan bhi hai{\\c&H00FFFFFF&} toh kya?
Dialogue: 1,0:00:11.50,0:00:15.00,LyricGold,,0,0,540,,{\\fad(200,200)}Yeh dil {\\c&H0055EEFF&}na maane{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:15.00,0:00:19.50,LyricGold,,0,0,540,,{\\fad(200,200)}Yeh gaadiyon ki aisi daudh sa...
Dialogue: 1,0:00:19.50,0:00:23.80,LyricGold,,0,0,540,,{\\fad(200,450)}{\\c&H00FFD700&}Tera bhi dil{\\c&H00FFFFFF&} daudhta hai...
"""
ass_content = ass_template.replace("__WIDTH__", str(WIDTH)).replace("__HEIGHT__", str(HEIGHT))
with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
    f.write(ass_content)

# 3. PROCEDURAL PARTICLES & ENVIRONMENTAL DETECTIONS
random.seed(77)
particles = []
for _ in range(45):
    particles.append({
        "x": random.uniform(50, 1030),
        "y": random.uniform(200, 1800),
        "vx": random.uniform(-0.4, 0.4),
        "vy": random.uniform(-0.6, -0.15),
        "radius": random.uniform(1.5, 4.0),
        "base_alpha": random.uniform(140, 240),
        "phase": random.uniform(0, math.pi * 2),
        "color": random.choice([(80, 210, 255), (100, 230, 255), (120, 240, 255), (70, 190, 255)]) # Warm amber/golden in BGR
    })

# Starfield & fairy lights in Shot 1
gray1 = cv2.cvtColor(canvas_s1[:, :, :3], cv2.COLOR_BGR2GRAY)
stars_s1 = []
for y in range(80, 500, 30):
    for x in range(60, 1020, 30):
        patch = gray1[y:y+15, x:x+15]
        if patch.max() > 180:
            stars_s1.append((x + 7, y + 7, random.uniform(1.2, 2.5), random.uniform(0, math.pi*2)))
if len(stars_s1) > 40:
    stars_s1 = stars_s1[:40]

fairy_lights = [
    (140, 830), (220, 845), (310, 860), (410, 875),
    (520, 885), (630, 890), (740, 905), (830, 925),
    (920, 940), (980, 960), (480, 820), (580, 835)
]

def apply_handheld_drift(frame, t, amp_x=2.8, amp_y=2.0):
    dx = math.sin(t * 0.75) * amp_x + math.sin(t * 1.4) * 0.8
    dy = math.cos(t * 0.55) * amp_y + math.cos(t * 1.1) * 0.6
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

# --- SHOT 1: Girl on rooftop under moon (0.0s - 6.0s) ---
def render_shot1(t, f_idx):
    frame = canvas_s1[:, :, :3].copy()
    
    # Torso breathing
    breath = math.sin(t * (2.0 * math.pi / 3.0)) * 3.0
    torso = frame[820:1150, 380:660]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.5]])
    warped_torso = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    frame[820:1150, 380:660] = cv2.addWeighted(frame[820:1150, 380:660], 0.15, warped_torso, 0.85, 0)
    
    # Hair breeze wave
    hair = frame[680:850, 430:570].copy()
    hh, hw = hair.shape[:2]
    wave = math.sin(t * 3.5) * 3.2
    pts1 = np.float32([[0, 0], [hw, 0], [0, hh], [hw, hh]])
    pts2 = np.float32([[0, 0], [hw, 0], [wave, hh], [hw + wave, hh]])
    M_h = cv2.getPerspectiveTransform(pts1, pts2)
    warped_hair = cv2.warpPerspective(hair, M_h, (hw, hh), borderMode=cv2.BORDER_REFLECT)
    frame[680:850, 430:570] = cv2.addWeighted(frame[680:850, 430:570], 0.25, warped_hair, 0.75, 0)
    
    # Eye blink at t=3.2s
    dt_blink = abs(t - 3.20)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s1[780:800, 480:500].mean(axis=(0,1)))
        cv2.ellipse(frame, (489, 783), (7, int(5 * b_p)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (481, 783), (497, 783), (35, 20, 25), 2)
        
    # Twinkling stars
    for sx, sy, r, phase in stars_s1:
        tw = (math.sin(t * 4.0 + phase) + 1.0) * 0.5
        cv2.circle(frame, (int(sx), int(sy)), int(r + tw * 1.5), (255, 250, 220), -1)
        
    # Fairy light bloom (warm amber in BGR)
    overlay = frame.copy()
    for fx, fy in fairy_lights:
        pulse = (math.sin(t * 3.0 + fx * 0.05) + 1.0) * 0.5
        rad = int(12 + pulse * 8)
        cv2.circle(overlay, (fx, fy), rad, (60, 190, 255), -1)
        cv2.circle(frame, (fx, fy), 4, (240, 255, 255), -1)
    cv2.addWeighted(overlay, 0.28, frame, 0.72, 0, frame)
    
    return apply_handheld_drift(frame, t)

# --- SHOT 2: Boy miles away under same sky (6.0s - 12.0s) ---
def render_shot2(t, f_idx):
    rel_t = max(0.0, t - 6.00)
    frame = canvas_s2[:, :, :3].copy()
    
    # Slow push-in
    zoom = 1.0 + 0.04 * min(1.0, rel_t / 6.0)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh))
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Breathing on boy
    breath = math.sin(rel_t * (2.0 * math.pi / 2.8)) * 3.2
    torso = frame[820:1180, 350:650]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[820:1180, 350:650] = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    
    # Hair breeze
    hair = frame[650:820, 360:540]
    hh, hw = hair.shape[:2]
    w_wave = math.sin(rel_t * 3.2) * 2.8
    M_hw = np.float32([[1, 0, w_wave], [0, 1, 0]])
    frame[650:820, 360:540] = cv2.addWeighted(frame[650:820, 360:540], 0.25, cv2.warpAffine(hair, M_hw, (hw, hh), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # Eye blink at t=9.2s (rel_t = 3.2s)
    dt_blink = abs(rel_t - 3.20)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s2[790:810, 430:450].mean(axis=(0,1)))
        cv2.ellipse(frame, (442, 802), (6, int(4 * b_p)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (435, 802), (449, 802), (30, 20, 25), 2)
        
    return apply_handheld_drift(frame, t)

# --- SHOT 3: Celestial stardust connection (12.0s - 18.0s) ---
def render_shot3(t, f_idx):
    rel_t = max(0.0, t - 12.00)
    frame = canvas_s3[:, :, :3].copy()
    
    rot_angle = math.sin(rel_t * 0.3) * 0.8
    M_rot = cv2.getRotationMatrix2D((WIDTH//2, HEIGHT//2), rot_angle, 1.02)
    frame = cv2.warpAffine(frame, M_rot, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
    
    nebula_pulse = (math.sin(rel_t * 2.5) + 1.0) * 0.08
    frame = cv2.addWeighted(frame, 1.0 + nebula_pulse, np.zeros_like(frame), 0, 0)
    
    # Shooting star at t=14.5s (rel_t = 2.5..3.2)
    if 2.3 <= rel_t <= 3.1:
        p_star = (rel_t - 2.3) / 0.8
        st_x1 = int(180 + p_star * 680)
        st_y1 = int(220 + p_star * 350)
        st_x0 = int(st_x1 - 140)
        st_y0 = int(st_y1 - 70)
        cv2.line(frame, (st_x0, st_y0), (st_x1, st_y1), (255, 230, 180), 3)
        cv2.circle(frame, (st_x1, st_y1), 5, (255, 255, 255), -1)
        
    return apply_handheld_drift(frame, t, amp_x=3.5, amp_y=2.8)

# --- SHOT 4: Emotional close-up (18.0s - 24.0s) ---
def render_shot4(t, f_idx):
    rel_t = max(0.0, t - 18.00)
    frame = canvas_s4[:, :, :3].copy()
    
    # Breathing on chest
    breath = math.sin(rel_t * (2.0 * math.pi / 2.7)) * 3.5
    chest = frame[900:1400, 200:880]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[900:1400, 200:880] = cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT)
    
    # Dual synchronized eye blink at t=20.8s (rel_t = 2.8s)
    dt_blink = abs(rel_t - 2.80)
    if dt_blink < 0.11:
        b_p = 1.0 - (dt_blink / 0.11)
        skin_bgr = tuple(int(c) for c in canvas_s4[630:650, 500:520].mean(axis=(0,1)))
        for ex, ey in [(467, 631), (571, 634)]:
            cv2.ellipse(frame, (ex, ey), (8, int(6 * b_p)), 0, 0, 360, skin_bgr, -1)
            cv2.line(frame, (ex - 10, ey), (ex + 10, ey), (35, 20, 25), 2)
            
    # Soft smile micro-expression
    smile_amp = (math.sin(rel_t * 1.5) + 1.0) * 0.5
    mouth = frame[670:740, 460:540]
    mh, mw = mouth.shape[:2]
    M_m = np.float32([[1, 0, 0], [0, 1, -smile_amp * 1.4]])
    frame[670:740, 460:540] = cv2.addWeighted(frame[670:740, 460:540], 0.35, cv2.warpAffine(mouth, M_m, (mw, mh), borderMode=cv2.BORDER_REFLECT), 0.65, 0)
    
    # Golden starlight rim lighting pulse
    golden_pulse = (math.sin(rel_t * 2.2) + 1.0) * 0.05
    frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, (10, 25, 45)), golden_pulse, 0)
    
    # Fade to black in last 0.5s
    if t >= 23.5:
        fade = max(0.0, 1.0 - (t - 23.5) / 0.5)
        frame = (frame * fade).astype(np.uint8)
        
    return apply_handheld_drift(frame, t)

# 4. MASTER RENDER PIPELINE
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "bgr24",
    "-r", str(FPS),
    "-i", "-",
    "-i", str(AUDIO_FILE),
    "-vf", f"subtitles={SUBTITLE_ASS}:fontsdir=/usr/share/fonts/truetype",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "17",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    str(FINAL_MP4)
]

print(f"🚀 Rendering Alag Aasmaan Living MV -> {FINAL_MP4.name}...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    
    if t < 6.00:
        base_frame = render_shot1(t, frame_idx)
        dt_cut = 6.00 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot2(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 12.00:
        base_frame = render_shot2(t, frame_idx)
        dt_cut = 12.00 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot3(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 18.00:
        base_frame = render_shot3(t, frame_idx)
        dt_cut = 18.00 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot4(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    else:
        base_frame = render_shot4(t, frame_idx)
        
    proc.stdin.write(base_frame.tobytes())
    
    if (frame_idx + 1) % 72 == 0 or frame_idx == TOTAL_FRAMES - 1:
        pct = int((frame_idx + 1) / TOTAL_FRAMES * 100)
        sys.stdout.write(f"\rRendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({pct}%) [{t:.1f}s]")
        sys.stdout.flush()

proc.stdin.close()
proc.wait()

print(f"\n🎉 Alag Aasmaan Living MV rendered: {FINAL_MP4}")

# Generate cover thumbnail
cover_path = OUT_DIR / "cover.jpg"
subprocess.run([
    "ffmpeg", "-y", "-ss", "17.5", "-i", str(FINAL_MP4),
    "-frames:v", "1", "-q:v", "2", str(cover_path)
], check=True)
print(f"📸 Cover thumbnail generated: {cover_path}")

