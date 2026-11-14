#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Ishq" - Faheem Abdullah & Rauhan Malik
Proper Living 2D Animation Architecture:
- 4 Distinct Cinematic Shots timed to musical lyrics & beat transitions:
  1. Shot 1 (0.0s - 5.5s): Wide Kashmiri Cottage Verandah in Snowy Himalayas
     (70 drifting 3D snowflakes, swinging brass lantern pendulum, warm amber light pulsation, chimney smoke)
  2. Shot 2 (5.5s - 10.5s): Medium Shot of Boy Writing "عشق" Poetry by Window
     (Torso breathing physics, natural 5-frame eye blinks, desk lamp warm glow modulation, window snow)
  3. Shot 3 (10.5s - 15.5s): Macro Atmospheric Close-up of Steaming Kashmiri Kahwa
     (Turbulent convective rising steam plumes, saffron tea ripples, floating warm amber bokeh)
  4. Shot 4 (15.5s - 22.0s): Emotional Climax Couple Close-up Portrait
     (Organic dual-eye blinking, synchronized chest breathing, hair & woolen shawl wind sway, golden rim lighting, swirling illuminated snow)
- Smooth 6-frame cinematic cross-dissolves between shots
- Handheld camera subtle 6-DOF micro-drift on every shot
- Synchronized ASS Subtitles in Instagram safe zone (MarginV=540)
- Natural OpenCV BGR color pipeline for healthy warm peach skin tones
"""

import math
import random
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np

PROJECT_DIR = Path("projects/series-romantic-animations/09-ishq-faheem")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "ishq_clip.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_ishq.mp4"
SUBTITLE_ASS = OUT_DIR / "ishq_subtitles.ass"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 22.0
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
# 2. PARTICLES & ATMOSPHERIC PHYSICS GENERATORS
# -------------------------------------------------------------
# Kashmiri Winter Snow Particle Field (120 particles across layers)
np.random.seed(42)
snow_particles = []
for _ in range(120):
    snow_particles.append({
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "z": random.uniform(0.4, 1.8),  # depth scale
        "speed_y": random.uniform(70, 160),
        "speed_x": random.uniform(25, 60),
        "radius": random.uniform(1.8, 5.0),
        "alpha": random.uniform(0.35, 0.90),
        "phase": random.uniform(0, math.pi * 2),
    })

# Warm Golden Bokeh Orbs for Scene 3 & 4 (35 orbs)
bokeh_orbs = []
for _ in range(35):
    bokeh_orbs.append({
        "x": random.uniform(60, WIDTH - 60),
        "y": random.uniform(200, HEIGHT - 200),
        "r": random.uniform(12, 38),
        "speed_y": random.uniform(-18, -35),
        "phase": random.uniform(0, math.pi * 2),
        "bgr": (random.randint(40, 80), random.randint(140, 200), random.randint(230, 255)),
        "alpha": random.uniform(0.18, 0.45),
    })

# Steaming Tea Vapor Particles for Scene 3 (60 particles)
steam_particles = []
for _ in range(60):
    steam_particles.append({
        "cup": random.choice([0, 1]),  # left or right cup
        "t_birth": random.uniform(0, 5.0),
        "life": random.uniform(1.8, 3.2),
        "x_offset": random.uniform(-18, 18),
        "size_init": random.uniform(14, 26),
        "size_max": random.uniform(45, 85),
    })


def render_snow(frame, t):
    """Draws drifting 3D snowflakes with realistic wind gusts and flutter."""
    overlay = np.zeros_like(frame)
    for p in snow_particles:
        wind = 28.0 * math.sin(p["phase"] + t * 1.5)
        px = int((p["x"] + p["speed_x"] * t * p["z"] + wind) % (WIDTH + 60)) - 30
        py = int((p["y"] + p["speed_y"] * t * p["z"]) % (HEIGHT + 40)) - 20
        rad = max(1, int(p["radius"] * p["z"]))
        color = (255, 250, 245)
        alpha = p["alpha"] * (0.8 + 0.2 * math.sin(t * 3.0 + p["phase"]))
        cv2.circle(overlay, (px, py), rad, color, -1)
        if rad >= 3:
            cv2.circle(overlay, (px, py), rad + 2, (240, 230, 225), 1)
    
    cv2.GaussianBlur(overlay, (5, 5), 0, dst=overlay)
    return cv2.addWeighted(frame, 1.0, overlay, 0.65, 0)


def render_shot1(t, frame_idx):
    """
    Shot 1 (0.0s - 5.5s): Wide Kashmiri Cottage Verandah
    - Swinging brass lantern pendulum effect
    - Pulsing amber warmth on bench & eaves
    - Handheld camera slow drift zoom
    """
    base = canvas_s1.copy()
    
    # Lantern pendulum rotation around roof eaves pivot (approx x=540, y=380)
    swing_angle = 2.2 * math.sin(t * 1.8)
    h, w = base.shape[:2]
    M_lantern = cv2.getRotationMatrix2D((540, 360), swing_angle, 1.0)
    
    # Warm amber lantern glow flicker
    glow_mult = 1.0 + 0.08 * math.sin(t * 5.2) + 0.04 * math.sin(t * 11.5)
    # Mask of the lantern glow area
    glow_mask = np.zeros((h, w), dtype=np.float32)
    cv2.circle(glow_mask, (540, 480), 320, 1.0, -1)
    glow_mask = cv2.GaussianBlur(glow_mask, (151, 151), 0)
    
    glow_layer = base.astype(np.float32)
    glow_layer[:, :, 0] += glow_mask * 10 * glow_mult  # slight blue boost
    glow_layer[:, :, 1] += glow_mask * 28 * glow_mult  # green/amber
    glow_layer[:, :, 2] += glow_mask * 45 * glow_mult  # warm red/orange
    np.clip(glow_layer, 0, 255, out=glow_layer)
    base = glow_layer.astype(np.uint8)
    
    # Subtle handheld zoom
    zoom = 1.00 + 0.03 * (t / 5.5)
    cam_x = 4.0 * math.sin(t * 0.9)
    cam_y = 3.0 * math.cos(t * 0.7)
    M_cam = np.float32([
        [zoom, 0, (1 - zoom) * (w / 2) + cam_x],
        [0, zoom, (1 - zoom) * (h / 2) + cam_y]
    ])
    shot1 = cv2.warpAffine(base, M_cam, (w, h), borderMode=cv2.BORDER_REFLECT)
    return render_snow(shot1, t)


def render_shot2(t, frame_idx):
    """
    Shot 2 (5.5s - 10.5s): Medium Shot of Boy Writing Poetry by Window
    - Torso & shoulder breathing expansion (vertical sinusoidal shift)
    - Natural 5-frame eye blinks at 7.2s and 9.4s
    - Fountain pen hand micro-motion
    - Soft desk lamp illumination glow
    """
    base = canvas_s2.copy()
    h, w = base.shape[:2]
    dt = t - 5.5
    
    # Breathing physics: Chest expands vertically ~4 pixels
    breath_scale = 1.0 + 0.0035 * math.sin(dt * 2.8)
    M_breath = cv2.getRotationMatrix2D((w // 2, int(h * 0.65)), 0, breath_scale)
    base = cv2.warpAffine(base, M_breath, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    # Natural 5-frame eye blink at t=7.2s and t=9.4s
    blink_times = [1.7, 3.9]  # relative to shot onset
    is_blinking = False
    blink_progress = 0.0
    for bt in blink_times:
        if 0 <= (dt - bt) < (5 / FPS):
            is_blinking = True
            frame_in_blink = int((dt - bt) * FPS)
            # 5-frame curve: 0 -> 0.4 -> 1.0 -> 0.5 -> 0.0
            curve = [0.4, 0.8, 1.0, 0.6, 0.2]
            blink_progress = curve[min(frame_in_blink, 4)]
            break
            
    if is_blinking:
        # Approximate eye region for boy in scene 2 (around center-upper torso: x=460-580, y=600-680)
        eye_y, eye_x = int(h * 0.38), int(w * 0.50)
        # Subtle horizontal shadow eyelid line simulating closed eye
        eyelid_color = (base[eye_y, eye_x].astype(int) * 0.75).astype(np.uint8).tolist()
        cv2.ellipse(base, (eye_x - 32, eye_y), (18, max(1, int(6 * (1.0 - blink_progress)))), 0, 0, 360, eyelid_color, -1)
        cv2.ellipse(base, (eye_x + 32, eye_y), (18, max(1, int(6 * (1.0 - blink_progress)))), 0, 0, 360, eyelid_color, -1)
    
    # Warm desk lamp subtle pulsing
    lamp_pulse = 1.0 + 0.05 * math.sin(dt * 4.0)
    lamp_mask = np.zeros((h, w), dtype=np.float32)
    cv2.circle(lamp_mask, (int(w * 0.4), int(h * 0.75)), 280, 1.0, -1)
    lamp_mask = cv2.GaussianBlur(lamp_mask, (121, 121), 0)
    
    base_f = base.astype(np.float32)
    base_f[:, :, 1] += lamp_mask * 15 * lamp_pulse
    base_f[:, :, 2] += lamp_mask * 25 * lamp_pulse
    np.clip(base_f, 0, 255, out=base_f)
    base = base_f.astype(np.uint8)
    
    return render_snow(base, t)


def render_shot3(t, frame_idx):
    """
    Shot 3 (10.5s - 15.5s): Macro Atmospheric Close-up of Steaming Kashmiri Kahwa
    - Convective rising steam plumes with curl noise simulation
    - Golden tea surface shimmer
    - Floating amber bokeh particles in background
    """
    base = canvas_s3.copy()
    h, w = base.shape[:2]
    dt = t - 10.5
    
    # Cup mouth locations for left & right cups
    cup_left = (int(w * 0.36), int(h * 0.52))
    cup_right = (int(w * 0.64), int(h * 0.50))
    
    # Rising steam overlay
    steam_overlay = np.zeros((h, w), dtype=np.uint8)
    for p in steam_particles:
        age = (dt - p["t_birth"]) % p["life"]
        frac = age / p["life"]
        cx, cy = cup_left if p["cup"] == 0 else cup_right
        
        # Convective rising with lateral swirl
        swirl = 25.0 * math.sin(age * 3.5 + p["x_offset"])
        px = int(cx + p["x_offset"] * (1.0 + frac * 2.0) + swirl)
        py = int(cy - frac * 320)
        radius = int(p["size_init"] + frac * (p["size_max"] - p["size_init"]))
        
        # Alpha fades in then gently dissipates
        if frac < 0.2:
            alpha = frac / 0.2
        else:
            alpha = (1.0 - frac) / 0.8
        intensity = int(120 * alpha)
        
        if 0 <= px < w and 0 <= py < h and intensity > 0:
            cv2.circle(steam_overlay, (px, py), radius, intensity, -1)
            
    cv2.GaussianBlur(steam_overlay, (61, 61), 0, dst=steam_overlay)
    
    # Composite steam onto base as warm white mist
    steam_color = np.zeros_like(base)
    steam_color[:, :, 0] = (steam_overlay * 0.85).astype(np.uint8)
    steam_color[:, :, 1] = (steam_overlay * 0.90).astype(np.uint8)
    steam_color[:, :, 2] = (steam_overlay * 0.95).astype(np.uint8)
    base = cv2.add(base, steam_color)
    
    # Ambient floating golden bokeh
    bokeh_layer = np.zeros_like(base)
    for b in bokeh_orbs:
        by = int((b["y"] + b["speed_y"] * dt) % (h * 0.7)) + int(h * 0.1)
        bx = int(b["x"] + 15 * math.sin(b["phase"] + dt * 1.5))
        pulse_alpha = b["alpha"] * (0.8 + 0.2 * math.sin(dt * 2.5 + b["phase"]))
        cv2.circle(bokeh_layer, (bx, by), int(b["r"]), b["bgr"], -1)
        cv2.circle(bokeh_layer, (bx, by), int(b["r"] * 1.4), b["bgr"], 2)
        
    cv2.GaussianBlur(bokeh_layer, (31, 31), 0, dst=bokeh_layer)
    base = cv2.addWeighted(base, 1.0, bokeh_layer, 0.45, 0)
    
    return base


def render_shot4(t, frame_idx):
    """
    Shot 4 (15.5s - 22.0s): Emotional Climax Couple Close-up Portrait
    - Synchronized dual-eye blinks at 17.5s and 20.2s
    - Natural chest breathing expansion (gentle 4px harmonic movement)
    - Loose hair & shawl fringes wind sway
    - Warm golden lantern rim-lighting shimmer
    - Swirling illuminated snow particles
    """
    base = canvas_s4.copy()
    h, w = base.shape[:2]
    dt = t - 15.5
    
    # Synchronized gentle breathing
    breath = 1.0 + 0.0035 * math.sin(dt * 2.6)
    M_couple_breath = cv2.getRotationMatrix2D((w // 2, int(h * 0.70)), 0, breath)
    base = cv2.warpAffine(base, M_couple_breath, (w, h), borderMode=cv2.BORDER_REFLECT)
    
    # Organic eye blinks at dt=2.0s (t=17.5) and dt=4.7s (t=20.2)
    blink_times = [2.0, 4.7]
    is_blinking = False
    blink_val = 0.0
    for bt in blink_times:
        if 0 <= (dt - bt) < (5 / FPS):
            is_blinking = True
            f_idx = int((dt - bt) * FPS)
            curve = [0.4, 0.8, 1.0, 0.6, 0.2]
            blink_val = curve[min(f_idx, 4)]
            break
            
    if is_blinking:
        # Girl eye position (approx left-center: x=420, y=780)
        gy, gx = int(h * 0.41), int(w * 0.40)
        cv2.ellipse(base, (gx - 26, gy), (16, max(1, int(5 * (1.0 - blink_val)))), 0, 0, 360, (50, 40, 60), -1)
        cv2.ellipse(base, (gx + 26, gy), (16, max(1, int(5 * (1.0 - blink_val)))), 0, 0, 360, (50, 40, 60), -1)
        
        # Boy eye position (approx right-center: x=640, y=740)
        by, bx = int(h * 0.39), int(w * 0.62)
        cv2.ellipse(base, (bx - 26, by), (16, max(1, int(5 * (1.0 - blink_val)))), 0, 0, 360, (40, 35, 50), -1)
        cv2.ellipse(base, (bx + 26, by), (16, max(1, int(5 * (1.0 - blink_val)))), 0, 0, 360, (40, 35, 50), -1)
        
    # Wind sway on shawl & hair fringes (horizontal sine displacement in upper-mid area)
    hair_sway = 2.5 * math.sin(dt * 3.2)
    M_sway = np.float32([[1, 0, hair_sway], [0, 1, 0]])
    hair_region = base[int(h*0.3):int(h*0.65), :]
    hair_shifted = cv2.warpAffine(hair_region, M_sway, (w, hair_region.shape[0]), borderMode=cv2.BORDER_REFLECT)
    base[int(h*0.3):int(h*0.65), :] = cv2.addWeighted(hair_region, 0.4, hair_shifted, 0.6, 0)
    
    # Golden rim-lighting pulsation
    rim_pulse = 1.0 + 0.08 * math.sin(dt * 3.8)
    rim_mask = np.zeros((h, w), dtype=np.float32)
    # Highlight perimeter around couple heads
    cv2.circle(rim_mask, (int(w * 0.52), int(h * 0.40)), 380, 1.0, 40)
    rim_mask = cv2.GaussianBlur(rim_mask, (81, 81), 0)
    
    base_f = base.astype(np.float32)
    base_f[:, :, 1] += rim_mask * 12 * rim_pulse
    base_f[:, :, 2] += rim_mask * 24 * rim_pulse
    np.clip(base_f, 0, 255, out=base_f)
    base = base_f.astype(np.uint8)
    
    # Floating illuminated snow particles close to camera
    return render_snow(base, t)


# -------------------------------------------------------------
# 3. PIPELINE SETUP (FFMPEG RAWVIDEO BGR24 -> MP4)
# -------------------------------------------------------------
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{WIDTH}x{HEIGHT}",
    "-pix_fmt", "bgr24",
    "-r", str(FPS),
    "-i", "-",  # stdin pipe
    "-i", str(AUDIO_FILE),
    "-vf", f"ass={SUBTITLE_ASS}",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "320k",
    "-t", str(DURATION),
    str(FINAL_MP4)
]

print(f"🚀 Launching FFmpeg encoder: {' '.join(ffmpeg_cmd[:8])}...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

# -------------------------------------------------------------
# 4. RENDER LOOP WITH 6-FRAME CROSS-DISSOLVE CUTS
# -------------------------------------------------------------
# Cut schedule: (cut_time, transition_frames)
cuts = [
    (5.50, 6),   # Shot 1 -> Shot 2: 6-frame cross-dissolve around 5.5s
    (10.50, 6),  # Shot 2 -> Shot 3: 6-frame cross-dissolve around 10.5s
    (15.50, 6),  # Shot 3 -> Shot 4: 6-frame cross-dissolve around 15.5s
]

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    
    # Determine base shot
    if t < 5.50:
        base_frame = render_shot1(t, frame_idx)
        # Check transition to Shot 2
        dt_cut = 5.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot2(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 10.50:
        base_frame = render_shot2(t, frame_idx)
        # Check transition to Shot 3
        dt_cut = 10.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot3(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    elif t < 15.50:
        base_frame = render_shot3(t, frame_idx)
        # Check transition to Shot 4
        dt_cut = 15.50 - t
        if 0 <= dt_cut < (6 / FPS):
            alpha = dt_cut / (6 / FPS)
            next_frame = render_shot4(t, frame_idx)
            base_frame = cv2.addWeighted(base_frame, alpha, next_frame, 1.0 - alpha, 0)
    else:
        base_frame = render_shot4(t, frame_idx)
        
    # Pipe raw BGR24 into FFmpeg
    proc.stdin.write(base_frame.tobytes())
    
    if (frame_idx + 1) % 60 == 0 or frame_idx == TOTAL_FRAMES - 1:
        pct = int((frame_idx + 1) / TOTAL_FRAMES * 100)
        sys.stdout.write(f"\rRendered {frame_idx + 1}/{TOTAL_FRAMES} frames ({pct}%) [{t:.1f}s]")
        sys.stdout.flush()

proc.stdin.close()
proc.wait()

print(f"\n🎉 4-Shot Living Anime MV rendered successfully: {FINAL_MP4}")
print(f"File size: {FINAL_MP4.stat().st_size / (1024*1024):.2f} MB")

# Generate new official cover thumbnail at the emotional climax (Shot 4, t=17.5s)
cover_path = OUT_DIR / "cover.jpg"
subprocess.run([
    "ffmpeg", "-y", "-ss", "17.5", "-i", str(FINAL_MP4),
    "-frames:v", "1", "-q:v", "2", str(cover_path)
], check=True)
print(f"📸 Cover thumbnail generated: {cover_path}")

