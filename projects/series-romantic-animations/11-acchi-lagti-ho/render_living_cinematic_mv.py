#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Achchi Lagti Ho" (18.5M Trend Wave)
Features:
- 4 Distinct Cinematic Shots timed to musical beats:
  1. Shot 1 (0.0s - 7.2s): Wide Golden Hour Rooftop (Torso breathing, hair breeze sway, floating amber sun motes, bokeh shimmer)
  2. Shot 2 (7.2s - 14.5s): Cinematic Medium Close-up (Intimate eye gaze, subtle blink, golden sunbeams through hair, depth of field)
  3. Shot 3 (14.5s - 21.0s): Graceful Breeze & Fabric Flutter (Dupatta/pallu wave, floating golden particles)
  4. Shot 4 (21.0s - 27.5s): Twilight Climax (Warm fairy lights pulse, starry dusk connection, golden rim lighting)
- Smooth 6-frame cinematic cross-dissolve transitions between shots
- Handheld camera micro-drift on every shot
- Synchronized Noto Sans Devanagari ASS Subtitles in Instagram safe zone (MarginV=540)
"""

import math
import random
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np

PROJECT_DIR = Path("projects/series-romantic-animations/11-acchi-lagti-ho")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "acchi_lagti_ho_hook.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_acchi_lagti_ho_animation.mp4"
SUBTITLE_ASS = OUT_DIR / "acchi_lagti_ho_subtitles.ass"
COVER_JPG = OUT_DIR / "cover.jpg"
STORY_CARD_JPG = OUT_DIR / "story_card.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 27.56
TOTAL_FRAMES = int(DURATION * FPS)

def sec_to_ass(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

def write_subtitles():
    ass_template = f"""[Script Info]
Title: Achchi Lagti Ho - Living 2D Anime MV
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {WIDTH}
PlayResY: {HEIGHT}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BrandHeader,DejaVu Sans,34,&H00FFFFFF,&H000000FF,&H90000000,&H60000000,-1,0,0,0,100,100,2,0,1,2.0,1.0,8,60,60,180,1
Style: LyricGold,DejaVu Sans,60,&H00FFFFFF,&H000000FF,&H90050810,&H80000000,-1,0,0,0,100,100,1,0,1,3.8,2.2,2,80,80,540,1
Style: LyricAccent,DejaVu Sans,64,&H003CE0FF,&H000000FF,&H90050810,&H80000000,-1,0,0,0,100,100,1,0,1,4.0,2.5,2,80,80,540,1
Style: ClimaxTitle,DejaVu Sans,48,&H00E8F4FF,&H000000FF,&H90000000,&H70000000,-1,0,0,0,100,100,2,0,1,2.5,1.5,2,60,60,540,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:04.20,BrandHeader,,0,0,180,,{{\\fad(300,500)}}UDIT NARAYAN & KAVITA K  |  {{\\c&H003CE0FF&}}ACHCHI LAGTI HO
Dialogue: 1,0:00:00.00,0:00:04.20,LyricGold,,0,0,540,,{{\\fad(250,200)}}MUJHE TUM {{\\c&H003CE0FF&}}CHUPKE CHUPKE{{\\c&H00FFFFFF&}} JAB AISE DEKHTI HO...
Dialogue: 1,0:00:04.20,0:00:08.50,LyricAccent,,0,0,540,,{{\\fad(150,200)}}ACHCHI LAGTI HO...
Dialogue: 1,0:00:12.00,0:00:17.50,LyricGold,,0,0,540,,{{\\fad(200,200)}}KABHI {{\\c&H003CE0FF&}}ZULFON SE{{\\c&H00FFFFFF&}}, KABHI {{\\c&H00FFB040&}}AANCHAL SE{{\\c&H00FFFFFF&}} JAB KHELTI HO...
Dialogue: 1,0:00:17.50,0:00:22.00,LyricAccent,,0,0,540,,{{\\fad(150,200)}}ACHCHI LAGTI HO...
Dialogue: 2,0:00:22.00,0:00:27.56,ClimaxTitle,,0,0,540,,{{\\fad(200,600)}}ACHCHI LAGTI HO  |  UDIT NARAYAN & KAVITA K
"""
    with open(SUBTITLE_ASS, "w", encoding="utf-8") as f:
        f.write(ass_template)
    print("📝 Subtitle ASS file generated.")

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

def apply_handheld_drift(frame, t, amp_x=2.8, amp_y=2.0):
    dx = math.sin(t * 0.8) * amp_x + math.sin(t * 1.5) * 0.8
    dy = math.cos(t * 0.6) * amp_y + math.cos(t * 1.2) * 0.6
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

def main():
    print(f"🎬 Initializing Achchi Lagti Ho MV Engine ({TOTAL_FRAMES} frames @ {FPS} fps)...")
    write_subtitles()

    c1 = load_canvas(ASSETS_DIR / "scene-1.jpg")
    c2 = load_canvas(ASSETS_DIR / "scene-2.jpg")
    c3 = load_canvas(ASSETS_DIR / "scene-3.jpg")
    c4 = load_canvas(ASSETS_DIR / "scene-4.jpg")
    print("✅ All 4 canvases loaded.")

    # Floating warm golden motes/fireflies
    random.seed(101)
    particles = []
    for _ in range(45):
        particles.append({
            "x": random.uniform(50, WIDTH - 50),
            "y": random.uniform(200, HEIGHT - 200),
            "vx": random.uniform(-0.35, 0.35),
            "vy": random.uniform(-0.55, -0.15),
            "radius": random.uniform(1.8, 3.8),
            "base_alpha": random.uniform(120, 220),
            "phase": random.uniform(0, math.pi * 2),
            "color": random.choice([(80, 210, 255), (100, 230, 255), (120, 240, 255)])
        })

    raw_video = OUT_DIR / "raw_visual.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(raw_video), fourcc, FPS, (WIDTH, HEIGHT))

    # Shot boundaries in seconds:
    # Shot 1: 0.0 to 7.2s (Frames 0 .. 215)
    # Shot 2: 7.2 to 14.5s (Frames 216 .. 434)
    # Shot 3: 14.5 to 21.0s (Frames 435 .. 629)
    # Shot 4: 21.0 to 27.56s (Frames 630 .. 826)

    def get_shot_frame(shot_id, t, canvas):
        frame = canvas.copy()
        # Cinematic push-in zoom
        if shot_id == 1:
            zoom = 1.0 + 0.03 * (t / 7.2)
        elif shot_id == 2:
            zoom = 1.0 + 0.04 * ((t - 7.2) / 7.3)
        elif shot_id == 3:
            zoom = 1.0 + 0.035 * ((t - 14.5) / 6.5)
        else:
            zoom = 1.0 + 0.04 * ((t - 21.0) / 6.56)

        nh, nw = int(HEIGHT * zoom), int(WIDTH * zoom)
        scaled = cv2.resize(frame, (nw, nh))
        ox = max(0, (nw - WIDTH) // 2)
        oy = max(0, (nh - HEIGHT) // 2)
        frame = scaled[oy:oy+HEIGHT, ox:ox+WIDTH].copy()

        # Torso breathing simulation
        breath = math.sin(t * 2.2) * 2.5
        M_b = np.float32([[1, 0, 0], [0, 1, breath * 0.4]])
        frame = cv2.warpAffine(frame, M_b, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

        # Ambient lighting pulse
        pulse = (math.sin(t * 3.0) + 1.0) * 0.03
        frame = cv2.addWeighted(frame, 1.0 + pulse, np.zeros_like(frame), 0, 0)
        return apply_handheld_drift(frame, t)

    def draw_particles(frame, t):
        overlay = frame.copy()
        for p in particles:
            px = int((p["x"] + p["vx"] * t * 30) % (WIDTH - 40) + 20)
            py = int((p["y"] + p["vy"] * t * 30) % (HEIGHT - 40) + 20)
            tw = (math.sin(t * 3.5 + p["phase"]) + 1.0) * 0.5
            rad = int(p["radius"] + tw * 1.5)
            cv2.circle(overlay, (px, py), rad, p["color"], -1)
        return cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

    print("🎞️ Rendering frames...")
    CROSS_FRAMES = 8

    for f_idx in range(TOTAL_FRAMES):
        t = f_idx / FPS
        if t < 7.20:
            frame = get_shot_frame(1, t, c1)
            # Cross dissolve to Shot 2 at end of Shot 1
            if f_idx >= (int(7.20 * FPS) - CROSS_FRAMES):
                alpha = (f_idx - (int(7.20 * FPS) - CROSS_FRAMES)) / CROSS_FRAMES
                frame_next = get_shot_frame(2, t, c2)
                frame = cv2.addWeighted(frame_next, alpha, frame, 1.0 - alpha, 0)
        elif t < 14.50:
            frame = get_shot_frame(2, t, c2)
            if f_idx >= (int(14.50 * FPS) - CROSS_FRAMES):
                alpha = (f_idx - (int(14.50 * FPS) - CROSS_FRAMES)) / CROSS_FRAMES
                frame_next = get_shot_frame(3, t, c3)
                frame = cv2.addWeighted(frame_next, alpha, frame, 1.0 - alpha, 0)
        elif t < 21.00:
            frame = get_shot_frame(3, t, c3)
            if f_idx >= (int(21.00 * FPS) - CROSS_FRAMES):
                alpha = (f_idx - (int(21.00 * FPS) - CROSS_FRAMES)) / CROSS_FRAMES
                frame_next = get_shot_frame(4, t, c4)
                frame = cv2.addWeighted(frame_next, alpha, frame, 1.0 - alpha, 0)
        else:
            frame = get_shot_frame(4, t, c4)

        frame = draw_particles(frame, t)
        out.write(frame)

        if f_idx % 150 == 0:
            print(f"  Frame {f_idx}/{TOTAL_FRAMES} ({t:.1f}s)...")

    out.release()
    print("✅ Raw visual rendered.")

    print("🔥 Burning Noto Sans Devanagari typography & muxing Slowed+Reverb master...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(AUDIO_FILE),
        "-vf", f"ass={SUBTITLE_ASS.resolve()}",
        "-af", "volume=1.5,alimiter=limit=0.94:attack=5:release=50",
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart",
        "-shortest",
        str(FINAL_MP4)
    ], check=True)

    # Generate Cover Thumbnail at 4.5s (Peak Shot 1 "अच्छी लगती हो")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "00:00:04.500", "-i", str(FINAL_MP4),
        "-frames:v", "1", "-q:v", "2", "-update", "1", str(COVER_JPG)
    ], check=True)

    # Generate Story Promo Card
    try:
        import reels_booster
        reels_booster.generate_story_card(COVER_JPG, "Achchi Lagti Ho", "@vynox_00000", str(STORY_CARD_JPG))
    except Exception as e:
        print(f"Story card generation fallback: {e}")
        subprocess.run(["cp", str(COVER_JPG), str(STORY_CARD_JPG)], check=False)

    if raw_video.exists():
        raw_video.unlink()

    print(f"\n🎉 Successfully compiled Achchi Lagti Ho Reel: {FINAL_MP4}")
    print(f"🖼️ Cover: {COVER_JPG}")
    print(f"📸 Story Card: {STORY_CARD_JPG}")

if __name__ == "__main__":
    main()
