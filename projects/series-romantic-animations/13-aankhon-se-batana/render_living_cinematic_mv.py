#!/usr/bin/env python3
"""
Living 2D Cinematic Anime Music Video Engine: "Aankhon Se Batana" (Dikshant)
Priority 3: Proven Anuv Jain / Indie Acoustic Aesthetic

Features:
- 4 Distinct Cinematic Shots timed to musical beats:
  1. Shot 1 (0.0s - 7.2s): Cozy Rooftop Terrace at Dusk (0.0s acoustic hook, breathing, fairy light glow, gentle evening breeze)
  2. Shot 2 (7.2s - 14.2s): Intimate Eye-Contact Close-up (Soft eye gaze, delicate blush, warm amber bokeh)
  3. Shot 3 (14.2s - 21.0s): Warm Terrace Laugh & Tea (Soft lateral pan, twinkling city lights below, cozy indie vibe)
  4. Shot 4 (21.0s - 27.56s): Climactic Starry Sky Panorama (Starfield shimmer, hand-in-hand terrace silhouette, poetic finale)
- 120 Floating warm golden bokeh particles & fairy light shimmering motes
- Smooth 6-frame cinematic cross-dissolve transitions between shots
- Handheld camera 6-DOF micro-drift on every shot
- Synchronized Noto Sans Devanagari ASS Subtitles in Instagram safe zone (MarginV=540)
- Automatic Cover & Story Card generation
"""

import math
import random
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np

PROJECT_DIR = Path("projects/series-romantic-animations/13-aankhon-se-batana")
ASSETS_DIR = PROJECT_DIR / "assets"
AUDIO_FILE = PROJECT_DIR / "audio" / "aankhon_se_batana_hook.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_MP4 = OUT_DIR / "film_aankhon_se_batana_animation.mp4"
SUBTITLE_ASS = OUT_DIR / "aankhon_se_batana_subtitles.ass"
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
Title: Aankhon Se Batana - Living 2D Anime MV
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {WIDTH}
PlayResY: {HEIGHT}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: BrandHeader,Noto Sans Devanagari,34,&H00FFFFFF,&H000000FF,&H90000000,&H60000000,-1,0,0,0,100,100,2,0,1,2.0,1.0,8,60,60,180,1
Style: LyricGold,Noto Sans Devanagari,64,&H00FFFFFF,&H000000FF,&H90050810,&H80000000,-1,0,0,0,100,100,1,0,1,3.8,2.2,2,80,80,540,1
Style: LyricAccent,Noto Sans Devanagari,66,&H003CE0FF,&H000000FF,&H90050810,&H80000000,-1,0,0,0,100,100,1,0,1,4.0,2.5,2,80,80,540,1
Style: ClimaxTitle,Noto Sans Devanagari,50,&H00E8F4FF,&H000000FF,&H90000000,&H70000000,-1,0,0,0,100,100,2,0,1,2.5,1.5,2,60,60,540,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.20,0:00:04.20,BrandHeader,,0,0,180,,{{\\fad(250,400)}}DIKSHANT  |  {{\\c&H003CE0FF&}}AANKHON SE BATANA
Dialogue: 1,0:00:00.00,0:00:04.50,LyricGold,,0,0,540,,{{\\fad(150,200)}}तुम {{\\c&H003CE0FF&}}आँखों से बताना{{\\c&H00FFFFFF&}}, हम समझ जाएँगे... 🕊️
Dialogue: 1,0:00:04.50,0:00:09.20,LyricAccent,,0,0,540,,{{\\fad(200,200)}}तुम {{\\c&H00FFB040&}}हल्की सी शर्माना{{\\c&H00FFFFFF&}}, हम तेरे हो जाएँगे... ✨
Dialogue: 1,0:00:09.20,0:00:14.20,LyricGold,,0,0,540,,{{\\fad(200,200)}}तुम {{\\c&H003CE0FF&}}आँखों से बताना{{\\c&H00FFFFFF&}}, हम समझ जाएँगे... 🌸
Dialogue: 1,0:00:14.20,0:00:20.80,LyricAccent,,0,0,540,,{{\\fad(200,200)}}हम {{\\c&H003CE0FF&}}संवर जाएँगे{{\\c&H00FFFFFF&}}, हम {{\\c&H00FFB040&}}तेरे हो जाएँगे{{\\c&H00FFFFFF&}}... 🥀
Dialogue: 2,0:00:21.00,0:00:27.20,ClimaxTitle,,0,0,540,,{{\\fad(200,600)}}आँखों से बताना  |  दीक्षांत
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

def apply_handheld_drift(frame, t, amp_x=2.2, amp_y=1.6):
    dx = math.sin(t * 0.7) * amp_x + math.sin(t * 1.3) * 0.6
    dy = math.cos(t * 0.5) * amp_y + math.cos(t * 1.1) * 0.4
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(frame, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

def init_bokeh_system(n=120):
    np.random.seed(42)
    particles = []
    for _ in range(n):
        radius = np.random.uniform(4, 18)
        speed = np.random.uniform(0.6, 2.2)
        alpha = np.random.uniform(0.15, 0.45)
        color = random.choice([
            (60, 224, 255),   # Golden amber
            (255, 230, 180),  # Soft warm white
            (180, 200, 255),  # Peach highlight
            (220, 180, 255)   # Lavender dust
        ])
        particles.append({
            "x": np.random.uniform(0, WIDTH),
            "y": np.random.uniform(0, HEIGHT),
            "radius": radius,
            "speed": speed,
            "alpha": alpha,
            "color": color,
            "drift_phase": np.random.uniform(0, math.pi * 2)
        })
    return particles

def update_and_draw_bokeh(frame, particles, t):
    overlay = np.zeros_like(frame)
    for p in particles:
        p["y"] -= p["speed"]
        p["x"] += math.sin(t * 1.5 + p["drift_phase"]) * 0.8

        if p["y"] < -20:
            p["y"] = HEIGHT + np.random.uniform(10, 50)
            p["x"] = np.random.uniform(0, WIDTH)

        cx = int(p["x"])
        cy = int(p["y"])
        r = int(p["radius"])
        # Draw soft circle
        b, g, r_col = p["color"]
        a = p["alpha"] * (0.8 + 0.2 * math.sin(t * 2.0 + p["drift_phase"]))
        cv2.circle(overlay, (cx, cy), r, (int(b * a), int(g * a), int(r_col * a)), -1)

    return cv2.add(frame, overlay)

def generate_cover_image(frame, out_path):
    cover = frame.copy()
    overlay = np.zeros_like(cover)
    cv2.rectangle(overlay, (0, 700), (WIDTH, 1220), (12, 10, 20), -1)
    cover = cv2.addWeighted(cover, 1.0, overlay, 0.55, 0)
    cv2.putText(cover, "AANKHON SE BATANA", (WIDTH // 2 - 300, 890),
                cv2.FONT_HERSHEY_DUPLEX, 1.25, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(cover, "DIKSHANT  |  INDIE ACOUSTIC", (WIDTH // 2 - 250, 950),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (60, 224, 255), 2, cv2.LINE_AA)
    cv2.putText(cover, "LIVING 2D ANIME ROMANCE", (WIDTH // 2 - 220, 1010),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, (220, 215, 235), 1, cv2.LINE_AA)
    cv2.imwrite(str(out_path), cover, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"📸 Cover generated: {out_path}")

def generate_story_card(cover_path, out_path, handle="@vynox_00000"):
    c = cv2.imread(str(cover_path))
    if c is None:
        return
    card = cv2.resize(c, (WIDTH, HEIGHT))
    banner = np.zeros_like(card)
    cv2.rectangle(banner, (0, 100), (WIDTH, 260), (18, 14, 28), -1)
    card = cv2.addWeighted(card, 1.0, banner, 0.65, 0)
    cv2.putText(card, "NEW INDIE ACOUSTIC REEL", (WIDTH // 2 - 280, 180),
                cv2.FONT_HERSHEY_DUPLEX, 1.1, (60, 224, 255), 2, cv2.LINE_AA)
    cv2.putText(card, "TAP TO WATCH IN FULL HD", (WIDTH // 2 - 180, 225),
                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(card, handle, (WIDTH // 2 - 110, 1820),
                cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imwrite(str(out_path), card, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"📱 Story Card generated: {out_path}")

def main():
    print(f"🎬 Initializing Aankhon Se Batana MV Engine ({TOTAL_FRAMES} frames @ {FPS} fps)...")
    write_subtitles()

    for p in [ASSETS_DIR / f"scene-{i}.jpg" for i in range(1, 5)]:
        if not p.exists():
            print(f"Waiting for {p.name}...")
            sys.exit(2)

    c1 = load_canvas(ASSETS_DIR / "scene-1.jpg")
    c2 = load_canvas(ASSETS_DIR / "scene-2.jpg")
    c3 = load_canvas(ASSETS_DIR / "scene-3.jpg")
    c4 = load_canvas(ASSETS_DIR / "scene-4.jpg")
    print("✅ Loaded all 4 scene canvases.")

    bokeh = init_bokeh_system(120)

    raw_video = OUT_DIR / "raw_video.mp4"
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(raw_video)
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    t1_end = 7.2
    t2_end = 14.2
    t3_end = 21.0
    f_total = TOTAL_FRAMES
    f_cross = 6

    cover_saved = False

    for f in range(f_total):
        t = f / FPS

        if t < t1_end:
            zoom = 1.0 + 0.025 * (t / t1_end)
            breath = 1.0 + 0.006 * math.sin(t * 1.6)
            M_scale = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom * breath)
            base = cv2.warpAffine(c1, M_scale, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
        elif t < t2_end:
            t_rel = (t - t1_end) / (t2_end - t1_end)
            zoom = 1.0 + 0.035 * t_rel
            M_scale = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom)
            base = cv2.warpAffine(c2, M_scale, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
            if f - int(t1_end * FPS) < f_cross:
                alpha = (f - int(t1_end * FPS)) / f_cross
                prev = cv2.warpAffine(c1, cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, 1.025), (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
                base = cv2.addWeighted(prev, 1.0 - alpha, base, alpha, 0)
        elif t < t3_end:
            t_rel = (t - t2_end) / (t3_end - t2_end)
            pan_x = math.sin(t_rel * math.pi) * 6.0
            M_pan = np.float32([[1, 0, pan_x], [0, 1, 0]])
            base = cv2.warpAffine(c3, M_pan, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
            if f - int(t2_end * FPS) < f_cross:
                alpha = (f - int(t2_end * FPS)) / f_cross
                prev = cv2.warpAffine(c2, cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, 1.035), (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
                base = cv2.addWeighted(prev, 1.0 - alpha, base, alpha, 0)
        else:
            t_rel = (t - t3_end) / (DURATION - t3_end)
            zoom = 1.0 + 0.03 * t_rel
            M_scale = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom)
            base = cv2.warpAffine(c4, M_scale, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
            if f - int(t3_end * FPS) < f_cross:
                alpha = (f - int(t3_end * FPS)) / f_cross
                prev = cv2.warpAffine(c3, np.float32([[1, 0, 0], [0, 1, 0]]), (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
                base = cv2.addWeighted(prev, 1.0 - alpha, base, alpha, 0)

        frame = update_and_draw_bokeh(base, bokeh, t)
        frame = apply_handheld_drift(frame, t)

        if not cover_saved and t >= 8.0:
            generate_cover_image(frame, COVER_JPG)
            generate_story_card(COVER_JPG, STORY_CARD_JPG)
            cover_saved = True

        proc.stdin.write(frame.tobytes())

        if f % 90 == 0:
            print(f"Rendering: {f}/{f_total} frames ({t:.1f}s / {DURATION:.1f}s)...")

    proc.stdin.close()
    proc.wait()
    print("✅ Raw video rendering complete.")

    print("🔥 Burning ASS Subtitles and muxing Slowed + Reverb audio...")
    burn_cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(AUDIO_FILE),
        "-vf", f"ass={SUBTITLE_ASS}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(FINAL_MP4)
    ]
    subprocess.run(burn_cmd, check=True)

    if raw_video.exists():
        raw_video.unlink()

    print(f"🎉 Final Living Anime MV ready: {FINAL_MP4}")

if __name__ == "__main__":
    main()
