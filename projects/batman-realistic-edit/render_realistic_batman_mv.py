#!/usr/bin/env python3
"""
100% Realistic Live-Action Cinema Edit: The Batman (2022) - Sajan Sajan (Slowed + Reverb)
Inspired directly by @freakyyyy.exe's viral Instagram Reel.

Pipeline:
1. Authentic 4K/1080p Hollywood footage from The Batman (Robert Pattinson).
2. Vertical 9:16 (1080x1920) mobile composition with cinematic 2.39:1 zoom & ambient motion glow.
3. Iconic Freakyyyy Crimson/Magenta neo-noir color grading (deep blacks, saturated crimson neon).
4. Signature center-screen stylized Hindi typography with smooth alpha fading.
5. Hyper-synchronized beat-drop strobe cuts (Bat-Signal, Batmobile flame, Penguin mirror).
6. 48kHz stereo master audio integration and custom cover/story card generation.
"""

import math
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAW_VIDEO = Path("projects/batman-realistic-edit/raw/batman_scenepack_1080p.mp4")
AUDIO_FILE = Path("projects/batman-sajan-sajan-edit/audio/master_audio.wav")
OUT_DIR = Path("projects/batman-realistic-edit/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_REEL = OUT_DIR / "The_Batman_Realistic_Sajan_Sajan_Reel.mp4"
COVER_FILE = OUT_DIR / "cover.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 28.53
TOTAL_FRAMES = int(DURATION * FPS)

print(f"🎬 Initializing 100% Realistic Live-Action Batman Edit ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# -------------------------------------------------------------
# 1. PRE-RENDER HINDI TYPOGRAPHY RGBA OVERLAYS
# -------------------------------------------------------------
font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
font_large = ImageFont.truetype(font_path, 115)
font_medium = ImageFont.truetype(font_path, 95)

def render_text_overlay(text, font=font_large, y_pos=None):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2 if y_pos is None else y_pos

    # Soft glowing black shadow outline
    glow_offsets = [(-4, -4), (4, 4), (-4, 4), (4, -4), (0, 6), (0, -6), (6, 0), (-6, 0),
                    (-2, -2), (2, 2), (-2, 2), (2, -2), (0, 3), (0, -3), (3, 0), (-3, 0)]
    for ox, oy in glow_offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 220))

    # Crisp pure white text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return np.array(img)

# Typography timeline schedule: (start_sec, end_sec, overlay_array)
TYPOGRAPHY_SCHEDULE = [
    (0.6, 5.0, render_text_overlay("चाँदनी")),
    (5.8, 10.5, render_text_overlay("सजन")),
    (11.2, 15.4, render_text_overlay("हूँ तेरे साथ")),
    (16.8, 21.2, render_text_overlay("साजन साजन")),
    (21.8, 28.0, render_text_overlay("तुझको पुकारे आजा", font=font_medium)),
]

# -------------------------------------------------------------
# 2. DEFINING CINEMATIC SHOT CUTS & TIMINGS
# -------------------------------------------------------------
# Each shot defines: (start_out_sec, end_out_sec, source_start_sec, zoom_factor, crop_offset_x)
SHOTS = [
    # Shot 1: Bruce Wayne walking through the rainy crowd (0.0s - 5.5s)
    {"out_start": 0.0, "out_end": 5.5, "src_start": 24.0, "zoom": 1.75, "cx_ratio": 0.50},
    # Shot 2: Batman marching through police corridor (5.5s - 11.0s)
    {"out_start": 5.5, "out_end": 11.0, "src_start": 158.5, "zoom": 1.85, "cx_ratio": 0.50},
    # Shot 3: Brooding Bruce Wayne in Batcave turning to camera (11.0s - 15.6s)
    {"out_start": 11.0, "out_end": 15.6, "src_start": 173.0, "zoom": 1.95, "cx_ratio": 0.58},
    # Shot 4: BEAT DROP STROBE CUT 1 - Bat-Signal in stormy clouds (15.6s - 16.0s)
    {"out_start": 15.6, "out_end": 16.0, "src_start": 51.5, "zoom": 1.70, "cx_ratio": 0.50},
    # Shot 5: BEAT DROP STROBE CUT 2 - Batmobile turbine engine flame (16.0s - 16.4s)
    {"out_start": 16.0, "out_end": 16.4, "src_start": 251.5, "zoom": 1.80, "cx_ratio": 0.50},
    # Shot 6: BEAT DROP STROBE CUT 3 - Colin Farrell Penguin reaction (16.4s - 16.8s)
    {"out_start": 16.4, "out_end": 16.8, "src_start": 264.2, "zoom": 2.05, "cx_ratio": 0.50},
    # Shot 7: THE BASS DROP - Batmobile flying through explosion / flipping car (16.8s - 21.5s)
    {"out_start": 16.8, "out_end": 21.5, "src_start": 266.5, "zoom": 1.75, "cx_ratio": 0.50},
    # Shot 8: CLIMACTIC OUTRO - Batman walking upside down through fire & rain (21.5s - 28.53s)
    {"out_start": 21.5, "out_end": DURATION, "src_start": 280.0, "zoom": 1.90, "cx_ratio": 0.52},
]

# -------------------------------------------------------------
# 3. COLOR GRADING LOOKUP TABLE (CRIMSON NEO-NOIR LUT)
# -------------------------------------------------------------
# Contrast S-curve
lut_s = np.zeros(256, dtype=np.uint8)
for i in range(256):
    norm = i / 255.0
    val = math.sin((norm - 0.5) * math.pi) * 0.5 + 0.5
    lut_s[i] = int(np.clip(val * 255, 0, 255))

# Pre-generate 10 frames of 35mm film grain
GRAIN_MASKS = [
    np.random.normal(0, 3.5, (HEIGHT, WIDTH, 3)).astype(np.float32)
    for _ in range(10)
]

def apply_crimson_grade(frame_bgr, grain_idx=0):
    """
    Signature Freakyyyy Neo-Noir Crimson Grading:
    - S-Curve contrast stretch
    - Boosted reds & magentas, pulled down green
    - Fine 35mm cinematic film grain
    """
    contrast = cv2.LUT(frame_bgr, lut_s)
    float_img = contrast.astype(np.float32)

    # BGR channel grading
    float_img[:, :, 2] = np.clip(float_img[:, :, 2] * 1.38 + 12, 0, 255)  # Crimson Red Boost
    float_img[:, :, 1] = np.clip(float_img[:, :, 1] * 0.72, 0, 255)       # Green Reduction
    float_img[:, :, 0] = np.clip(float_img[:, :, 0] * 1.25 + 8, 0, 255)   # Purple/Blue Tint

    # Add film grain
    float_img += GRAIN_MASKS[grain_idx % len(GRAIN_MASKS)]
    return np.clip(float_img, 0, 255).astype(np.uint8)

# -------------------------------------------------------------
# 4. VERTICAL 9:16 COMPOSITING ENGINE
# -------------------------------------------------------------
def composite_vertical(frame_bgr, zoom=1.85, cx_ratio=0.50):
    """
    Creates full-bleed vertical 9:16 composition:
    1. Zoomed, centered subject with smooth edges
    2. Subtle ambient blurred glow filling top & bottom
    """
    ih, iw = frame_bgr.shape[:2]

    # 1. Ambient blurred background
    bg = cv2.resize(frame_bgr, (WIDTH, HEIGHT))
    bg = cv2.GaussianBlur(bg, (81, 81), 0)
    bg = (bg * 0.38).astype(np.uint8)

    # 2. Main video with cinematic crop
    scale = (WIDTH / iw) * zoom
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_LANCZOS4)

    # Crop to WIDTH, NH
    center_x = int(nw * cx_ratio)
    x1 = max(0, center_x - WIDTH // 2)
    x2 = x1 + WIDTH
    if x2 > nw:
        x2 = nw
        x1 = x2 - WIDTH
    cropped = resized[:, x1:x2]

    # Place in vertical center
    y_off = (HEIGHT - nh) // 2
    if y_off >= 0:
        bg[y_off:y_off + nh, :] = cropped
        # Subtle horizontal separation lines
        cv2.line(bg, (0, y_off), (WIDTH, y_off), (45, 30, 40), 1)
        cv2.line(bg, (0, y_off + nh - 1), (WIDTH, y_off + nh - 1), (45, 30, 40), 1)
        return bg
    else:
        # If nh exceeds HEIGHT, crop vertically
        y1 = (nh - HEIGHT) // 2
        return cropped[y1:y1 + HEIGHT, :]

# -------------------------------------------------------------
# 5. OPEN SOURCE VIDEO & PREPARE FFmpeg STREAM
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
    "-crf", "17",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    str(FINAL_REEL)
], stdin=subprocess.PIPE)

print("🚀 Rendering realistic live-action edit with synchronized Hindi typography...")

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
    if active_shot_idx != current_shot_idx:
        current_shot_idx = active_shot_idx
        cap.set(cv2.CAP_PROP_POS_MSEC, active_shot["src_start"] * 1000)

    # 3. Read video frame
    ret, frame_raw = cap.read()
    if not ret:
        if last_frame_bgr is not None:
            frame_raw = last_frame_bgr
        else:
            frame_raw = np.zeros((804, 1920, 3), dtype=np.uint8)
    last_frame_bgr = frame_raw

    # 4. Vertical 9:16 compositing
    vertical_frame = composite_vertical(frame_raw, zoom=active_shot["zoom"], cx_ratio=active_shot["cx_ratio"])

    # 5. Apply Freakyyyy Crimson Neo-Noir Color Grading
    graded_frame = apply_crimson_grade(vertical_frame, grain_idx=frame_idx)

    # Save a frame from Shot 8 for high-impact cover
    if 24.0 <= t <= 24.1:
        best_cover_frame = graded_frame.copy()

    # 6. Synchronized Hindi Typography with Smooth Alpha Curves
    for t_start, t_end, overlay in TYPOGRAPHY_SCHEDULE:
        if t_start <= t <= t_end:
            # 0.35s fade in, 0.35s fade out
            fade_dur = 0.35
            if t < t_start + fade_dur:
                alpha = (t - t_start) / fade_dur
            elif t > t_end - fade_dur:
                alpha = (t_end - t) / fade_dur
            else:
                alpha = 1.0
            alpha = max(0.0, min(1.0, alpha))

            # Non-linear smoothstep curve: 3x^2 - 2x^3
            smooth_alpha = alpha * alpha * (3.0 - 2.0 * alpha)

            # Alpha blend text overlay onto graded frame
            text_alpha = (overlay[:, :, 3].astype(np.float32) / 255.0) * smooth_alpha
            text_alpha_3ch = text_alpha[:, :, np.newaxis]
            text_bgr = overlay[:, :, :3]  # RGB to BGR matches white text
            graded_frame = (graded_frame.astype(np.float32) * (1.0 - text_alpha_3ch) +
                            text_bgr.astype(np.float32) * text_alpha_3ch).astype(np.uint8)
            break

    # 7. Beat Drop Strobe Flash Effect (white/cyan pulse at 15.6s, 16.0s, 16.4s, 16.8s)
    flash_times = [15.6, 16.0, 16.4, 16.8]
    for ft in flash_times:
        if abs(t - ft) < 0.08:
            gain = 1.0 - abs(t - ft) / 0.08
            flash_overlay = np.full_like(graded_frame, 255)
            flash_overlay[:, :, 1] = 230
            flash_overlay[:, :, 2] = 210
            graded_frame = cv2.addWeighted(graded_frame, 1.0, flash_overlay, gain * 0.45, 0)
            break

    # 8. Outro fade to black (last 0.8s)
    if t > DURATION - 0.8:
        out_fade = max(0.0, (DURATION - t) / 0.8)
        graded_frame = (graded_frame.astype(np.float32) * out_fade).astype(np.uint8)

    # Pipe frame to FFmpeg
    raw_pipe.stdin.write(graded_frame.tobytes())

    if frame_idx % 90 == 0:
        pct = (frame_idx / TOTAL_FRAMES) * 100
        print(f"   [{pct:5.1f}%] Frame {frame_idx}/{TOTAL_FRAMES} ({t:.1f}s)")

cap.release()
raw_pipe.stdin.close()
raw_pipe.wait()

print(f"🎉 100% REALISTIC REEL COMPILED: {FINAL_REEL} ({FINAL_REEL.stat().st_size / (1024*1024):.2f} MB)")

# -------------------------------------------------------------
# 6. GENERATE CUSTOM COVER & COMPANION STORY PROMO CARD
# -------------------------------------------------------------
if best_cover_frame is None:
    best_cover_frame = graded_frame

# Cover Image (9:16 high-contrast poster)
cover_img = best_cover_frame.copy()
cv2.imwrite(str(COVER_FILE), cover_img, [cv2.IMWRITE_JPEG_QUALITY, 95])

# Story Promo Card (Glassmorphic card with Hindi typography)
story_card = best_cover_frame.copy()
card_overlay = story_card.copy()
cv2.rectangle(card_overlay, (80, 1260), (WIDTH - 80, 1720), (12, 8, 10), -1)
story_card = cv2.addWeighted(card_overlay, 0.82, story_card, 0.18, 0)
cv2.rectangle(story_card, (80, 1260), (WIDTH - 80, 1720), (220, 50, 110), 2, cv2.LINE_AA)

# Typography on story card
pil_card = Image.fromarray(cv2.cvtColor(story_card, cv2.COLOR_BGR2RGB))
card_draw = ImageDraw.Draw(pil_card)
font_card_hi = ImageFont.truetype(font_path, 72)
font_card_en = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
font_card_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)

card_draw.text((120, 1310), "साजन साजन", font=font_card_hi, fill=(255, 230, 240))
card_draw.text((120, 1420), "THE BATMAN (2022)", font=font_card_en, fill=(255, 255, 255))
card_draw.text((120, 1495), "Slowed + Reverb • Live Action Cinema", font=font_card_sub, fill=(230, 100, 150))
card_draw.text((120, 1570), "NEW REEL OUT NOW • TAP TO WATCH", font=font_card_sub, fill=(255, 255, 255))
card_draw.text((120, 1640), "@vynox_00000", font=font_card_sub, fill=(180, 180, 180))

story_card = cv2.cvtColor(np.array(pil_card), cv2.COLOR_RGB2BGR)
cv2.imwrite(str(STORY_CARD), story_card, [cv2.IMWRITE_JPEG_QUALITY, 95])
print("✅ Cover & Story Card saved successfully!")

