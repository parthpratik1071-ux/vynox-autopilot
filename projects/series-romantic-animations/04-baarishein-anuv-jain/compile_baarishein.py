#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD 2D Romantic Animated Lyric Reel for "Baarishein" by Anuv Jain.
Style: Hand-drawn 2D indie anime monsoon romance (inspired by @hzn.animx and @ujan_097).
Raindrops on glass, cozy sweater, warm creamy watercolor paper texture, tender window bench romance.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/series-romantic-animations/04-baarishein-anuv-jain")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.local/bin/ffmpeg"
FFPROBE = "/home/pratik/.local/bin/ffprobe"

audio_file = AUDIO_DIR / "baarishein_clip.wav"
total_dur = 21.00

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: Baarishein - Romantic 2D Animation Reel",
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
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(20.5)},TitleBadge,,0,0,0,,{{\\fade(400,400)}}♫  ANUV JAIN  •  BAARISHEIN",
    
    # Line 1: Tum sun zara mere paas aa (00.5s - 05.5s)
    f"Dialogue: 1,{sec_to_ass(0.5)},{sec_to_ass(5.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}{{\\c&H003CE0FF&}}Tum sun zara{{\\c&H00FFFFFF&}} mere paas aa...",
    
    # Line 2: Ab baithe hain hum bhi yahan (05.5s - 10.5s)
    f"Dialogue: 1,{sec_to_ass(5.5)},{sec_to_ass(10.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Ab baithe hain hum bhi {{\\c&H00FFB040&}}yahan{{\\c&H00FFFFFF&}}...",
    
    # Line 3: Dil ke darmiyan baarishein hain, baarishein hain (10.5s - 15.5s)
    f"Dialogue: 1,{sec_to_ass(10.5)},{sec_to_ass(15.5)},ModernLyric,,0,0,0,,{{\\fade(250,250)}}Dil ke darmiyan {{\\c&H003CE0FF&}}baarishein hain...{{\\c&H00FFFFFF&}}",
    
    # Line 4: Teri hi baaton pe maine saja li hai duniya yahan (15.5s - 20.8s)
    f"Dialogue: 1,{sec_to_ass(15.5)},{sec_to_ass(20.8)},ModernLyric,,0,0,0,,{{\\fade(250,450)}}Teri baaton pe {{\\c&H0055EEFF&}}saja li hai duniya yahan{{\\c&H00FFFFFF&}}..."
]

ass_file = OUT_DIR / "baarishein_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitle file written: {ass_file}")

shots_config = [
    # Shot 1: Girl by rain window - establishing wide (0.0s - 5.5s = 5.5s)
    {
        "img": ASSETS_DIR / "scene-1.jpg",
        "dur": 5.5,
        "zoom_expr": "'min(zoom+0.0006,1.08)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:gs=0.01:bs=0.04"
    },
    # Shot 2: Push-in on her wistful smile and raindrops (5.5s - 10.5s = 5.0s)
    {
        "img": ASSETS_DIR / "scene-1.jpg",
        "dur": 5.0,
        "zoom_expr": "'min(1.08+0.0007*on,1.16)'",
        "x_expr": "'iw*0.48-(iw/zoom/2)'",
        "y_expr": "'ih*0.42-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.04:bs=0.03"
    },
    # Shot 3: Boy joins her on bench, cozy rain atmosphere (10.5s - 15.5s = 5.0s)
    {
        "img": ASSETS_DIR / "scene-2.jpg",
        "dur": 5.0,
        "zoom_expr": "'min(1.02+0.0006*on,1.10)'",
        "x_expr": "'iw/2-(iw/zoom/2)'",
        "y_expr": "'ih/2-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.03:gs=0.01:bs=0.04"
    },
    # Shot 4: Close intimate zoom on their tender smiling eye contact (15.5s - 21.0s = 5.5s)
    {
        "img": ASSETS_DIR / "scene-2.jpg",
        "dur": 5.5,
        "zoom_expr": "'min(1.08+0.0006*on,1.16)'",
        "x_expr": "'iw*0.50-(iw/zoom/2)'",
        "y_expr": "'ih*0.40-(ih/zoom/2)'",
        "color_filter": "colorbalance=rs=0.04:bs=0.03"
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

final_mp4 = OUT_DIR / "film_baarishein_romantic.mp4"
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
    "-ss", "00:00:14.000",
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
