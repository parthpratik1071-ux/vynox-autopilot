#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD 2D Romantic Animated Lyric Reel for "Kashish" by Ashish Bhatia.
Art style inspired by @hzn.animx (1.89M views) - Hand-drawn 2D expressive character romance,
warm paper texture, soft watercolor aesthetic, prominent 66pt modern kinetic lyrics.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/series-romantic-animations/01-kashish")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

audio_file = AUDIO_DIR / "kashish_clip.wav"
total_dur = 12.70

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

# 1. Generate beautifully styled ASS subtitles with modern aesthetic typography (66pt)
ass_lines = [
    "[Script Info]",
    "Title: Kashish - Romantic 2D Animation Reel",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: TitleBadge,DejaVu Sans,30,&H00C0E8FF,&H00000000,&H00101010,&H80000000,-1,0,0,0,100,100,2,0,1,2,1,8,40,40,180,1",
    "Style: ModernLyric,DejaVu Sans,66,&H00FFFFFF,&H000000FF,&H00080808,&H90000000,-1,0,0,0,100,100,2,0,1,3.5,4,2,50,50,380,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    # Top Song Badge
    f"Dialogue: 0,{sec_to_ass(0.3)},{sec_to_ass(12.5)},TitleBadge,,0,0,0,,{{\\fade(400,400)}}♫  ASHISH BHATIA  •  KASHISH",
    
    # Line 1: Uski aankhon mein faila kajal (00.0s - 03.8s)
    f"Dialogue: 1,{sec_to_ass(0.2)},{sec_to_ass(3.8)},ModernLyric,,0,0,0,,{{\\fade(200,200)}}{{\\c&H003CE0FF&}}Uski aankhon mein{{\\c&H00FFFFFF&}} faila kajal...",
    
    # Line 2: Baaton se karti ghayal (03.8s - 08.2s)
    f"Dialogue: 1,{sec_to_ass(3.8)},{sec_to_ass(8.2)},ModernLyric,,0,0,0,,{{\\fade(200,200)}}Baaton se karti {{\\c&H003CE0FF&}}ghayal...{{\\c&H00FFFFFF&}}",
    
    # Line 3: Saanson mein uska hi hai naam (08.2s - 12.7s)
    f"Dialogue: 1,{sec_to_ass(8.2)},{sec_to_ass(12.5)},ModernLyric,,0,0,0,,{{\\fade(200,400)}}{{\\c&H003CE0FF&}}Saanson mein{{\\c&H00FFFFFF&}} uska hi hai naam..."
]

ass_file = OUT_DIR / "kashish_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitle file written: {ass_file}")

# 2. Render 3 cinematic shots
# Shots:
# Shot 1: 3.8s (Scene 1)
# Shot 2: 4.4s (Scene 2)
# Shot 3: 4.5s (Scene 3)
shots_config = [
    {
        "scene": 1,
        "dur": 3.8,
        "zoom_expr": "'min(zoom+0.0008,1.08)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih*0.42-(ih/zoom/2)'",
        "filter": "colorbalance=rs=0.03:gs=0.01:bs=0.02"
    },
    {
        "scene": 2,
        "dur": 4.4,
        "zoom_expr": "'min(1.04+0.0006*on,1.12)'",
        "x_expr": "'iw*0.48-(iw/zoom/2)'",
        "y_expr": "'ih*0.40-(ih/zoom/2)'",
        "filter": "colorbalance=rs=0.04:bs=0.03"
    },
    {
        "scene": 3,
        "dur": 4.5,
        "zoom_expr": "'max(1.10-0.0005*on,1.02)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih*0.45-(ih/zoom/2)'",
        "filter": "colorbalance=rs=0.03:gs=0.01:bs=0.04"
    }
]

tmp_shots = []
for i, sc in enumerate(shots_config):
    img_p = ASSETS_DIR / f"scene-{sc['scene']}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    dur = sc["dur"]
    frames = int(dur * 30)
    
    cmd_shot = [
        FFMPEG, "-y", "-loop", "1", "-i", str(img_p),
        "-vf", (
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z={sc['zoom_expr']}:x={sc['x_expr']}:y={sc['y_expr']}:d={frames}:s=1080x1920:fps=30,"
            f"{sc['filter']}"
        ),
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-crf", "17",
        str(shot_mp4)
    ]
    print(f"🎬 Rendering Shot {i+1}/3 ({dur}s)...")
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
final_film = OUT_DIR / "film_kashish_romantic.mp4"
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
print("🚀 Muxing final 1080x1920 Full HD romantic lyric reel...")
subprocess.run(cmd_final, check=True)

# 5. Extract cover image
cover_img = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y", "-ss", "00:00:03.000", "-i", str(final_film),
    "-vframes", "1", "-q:v", "2", str(cover_img)
], check=True)

print(f"\n🎉 Successfully created romantic film: {final_film}")
print(f"🖼️ Cover image generated: {cover_img}")

