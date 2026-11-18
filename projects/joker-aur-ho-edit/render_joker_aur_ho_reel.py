#!/usr/bin/env python3
"""
100% Realistic Live-Action Cinema Edit: The Dark Knight (Joker) - Aur Ho (Slowed + Reverb)
Created for @vynox_00000 Instagram Reels & YouTube Shorts.

Winning Architecture:
1. Authentic 1080p60 Hollywood cinema footage (Heath Ledger as Joker in The Dark Knight).
2. Vertical 9:16 (1080x1920) mobile composition with ambient blurred background & centered focus.
3. Signature Joker Emerald Neo-Noir color grading (vivid green midtones, cyan shadows, crushed blacks, 35mm grain).
4. Stylized center-screen Devanagari typography with smooth alpha sine curves.
5. Hyper-synchronized beat-drop strobe cuts aligned to A.R. Rahman & Mohit Chauhan's vocal climax.
6. Ultra-fast sequential rendering pipeline with -preset fast.
"""

import math
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# -------------------------------------------------------------
# CONFIGURATION & PATHS
# -------------------------------------------------------------
BASE_DIR = Path("projects/joker-aur-ho-edit")
RAW_VIDEO = BASE_DIR / "raw/joker_scenepack.mp4"
AUDIO_FILE = BASE_DIR / "audio/master_audio.wav"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_REEL = OUT_DIR / "The_Joker_Aur_Ho_Reel.mp4"
COVER_FILE = OUT_DIR / "cover.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 28.50
TOTAL_FRAMES = int(DURATION * FPS)  # 855 frames

print(f"🎬 Initializing 100% Realistic Live-Action Joker Edit ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# -------------------------------------------------------------
# 1. PRE-RENDER HINDI TYPOGRAPHY RGBA OVERLAYS
# -------------------------------------------------------------
font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
font_large = ImageFont.truetype(font_path, 115)
font_medium = ImageFont.truetype(font_path, 95)
font_brand = ImageFont.truetype(font_path, 55)

def render_text_overlay(text, font=font_large, y_pos=None, emerald_glow=True):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2 if y_pos is None else y_pos

    # Soft glowing emerald aura
    if emerald_glow:
        glow_offsets = [(-8, -8), (8, 8), (-8, 8), (8, -8), (0, 10), (0, -10), (10, 0), (-10, 0),
                        (-5, -5), (5, 5), (-5, 5), (5, -5)]
        for ox, oy in glow_offsets:
            draw.text((x + ox, y + oy), text, font=font, fill=(0, 160, 90, 100))

    # Inner dark shadow outline for crisp contrast
    shadow_offsets = [(-4, -4), (4, 4), (-4, 4), (4, -4), (0, 6), (0, -6), (6, 0), (-6, 0),
                      (-2, -2), (2, 2), (-2, 2), (2, -2), (0, 3), (0, -3), (3, 0), (-3, 0)]
    for ox, oy in shadow_offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 230))

    # Crisp pure white text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return np.array(img)

# Pre-render text overlays
OVERLAY_INTRO = render_text_overlay("दर्द भी तू...", font_large, y_pos=920)
OVERLAY_AUR_HO = render_text_overlay("और हो...", font_large, y_pos=900)
OVERLAY_SHOR_HO = render_text_overlay("सांस का शोर हो", font_medium, y_pos=910)
OVERLAY_TAPISH = render_text_overlay("तपिश और बढ़े", font_medium, y_pos=910)
OVERLAY_ZID_BADHE = render_text_overlay("और ज़िद बढ़े...", font_large, y_pos=900)
OVERLAY_BRAND = render_text_overlay("@vynox_00000", font_brand, y_pos=1680, emerald_glow=False)

TYPOGRAPHY_SCHEDULE = [
    (0.2, 3.2, OVERLAY_INTRO),
    (3.4, 8.5, OVERLAY_AUR_HO),
    (8.7, 11.7, OVERLAY_AUR_HO),
    (11.9, 17.4, OVERLAY_SHOR_HO),
    (17.6, 22.2, OVERLAY_TAPISH),
    (22.4, 25.8, OVERLAY_ZID_BADHE),
]

# -------------------------------------------------------------
# 2. DEFINE MASTER SHOTS TIMELINE
# -------------------------------------------------------------
SHOTS = [
    {
        "name": "Police Car Night Wind",
        "src_start": 118.0,
        "out_start": 0.0,
        "out_end": 3.30,
        "zoom": 1.90,
        "cx_ratio": 0.45,
    },
    {
        "name": "Interrogation Room Smile",
        "src_start": 217.0,
        "out_start": 3.30,
        "out_end": 8.60,
        "zoom": 1.95,
        "cx_ratio": 0.50,
    },
    {
        "name": "Jail Sarcastic Clap",
        "src_start": 151.2,
        "out_start": 8.60,
        "out_end": 11.80,
        "zoom": 1.85,
        "cx_ratio": 0.50,
    },
    {
        "name": "Hospital Detonator Walk",
        "src_start": 243.5,
        "out_start": 11.80,
        "out_end": 17.50,
        "zoom": 1.85,
        "cx_ratio": 0.50,
    },
    {
        "name": "Hospital Massive Explosion",
        "src_start": 252.0,
        "out_start": 17.50,
        "out_end": 22.30,
        "zoom": 1.80,
        "cx_ratio": 0.52,
    },
    {
        "name": "Burning Money Firelight",
        "src_start": 264.0,
        "out_start": 22.30,
        "out_end": 25.90,
        "zoom": 1.90,
        "cx_ratio": 0.48,
    },
    {
        "name": "Police Car Outro Glance",
        "src_start": 128.5,
        "out_start": 25.90,
        "out_end": 28.50,
        "zoom": 1.85,
        "cx_ratio": 0.45,
    },
]

# -------------------------------------------------------------
# 3. PRE-COMPUTE FILM GRAIN MASKS & VIGNETTE
# -------------------------------------------------------------
np.random.seed(42)
GRAIN_MASKS = [
    np.random.normal(0, 4.2, (HEIGHT, WIDTH, 3)).astype(np.float32)
    for _ in range(12)
]

# High-contrast S-curve LUT
LUT_CONTRAST = np.array([
    int(np.clip(255.0 / (1.0 + np.exp(-0.022 * (x - 128))), 0, 255))
    for x in range(256)
], dtype=np.uint8)

def apply_joker_grade(frame_bgr, grain_idx=0, is_strobe=False):
    # 1. Apply S-curve contrast via LUT
    contrast = cv2.LUT(frame_bgr, LUT_CONTRAST)
    float_img = contrast.astype(np.float32)

    # 2. Joker Emerald Neo-Noir BGR channel grading
    float_img[:, :, 1] = np.clip(float_img[:, :, 1] * 1.25 + 8, 0, 255)   # Emerald Green boost
    float_img[:, :, 0] = np.clip(float_img[:, :, 0] * 1.10 + 6, 0, 255)   # Cyan / Shadow boost
    float_img[:, :, 2] = np.clip(float_img[:, :, 2] * 0.95, 0, 255)       # Grim contrast

    # 3. Strobe beat transition flash
    if is_strobe:
        float_img = np.clip(float_img + 55, 0, 255)

    # 4. 35mm film grain
    float_img += GRAIN_MASKS[grain_idx % len(GRAIN_MASKS)]
    return np.clip(float_img, 0, 255).astype(np.uint8)

# -------------------------------------------------------------
# 4. VERTICAL 9:16 COMPOSITING ENGINE
# -------------------------------------------------------------
def composite_vertical(frame_bgr, zoom=1.85, cx_ratio=0.50):
    ih, iw = frame_bgr.shape[:2]

    # Ambient blurred background
    bg = cv2.resize(frame_bgr, (WIDTH, HEIGHT))
    bg = cv2.GaussianBlur(bg, (81, 81), 0)
    bg = (bg * 0.38).astype(np.uint8)

    # Main video with cinematic crop
    scale = (WIDTH / iw) * zoom
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)

    # Crop to WIDTH
    center_x = int(nw * cx_ratio)
    x1 = max(0, center_x - WIDTH // 2)
    x2 = x1 + WIDTH
    if x2 > nw:
        x2 = nw
        x1 = x2 - WIDTH
    cropped = resized[:, x1:x2]

    # Center vertically
    y_off = (HEIGHT - nh) // 2
    if y_off >= 0:
        bg[y_off:y_off + nh, :] = cropped
        # Subtle cinematic separation lines
        cv2.line(bg, (0, y_off), (WIDTH, y_off), (30, 45, 35), 1)
        cv2.line(bg, (0, y_off + nh - 1), (WIDTH, y_off + nh - 1), (30, 45, 35), 1)
        return bg
    else:
        y1 = (nh - HEIGHT) // 2
        return cropped[y1:y1 + HEIGHT, :]

# -------------------------------------------------------------
# 5. PREPARE FFmpeg STREAM & EXECUTE RENDER
# -------------------------------------------------------------
cap = cv2.VideoCapture(str(RAW_VIDEO))
if not cap.isOpened():
    raise RuntimeError(f"Cannot open {RAW_VIDEO}")

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
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    str(FINAL_REEL)
], stdin=subprocess.PIPE)

print("🚀 Rendering realistic live-action Joker edit with synchronized Hindi typography...")

current_shot_idx = -1
last_frame_bgr = None
best_cover_frame = None

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS

    # 1. Determine active shot
    active_shot = SHOTS[-1]
    active_shot_idx = len(SHOTS) - 1
    for idx, s in enumerate(SHOTS):
        if s["out_start"] <= t < s["out_end"]:
            active_shot = s
            active_shot_idx = idx
            break

    # 2. Seek video if new shot begins
    is_shot_transition = (active_shot_idx != current_shot_idx)
    if is_shot_transition:
        current_shot_idx = active_shot_idx
        cap.set(cv2.CAP_PROP_POS_MSEC, active_shot["src_start"] * 1000)

    # 3. Read video frame sequentially
    ret, frame_raw = cap.read()
    if not ret:
        frame_raw = last_frame_bgr if last_frame_bgr is not None else np.zeros((1080, 1920, 3), dtype=np.uint8)
    last_frame_bgr = frame_raw

    # 4. Vertical 9:16 compositing
    vertical_frame = composite_vertical(frame_raw, zoom=active_shot["zoom"], cx_ratio=active_shot["cx_ratio"])

    # 5. Apply Joker Emerald Neo-Noir color grading & strobe on transition
    is_strobe = is_shot_transition and (active_shot_idx > 0)
    graded_frame = apply_joker_grade(vertical_frame, grain_idx=frame_idx, is_strobe=is_strobe)

    # Save a frame from Interrogation Room (frame ~140, t ~ 4.6s) for high-impact cover
    if 4.5 <= t <= 4.6:
        best_cover_frame = graded_frame.copy()

    # 6. Synchronized Hindi Typography with Smooth Alpha Curves
    for t_start, t_end, overlay in TYPOGRAPHY_SCHEDULE:
        if t_start <= t <= t_end:
            fade_dur = 0.35
            if t < t_start + fade_dur:
                alpha = (t - t_start) / fade_dur
            elif t > t_end - fade_dur:
                alpha = (t_end - t) / fade_dur
            else:
                alpha = 1.0

            # Alpha blend text overlay
            alpha_mask = (overlay[:, :, 3].astype(np.float32) / 255.0) * alpha
            rgb_overlay = overlay[:, :, :3]
            for c in range(3):
                graded_frame[:, :, c] = np.clip(
                    graded_frame[:, :, c] * (1.0 - alpha_mask) + rgb_overlay[:, :, c] * alpha_mask,
                    0, 255
                ).astype(np.uint8)

    # 7. Apply subtle branding stamp (@vynox_00000)
    wm_alpha = (OVERLAY_BRAND[:, :, 3].astype(np.float32) / 255.0) * 0.70
    for c in range(3):
        graded_frame[:, :, c] = np.clip(
            graded_frame[:, :, c] * (1.0 - wm_alpha) + OVERLAY_BRAND[:, :, c] * wm_alpha,
            0, 255
        ).astype(np.uint8)

    # 8. Fade to black on the final 15 frames (0.5s)
    if frame_idx >= TOTAL_FRAMES - 15:
        fade_black = (TOTAL_FRAMES - 1 - frame_idx) / 15.0
        graded_frame = (graded_frame * fade_black).astype(np.uint8)

    # 9. Pipe frame into FFmpeg
    raw_pipe.stdin.write(graded_frame.tobytes())

    if (frame_idx + 1) % 150 == 0 or frame_idx == TOTAL_FRAMES - 1:
        pct = int(((frame_idx + 1) / TOTAL_FRAMES) * 100)
        print(f"  ⚡ Progress: {frame_idx + 1}/{TOTAL_FRAMES} frames ({pct}%)")

cap.release()
raw_pipe.stdin.close()
raw_pipe.wait()

print(f"✅ Render complete! Output: {FINAL_REEL} ({FINAL_REEL.stat().st_size / (1024*1024):.2f} MB)")

# -------------------------------------------------------------
# 6. GENERATE COVER AND STORY CARD
# -------------------------------------------------------------
if best_cover_frame is not None:
    cv2.imwrite(str(COVER_FILE), best_cover_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"✅ Generated high-CTR cover: {COVER_FILE}")

    # Generate Story Card (1080x1920 promo card with emerald border)
    story_img = Image.fromarray(cv2.cvtColor(best_cover_frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(story_img)
    draw.rectangle([(40, 40), (WIDTH - 40, HEIGHT - 40)], outline=(0, 255, 160), width=4)
    tag_font = ImageFont.truetype(font_path, 48)
    draw.text((WIDTH // 2 - 220, 200), "NEW REEL LIVE NOW ⚡", font=tag_font, fill=(0, 255, 180))
    story_img.save(str(STORY_CARD), quality=95)
    print(f"✅ Generated Story Promo Card: {STORY_CARD}")

print("🔥 All Joker Realistic Cinema Reel assets ready for release!")
