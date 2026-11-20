"""
High-Speed Renderer for Flagship 1tachi.aep Benchmark Reel:
Makoto Shinkai's 'The Garden of Words' x Darshan Raval 'Mere Nishaan (Slowed + Reverb)'
1080x1920 30fps Full Vertical Immersion
"""

import os
import sys
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

OUTPUT_DIR = "projects/garden-of-words-mere-nishaan/output"
TEMP_DIR = "projects/garden-of-words-mere-nishaan/temp"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

RAW_VIDEO = "projects/garden-of-words-mere-nishaan/raw/garden_confrontation_1080p.mp4"
AUDIO_PATH = "projects/garden-of-words-mere-nishaan/audio/mere_nishaan_slowed_reverb.mp3"
TEMP_VIDEO = os.path.join(TEMP_DIR, "video_stream.mp4")
FINAL_REEL = os.path.join(OUTPUT_DIR, "film_garden_of_words_mere_nishaan.mp4")
COVER_PATH = os.path.join(OUTPUT_DIR, "cover.jpg")

FPS = 30
WIDTH = 1080
HEIGHT = 1920

# Timeline Segments
SEGMENTS = [
    # (seg_idx, target_duration, raw_start, raw_end, focal_center_x_pct)
    (0, 2.80, 115.5, 118.3, 0.45),
    (1, 4.20, 118.3, 122.5, 0.45),
    (2, 4.20, 146.0, 150.2, 0.52),
    (3, 4.30, 119.5, 123.8, 0.46),
    (4, 6.03, 147.8, 150.8, 0.48)
]

LYRICS = [
    (0.2, 3.6, "", "Mera...", None, (255, 213, 79, 255), 0, 60, 94),
    (3.8, 7.0, "", "Rehnuma...", None, (255, 248, 225, 255), 0, 60, 96),
    (7.2, 9.6, "SAPNE TERE", "Sapne...", (0, 229, 255, 255), (255, 255, 255, 255), -3, 64, 88),
    (9.8, 12.0, "KHWAB MEIN", "Khwab...", (255, 176, 64, 255), (255, 255, 255, 255), -3, 64, 88),
    (12.2, 15.4, "SACH HO JAAYE", "Sach ho jaaye...", (0, 229, 255, 255), (255, 255, 255, 255), -4, 64, 90),
    (15.6, 21.5, "AGAR KHUDA", "Meherban...", (255, 176, 64, 255), (255, 255, 255, 255), -4, 68, 98)
]


def extract_segment_clips():
    """Pre-slices raw video clips using fast stream copying/reencoding."""
    clip_paths = []
    for idx, target_dur, start_s, end_s, _ in SEGMENTS:
        clip_path = os.path.join(TEMP_DIR, f"seg_{idx}.mp4")
        dur = end_s - start_s
        cmd = f'ffmpeg -y -ss {start_s:.3f} -i "{RAW_VIDEO}" -t {dur:.3f} -vf "scale=1920:1080,fps=30" -c:v libx264 -preset ultrafast -crf 16 -an "{clip_path}"'
        res = os.system(cmd)
        if res != 0 or not os.path.exists(clip_path):
            raise RuntimeError(f"Failed to slice segment {idx}")
        clip_paths.append(clip_path)
    return clip_paths


def render():
    print("=== Slicing Raw Segments ===")
    clip_paths = extract_segment_clips()

    print("=== Rendering AEP Cinema Video Stream ===")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(TEMP_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))

    flare = generate_rainbow_prism_flare(WIDTH, HEIGHT, intensity=0.42, blur_radius=40)
    flare_norm = np.clip(flare / 255.0, 0, 1)

    cover_saved = False
    global_frame = 0

    for seg_idx, (idx, target_dur, _, _, focal_center_pct) in enumerate(SEGMENTS):
        clip_path = clip_paths[seg_idx]
        cap = cv2.VideoCapture(clip_path)
        frames_needed = int(target_dur * FPS)

        raw_frames = []
        while True:
            ret, f = cap.read()
            if not ret:
                break
            raw_frames.append(f)
        cap.release()

        if not raw_frames:
            raise RuntimeError(f"No frames in clip {clip_path}")

        # Interpolate/cycle frames to match frames_needed
        num_raw = len(raw_frames)
        for i in range(frames_needed):
            raw_idx = int(i * (num_raw - 1) / max(1, frames_needed - 1))
            raw_frame = raw_frames[raw_idx]

            fh, fw = raw_frame.shape[:2]
            scale = HEIGHT / float(fh)
            scaled_w = int(fw * scale)
            resized = cv2.resize(raw_frame, (scaled_w, HEIGHT), interpolation=cv2.INTER_LANCZOS4)

            # Crop focal center
            ideal_center_x = int(scaled_w * focal_center_pct)
            crop_start_x = ideal_center_x - WIDTH // 2
            crop_start_x = max(0, min(crop_start_x, scaled_w - WIDTH))
            frame_cropped = resized[:, crop_start_x:crop_start_x + WIDTH]

            # VFX Stack: Deep Glow -> Rainbow Flare -> S-Curve Grade -> Grain
            glow = apply_deep_glow(frame_cropped, threshold=175, bloom_factor=0.55, tint=(0.88, 1.06, 1.22))
            g_norm = glow.astype(np.float32) / 255.0
            flared = np.clip((1.0 - (1.0 - g_norm) * (1.0 - flare_norm)) * 255.0, 0, 255).astype(np.uint8)
            graded = apply_cinema_grade(flared, lift=12, contrast=1.12, warm_highlight=1.07, cool_shadow=1.03)
            grained = add_film_grain(graded, intensity=3.0, seed=global_frame)

            # Typography
            current_time = global_frame / float(FPS)
            active_lyric = None
            for lyr in LYRICS:
                if lyr[0] <= current_time < lyr[1]:
                    active_lyric = lyr
                    break

            if active_lyric:
                canvas_pil = Image.fromarray(cv2.cvtColor(grained, cv2.COLOR_BGR2RGB))
                base_col = active_lyric[4] if active_lyric[4] else (255, 255, 255, 255)
                script_col = active_lyric[5] if active_lyric[5] else (255, 255, 255, 255)
                canvas_pil = render_dual_layer_typography(
                    canvas_pil,
                    base_text=active_lyric[2],
                    script_text=active_lyric[3],
                    center_xy=(WIDTH // 2, 1540),
                    base_font_size=active_lyric[7],
                    script_font_size=active_lyric[8],
                    base_color=base_col,
                    script_color=script_col,
                    script_offset=(0, -8),
                    script_angle=active_lyric[6],
                    shadow_blur=12,
                    shadow_alpha=220
                )
                final_bgr = cv2.cvtColor(np.array(canvas_pil), cv2.COLOR_RGB2BGR)
            else:
                final_bgr = grained

            if not cover_saved and current_time >= 18.0:
                cv2.imwrite(COVER_PATH, final_bgr)
                cover_saved = True

            writer.write(final_bgr)
            global_frame += 1

            if global_frame % 90 == 0:
                print(f"Rendered {global_frame}/645 frames ({current_time:.1f}s)")

    writer.release()
    print(f"Rendered {global_frame} frames total.")

    print("Muxing audio with FFmpeg...")
    cmd = f'ffmpeg -y -i "{TEMP_VIDEO}" -i "{AUDIO_PATH}" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "{FINAL_REEL}"'
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError("FFmpeg audio muxing failed!")

    print(f"=== FLAGSHIP REEL COMPLETE: {FINAL_REEL} ===")


if __name__ == "__main__":
    render()
