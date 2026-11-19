#!/usr/bin/env python3
"""
100% Realistic Live-Action Cinema Edit: Blade Runner 2049 (Ryan Gosling) - Tu Hai Kahan (Slowed + Reverb)
Created for @vynox_00000 Instagram Reels & YouTube Shorts.

Winning Architecture:
1. Authentic 1080p Hollywood cinema footage (Ryan Gosling as Officer K & Ana de Armas as Joi in Blade Runner 2049).
2. Vertical 9:16 (1080x1920) mobile composition with ambient blurred neon background & centered 2.40:1 scope.
3. Signature Cyberpunk Neon Noir color grading (boosted cyan/magenta neon, deep crushed blacks, 35mm grain).
4. Stylized center-screen Devanagari typography with neon glow aura and smooth alpha sine curves.
5. Hyper-synchronized beat-drop strobe cuts aligned to AUR's vocal climax.
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
BASE_DIR = Path("projects/ryan-gosling-blade-runner-edit")
RAW_VIDEO = BASE_DIR / "raw/bladerunner_scenepack.mp4"
AUDIO_FILE = BASE_DIR / "audio/master_audio.wav"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_REEL = OUT_DIR / "Blade_Runner_Tu_Hai_Kahan_Reel.mp4"
COVER_FILE = OUT_DIR / "cover.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 28.50
TOTAL_FRAMES = int(DURATION * FPS)  # 855 frames

print(f"🎬 Initializing 100% Realistic Live-Action Blade Runner 2049 Edit ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# -------------------------------------------------------------
# 1. PRE-RENDER HINDI TYPOGRAPHY RGBA OVERLAYS
# -------------------------------------------------------------
font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf"
font_large = ImageFont.truetype(font_path, 115)
font_medium = ImageFont.truetype(font_path, 95)
font_brand = ImageFont.truetype(font_path, 55)

# Try clean sans-serif for English cinematic title if possible
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
except Exception:
    font_title = font_medium

def render_text_overlay(text, font=font_large, y_pos=None, neon_glow=True, custom_color=(255, 255, 255)):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2 if y_pos is None else y_pos

    # Soft glowing neon aura (Magenta + Cyan dual halo)
    if neon_glow:
        # Magenta halo
        for ox, oy in [(-8, -8), (8, 8), (-8, 8), (8, -8), (0, 10), (0, -10), (10, 0), (-10, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill=(235, 30, 160, 120))
        # Cyan inner glow
        for ox, oy in [(-5, -5), (5, 5), (-5, 5), (5, -5), (0, 6), (0, -6), (6, 0), (-6, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill=(0, 210, 255, 90))

    # Inner dark shadow outline for crisp contrast
    shadow_offsets = [(-4, -4), (4, 4), (-4, 4), (4, -4), (0, 5), (0, -5), (5, 0), (-5, 0),
                      (-2, -2), (2, 2), (-2, 2), (2, -2), (0, 3), (0, -3), (3, 0), (-3, 0)]
    for ox, oy in shadow_offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 240))

    # Crisp text fill
    draw.text((x, y), text, font=font, fill=(custom_color[0], custom_color[1], custom_color[2], 255))
    return np.array(img)

# Pre-render text overlays
OVERLAY_TU_HAI_KAHAN = render_text_overlay("तू है कहाँ...", font_large, y_pos=910)
OVERLAY_MAIN_YAHAN   = render_text_overlay("मैं यहाँ...", font_large, y_pos=900)
OVERLAY_SAB_YAHAN    = render_text_overlay("सब यहाँ...", font_large, y_pos=900)
OVERLAY_PAR_TU_NAHIN = render_text_overlay("पर तू नहीं...", font_large, y_pos=900)
OVERLAY_KHWAABON     = render_text_overlay("ख्वाबों के शहर में...", font_medium, y_pos=910)
OVERLAY_TITLE        = render_text_overlay("BLADE RUNNER 2049", font_title, y_pos=880, neon_glow=True)
OVERLAY_BRAND        = render_text_overlay("@vynox_00000", font_brand, y_pos=1680, neon_glow=False)

TYPOGRAPHY_SCHEDULE = [
    (0.3, 4.9, OVERLAY_TU_HAI_KAHAN),
    (5.3, 11.3, OVERLAY_MAIN_YAHAN),
    (11.8, 17.2, OVERLAY_SAB_YAHAN),
    (17.6, 22.1, OVERLAY_PAR_TU_NAHIN),
    (22.5, 25.8, OVERLAY_KHWAABON),
    (26.0, 28.3, OVERLAY_TITLE),
]

# -------------------------------------------------------------
# 2. DEFINE MASTER SHOTS TIMELINE (Hollywood 1080p Cinema)
# -------------------------------------------------------------
SHOTS = [
    {
        "name": "Rainy Neon Street Walk",
        "src_start": 90.0,
        "out_start": 0.0,
        "out_end": 5.20,
        "zoom": 1.85,
        "cx_ratio": 0.48,
    },
    {
        "name": "Giant Hologram Joi",
        "src_start": 429.5,
        "out_start": 5.20,
        "out_end": 11.70,
        "zoom": 1.95,
        "cx_ratio": 0.50,
    },
    {
        "name": "Officer K Looking Up in Awe",
        "src_start": 436.5,
        "out_start": 11.70,
        "out_end": 17.50,
        "zoom": 1.90,
        "cx_ratio": 0.52,
    },
    {
        "name": "Spinner Flying Through Neon Rain",
        "src_start": 112.0,
        "out_start": 17.50,
        "out_end": 22.40,
        "zoom": 1.80,
        "cx_ratio": 0.50,
    },
    {
        "name": "Las Vegas Orange Ruined Statues",
        "src_start": 409.0,
        "out_start": 22.40,
        "out_end": 26.00,
        "zoom": 1.85,
        "cx_ratio": 0.48,
    },
    {
        "name": "Snowy Stairs Ending / Tears in Rain",
        "src_start": 454.0,
        "out_start": 26.00,
        "out_end": 28.50,
        "zoom": 1.85,
        "cx_ratio": 0.50,
    },
]

# -------------------------------------------------------------
# 3. PRE-COMPUTE FILM GRAIN MASKS & S-CURVE CONTRAST LUT
# -------------------------------------------------------------
np.random.seed(42)
GRAIN_MASKS = [
    np.random.normal(0, 4.0, (HEIGHT, WIDTH, 3)).astype(np.float32)
    for _ in range(12)
]

# High-contrast S-curve LUT
LUT_CONTRAST = np.array([
    int(np.clip(255.0 / (1.0 + np.exp(-0.024 * (x - 128))), 0, 255))
    for x in range(256)
], dtype=np.uint8)

def apply_blade_runner_grade(frame_bgr, grain_idx=0, is_strobe=False):
    # 1. Apply S-curve contrast via LUT
    contrast = cv2.LUT(frame_bgr, LUT_CONTRAST)
    float_img = contrast.astype(np.float32)

    # 2. Cyberpunk Neon Noir BGR channel grading
    float_img[:, :, 0] = np.clip(float_img[:, :, 0] * 1.15 + 6, 0, 255)   # Electric Blue / Cyan
    float_img[:, :, 1] = np.clip(float_img[:, :, 1] * 0.98, 0, 255)       # Controlled Green
    float_img[:, :, 2] = np.clip(float_img[:, :, 2] * 1.12 + 4, 0, 255)   # Magenta / Neon Red

    # 3. Beat strobe flash
    if is_strobe:
        float_img = np.clip(float_img + 60, 0, 255)

    # 4. 35mm film grain
    float_img += GRAIN_MASKS[grain_idx % len(GRAIN_MASKS)]
    return np.clip(float_img, 0, 255).astype(np.uint8)

# -------------------------------------------------------------
# 4. VERTICAL 9:16 COMPOSITING ENGINE
# -------------------------------------------------------------
def composite_vertical(frame_bgr, zoom=1.85, cx_ratio=0.50):
    ih, iw = frame_bgr.shape[:2]

    # Fast ambient blurred background (downsample -> blur -> upsample)
    small_bg = cv2.resize(frame_bgr, (270, 480))
    small_bg = cv2.GaussianBlur(small_bg, (25, 25), 0)
    bg = cv2.resize(small_bg, (WIDTH, HEIGHT))
    bg = (bg * 0.40).astype(np.uint8)

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
        cv2.line(bg, (0, y_off), (WIDTH, y_off), (45, 30, 60), 1)
        cv2.line(bg, (0, y_off + nh - 1), (WIDTH, y_off + nh - 1), (45, 30, 60), 1)
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

print("🚀 Rendering realistic live-action Blade Runner 2049 edit with synchronized Hindi typography...")

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
        frame_raw = last_frame_bgr if last_frame_bgr is not None else np.zeros((800, 1920, 3), dtype=np.uint8)
    last_frame_bgr = frame_raw

    # 4. Vertical 9:16 compositing
    vertical_frame = composite_vertical(frame_raw, zoom=active_shot["zoom"], cx_ratio=active_shot["cx_ratio"])

    # 5. Apply Blade Runner Cyberpunk Neon grading & strobe on transition
    is_strobe = is_shot_transition and (active_shot_idx > 0)
    graded_frame = apply_blade_runner_grade(vertical_frame, grain_idx=frame_idx, is_strobe=is_strobe)

    # Save a frame from Joi hologram (t ~ 6.2s) for high-impact cover
    if 6.1 <= t <= 6.2 and best_cover_frame is None:
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

    # 8. Fade to black on final 15 frames (0.5s)
    if frame_idx >= TOTAL_FRAMES - 15:
        fade_val = (TOTAL_FRAMES - frame_idx) / 15.0
        graded_frame = (graded_frame.astype(np.float32) * fade_val).astype(np.uint8)

    # 9. Pipe frame directly into ffmpeg stdin
    raw_pipe.stdin.write(graded_frame.tobytes())

    if (frame_idx + 1) % 150 == 0 or frame_idx == TOTAL_FRAMES - 1:
        print(f"  Frame {frame_idx + 1}/{TOTAL_FRAMES} ({(frame_idx+1)/TOTAL_FRAMES*100:.1f}%) rendered...")

# Finalize pipe
raw_pipe.stdin.close()
raw_pipe.wait()
cap.release()

print(f"✅ Video render complete: {FINAL_REEL} ({FINAL_REEL.stat().st_size / (1024*1024):.2f} MB)")

# -------------------------------------------------------------
# 6. GENERATE COVER AND STORY CARD
# -------------------------------------------------------------
if best_cover_frame is None:
    best_cover_frame = graded_frame

cv2.imwrite(str(COVER_FILE), best_cover_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
print(f"✅ Cover image generated: {COVER_FILE}")

# Story Card with high-impact "NEW REEL OUT NOW" badge
story_card_img = best_cover_frame.copy()
story_pil = Image.fromarray(cv2.cvtColor(story_card_img, cv2.COLOR_BGR2RGB))
draw_story = ImageDraw.Draw(story_pil)

# Story banner at top
box_y1, box_y2 = 280, 420
overlay_box = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
draw_box = ImageDraw.Draw(overlay_box)
draw_box.rectangle([(80, box_y1), (WIDTH - 80, box_y2)], fill=(200, 20, 120, 220))
story_pil = Image.alpha_composite(story_pil.convert("RGBA"), overlay_box)
draw_story = ImageDraw.Draw(story_pil)

badge_text = "NEW REEL OUT NOW"
try:
    badge_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
except Exception:
    badge_font = font_large
bbox = draw_story.textbbox((0, 0), badge_text, font=badge_font)
bw = bbox[2] - bbox[0]
draw_story.text(((WIDTH - bw) // 2, box_y1 + 40), badge_text, font=badge_font, fill=(255, 255, 255))

story_bgr = cv2.cvtColor(np.array(story_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
cv2.imwrite(str(STORY_CARD), story_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
print(f"✅ Story card generated: {STORY_CARD}")
print("🎉 All Blade Runner 2049 assets successfully created!")
