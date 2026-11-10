#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD 2D Romantic Animated Lyric Reel for "Husn" by Anuv Jain.
Style: Hand-drawn 2D indie anime midnight balcony & stargazing aesthetic (inspired by @hzn.animx and @ujan_097).
Deep sapphire night, glowing stars, floating memory petals, warm paper watercolor texture, 68pt English lyrics.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/series-romantic-animations/03-husn-anuv-jain")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.local/bin/ffmpeg"
FFPROBE = "/home/pratik/.local/bin/ffprobe"

audio_file = AUDIO_DIR / "husn_clip.wav"
total_dur = 25.00

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

# 1. Generate ASS subtitles with 68pt modern typography
ass_lines = [
    "[Script Info]",
    "Title: Husn - Romantic 2D Animation Reel",
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
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(24.5)},TitleBadge,,0,0,0,,{{\\fade(500,500)}}♫  ANUV JAIN  •  HUSN",
    
    # Line 1: Main mere husn ke alawa (00.5s - 06.5s)
    f"Dialogue: 1,{sec_to_ass(0.5)},{sec_to_ass(6.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H003CE0FF&}}Main mere husn ke{{\\c&H00FFFFFF&}} alawa...",
    
    # Line 2: Kabhi dil bhi maang lo na, haye pal mein main pighal jaaun (06.5s - 12.8s)
    f"Dialogue: 1,{sec_to_ass(6.5)},{sec_to_ass(12.8)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Kabhi dil bhi maang lo na, {{\\c&H00FFB040&}}haye pal mein main pighal jaaun{{\\c&H00FFFFFF&}}...",
    
    # Line 3: Haan ab aisa na karo ke dil jud na paaye (12.8s - 18.5s)
    f"Dialogue: 1,{sec_to_ass(12.8)},{sec_to_ass(18.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H003CE0FF&}}Haan ab aisa na karo{{\\c&H00FFFFFF&}} ke dil jud na paaye...",
    
    # Line 4: Vaapas teri baaton se bikhar jaaun (18.5s - 24.5s)
    f"Dialogue: 1,{sec_to_ass(18.5)},{sec_to_ass(24.5)},ModernLyric,,0,0,0,,{{\\fade(250,450)}}Vaapas teri baaton se {{\\c&H0055EEFF&}}bikhar jaaun{{\\c&H00FFFFFF&}}..."
]

ass_file = OUT_DIR / "husn_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitle file written: {ass_file}")

# 2. Define shots mapping to the 4 keyframes
shots_config = [
    # Shot 1: Scene 1 - Moonlit balcony stargazing (0.0s - 6.5s = 6.5s)
    {
        "img": ASSETS_DIR / "scene-1.jpg",
        "dur": 6.5,
        "zoom_expr": "'min(zoom+0.0006,1.08)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=-0.02:bs=0.05"
    },
    # Shot 2: Scene 2 - Holding glowing mug looking at quiet city (6.5s - 12.8s = 6.3s)
    {
        "img": ASSETS_DIR / "scene-2.jpg",
        "dur": 6.3,
        "zoom_expr": "'min(1.02+0.0007*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih*0.48-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:gs=0.01:bs=0.04"
    },
    # Shot 3: Scene 3 - Floating memory stardust & petals (12.8s - 18.5s = 5.7s)
    {
        "img": ASSETS_DIR / "scene-3.jpg",
        "dur": 5.7,
        "zoom_expr": "'min(1.05+0.0008*on,1.14)'",
        "x_expr": "'iw*0.50-(iw/zoom/2)'",
        "y_expr": "'ih*0.50-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.04:bs=0.06"
    },
    # Shot 4: Scene 4 - Hand reaching toward crescent moon & star (18.5s - 25.0s = 6.5s)
    {
        "img": ASSETS_DIR / "scene-4.jpg",
        "dur": 6.5,
        "zoom_expr": "'min(1.0+0.0005*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=-0.01:bs=0.06"
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

# 3. Concatenate shots
concat_list = OUT_DIR / "shots_concat.txt"
with open(concat_list, "w") as f:
    for sf in shot_files:
        f.write(f"file '{sf.resolve()}'\n")

concat_mp4 = OUT_DIR / "raw_visual.mp4"
cmd_concat = [
    FFMPEG, "-y",
    "-f", "concat", "-safe", "0", "-i", str(concat_list),
    "-c", "copy",
    str(concat_mp4)
]
subprocess.run(cmd_concat, check=True)

# 4. Burn ASS subtitles and mux audio
final_mp4 = OUT_DIR / "film_husn_romantic.mp4"
print(f"🔥 Burning subtitles & muxing final audio...")
cmd_final = [
    FFMPEG, "-y",
    "-i", str(concat_mp4),
    "-i", str(audio_file),
    "-vf", f"ass={ass_file.resolve()}",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-c:a", "aac", "-b:a", "256k",
    "-shortest",
    str(final_mp4)
]
subprocess.run(cmd_final, check=True)

# 5. Extract high quality cover thumbnail
cover_jpg = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y",
    "-ss", "00:00:20.000",
    "-i", str(final_mp4),
    "-frames:v", "1",
    "-q:v", "2",
    str(cover_jpg)
], check=True)

# Cleanup intermediate files
for sf in shot_files:
    if sf.exists():
        sf.unlink()
if concat_mp4.exists():
    concat_mp4.unlink()
if concat_list.exists():
    concat_list.unlink()

print(f"\n🎉 Successfully created romantic film: {final_mp4}")
print(f"🖼️ Cover image generated: {cover_jpg}")

