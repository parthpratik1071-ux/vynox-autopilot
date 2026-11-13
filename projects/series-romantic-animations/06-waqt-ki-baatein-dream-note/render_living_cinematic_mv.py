#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Waqt Ki Baatein" - Dream Note
Features:
- 4 Distinct Cinematic Shots timed to musical lyrics:
  1. Shot 1 (0.0s - 7.5s): Boy by train window at sunset (Train vibration micro-motion, breathing, golden light beam)
  2. Shot 2 (7.5s - 15.5s): Girl in autumn park (35 procedurally fluttering golden leaves, scarf sway, eye blink)
  3. Shot 3 (15.5s - 20.5s): Couple sharing warm scarf (Breathing, warm rising steam physics, soft eye blink)
  4. Shot 4 (20.5s - 25.0s): Emotional close-up (Dual eye blink, smiling micro-acting, golden sunset rim flare)
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

PROJECT_DIR = Path("projects/series-romantic-animations/06-waqt-ki-baatein-dream-note")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "waqt_clip.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_waqt_ki_baatein_romantic.mp4"
SUBTITLE_ASS = OUT_DIR / "waqt_subtitles.ass"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 25.00
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing Waqt Ki Baatein Living 2D Anime MV ({TOTAL_FRAMES} frames @ {FPS} fps)...")

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
Title: Waqt Ki Baatein - Living 2D Cinematic MV
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
Dialogue: 0,0:00:00.50,0:00:04.80,TitleBadge,,0,0,180,,{\\fad(350,450)}DREAM NOTE  |  {\\c&H003CE0FF&}WAQT KI BAATEIN
Dialogue: 1,0:00:02.50,0:00:05.80,LyricGold,,0,0,540,,{\\fad(200,200)}Maana dil {\\c&H003CE0FF&}dara-dara hai{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:05.80,0:00:09.80,LyricGold,,0,0,540,,{\\fad(200,200)}Toota ye {\\c&H003CE0FF&}zara-zara hai{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:09.80,0:00:15.50,LyricGold,,0,0,540,,{\\fad(200,200)}Dil ke is bawandar ko\\N{\\c&H00FFB040&}thehar jaane do{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:15.50,0:00:21.00,LyricGold,,0,0,540,,{\\fad(200,300)}{\\c&H003CE0FF&}Thehar jaane do{\\c&H00FFFFFF&}... {\\c&H0055EEFF&}ho oooo{\\c&H00FFFFFF&}...
Dialogue: 1,0:00:21.20,0:00:24.60,LyricGold,,0,0,540,,{\\fad(250,400)}{\\c&H00FFD700&}Waqt ki ye baatein hain{\\c&H00FFFFFF&}...
"""
ass_content = ass_template.replace("__WIDTH__", str(WIDTH)).replace("__HEIGHT__", str(HEIGHT))
with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
    f.write(ass_content)

# 3. PROCEDURAL PARTICLES & AUTUMN LEAVES
random.seed(101)
autumn_leaves = []
for _ in range(35):
    autumn_leaves.append({
        "x": random.uniform(20, 1060),
        "y": random.uniform(-100, 1900),
        "vx": random.uniform(0.8, 2.2),
        "vy": random.uniform(1.2, 2.8),
        "size": random.uniform(7.0, 16.0),
        "angle": random.uniform(0, 360),
        "spin": random.uniform(-2.5, 2.5),
        "color": random.choice([(25, 120, 210), (35, 150, 225), (40, 95, 190), (30, 140, 240)]) # Golden/amber BGR
    })

particles = []
for _ in range(40):
    particles.append({
        "x": random.uniform(40, 1040),
        "y": random.uniform(200, 1800),
        "vx": random.uniform(-0.3, 0.3),
        "vy": random.uniform(-0.6, -0.1),
        "radius": random.uniform(1.5, 3.5),
        "base_alpha": random.uniform(140, 240),
        "phase": random.uniform(0, math.pi * 2),
        "color": (180, 230, 255) # Warm sunlit dust
    })

def apply_handheld_drift(frame, t, amp_x=2.8, amp_y=2.0):
    dx = math.sin(t * 0.75) * amp_x + math.sin(t * 1.4) * 0.8
    dy = math.cos(t * 0.55) * amp_y + math.cos(t * 1.1) * 0.6
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

# --- SHOT 1: Boy by train window (0.0s - 7.5s) ---
def render_shot1(t, f_idx):
    frame = canvas_s1[:, :, :3].copy()
    
    # Train rhythmic vibration micro-motion
    vibe_y = math.sin(t * 22.0) * 0.7
    M_v = np.float32([[1, 0, 0], [0, 1, vibe_y]])
    frame = cv2.warpAffine(frame, M_v, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
    
    # Torso breathing physics (Y: 800..1200, X: 300..700)
    breath = math.sin(t * (2.0 * math.pi / 3.0)) * 3.2
    torso = frame[800:1200, 300:700]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.45]])
    frame[800:1200, 300:700] = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    
    # Sunset beam warmth through window
    sun_pulse = (math.sin(t * 2.0) + 1.0) * 0.06
    frame = cv2.addWeighted(frame, 1.0 + sun_pulse, np.zeros_like(frame), 0, 0)
    
    # Eye blink at t=4.2s
    dt_blink = abs(t - 4.20)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s1[765:785, 480:500].mean(axis=(0,1)))
        cv2.ellipse(frame, (490, 775), (7, int(5 * b_p)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (482, 775), (498, 775), (35, 25, 30), 2)
        
    return apply_handheld_drift(frame, t)

# --- SHOT 2: Girl walking in autumn park (7.5s - 15.5s) ---
def render_shot2(t, f_idx):
    rel_t = max(0.0, t - 7.50)
    frame = canvas_s2[:, :, :3].copy()
    
    # Slow cinematic camera tracking drift
    zoom = 1.0 + 0.04 * min(1.0, rel_t / 8.0)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh))
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Scarf and coat breeze displacement (Y: 750..1300, X: 350..750)
    wind = math.sin(rel_t * 3.4) * 3.2
    coat = frame[750:1300, 350:750]
    ch, cw = coat.shape[:2]
    M_w = np.float32([[1, 0, wind * 0.6], [0, 1, 0]])
    frame[750:1300, 350:750] = cv2.warpAffine(coat, M_w, (cw, ch), borderMode=cv2.BORDER_REFLECT)
    
    # Eye blink at t=11.2s (rel_t = 3.7s)
    dt_blink = abs(rel_t - 3.70)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s2[745:765, 500:520].mean(axis=(0,1)))
        cv2.ellipse(frame, (510, 755), (7, int(5 * b_p)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (502, 755), (518, 755), (40, 25, 35), 2)
        
    # Falling golden autumn leaves
    for leaf in autumn_leaves:
        leaf["x"] += leaf["vx"] + math.sin(rel_t * 2.0 + leaf["angle"]) * 0.6
        leaf["y"] += leaf["vy"]
        leaf["angle"] += leaf["spin"]
        if leaf["y"] > 1920:
            leaf["y"] = -50
            leaf["x"] = random.uniform(20, 1060)
        # Draw small rotated leaf
        lx, ly = int(leaf["x"]), int(leaf["y"])
        if 0 <= lx < WIDTH and 0 <= ly < HEIGHT:
            cv2.ellipse(frame, (lx, ly), (int(leaf["size"]), int(leaf["size"]*0.5)), int(leaf["angle"]), 0, 360, leaf["color"], -1)
            
    return apply_handheld_drift(frame, t)

# --- SHOT 3: Couple sharing warm scarf on bench (15.5s - 20.5s) ---
def render_shot3(t, f_idx):
    rel_t = max(0.0, t - 15.50)
    frame = canvas_s3[:, :, :3].copy()
    
    # Torso breathing physics
    breath = math.sin(rel_t * (2.0 * math.pi / 2.8)) * 3.0
    torso = frame[800:1300, 250:850]
    th, tw = torso.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[800:1300, 250:850] = cv2.warpAffine(torso, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    
    # Warm steam rising from coffee / breath
    steam_y = int(820 - (rel_t * 25) % 120)
    cv2.circle(frame, (480, steam_y), 8, (230, 240, 250), -1)
    
    # Eye blink at t=18.0s (rel_t = 2.5s)
    dt_blink = abs(rel_t - 2.50)
    if dt_blink < 0.10:
        b_p = 1.0 - (dt_blink / 0.10)
        skin_bgr = tuple(int(c) for c in canvas_s3[755:775, 525:545].mean(axis=(0,1)))
        cv2.ellipse(frame, (535, 765), (7, int(5 * b_p)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (527, 765), (543, 765), (45, 30, 35), 2)
        
    return apply_handheld_drift(frame, t)

# --- SHOT 4: Emotional close-up looking into golden future (20.5s - 25.0s) ---
def render_shot4(t, f_idx):
    rel_t = max(0.0, t - 20.50)
    frame = canvas_s4[:, :, :3].copy()
    
    # Breathing on chest
    breath = math.sin(rel_t * (2.0 * math.pi / 2.7)) * 3.5
    chest = frame[900:1400, 200:880]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[900:1400, 200:880] = cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT)
    
    # Dual synchronized eye blink at t=22.4s (rel_t = 1.9s)
    dt_blink = abs(rel_t - 1.90)
    if dt_blink < 0.11:
        b_p = 1.0 - (dt_blink / 0.11)
        skin_bgr = tuple(int(c) for c in canvas_s4[620:640, 500:520].mean(axis=(0,1)))
        for ex, ey in [(465, 630), (570, 635)]:
            cv2.ellipse(frame, (ex, ey), (8, int(6 * b_p)), 0, 0, 360, skin_bgr, -1)
            cv2.line(frame, (ex - 10, ey), (ex + 10, ey), (40, 25, 35), 2)
            
    # Soft smile micro-expression
    smile_amp = (math.sin(rel_t * 1.6) + 1.0) * 0.5
    mouth = frame[670:740, 460:540]
    mh, mw = mouth.shape[:2]
    M_m = np.float32([[1, 0, 0], [0, 1, -smile_amp * 1.5]])
    warped_mouth = cv2.warpAffine(mouth, M_m, (mw, mh), borderMode=cv2.BORDER_REFLECT)
    frame[670:740, 460:540] = cv2.addWeighted(frame[670:740, 460:540], 0.35, warped_mouth, 0.65, 0)
    
    # Golden sunset rim flare pulse
    golden_flare = (math.sin(rel_t * 2.2) + 1.0) * 0.06
    frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, (15, 35, 65)), golden_flare, 0)
    
    # Fade to black in last 0.5s
    if t >= 24.5:
        fade = max(0.0, 1.0 - (t - 24.5) / 0.5)
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

print(f"🚀 Rendering Waqt Ki Baatein Living MV -> {FINAL_MP4.name}...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    
    if t < 7.50:
        base_frame = render_shot1(t, frame_idx)
        dt_cut = 7.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot2(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 15.50:
        base_frame = render_shot2(t, frame_idx)
        dt_cut = 15.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot3(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 20.50:
        base_frame = render_shot3(t, frame_idx)
        dt_cut = 20.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot4(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    else:
        base_frame = render_shot4(t, frame_idx)
        
    proc.stdin.write(base_frame.tobytes())
    
    if (frame_idx + 1) % 75 == 0 or frame_idx == TOTAL_FRAMES - 1:
        pct = int((frame_idx + 1) / TOTAL_FRAMES * 100)
        sys.stdout.write(f"\rRendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({pct}%) [{t:.1f}s]")
        sys.stdout.flush()

proc.stdin.close()
proc.wait()

print(f"\n🎉 Waqt Ki Baatein Living MV rendered: {FINAL_MP4}")

# Generate cover thumbnail
cover_path = OUT_DIR / "cover.jpg"
subprocess.run([
    "ffmpeg", "-y", "-ss", "18.5", "-i", str(FINAL_MP4),
    "-frames:v", "1", "-q:v", "2", str(cover_path)
], check=True)
print(f"📸 Cover thumbnail generated: {cover_path}")

