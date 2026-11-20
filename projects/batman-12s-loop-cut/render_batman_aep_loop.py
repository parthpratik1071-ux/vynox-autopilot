#!/usr/bin/env python3
"""
The Batman (2022) - 12s Ultra-Punchy Loop Cut (AEP Cinema Standard)
Engineered for >150% loop retention with @1tachi.aep benchmark graphics:
- Optical Deep Glow on turbine flames & fireballs
- Rainbow Prism anamorphic lens dispersion
- S-curve film grade (lifted milky blacks + neon crimson shadows)
- 35mm fine film grain
- Dual-Layer Typography (DejaVu Sans Bold + Great Vibes Cursive Script)
- Seamless 12.0s infinite retention loop
"""

import math
import os
import sys
import subprocess
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
    render_dual_layer_typography
)
import reels_booster

PROJECT_DIR = Path("projects/batman-12s-loop-cut")
RAW_VIDEO = Path("projects/batman-realistic-edit/raw/batman_scenepack_1080p.mp4")
AUDIO_FILE = PROJECT_DIR / "audio/batman_12s_hook.wav"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_REEL = OUT_DIR / "film_batman_12s_ultra_loop.mp4"
COVER_FILE = OUT_DIR / "cover.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 12.00
TOTAL_FRAMES = int(DURATION * FPS)  # 360 frames

SHOTS = [
    # Shot 1: Colin Farrell Penguin tension in mirror (0.0s - 0.8s)
    {"out_start": 0.0, "out_end": 0.8, "src_start": 263.8, "zoom": 2.10, "cx_ratio": 0.50},
    # Shot 2: STROBE CUT 1 - Bat-Signal in lightning storm clouds (0.8s - 1.2s)
    {"out_start": 0.8, "out_end": 1.2, "src_start": 51.5, "zoom": 1.70, "cx_ratio": 0.50},
    # Shot 3: STROBE CUT 2 - Batmobile turbine engine flame (1.2s - 1.6s)
    {"out_start": 1.2, "out_end": 1.6, "src_start": 251.5, "zoom": 1.85, "cx_ratio": 0.50},
    # Shot 4: STROBE CUT 3 - Penguin eyes widening in terror (1.6s - 2.0s)
    {"out_start": 1.6, "out_end": 2.0, "src_start": 264.4, "zoom": 2.15, "cx_ratio": 0.50},
    # Shot 5: THE BASS DROP - Batmobile flying through explosion (2.0s - 6.7s)
    {"out_start": 2.0, "out_end": 6.7, "src_start": 266.5, "zoom": 1.75, "cx_ratio": 0.50},
    # Shot 6: CLIMAX - Batman walking upside down through fire & rain (6.7s - 12.0s)
    {"out_start": 6.7, "out_end": DURATION, "src_start": 280.0, "zoom": 1.90, "cx_ratio": 0.52},
]

LYRICS = [
    (0.1, 1.8, "THE BATMAN", "I am vengeance...", (0, 229, 255, 255), (255, 255, 255, 255), -3, 68, 88, 920),
    (2.0, 6.6, "SAJAN SAJAN", "Tujhko pukaare aaja...", (255, 60, 100, 255), (255, 255, 255, 255), -4, 76, 96, 910),
    (6.8, 11.8, "TUJHKO PUKAARE", "Aaja aaja sajan...", (255, 60, 100, 255), (255, 255, 255, 255), -3, 72, 92, 920),
]


def composite_vertical(frame_bgr, zoom=1.85, cx_ratio=0.50):
    ih, iw = frame_bgr.shape[:2]
    bg = cv2.resize(frame_bgr, (WIDTH, HEIGHT))
    bg = cv2.GaussianBlur(bg, (81, 81), 0)
    bg = (bg * 0.38).astype(np.uint8)

    scale = (WIDTH / iw) * zoom
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

    center_x = int(nw * cx_ratio)
    x1 = max(0, center_x - WIDTH // 2)
    x2 = x1 + WIDTH
    if x2 > nw:
        x2 = nw
        x1 = x2 - WIDTH
    cropped = resized[:, x1:x2]

    y_off = (HEIGHT - nh) // 2
    if y_off >= 0:
        bg[y_off:y_off + nh, :] = cropped
        cv2.line(bg, (0, y_off), (WIDTH, y_off), (45, 30, 40), 1)
        cv2.line(bg, (0, y_off + nh - 1), (WIDTH, y_off + nh - 1), (45, 30, 40), 1)
        return bg
    else:
        y1 = (nh - HEIGHT) // 2
        return cropped[y1:y1 + HEIGHT, :]


def main():
    print(f"🎬 Initializing 12s Batman AEP Ultra-Loop Cut ({TOTAL_FRAMES} frames)...")
    cap = cv2.VideoCapture(str(RAW_VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open raw video: {RAW_VIDEO}")

    temp_video = PROJECT_DIR / "temp_aep_stream.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_video), fourcc, FPS, (WIDTH, HEIGHT))

    flare = generate_rainbow_prism_flare(WIDTH, HEIGHT, intensity=0.35, blur_radius=35)
    flare_norm = np.clip(flare / 255.0, 0, 1)

    current_shot_idx = -1
    last_frame_bgr = None
    best_cover_frame = None

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)

        # 1. Active shot lookup
        active_shot = SHOTS[-1]
        active_shot_idx = len(SHOTS) - 1
        for idx, s in enumerate(SHOTS):
            if s["out_start"] <= t < s["out_end"]:
                active_shot = s
                active_shot_idx = idx
                break

        # Seek if shot transition
        if active_shot_idx != current_shot_idx:
            current_shot_idx = active_shot_idx
            cap.set(cv2.CAP_PROP_POS_MSEC, active_shot["src_start"] * 1000)

        ret, frame_raw = cap.read()
        if not ret:
            frame_raw = last_frame_bgr if last_frame_bgr is not None else np.zeros((804, 1920, 3), dtype=np.uint8)
        last_frame_bgr = frame_raw

        # Dynamic zoom push-in for climax (upside-down walk)
        zoom = active_shot["zoom"]
        if active_shot_idx == 5:
            t_rel = (t - 6.7) / (DURATION - 6.7)
            zoom = 1.90 + 0.12 * t_rel

        vertical_frame = composite_vertical(frame_raw, zoom=zoom, cx_ratio=active_shot["cx_ratio"])

        # 2. VFX Pipeline: Deep Glow -> Rainbow Prism -> Cinema Grade -> 35mm Grain
        glow = apply_deep_glow(vertical_frame, threshold=165, bloom_factor=0.60, tint=(1.10, 0.85, 0.90))
        g_norm = glow.astype(np.float32) / 255.0
        flared = np.clip((1.0 - (1.0 - g_norm) * (1.0 - flare_norm)) * 255.0, 0, 255).astype(np.uint8)
        graded = apply_cinema_grade(flared, lift=12, contrast=1.15, warm_highlight=1.08, cool_shadow=1.05)
        grained = add_film_grain(graded, intensity=3.0, seed=frame_idx)

        # Strobe beat-drop flash at bass drop (t = 2.0s)
        if 2.00 <= t <= 2.12:
            strobe_intensity = math.sin((t - 2.00) / 0.12 * math.pi) * 0.55
            white_screen = np.full_like(grained, 255)
            grained = cv2.addWeighted(grained, 1.0 - strobe_intensity, white_screen, strobe_intensity, 0)

        # 3. Dual-Layer Typography
        active_lyric = None
        for lyr in LYRICS:
            if lyr[0] <= t < lyr[1]:
                active_lyric = lyr
                break

        if active_lyric:
            canvas_pil = Image.fromarray(cv2.cvtColor(grained, cv2.COLOR_BGR2RGB))
            canvas_pil = render_dual_layer_typography(
                canvas_pil,
                base_text=active_lyric[2],
                script_text=active_lyric[3],
                center_xy=(WIDTH // 2, active_lyric[9]),
                base_font_size=active_lyric[7],
                script_font_size=active_lyric[8],
                base_color=active_lyric[4],
                script_color=active_lyric[5],
                script_offset=(0, -8),
                script_angle=active_lyric[6],
                shadow_blur=12,
                shadow_alpha=220
            )
            final_bgr = cv2.cvtColor(np.array(canvas_pil), cv2.COLOR_RGB2BGR)
        else:
            final_bgr = grained

        # Cover frame at peak fireball explosion
        if 4.4 <= t <= 4.5 and best_cover_frame is None:
            best_cover_frame = final_bgr.copy()

        writer.write(final_bgr)
        if frame_idx % 60 == 0:
            print(f"  Frame {frame_idx}/{TOTAL_FRAMES} ({t:.1f}s)...")

    cap.release()
    writer.release()

    # Mux audio
    print("🎬 Muxing audio with FFmpeg...")
    cmd = f'ffmpeg -y -i "{temp_video}" -i "{AUDIO_FILE}" -af "volume=1.4,alimiter=limit=0.94:attack=5:release=50" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "{FINAL_REEL}"'
    res = os.system(cmd)
    if res != 0:
        raise RuntimeError("FFmpeg muxing failed!")

    if temp_video.exists():
        temp_video.unlink()

    # Generate Cover & Story Card
    if best_cover_frame is not None:
        cv2.imwrite(str(COVER_FILE), best_cover_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"✅ Cover saved: {COVER_FILE}")
        reels_booster.generate_story_card(str(COVER_FILE), "The Batman - Sajan Sajan", str(STORY_CARD), "@vynox_00000")
        print(f"✅ Story Card saved: {STORY_CARD}")

    print(f"✅ Batman AEP Ultra-Loop COMPLETE: {FINAL_REEL}")


if __name__ == "__main__":
    main()
