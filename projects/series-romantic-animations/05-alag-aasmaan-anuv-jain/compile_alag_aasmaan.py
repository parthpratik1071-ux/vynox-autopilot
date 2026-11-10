#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD 2D Romantic Animated Lyric Reel for "Alag Aasmaan" by Anuv Jain.
Style: Hand-drawn 2D indie anime long-distance romance (inspired by @hzn.animx and @ujan_097).
Rooftop moon, parallel skies, glowing celestial thread, warm watercolor paper texture.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/series-romantic-animations/05-alag-aasmaan-anuv-jain")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.local/bin/ffmpeg"
FFPROBE = "/home/pratik/.local/bin/ffprobe"

audio_file = AUDIO_DIR / "alag_clip.wav"
total_dur = 24.00

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: Alag Aasmaan - Romantic 2D Animation Reel",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: TitleBadge,DejaVu Sans,30,&H00C0E8FF,&H00000000,&H00101010,&H80000000,-1,0,0,0,100,100,2,0,1,2,1,8,40,40,180,1",
    "Style: ModernLyric,DejaVu Sans,68,&H00FFFFFF,&H000000FF,&H00080808,&H90000000,-1,0,0,0,100,100,2,0,1,3.5,4,2,50,50,400,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    # Top Song Badge
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(23.5)},TitleBadge,,0,0,0,,{{\\fade(400,400)}}♫  ANUV JAIN  •  ALAG AASMAAN",
    
    # Line 1: Dil ko mere yeh hai pata (00.5s - 05.5s)
    f"Dialogue: 1,{sec_to_ass(0.5)},{sec_to_ass(5.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H003CE0FF&}}Dil ko mere{{\\c&H00FFFFFF&}} yeh hai pata...",
    
    # Line 2: Ke milon ka yeh faasla hai (05.5s - 12.0s)
    f"Dialogue: 1,{sec_to_ass(5.5)},{sec_to_ass(12.0)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Ke milon ka yeh {{\\c&H00FFB040&}}faasla hai{{\\c&H00FFFFFF&}}...",
    
    # Line 3: Alag aasmaan bhi hai toh kya? (12.0s - 18.0s)
    f"Dialogue: 1,{sec_to_ass(12.0)},{sec_to_ass(18.0)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H003CE0FF&}}Alag aasmaan bhi hai{{\\c&H00FFFFFF&}} toh kya?...",
    
    # Line 4: Yeh dil na maane (18.0s - 23.5s)
    f"Dialogue: 1,{sec_to_ass(18.0)},{sec_to_ass(23.5)},ModernLyric,,0,0,0,,{{\\fade(250,450)}}Yeh dil {{\\c&H0055EEFF&}}na maane{{\\c&H00FFFFFF&}}..."
]

ass_file = OUT_DIR / "alag_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitle file written: {ass_file}")

shots_config = [
    # Shot 1: Girl on rooftop looking at moon (0.0s - 6.0s = 6.0s)
    {
        "img": ASSETS_DIR / "scene-1.jpg",
        "dur": 6.0,
        "zoom_expr": "'min(zoom+0.0006,1.08)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=-0.01:bs=0.05"
    },
    # Shot 2: Boy miles away looking at same sky (6.0s - 12.0s = 6.0s)
    {
        "img": ASSETS_DIR / "scene-2.jpg",
        "dur": 6.0,
        "zoom_expr": "'min(1.02+0.0007*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih*0.48-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.02:bs=0.04"
    },
    # Shot 3: Celestial stardust connecting both across distance (12.0s - 18.0s = 6.0s)
    {
        "img": ASSETS_DIR / "scene-3.jpg",
        "dur": 6.0,
        "zoom_expr": "'min(1.04+0.0007*on,1.12)'",
        "x_expr": "'iw*0.50-(iw/zoom/2)'",
        "y_expr": "'ih*0.50-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:bs=0.06"
    },
    # Shot 4: Girl smiling softly with starlight eyes (18.0s - 24.0s = 6.0s)
    {
        "img": ASSETS_DIR / "scene-4.jpg",
        "dur": 6.0,
        "zoom_expr": "'min(1.0+0.0005*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.02:bs=0.04"
    }
]

shot_files = []
for idx, s in enumerate(shots_config):
    shot_mp4 = OUT_DIR / f"shot_{idx}.mp4"
    frames = int(s["dur"] * 30)
    print(f"🎬 Rendering Shot {idx+1}/{len(shots_config)} ({s['dur']}s)...")
    
    vf = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z={s['zoom_expr']}:x={s['x_expr']}:y={s['y_expr']}:d={frames}:s=1080x1920:fps=30,"
        f"{s['color_filter']},"
        f"format=yuv420p"
    )
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(s["img"]),
        "-vf", vf,
        "-t", str(s["dur"]),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        str(shot_mp4)
    ]
    subprocess.run(cmd, check=True)
    shot_files.append(shot_mp4)

concat_list = OUT_DIR / "shots_concat.txt"
with open(concat_list, "w") as f:
    for sf in shot_files:
        f.write(f"file '{sf.resolve()}'\n")

concat_mp4 = OUT_DIR / "raw_visual.mp4"
subprocess.run([
    FFMPEG, "-y",
    "-f", "concat", "-safe", "0", "-i", str(concat_list),
    "-c", "copy",
    str(concat_mp4)
], check=True)

final_mp4 = OUT_DIR / "film_alag_aasmaan_romantic.mp4"
print(f"🔥 Burning subtitles & muxing final audio...")
subprocess.run([
    FFMPEG, "-y",
    "-i", str(concat_mp4),
    "-i", str(audio_file),
    "-vf", f"ass={ass_file.resolve()}",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-c:a", "aac", "-b:a", "256k",
    "-shortest",
    str(final_mp4)
], check=True)

cover_jpg = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y",
    "-ss", "00:00:19.500",
    "-i", str(final_mp4),
    "-frames:v", "1",
    "-q:v", "2",
    str(cover_jpg)
], check=True)

for sf in shot_files:
    if sf.exists():
        sf.unlink()
if concat_mp4.exists():
    concat_mp4.unlink()
if concat_list.exists():
    concat_list.unlink()

print(f"\n🎉 Successfully created romantic film: {final_mp4}")
print(f"🖼️ Cover image generated: {cover_jpg}")

