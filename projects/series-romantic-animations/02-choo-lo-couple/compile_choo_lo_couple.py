#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD 2D Romantic Animated Lyric Reel for "Choo Lo" by The Local Train.
Style: Hand-drawn 2D indie anime couple in rain (inspired by @ujan_097 and @hzn.animx).
Warm paper watercolor aesthetic, 4 keyframe character scenes, 68pt prominent English lyrics.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/series-romantic-animations/02-choo-lo-couple")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.local/bin/ffmpeg"
FFPROBE = "/home/pratik/.local/bin/ffprobe"

audio_file = AUDIO_DIR / "choo_lo_clip.wav"
total_dur = 27.50

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

# 1. Generate ASS subtitles with 68pt modern typography
ass_lines = [
    "[Script Info]",
    "Title: Choo Lo - Romantic 2D Animation Reel",
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
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(27.0)},TitleBadge,,0,0,0,,{{\\fade(500,500)}}♫  THE LOCAL TRAIN  •  CHOO LO",
    
    # Line 1: Khada hoon aaj bhi wahin (02.8s - 07.2s)
    f"Dialogue: 1,{sec_to_ass(2.8)},{sec_to_ass(7.2)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H0044EEFF&}}Khada hoon{{\\c&H00FFFFFF&}} aaj bhi wahin...",
    
    # Line 2: Ke dil phir bekarar hai (07.2s - 13.0s)
    f"Dialogue: 1,{sec_to_ass(7.2)},{sec_to_ass(13.0)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Ke dil phir {{\\c&H0055EEFF&}}bekarar{{\\c&H00FFFFFF&}} hai...",
    
    # Line 3: Khada hoon aaj bhi wahin (13.0s - 18.2s)
    f"Dialogue: 1,{sec_to_ass(13.0)},{sec_to_ass(18.2)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H0044EEFF&}}Khada hoon{{\\c&H00FFFFFF&}} aaj bhi wahin...",
    
    # Line 4: Ke tera intezaar hai (18.2s - 22.2s)
    f"Dialogue: 1,{sec_to_ass(18.2)},{sec_to_ass(22.2)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Ke tera {{\\c&H0066FFFF&}}intezaar{{\\c&H00FFFFFF&}} hai...",
    
    # Line 5 / Drop: Choo lo jo mujhe tum kabhi (22.2s - 27.2s)
    f"Dialogue: 1,{sec_to_ass(22.2)},{sec_to_ass(27.2)},ModernLyric,,0,0,0,,{{\\fade(250,450)}}{{\\c&H0038E8FF&}}Choo lo{{\\c&H00FFFFFF&}} jo mujhe tum kabhi..."
]

ass_file = OUT_DIR / "choo_lo_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitle file written: {ass_file}")

# 2. Define shots mapping to the 4 keyframes
shots_config = [
    # Shot 1: Scene 1 - Waiting in rain (0.0s - 7.2s = 7.2s)
    {
        "img": ASSETS_DIR / "scene-1.jpg",
        "dur": 7.2,
        "zoom_expr": "'min(zoom+0.0006,1.08)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:gs=0.01:bs=0.04"
    },
    # Shot 2: Scene 2 - Boy under umbrella, shy eye contact (7.2s - 13.0s = 5.8s)
    {
        "img": ASSETS_DIR / "scene-2.jpg",
        "dur": 5.8,
        "zoom_expr": "'min(1.02+0.0007*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih*0.48-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.04:bs=0.03"
    },
    # Shot 3: Scene 3 - Tender hand touch detail (13.0s - 18.2s = 5.2s)
    {
        "img": ASSETS_DIR / "scene-3.jpg",
        "dur": 5.2,
        "zoom_expr": "'min(1.05+0.0008*on,1.14)'",
        "x_expr": "'iw*0.50-(iw/zoom/2)'",
        "y_expr": "'ih*0.52-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.05:gs=0.01:bs=0.03"
    },
    # Shot 4: Scene 4 - Smiling together climax (18.2s - 27.5s = 9.3s)
    {
        "img": ASSETS_DIR / "scene-4.jpg",
        "dur": 9.3,
        "zoom_expr": "'min(1.0+0.0005*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:bs=0.04"
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
final_mp4 = OUT_DIR / "film_choo_lo_romantic.mp4"
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
    "-ss", "00:00:23.500",
    "-i", str(final_mp4),
    "-frames:v", "1",
    "-q:v", "2",
    str(cover_jpg)
], check=True)

# Cleanup intermediate files to keep disk clean
for sf in shot_files:
    if sf.exists():
        sf.unlink()
if concat_mp4.exists():
    concat_mp4.unlink()
if concat_list.exists():
    concat_list.unlink()

print(f"\n🎉 Successfully created romantic film: {final_mp4}")
print(f"🖼️ Cover image generated: {cover_jpg}")

