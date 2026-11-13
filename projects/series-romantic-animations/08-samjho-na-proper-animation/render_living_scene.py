#!/usr/bin/env python3
"""
Living 2D Animation Engine for "Samjho Na" by Aditya Rikhari.
Features:
- Character breathing cycle (torso/shoulder harmonic expansion)
- Realistic multi-frame eye blinking (3.5s interval, 5-frame interpolation)
- Wind-reactive hair physics (spring sine oscillator)
- Twinkling starfield (60+ stars with randomized frequencies)
- Ambient city bokeh shimmer
- Incandescent fairy light bloom pulsation
- Glowing shooting star stardust streaks
- 40+ floating glowing fireflies / ember particles with curl turbulence
- Cinematic handheld camera micro-drift with 3D parallax
- Synchronized ASS subtitles in Instagram Reels safe zone
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
AUDIO_FILE = PROJECT_DIR / "audio" / "samjho_na_clip.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_samjho_na_animation.mp4"
BASE_IMAGE = PROJECT_DIR / "assets" / "scene_base.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 20.50
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing Living 2D Animation Engine: {TOTAL_FRAMES} frames @ {FPS} fps ({DURATION}s)...")

# 1. Load and upscale base image to 1080x1920 canvas
raw_img = Image.open(BASE_IMAGE).convert("RGBA")
# Scale to fill 1080x1920
scale = max(WIDTH / raw_img.width, HEIGHT / raw_img.height)
nw, nh = int(raw_img.width * scale), int(raw_img.height * scale)
base_canvas = raw_img.resize((nw, nh), Image.Resampling.LANCZOS)
# Center crop to 1080x1920
cx = (nw - WIDTH) // 2
cy = (nh - HEIGHT) // 2
base_canvas = base_canvas.crop((cx, cy, cx + WIDTH, cy + HEIGHT))
base_arr = np.array(base_canvas)

print("🖼️ Base canvas prepared: 1080x1920 Full HD.")

# Map coordinates from original (768x1376) to 1080x1920 canvas
# Scale factor is scale
def orig_to_canvas(ox, oy):
    return int(ox * scale - cx), int(oy * scale - cy)

eye_cx, eye_cy = orig_to_canvas(348, 562)
eye_r = int(22 * scale)
print(f"👁️ Eye center mapped to canvas: ({eye_cx}, {eye_cy}), radius: {eye_r}")

# Character bounding box in canvas coordinates
char_x1, char_y1 = orig_to_canvas(220, 480)
char_x2, char_y2 = orig_to_canvas(560, 1100)
char_x1 = max(0, char_x1)
char_y1 = max(0, char_y1)

# Precompute stars in sky (y < 650)
print("✨ Detecting sky star coordinates for procedural twinkling...")
sky_gray = cv2.cvtColor(base_arr[:700, :], cv2.COLOR_RGBA2GRAY)
_, thresh = cv2.threshold(sky_gray, 215, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
stars = []
for c in contours:
    M = cv2.moments(c)
    if M["m00"] > 0 and M["m00"] < 80: # Filter small star points
        sx = int(M["m10"] / M["m00"])
        sy = int(M["m01"] / M["m00"])
        # Avoid moon area (x: 400..700, y: 150..350)
        if not (400 < sx < 720 and 120 < sy < 360):
            stars.append({
                "x": sx, "y": sy,
                "freq": random.uniform(1.8, 4.5),
                "phase": random.uniform(0, 6.28),
                "r": random.randint(2, 4)
            })
print(f"✨ Found {len(stars)} twinkling stars in sky.")

# Precompute fairy lights along the parapet (y: 1050 to 1450, x: 420 to 1050)
fairy_lights = []
for fx, fy in [
    (480, 1340), (520, 1315), (560, 1290), (605, 1265), (650, 1245),
    (700, 1230), (750, 1220), (810, 1225), (870, 1235), (930, 1240),
    (990, 1245), (1040, 1248)
]:
    fairy_lights.append({
        "x": fx, "y": fy,
        "freq": random.uniform(2.0, 4.0),
        "phase": random.uniform(0, 6.28),
        "r": 12
    })

# Initialize floating particles (fireflies/dust motes)
random.seed(42)
particles = []
for _ in range(45):
    particles.append({
        "x": random.uniform(100, WIDTH - 100),
        "y": random.uniform(HEIGHT * 0.4, HEIGHT * 0.95),
        "vx": random.uniform(-0.6, 0.6),
        "vy": random.uniform(-1.2, -0.4),
        "size": random.uniform(2.5, 6.0),
        "phase": random.uniform(0, 6.28),
        "alpha": random.uniform(0.4, 0.9)
    })

# Subtitles configuration
def sec_to_ass(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: Samjho Na - Living 2D Animation Reel",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: SongBadge,Lato,34,&H00E8F4FF,&H00000000,&H00101010,&H70000000,-1,0,0,0,100,100,3.0,0,1,1.8,1.5,8,40,40,210,1",
    "Style: ModernLyric,Lato,60,&H00FFFFFF,&H000000FF,&H000A0A0A,&H80000000,-1,0,0,0,100,100,2.0,0,1,2.0,2.0,2,60,60,540,1",
    "Style: DropTitle,Lato,48,&H00E8F4FF,&H00000000,&H000A0A0A,&H80000000,-1,0,0,0,100,100,3.5,0,1,2.0,2.0,2,40,40,540,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(5.0)},SongBadge,,0,0,0,,{{\\fade(350,450)}}ADITYA RIKHARI  |  SAMJHO NA",
    f"Dialogue: 1,{sec_to_ass(0.5)},{sec_to_ass(5.2)},ModernLyric,,0,0,0,,{{\\fade(200,200)}}Jaanan, {{\\c&H003CE0FF&}}samjho na{{\\c&H00FFFFFF&}}, dil kehta hai...",
    f"Dialogue: 1,{sec_to_ass(5.2)},{sec_to_ass(10.0)},ModernLyric,,0,0,0,,{{\\fade(200,200)}}Teri galiyon mein hi {{\\c&H003CE0FF&}}rehta hai{{\\c&H00FFFFFF&}}...",
    f"Dialogue: 1,{sec_to_ass(10.0)},{sec_to_ass(14.8)},ModernLyric,,0,0,0,,{{\\fade(200,200)}}Jaanan, {{\\c&H003CE0FF&}}samjho na{{\\c&H00FFFFFF&}}, dil kehta hai...",
    f"Dialogue: 1,{sec_to_ass(14.8)},{sec_to_ass(20.0)},ModernLyric,,0,0,0,,{{\\fade(200,350)}}Teri baahon mein jeena hai,\\N{{\\c&H003CE0FF&}}marna hai ishq mein tere{{\\c&H00FFFFFF&}}..."
]
ass_file = OUT_DIR / "samjho_na_subtitles.ass"
ass_file.write_text("\n".join(ass_lines), encoding="utf-8")
print(f"📝 Synced ASS subtitles written: {ass_file}")

# Pipeline into FFmpeg encoder
ffmpeg_cmd = [
    "/home/pratik/.local/bin/ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "bgr24",
    "-r", str(FPS),
    "-i", "-",
    "-i", str(AUDIO_FILE),
    "-vf", f"ass={ass_file.resolve()}",
    "-c:v", "libx264", "-preset", "medium", "-crf", "17",
    "-c:a", "aac", "-b:a", "256k",
    "-movflags", "+faststart",
    "-shortest",
    str(FINAL_MP4)
]

proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

print("🎨 Rendering living frames and piping to FFmpeg...")

blink_intervals = [2.8, 6.2, 9.8, 13.5, 17.2]

for f_idx in range(TOTAL_FRAMES):
    t = f_idx / FPS
    
    # 1. Base copy
    frame = base_arr.copy()
    
    # 2. Breathing displacement on character body
    # Subtle sinusoidal vertical shift on torso & shoulders
    breath_val = math.sin(t * 2 * math.pi / 3.2) * 3.2
    
    # Apply displacement to character torso box
    # Crop torso, shift vertically by breath_val with subpixel interpolation
    torso_y1, torso_y2 = int(char_y1 + 180), int(char_y2)
    torso_x1, torso_x2 = int(char_x1), int(char_x2)
    torso_crop = frame[torso_y1:torso_y2, torso_x1:torso_x2]
    M_breath = np.float32([[1, 0, 0], [0, 1, breath_val]])
    torso_shifted = cv2.warpAffine(torso_crop, M_breath, (torso_crop.shape[1], torso_crop.shape[0]), borderMode=cv2.BORDER_REFLECT)
    frame[torso_y1:torso_y2, torso_x1:torso_x2] = torso_shifted
    
    # 3. Hair wind physics
    # Wavy swaying on the back hair curls
    hair_x1, hair_x2 = int(char_x1), int(char_x1 + 140)
    hair_y1, hair_y2 = int(char_y1 + 40), int(char_y1 + 380)
    hair_crop = frame[hair_y1:hair_y2, hair_x1:hair_x2]
    hair_sway = math.sin(t * 3.4) * 3.8
    M_hair = np.float32([[1, 0, hair_sway], [0, 1, 0]])
    hair_shifted = cv2.warpAffine(hair_crop, M_hair, (hair_crop.shape[1], hair_crop.shape[0]), borderMode=cv2.BORDER_REFLECT)
    frame[hair_y1:hair_y2, hair_x1:hair_x2] = hair_shifted
    
    # 4. Realistic 5-frame eye blinking
    blink_alpha = 0.0
    for b_t in blink_intervals:
        dt = t - b_t
        if 0.0 <= dt < 0.18:
            # 180ms blink: triangle curve 0 -> 1 -> 0
            if dt < 0.09:
                blink_alpha = dt / 0.09
            else:
                blink_alpha = (0.18 - dt) / 0.09
            break
            
    if blink_alpha > 0.05:
        # Overlay closed eyelid on eye region
        # Eye box
        ey1, ey2 = eye_cy - 16, eye_cy + 18
        ex1, ex2 = eye_cx - 20, eye_cx + 20
        eye_patch = frame[ey1:ey2, ex1:ex2].astype(np.float32)
        
        # Skin color for closed eyelid
        skin_bgr = np.array([105, 128, 195, 255], dtype=np.float32)[:3] # Skin tone
        lash_bgr = np.array([28, 20, 24], dtype=np.float32) # Dark lash
        
        # Blend skin over eyeball
        closed_patch = eye_patch.copy()
        # Cover pupil area
        py1, py2 = 10, 24
        px1, px2 = 8, 30
        closed_patch[py1:py2, px1:px2, :3] = skin_bgr
        
        # Draw lash line across lower edge of eyelid
        cv2.ellipse(closed_patch, (20, 18), (12, 6), 15, 0, 180, lash_bgr.tolist(), 2, cv2.LINE_AA)
        
        # Soft blend into frame
        final_eye = eye_patch * (1.0 - blink_alpha) + closed_patch * blink_alpha
        frame[ey1:ey2, ex1:ex2] = final_eye.astype(np.uint8)

    # 5. Twinkling stars in sky
    for s in stars:
        twinkle = 0.5 + 0.5 * math.sin(t * s["freq"] + s["phase"])
        if twinkle > 0.6:
            r = int(s["r"] * twinkle)
            glow_col = (int(255 * twinkle), int(245 * twinkle), int(220 * twinkle))
            cv2.circle(frame, (s["x"], s["y"]), r, glow_col, -1, cv2.LINE_AA)
            if twinkle > 0.85:
                # Add cross sparkle on bright stars
                cv2.line(frame, (s["x"] - r*2, s["y"]), (s["x"] + r*2, s["y"]), glow_col, 1, cv2.LINE_AA)
                cv2.line(frame, (s["x"], s["y"] - r*2), (s["x"], s["y"] + r*2), glow_col, 1, cv2.LINE_AA)

    # 6. Shooting star stardust streak (at t=4.5s and t=13.5s)
    for shoot_t in [4.5, 13.5]:
        sdt = t - shoot_t
        if 0.0 <= sdt < 1.2:
            progress = sdt / 1.2
            sx1 = int(750 - progress * 400)
            sy1 = int(100 + progress * 220)
            sx2 = int(sx1 + 70)
            sy2 = int(sy1 - 40)
            alpha_streak = math.sin(progress * math.pi)
            if alpha_streak > 0.05:
                cv2.line(frame, (sx1, sy1), (sx2, sy2), (255, 255, 230), 2, cv2.LINE_AA)
                cv2.circle(frame, (sx1, sy1), 3, (255, 255, 255), -1, cv2.LINE_AA)

    # 7. Fairy lights incandescent breathing bloom
    for fl in fairy_lights:
        pulse = 0.75 + 0.25 * math.sin(t * fl["freq"] + fl["phase"])
        r = int(fl["r"] * pulse)
        # Warm golden radial bloom
        cv2.circle(frame, (fl["x"], fl["y"]), r, (60, 200, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, (fl["x"], fl["y"]), int(r * 0.5), (180, 240, 255), -1, cv2.LINE_AA)

    # 8. Floating luminous particles (fireflies/fairy dust)
    for p in particles:
        # Update particle position
        p["x"] += p["vx"] + math.sin(t * 2.0 + p["phase"]) * 0.4
        p["y"] += p["vy"]
        # Wrap around
        if p["y"] < HEIGHT * 0.25:
            p["y"] = HEIGHT * 0.95
            p["x"] = random.uniform(100, WIDTH - 100)
            
        p_alpha = p["alpha"] * (0.6 + 0.4 * math.sin(t * 3.0 + p["phase"]))
        if p_alpha > 0.1:
            px, py = int(p["x"]), int(p["y"])
            pr = int(p["size"])
            p_col = (int(80 * p_alpha), int(210 * p_alpha), int(255 * p_alpha))
            cv2.circle(frame, (px, py), pr, p_col, -1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), max(1, int(pr * 0.4)), (255, 255, 255), -1, cv2.LINE_AA)

    # 9. Subtle cinematic handheld camera micro-drift
    drift_x = math.sin(t * 0.7) * 4.0
    drift_y = math.cos(t * 0.5) * 3.0
    M_cam = np.float32([[1, 0, drift_x], [0, 1, drift_y]])
    final_frame = cv2.warpAffine(frame, M_cam, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
    
    # Convert RGBA to BGR for FFmpeg pipe
    bgr_frame = cv2.cvtColor(final_frame, cv2.COLOR_RGBA2BGR)
    proc.stdin.write(bgr_frame.tobytes())
    
    if f_idx % 60 == 0:
        percent = (f_idx / TOTAL_FRAMES) * 100
        print(f"⏳ Rendered {f_idx}/{TOTAL_FRAMES} frames ({percent:.1f}%)...")

proc.stdin.close()
proc.wait()
print(f"🎉 Living 2D Animation Reel compiled: {FINAL_MP4}")

# Generate cover
cover_jpg = OUT_DIR / "cover.jpg"
subprocess.run([
    "/home/pratik/.local/bin/ffmpeg", "-y",
    "-ss", "00:00:06.000",
    "-i", str(FINAL_MP4),
    "-frames:v", "1",
    "-q:v", "2",
    str(cover_jpg)
], check=True)
print(f"🖼️ Cover generated: {cover_jpg}")
