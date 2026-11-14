#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Samjho Na" - Aditya Rikhari
Features:
- 4 Distinct Cinematic Shots timed to musical beats:
  1. Shot 1 (0.0s - 5.2s): Wide Establishing Rooftop Scene (Breathing, 5-frame eye blink, hair sway, 40 twinkling stars, fairy lights)
  2. Shot 2 (5.2s - 10.0s): Medium Shot of Boy Looking at City (Torso breathing, eye blink, hair wind, city bokeh shimmer)
  3. Shot 3 (10.0s - 14.8s): Celestial Stardust Connection (Swirling nebula particle vortex, shooting star, cosmic glow)
  4. Shot 4 (14.8s - 20.5s): Emotional Climax Close-up (Dual-eye synchronized blink, smiling micro-acting, golden rim lighting, floating fireflies)
- Smooth 6-frame cinematic cross-dissolve transitions between shots
- Handheld camera micro-drift on every shot
- Synchronized ASS Subtitles in Instagram safe zone (MarginV=540)
"""

import math
import random
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJECT_DIR = Path("projects/series-romantic-animations/08-samjho-na-proper-animation")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "samjho_na_clip.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_samjho_na_animation.mp4"
SUBTITLE_ASS = OUT_DIR / "samjho_na_subtitles.ass"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 20.50
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing 4-Shot Living 2D Anime MV Engine ({TOTAL_FRAMES} frames @ {FPS} fps)...")

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
# 2. WRITE MASTER ASS SUBTITLES (Lato-Bold, MarginV=540)
# -------------------------------------------------------------
ass_template = """[Script Info]
Title: Samjho Na - Cinematic Living 2D MV
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
Dialogue: 0,0:00:00.60,0:00:04.80,TitleBadge,,0,0,180,,{\\fad(400,600)}ADITYA RIKHARI  |  {\\c&H003CE0FF&}SAMJHO NA
Dialogue: 1,0:00:00.60,0:00:05.10,LyricGold,,0,0,540,,{\\fad(250,200)}Jaanan, {\\c&H003CE0FF&}samjho na{\\c&H00FFFFFF&}, dil kehta hai...
Dialogue: 1,0:00:05.20,0:00:09.90,LyricGold,,0,0,540,,{\\fad(200,200)}Teri {\\c&H00FFB040&}galiyon mein hi{\\c&H00FFFFFF&} rehta hai...
Dialogue: 1,0:00:10.00,0:00:14.60,LyricGold,,0,0,540,,{\\fad(200,200)}Jaanan, {\\c&H003CE0FF&}samjho na{\\c&H00FFFFFF&}, dil kehta hai...
Dialogue: 1,0:00:14.80,0:00:20.10,LyricGold,,0,0,540,,{\\fad(200,400)}Teri {\\c&H003CE0FF&}baahon mein jeena hai{\\c&H00FFFFFF&}, marna hai {\\c&H0055EEFF&}ishq mein tere{\\c&H00FFFFFF&}...
"""
ass_content = ass_template.replace("__WIDTH__", str(WIDTH)).replace("__HEIGHT__", str(HEIGHT))

with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
    f.write(ass_content)

# -------------------------------------------------------------
# 3. PROCEDURAL PARTICLES & ENVIRONMENTAL DETECTIONS
# -------------------------------------------------------------
# Starfield in Shot 1 & Shot 3
gray1 = cv2.cvtColor(canvas_s1[:, :, :3], cv2.COLOR_BGR2GRAY)
stars_s1 = []
for y in range(80, 500, 30):
    for x in range(60, 1020, 30):
        patch = gray1[y:y+15, x:x+15]
        if patch.max() > 180:
            stars_s1.append((x + 7, y + 7, random.uniform(1.2, 2.5), random.uniform(0, math.pi*2)))
if len(stars_s1) > 40:
    stars_s1 = stars_s1[:40]

# Fairy lights in Shot 1
fairy_lights = [
    (140, 830), (220, 845), (310, 860), (410, 875),
    (520, 885), (630, 890), (740, 905), (830, 925),
    (920, 940), (980, 960), (480, 820), (580, 835)
]

# Floating motes/fireflies across scene
random.seed(42)
particles = []
for _ in range(50):
    particles.append({
        "x": random.uniform(50, 1030),
        "y": random.uniform(300, 1750),
        "vx": random.uniform(-0.4, 0.4),
        "vy": random.uniform(-0.6, -0.1),
        "radius": random.uniform(1.5, 4.0),
        "base_alpha": random.uniform(140, 240),
        "phase": random.uniform(0, math.pi * 2),
        "color": random.choice([(80, 210, 255), (100, 230, 255), (120, 240, 255), (70, 190, 255)]) # Warm amber/golden fireflies in BGR
    })

# -------------------------------------------------------------
# 4. SHOT-SPECIFIC FRAME RENDERERS
# -------------------------------------------------------------

def apply_handheld_drift(frame, t, amp_x=3.0, amp_y=2.2):
    dx = math.sin(t * 0.8) * amp_x + math.sin(t * 1.5) * 1.0
    dy = math.cos(t * 0.6) * amp_y + math.cos(t * 1.2) * 0.8
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

# --- SHOT 1: Wide Rooftop Scene (0.0s - 5.2s) ---
def render_shot1(t, f_idx):
    frame = canvas_s1[:, :, :3].copy()
    
    # Breathing physics on torso (Y: 820..1150)
    breath = math.sin(t * (2.0 * math.pi / 3.0)) * 3.0
    torso_region = frame[820:1150, 380:660]
    th, tw = torso_region.shape[:2]
    M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.5]])
    warped_torso = cv2.warpAffine(torso_region, M_b, (tw, th), borderMode=cv2.BORDER_REFLECT)
    frame[820:1150, 380:660] = cv2.addWeighted(frame[820:1150, 380:660], 0.15, warped_torso, 0.85, 0)
    
    # Hair breeze wave (Y: 680..850, X: 430..570)
    hair_region = frame[680:850, 430:570].copy()
    hh, hw = hair_region.shape[:2]
    wave = math.sin(t * 3.5) * 3.2
    pts1 = np.float32([[0, 0], [hw, 0], [0, hh], [hw, hh]])
    pts2 = np.float32([[0, 0], [hw, 0], [wave, hh], [hw + wave, hh]])
    M_h = cv2.getPerspectiveTransform(pts1, pts2)
    warped_hair = cv2.warpPerspective(hair_region, M_h, (hw, hh), borderMode=cv2.BORDER_REFLECT)
    frame[680:850, 430:570] = cv2.addWeighted(frame[680:850, 430:570], 0.25, warped_hair, 0.75, 0)
    
    # Eye blink at t=2.8s (frames 80..86)
    blink_center = 2.80
    dt_blink = abs(t - blink_center)
    if dt_blink < 0.10:
        b_phase = 1.0 - (dt_blink / 0.10)
        ey_cx, ey_cy = 489, 783
        skin_bgr = tuple(int(c) for c in canvas_s1[780:800, 480:500].mean(axis=(0,1)))
        cv2.ellipse(frame, (ey_cx, ey_cy), (7, int(5 * b_phase)), 0, 0, 360, skin_bgr, -1)
        cv2.line(frame, (ey_cx - 8, ey_cy), (ey_cx + 8, ey_cy), (35, 20, 25), 2)
    
    # Twinkling stars
    for sx, sy, r, phase in stars_s1:
        tw = (math.sin(t * 4.0 + phase) + 1.0) * 0.5
        cv2.circle(frame, (int(sx), int(sy)), int(r + tw * 1.5), (255, 250, 220), -1)
    
    # Fairy light radial bloom (warm golden amber in BGR)
    overlay = frame.copy()
    for fx, fy in fairy_lights:
        pulse = (math.sin(t * 3.0 + fx * 0.05) + 1.0) * 0.5
        rad = int(12 + pulse * 8)
        cv2.circle(overlay, (fx, fy), rad, (60, 190, 255), -1)
        cv2.circle(frame, (fx, fy), 4, (240, 255, 255), -1)
    cv2.addWeighted(overlay, 0.28, frame, 0.72, 0, frame)
    
    # Shooting star at t=4.2s (t=4.0..4.6)
    if 4.0 <= t <= 4.6:
        st_p = (t - 4.0) / 0.6
        sx1 = int(200 + st_p * 500)
        sy1 = int(120 + st_p * 220)
        sx0 = int(sx1 - 90)
        sy0 = int(sy1 - 40)
        cv2.line(frame, (sx0, sy0), (sx1, sy1), (255, 240, 200), 2)
        cv2.circle(frame, (sx1, sy1), 3, (255, 255, 255), -1)
        
    return apply_handheld_drift(frame, t)

# --- SHOT 2: Atmospheric Alleyway - Gali (5.2s - 10.0s) ---
def render_shot2(t, f_idx):
    rel_t = max(0.0, t - 5.20)
    frame = canvas_s2[:, :, :3].copy()
    
    # Slow cinematic push-in (zoom 1.0 to 1.04)
    zoom = 1.0 + 0.04 * min(1.0, rel_t / 4.8)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh))
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Breeze waving her dupatta / scarf
    scarf = frame[750:1050, 400:680]
    sh, sw = scarf.shape[:2]
    w_wave = math.sin(rel_t * 3.5) * 3.0
    M_s = np.float32([[1, 0, w_wave], [0, 1, 0]])
    frame[750:1050, 400:680] = cv2.addWeighted(scarf, 0.25, cv2.warpAffine(scarf, M_s, (sw, sh), borderMode=cv2.BORDER_REFLECT), 0.75, 0)
    
    # Ambient string lights shimmer in alleyway
    shimmer = (math.sin(rel_t * 3.8) + 1.0) * 0.03
    frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, (25, 50, 80)), shimmer, 0)
    
    return apply_handheld_drift(frame, t, amp_x=2.5, amp_y=2.0)

# --- SHOT 3: Steaming Chai Kulhads & Lyrics Notebook (10.0s - 14.8s) ---
def render_shot3(t, f_idx):
    rel_t = max(0.0, t - 10.00)
    frame = canvas_s3[:, :, :3].copy()
    
    # Slow cinematic push-in
    zoom = 1.0 + 0.03 * min(1.0, rel_t / 4.8)
    nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
    scaled = cv2.resize(frame, (nw, nh))
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()
    
    # Warm golden bokeh pulse in background
    bokeh_pulse = (math.sin(rel_t * 2.5) + 1.0) * 0.05
    frame = cv2.addWeighted(frame, 1.0 + bokeh_pulse, np.zeros_like(frame), 0, 0)
    
    # Rising steam curls from the two chai kulhads
    for k_idx, k_cx in enumerate([460, 620]):
        for s_idx in range(4):
            s_t = rel_t + s_idx * 0.45 + k_idx * 0.25
            sy = int(820 - (s_t * 55) % 180)
            sway = math.sin(s_t * 3.5 + k_idx) * 14
            sx = int(k_cx + sway)
            rad = int(8 + ((820 - sy) / 180) * 12)
            alpha = max(0.0, 1.0 - (820 - sy) / 180) * 0.45
            overlay = frame.copy()
            cv2.circle(overlay, (sx, sy), rad, (225, 235, 245), -1)
            frame = cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0)
            
    return apply_handheld_drift(frame, t, amp_x=2.5, amp_y=1.8)

# --- SHOT 4: Emotional Climax Close-up (14.8s - 20.5s) ---
def render_shot4(t, f_idx):
    rel_t = max(0.0, t - 14.80)
    frame = canvas_s4[:, :, :3].copy()
    
    # Breathing physics on shoulders/chest (Y: 900..1400)
    breath = math.sin(rel_t * (2.0 * math.pi / 2.7)) * 3.5
    chest = frame[900:1400, 200:880]
    ch, cw = chest.shape[:2]
    M_c = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
    frame[900:1400, 200:880] = cv2.warpAffine(chest, M_c, (cw, ch), borderMode=cv2.BORDER_REFLECT)
    
    # Dual synchronized gentle eye blink at t=17.2s (rel_t = 2.4s)
    dt_blink = abs(rel_t - 2.40)
    if dt_blink < 0.11:
        b_phase = 1.0 - (dt_blink / 0.11)
        skin_bgr = tuple(int(c) for c in canvas_s4[700:750, 450:520].mean(axis=(0,1)))
        for ex, ey in [(465, 710), (590, 715)]:
            cv2.ellipse(frame, (ex, ey), (8, int(6 * b_phase)), 0, 0, 360, skin_bgr, -1)
            cv2.line(frame, (ex - 10, ey), (ex + 10, ey), (35, 20, 25), 2)
            
    # Subtle smiling micro-movement (corners of lips relaxing upwards)
    smile_amp = (math.sin(rel_t * 1.5) + 1.0) * 0.5  # 0 to 1
    mouth_region = frame[750:830, 460:550]
    mh, mw = mouth_region.shape[:2]
    M_m = np.float32([[1, 0, 0], [0, 1, -smile_amp * 1.4]])
    warped_mouth = cv2.warpAffine(mouth_region, M_m, (mw, mh), borderMode=cv2.BORDER_REFLECT)
    frame[750:830, 460:550] = cv2.addWeighted(mouth_region, 0.35, warped_mouth, 0.65, 0)
    
    # Hair breeze wave (Y: 450..850, X: 250..800)
    hair_c = frame[450:850, 250:800]
    hh, hw = hair_c.shape[:2]
    h_wave = math.sin(rel_t * 3.0) * 3.0
    M_hw = np.float32([[1, 0, h_wave * 0.6], [0, 1, 0]])
    warped_hair_c = cv2.warpAffine(hair_c, M_hw, (hw, hh), borderMode=cv2.BORDER_REFLECT)
    frame[450:850, 250:800] = cv2.addWeighted(frame[450:850, 250:800], 0.25, warped_hair_c, 0.75, 0)
    
    # Warm golden rim lighting pulse on hair
    golden_pulse = (math.sin(rel_t * 2.2) + 1.0) * 0.05
    frame = cv2.addWeighted(frame, 1.0, np.full_like(frame, (10, 25, 45)), golden_pulse, 0)
    
    # Fade to black in last 0.5s
    if t >= 20.0:
        fade = max(0.0, 1.0 - (t - 20.0) / 0.5)
        frame = (frame * fade).astype(np.uint8)
        
    return apply_handheld_drift(frame, t, amp_x=2.2, amp_y=1.8)

# -------------------------------------------------------------
# 5. GLOBAL FLOATING MOTES / FIREFLIES OVERLAY
# -------------------------------------------------------------
def apply_particles(frame, t):
    overlay = frame.copy()
    for p in particles:
        p["x"] += p["vx"] + math.sin(t * 1.8 + p["phase"]) * 0.35
        p["y"] += p["vy"]
        if p["y"] < 100:
            p["y"] = 1880
            p["x"] = random.uniform(50, 1030)
        pulse = (math.sin(t * 3.5 + p["phase"]) + 1.0) * 0.5
        alpha = int(p["base_alpha"] * pulse)
        rad = max(1, int(p["radius"] * (0.8 + 0.4 * pulse)))
        cv2.circle(overlay, (int(p["x"]), int(p["y"])), rad, p["color"], -1)
    return cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

# -------------------------------------------------------------
# 6. MASTER RENDER PIPELINE WITH CROSS-DISSOLVE CUTS
# -------------------------------------------------------------
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "bgr24",
    "-r", str(FPS),
    "-i", "-",  # Video stream from stdin
    "-i", str(AUDIO_FILE),  # Master audio
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

print(f"🚀 Launching FFmpeg render process -> {FINAL_MP4.name}...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

# Shot boundaries in seconds and frames:
# Shot 1: 0.0s - 5.2s (frames 0 - 155)
# Shot 2: 5.2s - 10.0s (frames 156 - 299)
# Shot 3: 10.0s - 14.8s (frames 300 - 443)
# Shot 4: 14.8s - 20.5s (frames 444 - 614)
CUTS = [
    (5.20, 6),   # Shot 1 -> Shot 2: 6-frame cross-dissolve around 5.2s
    (10.00, 6),  # Shot 2 -> Shot 3: 6-frame cross-dissolve around 10.0s
    (14.80, 6),  # Shot 3 -> Shot 4: 6-frame cross-dissolve around 14.8s
]

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    
    # Determine base shot
    if t < 5.20:
        base_frame = render_shot1(t, frame_idx)
        # Check transition to Shot 2
        dt_cut = 5.20 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot2(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 10.00:
        base_frame = render_shot2(t, frame_idx)
        # Check transition to Shot 3
        dt_cut = 10.00 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot3(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 14.80:
        base_frame = render_shot3(t, frame_idx)
        # Check transition to Shot 4
        dt_cut = 14.80 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot4(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    else:
        base_frame = render_shot4(t, frame_idx)
        
    # Global atmospheric floating particles overlay
    final_frame = apply_particles(base_frame, t)
    
    # Pipe raw BGR24 into FFmpeg
    proc.stdin.write(final_frame.tobytes())
    
    if (frame_idx + 1) % 60 == 0 or frame_idx == TOTAL_FRAMES - 1:
        pct = int((frame_idx + 1) / TOTAL_FRAMES * 100)
        sys.stdout.write(f"\rRendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({pct}%) [{t:.1f}s]")
        sys.stdout.flush()

proc.stdin.close()
proc.wait()

print(f"\n🎉 4-Shot Living Anime MV rendered successfully: {FINAL_MP4}")
print(f"File size: {FINAL_MP4.stat().st_size / (1024*1024):.2f} MB")

# Generate new official cover thumbnail at the emotional climax (Shot 4, t=16.5s)
cover_path = OUT_DIR / "cover.jpg"
subprocess.run([
    "ffmpeg", "-y", "-ss", "16.5", "-i", str(FINAL_MP4),
    "-frames:v", "1", "-q:v", "2", str(cover_path)
], check=True)
print(f"📸 Cover thumbnail generated: {cover_path}")
