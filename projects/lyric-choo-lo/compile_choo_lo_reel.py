#!/usr/bin/env python3
"""
Compile flagship 1080x1920 Full HD Animated Lyric Video for "Choo Lo" by The Local Train.
Cinematic Anime Pastel aesthetic (Makoto Shinkai skies, volumetric god rays, breezy train tracks).
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/lyric-choo-lo")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

audio_file = AUDIO_DIR / "choo_lo_clip.wav"
total_dur = 27.50

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

# 1. Generate beautifully styled ASS subtitles with pure Romanized lyrics & modern aesthetic typography
ass_lines = [
    "[Script Info]",
    "Title: The Local Train - Choo Lo (Aesthetic Lyric Reel)",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: TitleBadge,DejaVu Sans,30,&H00C0E8FF,&H00000000,&H00101010,&H80000000,-1,0,0,0,100,100,2,0,1,2,1,8,40,40,180,1",
    "Style: ModernLyric,DejaVu Sans,68,&H00FFFFFF,&H000000FF,&H00080808,&H90000000,-1,0,0,0,100,100,2,0,1,3.5,4,2,50,50,380,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    # Top Song Badge
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(27.0)},TitleBadge,,0,0,0,,{{\\fade(500,500)}}♫  THE LOCAL TRAIN  •  CHOO LO",
    
    # Line 1: Khada hoon aaj bhi wahin (02.8s - 07.2s)
    f"Dialogue: 1,{sec_to_ass(2.8)},{sec_to_ass(7.2)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H0044EEFF&}}Khada hoon{{\\c&H00FFFFFF&}} aaj bhi wahin...",
    
    # Line 2: Ke dil phir bekarar hai (07.2s - 12.5s)
    f"Dialogue: 1,{sec_to_ass(7.2)},{sec_to_ass(12.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Ke dil phir {{\\c&H0055EEFF&}}bekarar{{\\c&H00FFFFFF&}} hai...",
    
    # Line 3: Khada hoon aaj bhi wahin (12.5s - 17.8s)
    f"Dialogue: 1,{sec_to_ass(12.5)},{sec_to_ass(17.8)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H0044EEFF&}}Khada hoon{{\\c&H00FFFFFF&}} aaj bhi wahin...",
    
    # Line 4: Ke tera intezaar hai (17.8s - 22.2s)
    f"Dialogue: 1,{sec_to_ass(17.8)},{sec_to_ass(22.2)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Ke tera {{\\c&H0066FFFF&}}intezaar{{\\c&H00FFFFFF&}} hai...",
    
    # Line 5 / Drop: Choo lo jo mujhe tum kabhi (22.2s - 27.2s)
    f"Dialogue: 1,{sec_to_ass(22.2)},{sec_to_ass(27.2)},ModernLyric,,0,0,0,,{{\\fade(250,450)}}{{\\c&H0038E8FF&}}Choo lo{{\\c&H00FFFFFF&}} jo mujhe tum kabhi..."
]

ass_file = OUT_DIR / "choo_lo_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitle file written: {ass_file}")

# 2. Render 4 cinematic camera movements from the Makoto Shinkai artwork
img_p = ASSETS_DIR / "scene-1.jpg"

shots_config = [
    # Shot 1: Establishing wide platform shot (0.0 - 6.8s)
    {
        "dur": 6.8,
        "zoom_expr": "'min(zoom+0.0006,1.08)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.02:bs=0.03"
    },
    # Shot 2: Intimate bench & lantern push-in (6.8s - 12.5s)
    {
        "dur": 5.7,
        "zoom_expr": "'min(1.18+0.0005*on,1.26)'",
        "x_expr": "'iw*0.48-(iw/zoom/2)'",
        "y_expr": "'ih*0.62-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.04:gs=-0.01:bs=0.05"
    },
    # Shot 3: Tracks perspective pan (12.5s - 17.8s)
    {
        "dur": 5.3,
        "zoom_expr": "'min(1.15+0.0004*on,1.22)'",
        "x_expr": "'(iw*0.52+0.0001*on*iw)-(iw/zoom/2)'",
        "y_expr": "'ih*0.50-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=-0.02:bs=0.06"
    },
    # Shot 4: Skyward tilt to god rays & cloud cathedral (17.8s - 27.5s)
    {
        "dur": 9.7,
        "zoom_expr": "'min(1.10+0.0004*on,1.20)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'max(ih*0.45-0.0003*on*ih,ih*0.28)-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:gs=0.01:bs=0.04"
    }
]

tmp_shots = []
for i, sc in enumerate(shots_config):
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    dur = sc["dur"]
    frames = int(dur * 30)
    
    cmd_shot = [
        FFMPEG, "-y", "-loop", "1", "-i", str(img_p),
        "-vf", (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z={sc['zoom_expr']}:x={sc['x_expr']}:y={sc['y_expr']}:d={frames}:s=1080x1920:fps=30,"
            f"{sc['color_filter']}"
        ),
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-crf", "17",
        str(shot_mp4)
    ]
    print(f"🎬 Rendering Shot {i+1}/4 ({dur}s)...")
    subprocess.run(cmd_shot, check=True)
    tmp_shots.append(shot_mp4)

# 3. Concat shots into visual stream
shots_concat = OUT_DIR / "shots_concat.txt"
with open(shots_concat, "w") as f:
    for sp in tmp_shots:
        f.write(f"file '{sp.name}'\n")

raw_video = OUT_DIR / "raw_visual.mp4"
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0",
    "-i", str(shots_concat),
    "-c", "copy",
    str(raw_video)
], check=True)

# 4. Final Mux with Audio + Subtitles + High-Quality Encoding
final_film = OUT_DIR / "film_choo_lo_lyric.mp4"
cmd_final = [
    FFMPEG, "-y",
    "-i", str(raw_video),
    "-i", str(audio_file),
    "-vf", f"ass={ass_file}",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-c:a", "aac", "-b:a", "256k",
    "-t", str(total_dur),
    str(final_film)
]
print("🚀 Muxing final 1080x1920 Full HD lyric video...")
subprocess.run(cmd_final, check=True)

# 5. Extract cover image
cover_img = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y", "-ss", "00:00:04.500", "-i", str(final_film),
    "-vframes", "1", "-q:v", "2", str(cover_img)
], check=True)

print(f"\n🎉 Successfully created lyric film: {final_film}")
print(f"🖼️ Cover image generated: {cover_img}")
