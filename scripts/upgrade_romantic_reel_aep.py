"""
Unified AEP Cinema Upgrader for Romantic & Indie Series Reels:
- Achchi Lagti Ho (11-acchi-lagti-ho)
- Jeene Laga Hoon (12-jeene-laga-hoon)
- Aankhon Se Batana (13-aankhon-se-batana)
- Sahiba (07-sahiba-crimson-manga)
- The Batman (12s Ultra-Loop Cut)
Applies 1tachi.aep benchmark graphics stack:
1. Deep Glow bloom filter
2. Rainbow Prism chromatic dispersion flare
3. S-curve film grade (lifted milky blacks + warm highlights)
4. 35mm fine grain
5. Dual-Layer Typography (Bold Sans + Flowing Great Vibes Cursive Script)
"""

import math
import os
import random
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
    render_dual_layer_typography,
    render_cinema_single_caption
)

FPS = 30
WIDTH = 1080
HEIGHT = 1920

PROJECT_CONFIGS = {
    "acchi_lagti_ho": {
        "dir": "projects/series-romantic-animations/11-acchi-lagti-ho",
        "audio": "projects/series-romantic-animations/11-acchi-lagti-ho/audio/acchi_lagti_ho_hook.wav",
        "output": "projects/series-romantic-animations/11-acchi-lagti-ho/output/film_acchi_lagti_ho_aep.mp4",
        "cover": "projects/series-romantic-animations/11-acchi-lagti-ho/output/cover_aep.jpg",
        "story_card": "projects/series-romantic-animations/11-acchi-lagti-ho/output/story_card_aep.jpg",
        "title": "Achchi Lagti Ho",
        "duration": 27.56,
        "scenes": [
            ("scene-1.jpg", 0.0, 7.2),
            ("scene-2.jpg", 7.2, 14.5),
            ("scene-3.jpg", 14.5, 21.0),
            ("scene-4.jpg", 21.0, 27.56)
        ],
        "lyrics": [
            (0.2, 4.2, "Chupke chupke jab aise dekhti ho...", (255, 255, 255, 255), 46, 1390),
            (4.2, 8.5, "Achchi lagti ho...", (255, 255, 255, 255), 52, 1390),
            (11.8, 17.5, "Kabhi zulfon se jab khelti ho...", (255, 255, 255, 255), 46, 1390),
            (17.5, 22.0, "Achchi lagti ho...", (255, 255, 255, 255), 52, 1390),
            (22.2, 27.5, "Kuch Naa Kaho • Udit Narayan", (255, 255, 255, 255), 44, 1390)
        ]
    },
    "jeene_laga_hoon": {
        "dir": "projects/series-romantic-animations/12-jeene-laga-hoon",
        "audio": "projects/series-romantic-animations/12-jeene-laga-hoon/audio/jeene_laga_hoon_hook.wav",
        "output": "projects/series-romantic-animations/12-jeene-laga-hoon/output/film_jeene_laga_hoon_aep.mp4",
        "cover": "projects/series-romantic-animations/12-jeene-laga-hoon/output/cover_aep.jpg",
        "story_card": "projects/series-romantic-animations/12-jeene-laga-hoon/output/story_card_aep.jpg",
        "title": "Jeene Laga Hoon",
        "duration": 27.56,
        "scenes": [
            ("scene-1.jpg", 0.0, 7.2),
            ("scene-2.jpg", 7.2, 14.5),
            ("scene-3.jpg", 14.5, 21.0),
            ("scene-4.jpg", 21.0, 27.56)
        ],
        "lyrics": [
            (0.2, 6.5, "Jeene laga hoon pehle se zyada...", (255, 255, 255, 255), 46, 1390),
            (7.0, 13.5, "Pehle se zyada tum pe marne laga...", (255, 255, 255, 255), 46, 1390),
            (14.0, 20.5, "Main mera dil tere hawale...", (255, 255, 255, 255), 48, 1390),
            (21.0, 27.5, "Ramaiya Vastavaiya • Atif Aslam", (255, 255, 255, 255), 44, 1390)
        ]
    },
    "aankhon_se_batana": {
        "dir": "projects/series-romantic-animations/13-aankhon-se-batana",
        "audio": "projects/series-romantic-animations/13-aankhon-se-batana/audio/aankhon_se_batana_hook.wav",
        "output": "projects/series-romantic-animations/13-aankhon-se-batana/output/film_aankhon_se_batana_aep.mp4",
        "cover": "projects/series-romantic-animations/13-aankhon-se-batana/output/cover_aep.jpg",
        "story_card": "projects/series-romantic-animations/13-aankhon-se-batana/output/story_card_aep.jpg",
        "title": "Aankhon Se Batana",
        "duration": 27.56,
        "scenes": [
            ("scene-1.jpg", 0.0, 7.2),
            ("scene-2.jpg", 7.2, 14.5),
            ("scene-3.jpg", 14.5, 21.0),
            ("scene-4.jpg", 21.0, 27.56)
        ],
        "lyrics": [
            (0.2, 6.5, "Tum aankhon se batana hum samajh jaayenge...", (255, 255, 255, 255), 44, 1390),
            (7.0, 13.5, "Tum halki si sharmaana hum tere ho jaayenge...", (255, 255, 255, 255), 44, 1390),
            (14.0, 20.5, "Paas jo tu aaye saari duniya bhool...", (255, 255, 255, 255), 46, 1390),
            (21.0, 27.5, "Aankhon Se Batana • Dikshant", (255, 255, 255, 255), 44, 1390)
        ]
    },
    "sahiba": {
        "dir": "projects/series-romantic-animations/07-sahiba-crimson-manga",
        "audio": "projects/series-romantic-animations/07-sahiba-crimson-manga/audio/sahiba_clip.wav",
        "output": "projects/series-romantic-animations/07-sahiba-crimson-manga/output/film_sahiba_aep.mp4",
        "cover": "projects/series-romantic-animations/07-sahiba-crimson-manga/output/cover_aep.jpg",
        "story_card": "projects/series-romantic-animations/07-sahiba-crimson-manga/output/story_card_aep.jpg",
        "title": "Sahiba",
        "duration": 22.50,
        "scenes": [
            ("scene-1.jpg", 0.0, 6.8),
            ("scene-2.jpg", 6.8, 10.5),
            ("scene-3.jpg", 10.5, 16.5),
            ("scene-4.jpg", 16.5, 22.50)
        ],
        "lyrics": [
            (0.0, 2.4, "Saahiba...", (255, 255, 255, 255), 52, 1390),
            (2.4, 4.8, "Aaye ghar kaahe na...", (255, 255, 255, 255), 48, 1390),
            (4.8, 6.8, "Aise toh sataaye na...", (255, 255, 255, 255), 48, 1390),
            (6.8, 10.5, "Dekhoon tujhko toh chain aata hai...", (255, 255, 255, 255), 46, 1390),
            (10.5, 12.8, "Saahiba...", (255, 255, 255, 255), 52, 1390),
            (12.8, 16.5, "Neendein aayein na, raatein kaati...", (255, 255, 255, 255), 46, 1390),
            (16.5, 20.4, "Tera hi khayaal din-rain aata hai...", (255, 255, 255, 255), 46, 1390),
            (20.4, 22.5, "Sahiba • Aditya Rikhari", (255, 255, 255, 255), 44, 1390)
        ]
    },
    "arz_kiya_hai": {
        "dir": "projects/series-romantic-animations/10-arz-kiya-hai-anuv-jain",
        "audio": "projects/series-romantic-animations/10-arz-kiya-hai-anuv-jain/audio/arz_kiya_hai_clip.wav",
        "output": "projects/series-romantic-animations/10-arz-kiya-hai-anuv-jain/output/film_arz_kiya_hai_aep.mp4",
        "cover": "projects/series-romantic-animations/10-arz-kiya-hai-anuv-jain/output/cover_aep.jpg",
        "story_card": "projects/series-romantic-animations/10-arz-kiya-hai-anuv-jain/output/story_card_aep.jpg",
        "title": "Arz Kiya Hai",
        "duration": 23.50,
        "scenes": [
            ("scene-1.jpg", 0.0, 6.0),
            ("scene-2.jpg", 6.0, 11.2),
            ("scene-3.jpg", 11.2, 16.8),
            ("scene-4.jpg", 16.8, 23.50)
        ],
        "lyrics": [
            (0.6, 2.6, "Arz kiya hai...", (255, 255, 255, 255), 52, 1390),
            (2.8, 6.4, "Humne bhi likha kuch tere baare mein hai...", (255, 255, 255, 255), 44, 1390),
            (6.6, 10.7, "Aise tu lagay ki gulaab hai...", (255, 255, 255, 255), 48, 1390),
            (11.0, 15.2, "Aur aise tu lagay ki gulaab hai...", (255, 255, 255, 255), 48, 1390),
            (15.6, 20.1, "Baghon mein dil ke, khilke in fizaon mein...", (255, 255, 255, 255), 44, 1390),
            (20.4, 23.5, "Chhaye ho...", (255, 255, 255, 255), 52, 1390)
        ]
    }
}


def load_scaled_scene(path):
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Missing {path}")
    ih, iw = img.shape[:2]
    scale = max(WIDTH / float(iw), HEIGHT / float(ih))
    nw, nh = int(iw * scale), int(ih * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    ox = (nw - WIDTH) // 2
    oy = (nh - HEIGHT) // 2
    return resized[oy:oy + HEIGHT, ox:ox + WIDTH].copy()


def upgrade_project(key):
    cfg = PROJECT_CONFIGS[key]
    print(f"\n==========================================")
    print(f"🎬 Upgrading {cfg['title']} to AEP Cinema Standard")
    print(f"==========================================")

    pdir = Path(cfg["dir"])
    assets_dir = pdir / "assets"
    total_frames = int(cfg["duration"] * FPS)
    temp_video = pdir / "temp_aep_stream.mp4"

    # Pre-load scenes
    scenes_data = []
    for sfile, s_start, s_end in cfg["scenes"]:
        img = load_scaled_scene(assets_dir / sfile)
        scenes_data.append((img, s_start, s_end))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(temp_video), fourcc, FPS, (WIDTH, HEIGHT))

    flare = generate_rainbow_prism_flare(WIDTH, HEIGHT, intensity=0.40, blur_radius=40)
    flare_norm = np.clip(flare / 255.0, 0, 1)

    cover_saved = False

    particles = []
    np.random.seed(42)
    for _ in range(50):
        particles.append({
            "x": np.random.uniform(20, WIDTH - 20),
            "y": np.random.uniform(0, HEIGHT),
            "radius": np.random.uniform(3, 8),
            "speed": np.random.uniform(0.7, 1.8),
            "phase": np.random.uniform(0, math.pi * 2),
            "color": random.choice([
                (70, 210, 255),   # Golden amber
                (255, 235, 200),  # Warm white
                (170, 180, 255),  # Soft peach rose
                (230, 210, 255)   # Stardust violet
            ])
        })

    cross_frames = 10

    for frame_idx in range(total_frames):
        t = frame_idx / float(FPS)

        # 1. Determine active scene and compute dynamic zoom/motion + cross-dissolve
        active_idx = len(scenes_data) - 1
        for i, (s_img, s_start, s_end) in enumerate(scenes_data):
            if s_start <= t < s_end:
                active_idx = i
                break

        curr_img, s_start, s_end = scenes_data[active_idx]
        t_shot = t - s_start
        dur_shot = max(0.1, s_end - s_start)

        # Per-shot dynamic camera motion (push-in, float, lateral pan)
        if active_idx % 2 == 0:
            zoom = 1.0 + 0.035 * (t_shot / dur_shot)
            dx = math.sin(t_shot * 0.8) * 3.0
            dy = math.cos(t_shot * 0.6) * 2.0
        else:
            zoom = 1.035 - 0.025 * (t_shot / dur_shot)
            dx = -math.sin(t_shot * 0.7) * 3.0
            dy = math.sin(t_shot * 0.5) * 2.0

        zw, zh = int(WIDTH * zoom), int(HEIGHT * zoom)
        scaled_scene = cv2.resize(curr_img, (zw, zh), interpolation=cv2.INTER_LINEAR)
        ox = max(0, min(int((zw - WIDTH) // 2 + dx), zw - WIDTH))
        oy = max(0, min(int((zh - HEIGHT) // 2 + dy), zh - HEIGHT))
        frame_base = scaled_scene[oy:oy + HEIGHT, ox:ox + WIDTH]
        if frame_base.shape[:2] != (HEIGHT, WIDTH):
            frame_base = cv2.resize(frame_base, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)

        # Cross-fade with previous shot if at transition
        if active_idx > 0:
            frame_in_shot = frame_idx - int(s_start * FPS)
            if 0 <= frame_in_shot < cross_frames:
                alpha = frame_in_shot / float(cross_frames)
                prev_img = scenes_data[active_idx - 1][0]
                prev_scaled = cv2.resize(prev_img, (WIDTH, HEIGHT), interpolation=cv2.INTER_LINEAR)
                frame_base = cv2.addWeighted(prev_scaled, 1.0 - alpha, frame_base, alpha, 0)

        # 2. Living Ambient Light Particles (Floating Bokeh)
        particle_overlay = frame_base.copy()
        for p in particles:
            py = int((p["y"] - t * p["speed"] * 38) % HEIGHT)
            px = int(p["x"] + math.sin(t * 1.2 + p["phase"]) * 14)
            px = max(5, min(px, WIDTH - 5))
            rad = int(p["radius"] * (1.0 + 0.25 * math.sin(t * 2.5 + p["phase"])))
            cv2.circle(particle_overlay, (px, py), rad, p["color"], -1, cv2.LINE_AA)
        frame_base = cv2.addWeighted(particle_overlay, 0.35, frame_base, 0.65, 0)

        # 2. VFX: Deep Glow -> Rainbow Prism -> Cinema S-Curve -> Grain
        glow = apply_deep_glow(frame_base, threshold=175, bloom_factor=0.55, tint=(0.92, 1.05, 1.18))
        g_norm = glow.astype(np.float32) / 255.0
        flared = np.clip((1.0 - (1.0 - g_norm) * (1.0 - flare_norm)) * 255.0, 0, 255).astype(np.uint8)
        graded = apply_cinema_grade(flared, lift=12, contrast=1.12, warm_highlight=1.07, cool_shadow=1.03)
        grained = add_film_grain(graded, intensity=3.0, seed=frame_idx)

        # 3. Single-Layer Cinema Caption (Zero dual-caption clutter)
        active_lyric = None
        for lyr in cfg["lyrics"]:
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

        if not cover_saved and t >= 5.0:
            cv2.imwrite(cfg["cover"], final_bgr)
            cover_saved = True

        writer.write(final_bgr)

        if frame_idx % 200 == 0:
            print(f"[{cfg['title']}] Rendered {frame_idx}/{total_frames} frames ({t:.1f}s)")

    writer.release()

    # Mux audio
    print(f"[{cfg['title']}] Muxing Audio with FFmpeg...")
    final_output = cfg["output"]
    cmd = f'ffmpeg -y -i "{temp_video}" -i "{cfg["audio"]}" -af "volume=1.4,alimiter=limit=0.94:attack=5:release=50" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -c:a aac -b:a 320k -shortest "{final_output}"'
    res = os.system(cmd)
    if res != 0:
        raise RuntimeError("FFmpeg muxing failed!")

    if temp_video.exists():
        temp_video.unlink()

    # Story Card
    import reels_booster
    reels_booster.generate_story_card(cfg["cover"], cfg["title"], cfg["story_card"], "@vynox_00000")
    print(f"✅ {cfg['title']} AEP Upgrade COMPLETE: {final_output}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for k in PROJECT_CONFIGS:
            upgrade_project(k)
    elif target in PROJECT_CONFIGS:
        upgrade_project(target)
    else:
        print(f"Unknown target: {target}")
