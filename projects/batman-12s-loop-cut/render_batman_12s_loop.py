#!/usr/bin/env python3
"""
12-Second Ultra-Punchy Loop Cut: The Batman (2022) - Sajan Sajan (Slowed + Reverb)
Designed specifically for >150% average watch-time loop retention on Instagram Reels.

Architecture:
1. 0.0s - 0.8s: Penguin tension in rain-soaked rearview mirror
2. 0.8s - 2.0s: Rapid 3-beat strobe flashes (Bat-Signal -> Turbine Flame -> Penguin Eyes)
3. 2.0s - 6.7s: Massive Bass Drop ("SAJAN SAJAN") - Batmobile flying through fireball
4. 6.7s - 12.0s: The Climactic Upside-Down Walk ("TUJHKO PUKAARE AAJA")
5. 11.8s - 12.0s: Seamless cut back to frame 0 for an infinite retention loop
6. English/Romanized typography (DejaVu Sans Bold) + Freakyyyy Crimson Neo-Noir grade
"""

import math
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

print(f"🎬 Initializing 12s Batman Ultra-Loop Cut ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# -------------------------------------------------------------
# 1. PRE-RENDER ENGLISH TYPOGRAPHY RGBA OVERLAYS
# -------------------------------------------------------------
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_large = ImageFont.truetype(font_path, 80)
font_huge = ImageFont.truetype(font_path, 100)
font_medium = ImageFont.truetype(font_path, 60)
font_hook = ImageFont.truetype(font_path, 36)

def render_text_overlay(text, font=font_large, y_pos=None, crimson_glow=True, custom_color=(255, 255, 255)):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2 if y_pos is None else y_pos

    # Crimson/Magenta neo-noir halo
    if crimson_glow:
        for ox, oy in [(-8, -8), (8, 8), (-8, 8), (8, -8), (0, 10), (0, -10), (10, 0), (-10, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill=(240, 30, 80, 140))
        for ox, oy in [(-4, -4), (4, 4), (-4, 4), (4, -4), (0, 5), (0, -5), (5, 0), (-5, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill=(255, 60, 120, 110))

    # Inner dark shadow outline for contrast
    shadow_offsets = [(-4, -4), (4, 4), (-4, 4), (4, -4), (0, 5), (0, -5), (5, 0), (-5, 0),
                      (-2, -2), (2, 2), (-2, 2), (2, -2), (0, 3), (0, -3), (3, 0), (-3, 0)]
    for ox, oy in shadow_offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 240))

    # Crisp text fill
    draw.text((x, y), text, font=font, fill=(custom_color[0], custom_color[1], custom_color[2], 255))
    return np.array(img)

# Pre-render overlays
OVERLAY_HOOK = render_text_overlay("SEND THIS TO YOUR BROTHER 🦇", font=font_hook, y_pos=220, crimson_glow=False, custom_color=(255, 220, 230))
OVERLAY_TEEN = render_text_overlay("HU MAIN TERE SAATH...", font_large, y_pos=920)
OVERLAY_SAJAN = render_text_overlay("SAJAN SAJAN...", font_huge, y_pos=900)
OVERLAY_PUKARE = render_text_overlay("TUJHKO PUKAARE AAJA...", font_medium, y_pos=920)
OVERLAY_BRAND = render_text_overlay("@vynox_00000", font=font_hook, y_pos=1680, crimson_glow=False)

TYPOGRAPHY_SCHEDULE = [
    (0.0, 1.8, OVERLAY_TEEN),
    (2.0, 6.5, OVERLAY_SAJAN),
    (6.7, 11.6, OVERLAY_PUKARE),
]

# -------------------------------------------------------------
# 2. DEFINING CINEMATIC SHOT CUTS & TIMINGS (12-Second Loop)
# -------------------------------------------------------------
SHOTS = [
    # Shot 1: Colin Farrell Penguin tension in mirror (0.0s - 0.8s)
    {"out_start": 0.0, "out_end": 0.8, "src_start": 263.8, "zoom": 2.10, "cx_ratio": 0.50},
    # Shot 2: STROBE CUT 1 - Bat-Signal in lightning storm clouds (0.8s - 1.2s)
    {"out_start": 0.8, "out_end": 1.2, "src_start": 51.5, "zoom": 1.70, "cx_ratio": 0.50},
    # Shot 3: STROBE CUT 2 - Batmobile turbine engine flame (1.2s - 1.6s)
    {"out_start": 1.2, "out_end": 1.6, "src_start": 251.5, "zoom": 1.85, "cx_ratio": 0.50},
    # Shot 4: STROBE CUT 3 - Colin Farrell Penguin eyes widening in terror (1.6s - 2.0s)
    {"out_start": 1.6, "out_end": 2.0, "src_start": 264.4, "zoom": 2.15, "cx_ratio": 0.50},
    # Shot 5: THE BASS DROP - Batmobile flying through explosion & landing (2.0s - 6.7s)
    {"out_start": 2.0, "out_end": 6.7, "src_start": 266.5, "zoom": 1.75, "cx_ratio": 0.50},
    # Shot 6: CLIMAX - Batman walking upside down through fire & rain (6.7s - 12.0s)
    {"out_start": 6.7, "out_end": DURATION, "src_start": 280.0, "zoom": 1.90, "cx_ratio": 0.52},
]

# -------------------------------------------------------------
# 3. COLOR GRADING LOOKUP TABLE (CRIMSON NEO-NOIR LUT)
# -------------------------------------------------------------
lut_s = np.zeros(256, dtype=np.uint8)
for i in range(256):
    norm = i / 255.0
    val = math.sin((norm - 0.5) * math.pi) * 0.5 + 0.5
    lut_s[i] = int(np.clip(val * 255, 0, 255))

GRAIN_MASKS = [
    np.random.normal(0, 3.5, (HEIGHT, WIDTH, 3)).astype(np.float32)
    for _ in range(10)
]

def apply_crimson_grade(frame_bgr, grain_idx=0):
    contrast = cv2.LUT(frame_bgr, lut_s)
    float_img = contrast.astype(np.float32)
    float_img[:, :, 2] = np.clip(float_img[:, :, 2] * 1.38 + 12, 0, 255)  # Red Boost
    float_img[:, :, 1] = np.clip(float_img[:, :, 1] * 0.72, 0, 255)       # Green Reduction
    float_img[:, :, 0] = np.clip(float_img[:, :, 0] * 1.25 + 8, 0, 255)   # Purple/Blue Tint
    float_img += GRAIN_MASKS[grain_idx % len(GRAIN_MASKS)]
    return np.clip(float_img, 0, 255).astype(np.uint8)

# -------------------------------------------------------------
# 4. VERTICAL 9:16 COMPOSITING ENGINE
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# 5. RENDER ENGINE & FFMPEG MUX
# -------------------------------------------------------------
def main():
    cap = cv2.VideoCapture(str(RAW_VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open raw video: {RAW_VIDEO}")

    raw_pipe = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "bgr24",
        "-r", str(FPS),
        "-i", "-",
        "-i", str(AUDIO_FILE),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        str(FINAL_REEL)
    ], stdin=subprocess.PIPE)

    print("🚀 Rendering 12s Batman Ultra-Loop Cut with Crimson Neo-Noir Grade...")

    current_shot_idx = -1
    last_frame_bgr = None
    best_cover_frame = None

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS

        # Active shot detection
        active_shot = SHOTS[-1]
        active_shot_idx = len(SHOTS) - 1
        for idx, s in enumerate(SHOTS):
            if s["out_start"] <= t < s["out_end"]:
                active_shot = s
                active_shot_idx = idx
                break

        # Seek if new shot begins
        if active_shot_idx != current_shot_idx:
            current_shot_idx = active_shot_idx
            cap.set(cv2.CAP_PROP_POS_MSEC, active_shot["src_start"] * 1000)

        ret, frame_raw = cap.read()
        if not ret:
            frame_raw = last_frame_bgr if last_frame_bgr is not None else np.zeros((804, 1920, 3), dtype=np.uint8)
        last_frame_bgr = frame_raw

        # Dynamic zoom push-in for climax (upside-down walk)
        zoom = active_shot["zoom"]
        if active_shot_idx == 5:  # Climax walk
            t_rel = (t - 6.7) / (DURATION - 6.7)
            zoom = 1.90 + 0.12 * t_rel  # Subtle creeping push-in

        vertical_frame = composite_vertical(frame_raw, zoom=zoom, cx_ratio=active_shot["cx_ratio"])
        graded_frame = apply_crimson_grade(vertical_frame, grain_idx=frame_idx)

        # Save peak frame for cover (at 4.5s: Batmobile flying through fireball)
        if 4.4 <= t <= 4.5:
            best_cover_frame = graded_frame.copy()

        # Permanent subtle top hook & brand watermark in safe zones
        hook_alpha = min(1.0, t / 0.5)
        if hook_alpha > 0:
            h_bgr = OVERLAY_HOOK[:, :, :3]
            h_mask = (OVERLAY_HOOK[:, :, 3:] / 255.0) * hook_alpha * 0.88
            graded_frame = (graded_frame * (1.0 - h_mask) + h_bgr * h_mask).astype(np.uint8)

        b_bgr = OVERLAY_BRAND[:, :, :3]
        b_mask = (OVERLAY_BRAND[:, :, 3:] / 255.0) * 0.65
        graded_frame = (graded_frame * (1.0 - b_mask) + b_bgr * b_mask).astype(np.uint8)

        # Synchronized English Typography with Smooth Alpha Curves
        for t_start, t_end, overlay in TYPOGRAPHY_SCHEDULE:
            if t_start <= t <= t_end:
                fade_dur = 0.25
                if t < t_start + fade_dur:
                    alpha = (t - t_start) / fade_dur
                elif t > t_end - fade_dur:
                    alpha = (t_end - t) / fade_dur
                else:
                    alpha = 1.0

                text_bgr = overlay[:, :, :3]
                text_mask = (overlay[:, :, 3:] / 255.0) * alpha
                graded_frame = (graded_frame * (1.0 - text_mask) + text_bgr * text_mask).astype(np.uint8)

        # Strobe beat-drop flash effect at beat transition (t = 2.0s)
        if 2.00 <= t <= 2.12:
            strobe_intensity = math.sin((t - 2.00) / 0.12 * math.pi) * 0.55
            white_screen = np.full_like(graded_frame, 255)
            graded_frame = cv2.addWeighted(graded_frame, 1.0 - strobe_intensity, white_screen, strobe_intensity, 0)

        raw_pipe.stdin.write(graded_frame.tobytes())

        if frame_idx % 60 == 0:
            print(f"  Frame {frame_idx}/{TOTAL_FRAMES} ({t:.1f}s / {DURATION:.1f}s)...")

    cap.release()
    raw_pipe.stdin.close()
    raw_pipe.wait()

    print(f"✅ Video render complete: {FINAL_REEL} ({FINAL_REEL.stat().st_size / (1024*1024):.2f} MB)")

    # Generate Cover
    if best_cover_frame is not None:
        cv2.imwrite(str(COVER_FILE), best_cover_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"✅ Cover generated: {COVER_FILE}")

    # Generate Companion Story Card
    story_card_img = best_cover_frame.copy() if best_cover_frame is not None else np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    banner = np.zeros_like(story_card_img)
    cv2.rectangle(banner, (0, 100), (WIDTH, 260), (10, 8, 18), -1)
    story_card_img = cv2.addWeighted(story_card_img, 1.0, banner, 0.70, 0)
    cv2.putText(story_card_img, "THE BATMAN (2022)", (WIDTH // 2 - 220, 175),
                cv2.FONT_HERSHEY_DUPLEX, 1.15, (255, 60, 100), 2, cv2.LINE_AA)
    cv2.putText(story_card_img, "12S ULTRA-LOOP EDITION | SAJAN SAJAN", (WIDTH // 2 - 280, 225),
                cv2.FONT_HERSHEY_DUPLEX, 0.60, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(story_card_img, "@vynox_00000", (WIDTH // 2 - 110, 1820),
                cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imwrite(str(STORY_CARD), story_card_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"✅ Story Card generated: {STORY_CARD}")

if __name__ == "__main__":
    main()
