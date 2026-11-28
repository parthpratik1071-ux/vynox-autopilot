#!/usr/bin/env python3
"""
Living 2D Cinematic Anime MV: "Kasoor" - Prateek Kuhad
Features:
- 4 Master Scenes with consistent Makoto Shinkai / Studio Ghibli warmth
- 60 Floating ambient golden bokeh & shimmering light motes
- Smooth 8-frame cross-dissolves between scenes
- Handheld 6-DOF camera micro-drift & scene breathing
- AEP Cinema VFX: Deep Glow bloom + Rainbow Prism flare + 35mm grain + Film S-Curve
- Clean Single-Caption Subtitles with safe-zone baseline at y = 1390
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

BASE_DIR = Path("projects/series-romantic-animations/14-kasoor-prateek-kuhad")
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_FILE = BASE_DIR / "audio" / "kasoor_clip.wav"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_VIDEO = OUT_DIR / "temp_kasoor.mp4"
FINAL_REEL = OUT_DIR / "film_kasoor_aep.mp4"
COVER_FILE = OUT_DIR / "cover_aep.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 22.00
TOTAL_FRAMES = int(DURATION * FPS)

SHOTS = [
    ("scene-1.jpg", 0.0, 5.5),
    ("scene-2.jpg", 5.5, 11.0),
    ("scene-3.jpg", 11.0, 16.5),
    ("scene-4.jpg", 16.5, DURATION)
]

LYRICS = [
    (0.5, 5.2, "Teri zulfon ki yeh nami...", (255, 255, 255, 255), 48, 1390),
    (5.5, 10.8, "Teri aankhon ka yeh nashaa...", (255, 255, 255, 255), 48, 1390),
    (11.0, 16.2, "Yahaan kho bhi jaaun toh main...", (255, 255, 255, 255), 48, 1390),
    (16.5, 21.8, "Kya kasoor hai mera?... ✨", (255, 255, 255, 255), 50, 1390)
]


def load_canvas(path):
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Missing scene: {path}")
    ih, iw = img.shape[:2]
    scale = max(WIDTH / float(iw), HEIGHT / float(ih))
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    ox = max(0, (nw - WIDTH) // 2)
    oy = max(0, (nh - HEIGHT) // 2)
    return resized[oy:oy + HEIGHT, ox:ox + WIDTH].copy()


def init_particles(n=60):
    np.random.seed(42)
    particles = []
    for _ in range(n):
        particles.append({
            "x": np.random.uniform(20, WIDTH - 20),
            "y": np.random.uniform(0, HEIGHT),
            "radius": np.random.uniform(3, 10),
            "speed": np.random.uniform(0.8, 2.0),
            "alpha": np.random.uniform(0.20, 0.55),
            "phase": np.random.uniform(0, math.pi * 2),
            "color": random.choice([
                (70, 210, 255),   # Golden amber
                (255, 235, 200),  # Warm white
                (170, 180, 255),  # Soft peach rose
                (230, 210, 255)   # Stardust violet
            ])
        })
    return particles


def draw_particles(frame, particles, t):
    overlay = frame.copy()
    for p in particles:
        py = int((p["y"] - t * p["speed"] * 45) % HEIGHT)
        px = int(p["x"] + math.sin(t * 1.2 + p["phase"]) * 18)
        px = max(5, min(px, WIDTH - 5))
        rad = int(p["radius"] * (1.0 + 0.25 * math.sin(t * 2.5 + p["phase"])))
        cv2.circle(overlay, (px, py), rad, p["color"], -1, cv2.LINE_AA)
    return cv2.addWeighted(overlay, 0.40, frame, 0.60, 0)


def render():
    print(f"🎬 Rendering Living 2D Anime MV: Kasoor ({TOTAL_FRAMES} frames)...")
    scenes = [load_canvas(ASSETS_DIR / s[0]) for s in SHOTS]
    particles = init_particles(60)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(TEMP_VIDEO), fourcc, FPS, (WIDTH, HEIGHT))

    flare = generate_rainbow_prism_flare(WIDTH, HEIGHT, intensity=0.38, blur_radius=42)
    flare_norm = np.clip(flare / 255.0, 0, 1)

    cover_saved = False
    cross_frames = 10

    for f in range(TOTAL_FRAMES):
        t = f / float(FPS)

        # 1. Determine active shot & compute smooth cross-dissolve
        shot_idx = 0
        for i, s in enumerate(SHOTS):
            if s[1] <= t < s[2]:
                shot_idx = i
                break

        curr_img = scenes[shot_idx]
        s_start, s_end = SHOTS[shot_idx][1], SHOTS[shot_idx][2]
        t_shot = t - s_start
        dur_shot = s_end - s_start

        # Shot-specific dynamic movement
        if shot_idx == 0:
            # Pensive by window: subtle slow push-in + breath
            zoom = 1.0 + 0.03 * (t_shot / dur_shot)
            M = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom)
            base = cv2.warpAffine(curr_img, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
        elif shot_idx == 1:
            # Girl with Polaroid camera: soft lateral drift + breathing
            dx = math.sin(t_shot * 0.8) * 4.0
            zoom = 1.0 + 0.02 * math.sin(t_shot * 0.6)
            M = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom)
            M[0, 2] += dx
            base = cv2.warpAffine(curr_img, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
        elif shot_idx == 2:
            # Polaroid photos on fairy lights: floating detail drift
            dy = math.sin(t_shot * 1.2) * 3.5
            zoom = 1.0 + 0.025 * (t_shot / dur_shot)
            M = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom)
            M[1, 2] += dy
            base = cv2.warpAffine(curr_img, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)
        else:
            # Wrapped in blanket under stars: gentle upward float
            dy = -2.0 * (t_shot / dur_shot) * 10.0
            zoom = 1.0 + 0.035 * (t_shot / dur_shot)
            M = cv2.getRotationMatrix2D((WIDTH // 2, HEIGHT // 2), 0, zoom)
            M[1, 2] += dy
            base = cv2.warpAffine(curr_img, M, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

        # Cross-fade with previous shot
        if shot_idx > 0:
            frame_in_shot = f - int(s_start * FPS)
            if 0 <= frame_in_shot < cross_frames:
                alpha = frame_in_shot / float(cross_frames)
                prev_img = scenes[shot_idx - 1]
                base = cv2.addWeighted(prev_img, 1.0 - alpha, base, alpha, 0)

        # 2. Living Bokeh & Light Particles
        with_particles = draw_particles(base, particles, t)

        # 3. Handheld 6-DOF Camera Micro-drift
        drift_x = math.sin(t * 0.7) * 2.0
        drift_y = math.cos(t * 0.5) * 1.5
        M_drift = np.float32([[1, 0, drift_x], [0, 1, drift_y]])
        drifted = cv2.warpAffine(with_particles, M_drift, (WIDTH, HEIGHT), borderMode=cv2.BORDER_REFLECT)

        # 4. AEP Cinema VFX: Deep Glow -> Rainbow Prism -> Cinema Grade -> 35mm Grain
        glow = apply_deep_glow(drifted, threshold=175, bloom_factor=0.52, tint=(0.95, 1.05, 1.15))
        g_norm = glow.astype(np.float32) / 255.0
        flared = np.clip((1.0 - (1.0 - g_norm) * (1.0 - flare_norm)) * 255.0, 0, 255).astype(np.uint8)
        graded = apply_cinema_grade(flared, lift=12, contrast=1.12, warm_highlight=1.07, cool_shadow=1.03)
        grained = add_film_grain(graded, intensity=2.8, seed=f)

        # 5. Clean Single-Caption Subtitles at safe-zone y = 1390
        active_lyric = None
        for lyr in LYRICS:
            if lyr[0] <= t < lyr[1]:
                active_lyric = lyr
                break

        if active_lyric:
            canvas_pil = Image.fromarray(cv2.cvtColor(grained, cv2.COLOR_BGR2RGB))
            canvas_pil = render_cinema_single_caption(
                canvas_pil,
                text=active_lyric[2],
                center_xy=(WIDTH // 2, active_lyric[5]),
                font_size=active_lyric[4],
                text_color=active_lyric[3],
                tracking=1,
                shadow_blur=8,
                shadow_alpha=230,
                max_width=840
            )
            final_bgr = cv2.cvtColor(np.array(canvas_pil), cv2.COLOR_RGB2BGR)
        else:
            final_bgr = grained

        if not cover_saved and t >= 8.0:
            cv2.imwrite(str(COVER_FILE), final_bgr)
            cover_saved = True

        writer.write(final_bgr)

        if f % 150 == 0:
            print(f"Rendered: {f}/{TOTAL_FRAMES} frames ({t:.1f}s / {DURATION:.1f}s)...")

    writer.release()
    print("✅ Video frames rendered successfully.")

    # Generate Story Promo Card
    if COVER_FILE.exists():
        cv2.imwrite(str(STORY_CARD), cv2.imread(str(COVER_FILE)))

    # Mux High-Fidelity Audio
    print("🎬 Muxing high-fidelity audio with FFmpeg...")
    cmd = (
        f'ffmpeg -y -i "{TEMP_VIDEO}" -i "{AUDIO_FILE}" '
        f'-af "volume=1.4,alimiter=limit=0.94:attack=5:release=50" '
        f'-c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p '
        f'-c:a aac -b:a 320k -shortest "{FINAL_REEL}"'
    )
    subprocess.run(cmd, shell=True, check=True)

    if TEMP_VIDEO.exists():
        TEMP_VIDEO.unlink()

    print(f"🎉 Kasoor Master Film Ready: {FINAL_REEL}")


if __name__ == "__main__":
    render()
