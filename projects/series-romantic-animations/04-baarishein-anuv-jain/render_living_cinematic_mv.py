#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Baarishein" - Anuv Jain
Features:
- 4 Distinct Cinematic Shots timed to lyrics:
  1. Shot 1 (0.0s - 5.5s): Girl by rainy window bench (Breathing, 5-frame eye blink, rain streaks, window droplets)
  2. Shot 2 (5.5s - 10.5s): Intimate close-up on wistful smile & rain (Micro-smile, eye blink, falling rain)
  3. Shot 3 (10.5s - 15.5s): Boy joins on bench (Breathing on couple, cozy coffee steam, rain atmosphere)
  4. Shot 4 (15.5s - 21.0s): Emotional close-up eye contact (Dual eye blink, smiling micro-acting, warm golden rim lights)
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

PROJECT_DIR = Path("projects/series-romantic-animations/04-baarishein-anuv-jain")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "baarishein_clip.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_baarishein_romantic.mp4"
SUBTITLE_ASS = OUT_DIR / "baarishein_subtitles.ass"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 21.00
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing Baarishein Living 2D Anime MV ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# 1. LOAD & PREPARE CANVASES
def load_canvas(path, zoom_crop=False):
    img = Image.open(path).convert("RGBA")
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    if zoom_crop:
        scale *= 1.15
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    return np.array(resized.crop((ox, oy, ox + WIDTH, oy + HEIGHT)))

canvas_s1 = load_canvas(ASSETS_DIR / "scene-1.jpg")
canvas_s1_close = load_canvas(ASSETS_DIR / "scene-1.jpg", zoom_crop=True)
canvas_s2 = load_canvas(ASSETS_DIR / "scene-2.jpg")
canvas_s2_close = load_canvas(ASSETS_DIR / "scene-2.jpg", zoom_crop=True)

print("✅ Loaded all scene canvases.")

# 2. WRITE MASTER ASS SUBTITLES
ass_template = """[Script Info]
Title: Baarishein - Living 2D Cinematic MV
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
Dialogue: 0,0:00:00.50,0:00:04.80,TitleBadge,,0,0,180,,{\\fad(350,450)}ANUV JAIN  |  {\\c&H003CE0FF&}BAARISHEIN
Dialogue: 1,0:00:00.50,0:00:03.50,LyricGold,,0,0,540,,{\\fad(200,200)}{\\c&H003CE0FF&}Tum sun zara,{\\c&H00FFFFFF&} mere paas aa...
Dialogue: 1,0:00:03.50,0:00:07.20,LyricGold,,0,0,540,,{\\fad(200,200)}Ab baithe hain hum bhi {\\c&H003CE0FF&}yahan{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:07.20,0:00:13.00,LyricGold,,0,0,540,,{\\fad(200,200)}Dil ke darmiyan {\\c&H003CE0FF&}baarishein hain{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:13.00,0:00:19.50,LyricGold,,0,0,540,,{\\fad(200,300)}Teri hi baaton pe maine\\N{\\c&H00FFB040&}saja li hai duniya yahan{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:19.50,0:00:20.80,LyricGold,,0,0,540,,{\\fad(200,350)}{\\c&H00FFD700&}Dil ke darmiyan baarishein{\\c&H00FFFFFF&}...
"""
ass_content = ass_template.replace("__WIDTH__", str(WIDTH)).replace("__HEIGHT__", str(HEIGHT))
with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
    f.write(ass_content)

# 3. PROCEDURAL RAIN PARTICLES
random.seed(88)
rain_streaks = []
for _ in range(70):
    rain_streaks.append({
        "x": random.uniform(-100, 1180),
        "y": random.uniform(-200, 1920),
        "speed": random.uniform(22.0, 34.0),
        "length": random.uniform(20.0, 45.0),
        "alpha": random.uniform(0.25, 0.65),
        "thickness": random.choice([1, 2])
    })

def apply_rain(frame):
    overlay = frame.copy()
    for drop in rain_streaks:
        drop["y"] += drop["speed"]
        drop["x"] += drop["speed"] * 0.22 # slight diagonal slant
        if drop["y"] > 1920:
            drop["y"] = random.uniform(-200, 0)
            drop["x"] = random.uniform(-100, 1180)
        x1, y1 = int(drop["x"]), int(drop["y"])
        x2, y2 = int(x1 + drop["length"] * 0.22), int(y1 + drop["length"])
        cv2.line(overlay, (x1, y1), (x2, y2), (220, 230, 245), drop["thickness"])
    return cv2.addWeighted(overlay, 0.40, frame, 0.60, 0)

def apply_handheld_drift(frame, t, amp_x=2.5, amp_y=1.8):
    dx = math.sin(t * 0.75) * amp_x + math.sin(t * 1.4) * 0.7
    dy = math.cos(t * 0.55) * amp_y + math.cos(t * 1.1) * 0.5
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

# --- SHOT 1: Girl by rain window (0.0s - 5.5s) ---
def render_shot1(t, f_idx):
    frame = canvas_s1[:, :, :3].copy()
    
    # Torso breathing physics
    breath = math.sin(t * (2.0 * math.pi / 3.0)) * 3.2
    torso = frame[800:1250, 350:700]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.45]])
    frame[800:1250, 350:700] = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    
    # Eye blink at t=2.6s
    dt_blink = abs(t - 2.60)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        cv2.ellipse(frame, (510, 750), (7, int(5 * b_p)), 0, 0, 360, (190, 195, 220), -1)
        cv2.line(frame, (502, 750), (518, 750), (45, 30, 35), 2)
        
    # Cozy warm indoor ambient light pulse
    warmth = (math.sin(t * 2.0) + 1.0) * 0.04
    frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, (20, 35, 55)), warmth, 0)
    
    frame = apply_rain(frame)
    return apply_handheld_drift(frame, t)

# --- SHOT 2: Intimate close-up on wistful smile & rain (5.5s - 10.5s) ---
def render_shot2(t, f_idx):
    rel_t = max(0.0, t - 5.50)
    frame = canvas_s1_close[:, :, :3].copy()
    
    # Breathing on chest
    breath = math.sin(rel_t * (2.0 * math.pi / 2.8)) * 3.0
    chest = frame[850:1300, 250:850]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[850:1300, 250:850] = cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT)
    
    # Eye blink at t=8.0s (rel_t = 2.5s)
    dt_blink = abs(rel_t - 2.50)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        cv2.ellipse(frame, (530, 710), (8, int(6 * b_p)), 0, 0, 360, (195, 200, 225), -1)
        cv2.line(frame, (521, 710), (539, 710), (45, 30, 35), 2)
        
    # Micro-smile movement
    smile_amp = (math.sin(rel_t * 1.8) + 1.0) * 0.5
    mouth = frame[780:850, 480:580]
    mh, mw = mouth.shape[:2]
    M_m = np.float32([[1, 0, 0], [0, 1, -smile_amp * 1.5]])
    frame[780:850, 480:580] = cv2.addWeighted(frame[780:850, 480:580], 0.35, cv2.warpAffine(mouth, M_m, (mw, mh), borderMode=cv2.BORDER_REFLECT), 0.65, 0)
    
    frame = apply_rain(frame)
    return apply_handheld_drift(frame, t)

# --- SHOT 3: Boy joins on bench, cozy atmosphere (10.5s - 15.5s) ---
def render_shot3(t, f_idx):
    rel_t = max(0.0, t - 10.50)
    frame = canvas_s2[:, :, :3].copy()
    
    # Breathing on couple
    breath = math.sin(rel_t * (2.0 * math.pi / 2.7)) * 3.2
    torso = frame[800:1350, 200:900]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[800:1350, 200:900] = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    
    # Coffee steam rising
    steam_y = int(780 - (rel_t * 22) % 100)
    cv2.circle(frame, (520, steam_y), 7, (235, 240, 250), -1)
    
    # Eye blink at t=13.2s (rel_t = 2.7s)
    dt_blink = abs(rel_t - 2.70)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        cv2.ellipse(frame, (475, 750), (7, int(5 * b_p)), 0, 0, 360, (185, 190, 220), -1)
        cv2.line(frame, (467, 750), (483, 750), (40, 25, 30), 2)
        
    frame = apply_rain(frame)
    return apply_handheld_drift(frame, t)

# --- SHOT 4: Emotional close-up eye contact (15.5s - 21.0s) ---
def render_shot4(t, f_idx):
    rel_t = max(0.0, t - 15.50)
    frame = canvas_s2_close[:, :, :3].copy()
    
    # Breathing
    breath = math.sin(rel_t * (2.0 * math.pi / 2.7)) * 3.5
    chest = frame[900:1400, 200:880]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[900:1400, 200:880] = cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT)
    
    # Dual synchronized eye blink at t=17.8s (rel_t = 2.3s)
    dt_blink = abs(rel_t - 2.30)
    if dt_blink < 0.11:
        b_p = 1.0 - (dt_blink / 0.11)
        for ex, ey in [(465, 680), (575, 685)]:
            cv2.ellipse(frame, (ex, ey), (8, int(6 * b_p)), 0, 0, 360, (200, 195, 225), -1)
            cv2.line(frame, (ex - 10, ey), (ex + 10, ey), (40, 25, 35), 2)
            
    # Soft smile micro-expression
    smile_amp = (math.sin(rel_t * 1.5) + 1.0) * 0.5
    mouth = frame[750:820, 480:560]
    mh, mw = mouth.shape[:2]
    M_m = np.float32([[1, 0, 0], [0, 1, -smile_amp * 1.5]])
    frame[750:820, 480:560] = cv2.addWeighted(frame[750:820, 480:560], 0.35, cv2.warpAffine(mouth, M_m, (mw, mh), borderMode=cv2.BORDER_REFLECT), 0.65, 0)
    
    # Warm golden rim lighting
    golden_pulse = (math.sin(rel_t * 2.2) + 1.0) * 0.05
    frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, (15, 30, 55)), golden_pulse, 0)
    
    # Fade to black in last 0.5s
    if t >= 20.5:
        fade = max(0.0, 1.0 - (t - 20.5) / 0.5)
        frame = (frame * fade).astype(np.uint8)
        
    frame = apply_rain(frame)
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

print(f"🚀 Rendering Baarishein Living MV -> {FINAL_MP4.name}...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    
    if t < 5.50:
        base_frame = render_shot1(t, frame_idx)
        dt_cut = 5.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot2(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 10.50:
        base_frame = render_shot2(t, frame_idx)
        dt_cut = 10.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot3(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 15.50:
        base_frame = render_shot3(t, frame_idx)
        dt_cut = 15.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot4(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    else:
        base_frame = render_shot4(t, frame_idx)
        
    proc.stdin.write(base_frame.tobytes())
    
    if (frame_idx + 1) % 63 == 0 or frame_idx == TOTAL_FRAMES - 1:
        pct = int((frame_idx + 1) / TOTAL_FRAMES * 100)
        sys.stdout.write(f"\rRendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({pct}%) [{t:.1f}s]")
        sys.stdout.flush()

proc.stdin.close()
proc.wait()

print(f"\n🎉 Baarishein Living MV rendered: {FINAL_MP4}")

# Generate cover thumbnail
cover_path = OUT_DIR / "cover.jpg"
subprocess.run([
    "ffmpeg", "-y", "-ss", "16.5", "-i", str(FINAL_MP4),
    "-frames:v", "1", "-q:v", "2", str(cover_path)
], check=True)
print(f"📸 Cover thumbnail generated: {cover_path}")
