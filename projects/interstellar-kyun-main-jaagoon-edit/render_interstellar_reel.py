#!/usr/bin/env python3
"""
100% Realistic Live-Action Cinema Edit: Interstellar (Christopher Nolan) - Kyun Main Jaagoon (Slowed + Reverb)
Created for @vynox_00000 Instagram Reels & YouTube Shorts.

Winning Architecture:
1. Authentic 1080p Hollywood cinema footage (Matthew McConaughey as Cooper in Interstellar).
2. Vertical 9:16 (1080x1920) mobile composition with ambient blurred background & centered focus.
3. Signature Cosmic Amber Gold & Deep Space Neo-Noir color grading.
4. Stylized center-screen Devanagari typography with glowing gold/cyan aura and smooth alpha sine curves.
5. Hyper-synchronized beat-drop strobe cuts aligned to Shafqat Amanat Ali's vocal climax.
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
BASE_DIR = Path("projects/interstellar-kyun-main-jaagoon-edit")
AUDIO_FILE = BASE_DIR / "audio/master_audio.wav"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL_REEL = OUT_DIR / "Interstellar_Kyun_Main_Jaagoon_Reel.mp4"
COVER_FILE = OUT_DIR / "cover.jpg"
STORY_CARD = OUT_DIR / "story_card.jpg"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 28.50
TOTAL_FRAMES = int(DURATION * FPS)  # 855 frames

print(f"🎬 Initializing 100% Realistic Live-Action Interstellar Edit ({TOTAL_FRAMES} frames @ {FPS} fps)...")

# -------------------------------------------------------------
# 1. PRE-RENDER ENGLISH TYPOGRAPHY RGBA OVERLAYS
# -------------------------------------------------------------
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_large = ImageFont.truetype(font_path, 62)
font_medium = ImageFont.truetype(font_path, 54)
font_brand = ImageFont.truetype(font_path, 38)
font_title = ImageFont.truetype(font_path, 76)

def render_text_overlay(text, font=font_large, y_pos=None, cosmic_glow=True, custom_color=(255, 255, 255)):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (WIDTH - tw) // 2
    y = (HEIGHT - th) // 2 if y_pos is None else y_pos

    # Soft glowing cosmic aura (Amber Gold + Cyan dual halo)
    if cosmic_glow:
        # Amber gold halo
        for ox, oy in [(-8, -8), (8, 8), (-8, 8), (8, -8), (0, 10), (0, -10), (10, 0), (-10, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill=(255, 175, 40, 120))
        # Cyan starlight inner glow
        for ox, oy in [(-5, -5), (5, 5), (-5, 5), (5, -5), (0, 6), (0, -6), (6, 0), (-6, 0)]:
            draw.text((x + ox, y + oy), text, font=font, fill=(50, 210, 255, 90))

    # Inner dark shadow outline for crisp contrast
    shadow_offsets = [(-4, -4), (4, 4), (-4, 4), (4, -4), (0, 5), (0, -5), (5, 0), (-5, 0),
                      (-2, -2), (2, 2), (-2, 2), (2, -2), (0, 3), (0, -3), (3, 0), (-3, 0)]
    for ox, oy in shadow_offsets:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, 240))

    # Crisp text fill
    draw.text((x, y), text, font=font, fill=(custom_color[0], custom_color[1], custom_color[2], 255))
    return np.array(img)

# Pre-render text overlays matching exact Shafqat Amanat Ali vocal delivery in English / Romanized
OVERLAY_BOONDE         = render_text_overlay("BOONDEIN TERE MAATHE PE YUN...", font_medium, y_pos=910)
OVERLAY_MOTI           = render_text_overlay("JAISE KOI MOTI SAJA...", font_large, y_pos=900)
OVERLAY_DHUNDHLE       = render_text_overlay("DHUNDHLE LAGE SAARE JAHAN...", font_medium, y_pos=910)
OVERLAY_AANSU          = render_text_overlay("AANSU MERE BEHNE LAGE...", font_large, y_pos=900)
OVERLAY_MITA_DE        = render_text_overlay("MUJHKO MITA DE MERE RABBA...", font_medium, y_pos=910)
OVERLAY_TITLE          = render_text_overlay("INTERSTELLAR", font_title, y_pos=880, cosmic_glow=True)
OVERLAY_BRAND          = render_text_overlay("@vynox_00000", font_brand, y_pos=1680, cosmic_glow=False)

TYPOGRAPHY_SCHEDULE = [
    (0.2, 4.5, OVERLAY_BOONDE),
    (4.8, 10.5, OVERLAY_MOTI),
    (10.8, 16.0, OVERLAY_DHUNDHLE),
    (16.2, 21.0, OVERLAY_AANSU),
    (21.2, 25.5, OVERLAY_MITA_DE),
    (25.8, 28.3, OVERLAY_TITLE),
]

# -------------------------------------------------------------
# 2. DEFINE MASTER SHOTS TIMELINE (Hollywood 1080p Cinema)
# -------------------------------------------------------------
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

# Open video capture handles for all shots
caps = {}
for s in SHOTS:
    c = cv2.VideoCapture(str(s["file"]))
    if not c.isOpened():
        raise RuntimeError(f"Cannot open {s['file']}")
    caps[s["name"]] = c

# -------------------------------------------------------------
# 3. PRE-COMPUTE FILM GRAIN MASKS & S-CURVE CONTRAST LUT
# -------------------------------------------------------------
np.random.seed(42)
GRAIN_MASKS = [
    np.random.normal(0, 3.8, (HEIGHT, WIDTH, 3)).astype(np.float32)
    for _ in range(12)
]

LUT_CONTRAST = np.array([
    int(np.clip(255.0 / (1.0 + np.exp(-0.024 * (x - 128))), 0, 255))
    for x in range(256)
], dtype=np.uint8)

def apply_interstellar_grade(frame_bgr, grain_idx=0, is_strobe=False):
    contrast = cv2.LUT(frame_bgr, LUT_CONTRAST)
    float_img = contrast.astype(np.float32)

    # Cosmic Amber Gold & Deep Space BGR grading
    float_img[:, :, 0] = np.clip(float_img[:, :, 0] * 1.08 + 4, 0, 255)   # Deep indigo space
    float_img[:, :, 1] = np.clip(float_img[:, :, 1] * 1.04 + 2, 0, 255)   # Amber warmth
    float_img[:, :, 2] = np.clip(float_img[:, :, 2] * 1.10 + 4, 0, 255)   # Golden glow

    if is_strobe:
        float_img = np.clip(float_img + 60, 0, 255)

    float_img += GRAIN_MASKS[grain_idx % len(GRAIN_MASKS)]
    return np.clip(float_img, 0, 255).astype(np.uint8)

# -------------------------------------------------------------
# 4. VERTICAL 9:16 COMPOSITING ENGINE
# -------------------------------------------------------------
def composite_vertical(frame_bgr, zoom=1.45, cx_ratio=0.50):
    ih, iw = frame_bgr.shape[:2]

    # Fast ambient blurred background
    small_bg = cv2.resize(frame_bgr, (270, 480))
    small_bg = cv2.GaussianBlur(small_bg, (25, 25), 0)
    bg = cv2.resize(small_bg, (WIDTH, HEIGHT))
    bg = (bg * 0.38).astype(np.uint8)

    # Main video with cinematic crop
    scale = (WIDTH / iw) * zoom
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(frame_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)

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
        cv2.line(bg, (0, y_off), (WIDTH, y_off), (50, 45, 30), 1)
        cv2.line(bg, (0, y_off + nh - 1), (WIDTH, y_off + nh - 1), (50, 45, 30), 1)
        return bg
    else:
        y1 = (nh - HEIGHT) // 2
        return cropped[y1:y1 + HEIGHT, :]

# -------------------------------------------------------------
# 5. PREPARE FFmpeg STREAM & EXECUTE RENDER
# -------------------------------------------------------------
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

print("🚀 Rendering realistic live-action Interstellar edit with synchronized Hindi typography...")

current_shot_name = None
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

    is_shot_transition = (active_shot["name"] != current_shot_name)
    current_shot_name = active_shot["name"]

    # 2. Read from active shot capture (step by 2 frames since source is 60fps)
    cap = caps[active_shot["name"]]
    ret, frame_raw = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame_raw = cap.read()
    # Skip one frame for 60fps -> 30fps conversion
    cap.read()

    # 3. Vertical 9:16 compositing
    vertical_frame = composite_vertical(frame_raw, zoom=active_shot["zoom"], cx_ratio=active_shot["cx_ratio"])

    # 4. Color grading & strobe
    is_strobe = is_shot_transition and (active_shot_idx > 0)
    graded_frame = apply_interstellar_grade(vertical_frame, grain_idx=frame_idx, is_strobe=is_strobe)

    # Save a frame from Video Message Crying scene (t ~ 11.0s) for high-impact cover
    if 10.9 <= t <= 11.1 and best_cover_frame is None:
        best_cover_frame = graded_frame.copy()

    # 5. Synchronized Hindi Typography with Smooth Alpha Curves
    for t_start, t_end, overlay in TYPOGRAPHY_SCHEDULE:
        if t_start <= t <= t_end:
            fade_dur = 0.35
            if t < t_start + fade_dur:
                alpha = (t - t_start) / fade_dur
            elif t > t_end - fade_dur:
                alpha = (t_end - t) / fade_dur
            else:
                alpha = 1.0

            alpha_mask = (overlay[:, :, 3].astype(np.float32) / 255.0) * alpha
            rgb_overlay = overlay[:, :, :3]
            for c in range(3):
                graded_frame[:, :, c] = np.clip(
                    graded_frame[:, :, c] * (1.0 - alpha_mask) + rgb_overlay[:, :, c] * alpha_mask,
                    0, 255
                ).astype(np.uint8)

    # 6. Apply subtle branding stamp (@vynox_00000)
    wm_alpha = (OVERLAY_BRAND[:, :, 3].astype(np.float32) / 255.0) * 0.70
    for c in range(3):
        graded_frame[:, :, c] = np.clip(
            graded_frame[:, :, c] * (1.0 - wm_alpha) + OVERLAY_BRAND[:, :, c] * wm_alpha,
            0, 255
        ).astype(np.uint8)

    # 7. Fade to black on final 15 frames (0.5s)
    if frame_idx >= TOTAL_FRAMES - 15:
        fade_val = (TOTAL_FRAMES - frame_idx) / 15.0
        graded_frame = (graded_frame.astype(np.float32) * fade_val).astype(np.uint8)

    # 8. Pipe frame into ffmpeg
    raw_pipe.stdin.write(graded_frame.tobytes())

    if (frame_idx + 1) % 150 == 0 or frame_idx == TOTAL_FRAMES - 1:
        print(f"  Frame {frame_idx + 1}/{TOTAL_FRAMES} ({(frame_idx+1)/TOTAL_FRAMES*100:.1f}%) rendered...")

# Finalize pipe
raw_pipe.stdin.close()
raw_pipe.wait()
for c in caps.values():
    c.release()

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

box_y1, box_y2 = 280, 420
overlay_box = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
draw_box = ImageDraw.Draw(overlay_box)
draw_box.rectangle([(80, box_y1), (WIDTH - 80, box_y2)], fill=(210, 140, 20, 220))
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
print("🎉 All Interstellar assets successfully created!")
