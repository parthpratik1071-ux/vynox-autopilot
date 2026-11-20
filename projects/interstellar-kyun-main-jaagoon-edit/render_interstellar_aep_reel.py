"""
AEP Cinema Edition: Interstellar (Christopher Nolan) x Kyun Main Jaagoon (Slowed + Reverb)
Upgrades Interstellar edit to 1tachi.aep benchmark quality:
- Cosmic Deep Glow on accretion disk and tears
- Anamorphic horizontal / diagonal cyan-amber flare
- Dual-Layer Typography (Bold Block Sans + Flowing Great Vibes Cursive Script)
- S-Curve film grade with lifted milky blacks and 35mm grain
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

sys.path.insert(0, os.path.abspath("scripts"))
from aep_cinema_engine import (
    generate_rainbow_prism_flare,
    apply_deep_glow,
    apply_cinema_grade,
    add_film_grain,
    render_dual_layer_typography
)

BASE_DIR = Path("projects/interstellar-kyun-main-jaagoon-edit")
AUDIO_FILE = BASE_DIR / "audio/master_audio.wav"
OUT_DIR = BASE_DIR / "output"
FINAL_REEL = OUT_DIR / "Interstellar_Kyun_Main_Jaagoon_Reel.mp4"
TEMP_VIDEO = OUT_DIR / "temp_aep_interstellar.mp4"
COVER_FILE = OUT_DIR / "cover.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 28.50
TOTAL_FRAMES = int(DURATION * FPS)

# Master Shots
SHOTS = [
    {
        "name": "Earth Departure Dust",
        "file": OUT_DIR / "shot1_departure.mp4",
        "out_start": 0.0,
        "out_end": 3.80,
        "zoom": 1.40,
        "cx_ratio": 0.50,
    },
    {
        "name": "Gargantua Black Hole",
        "file": OUT_DIR / "shot2_gargantua.mp4",
        "out_start": 3.80,
        "out_end": 9.20,
        "zoom": 1.45,
        "cx_ratio": 0.50,
    },
    {
        "name": "Video Messages Tears",
        "file": OUT_DIR / "shot3_crying.mp4",
        "out_start": 9.20,
        "out_end": 15.20,
        "zoom": 1.55,
        "cx_ratio": 0.50,
    },
    {
        "name": "Wormhole Transit",
        "file": OUT_DIR / "shot4_wormhole.mp4",
        "out_start": 15.20,
        "out_end": 20.60,
        "zoom": 1.40,
        "cx_ratio": 0.50,
    },
    {
        "name": "Tesseract Bookshelf",
        "file": OUT_DIR / "shot5_tesseract.mp4",
        "out_start": 20.60,
        "out_end": 25.80,
        "zoom": 1.40,
        "cx_ratio": 0.50,
    },
    {
        "name": "Cosmic Solitude Outro",
        "file": OUT_DIR / "shot6_ending_tears.mp4",
        "out_start": 25.80,
        "out_end": 28.50,
        "zoom": 1.50,
        "cx_ratio": 0.50,
    },
]

# Dual-Layer Typography Schedule
# (start_s, end_s, base_text, script_text, base_col, script_col, angle, base_size, script_size, y_pos)
LYRICS = [
    (0.2, 4.5, "BOONDEIN TERE", "Jaise moti saja...", (255, 176, 64, 255), (255, 255, 255, 255), -3, 62, 86, 1480),
    (4.8, 10.5, "DHUNDHLE LAGE", "Saare jahan...", (0, 229, 255, 255), (255, 255, 255, 255), -3, 62, 88, 1480),
    (10.8, 16.0, "MUJHKO MITA DE", "Mere rabba...", (255, 176, 64, 255), (255, 255, 255, 255), -4, 62, 88, 1480),
    (16.2, 21.0, "KYUN MAIN JAAGOON", "Main jaagoon...", (0, 229, 255, 255), (255, 255, 255, 255), -4, 64, 92, 1480),
    (21.2, 25.5, "AANSU MERE", "Behne lage...", (255, 176, 64, 255), (255, 255, 255, 255), -3, 62, 88, 1480),
    (25.8, 28.3, "INTERSTELLAR", "Christopher Nolan", (255, 255, 255, 255), (255, 213, 79, 255), 0, 72, 84, 1480),
]


def render():
    print("=== Rendering AEP Cinema Interstellar Edit ===")
    caps = {}
    for s in SHOTS:
        c = cv2.VideoCapture(str(s["file"]))
        if not c.isOpened():
            raise RuntimeError(f"Cannot open {s['file']}")
        caps[s["name"]] = c

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(TEMP_VIDEO), fourcc, FPS, (WIDTH, HEIGHT))

    flare = generate_rainbow_prism_flare(WIDTH, HEIGHT, intensity=0.35, blur_radius=45)
    flare_norm = np.clip(flare / 255.0, 0, 1)

    cover_saved = False

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)

        # Find current shot
        shot = None
        for s in SHOTS:
            if s["out_start"] <= t < s["out_end"]:
                shot = s
                break
        if shot is None:
            shot = SHOTS[-1]

        c = caps[shot["name"]]
        ret, frame_bgr = c.read()
        if not ret:
            c.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame_bgr = c.read()

        # Ambient 9:16 vertical layout
        ih, iw = frame_bgr.shape[:2]
        small_bg = cv2.resize(frame_bgr, (270, 480))
        small_bg = cv2.GaussianBlur(small_bg, (25, 25), 0)
        bg = cv2.resize(small_bg, (WIDTH, HEIGHT))
        bg = (bg * 0.35).astype(np.uint8)

        # Scale main video
        scale = (WIDTH / float(iw)) * shot["zoom"]
        nw, nh = int(iw * scale), int(ih * scale)
        scaled = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)

        ideal_cx = int(nw * shot["cx_ratio"])
        crop_x = max(0, min(ideal_cx - WIDTH // 2, nw - WIDTH))

        if nh <= HEIGHT:
            start_y = (HEIGHT - nh) // 2
            bg[start_y:start_y + nh, 0:WIDTH] = scaled[:, crop_x:crop_x + WIDTH]
        else:
            start_y = (nh - HEIGHT) // 2
            bg = scaled[start_y:start_y + HEIGHT, crop_x:crop_x + WIDTH]

        # VFX: Optical Deep Glow + Prism Flare + Cinema S-Curve + 35mm Grain
        glow = apply_deep_glow(bg, threshold=170, bloom_factor=0.50, tint=(1.15, 1.05, 0.90))
        g_norm = glow.astype(np.float32) / 255.0
        flared = np.clip((1.0 - (1.0 - g_norm) * (1.0 - flare_norm)) * 255.0, 0, 255).astype(np.uint8)
        graded = apply_cinema_grade(flared, lift=12, contrast=1.12, warm_highlight=1.06, cool_shadow=1.05)
        grained = add_film_grain(graded, intensity=3.2, seed=frame_idx)

        # Dual-Layer Typography
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

        if not cover_saved and t >= 12.0:
            cv2.imwrite(str(COVER_FILE), final_bgr)
            cover_saved = True

        writer.write(final_bgr)

        if frame_idx % 150 == 0:
            print(f"Interstellar: Rendered {frame_idx}/{TOTAL_FRAMES} frames ({t:.1f}s)")

    for c in caps.values():
        c.release()
    writer.release()

    print("Muxing audio with FFmpeg...")
    cmd = f'ffmpeg -y -i "{TEMP_VIDEO}" -i "{AUDIO_FILE}" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "{FINAL_REEL}"'
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError("FFmpeg muxing failed!")
    print(f"=== Interstellar AEP Upgrade Complete: {FINAL_REEL} ===")


if __name__ == "__main__":
    render()
