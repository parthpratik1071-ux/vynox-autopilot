#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD Viral Comedy Reel: "Sheru vs Oggy (Part 2)"
Re-branded and adapted for @vynox_00000.
Features 9:16 ambient blurred background, crisp centered 16:9 animation,
custom @vynox_00000 branding pill, and high-energy Romanized comedy captions (no glyph boxes).
"""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/sheru-vs-oggy-part2")
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.local/bin/ffmpeg"
FFPROBE = "/home/pratik/.local/bin/ffprobe"

raw_video = ASSETS_DIR / "raw_video.mp4"
total_dur = 32.53

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

# 1. Generate Clean High-Impact ASS Subtitles (no unrendered emoji boxes)
ass_lines = [
    "[Script Info]",
    "Title: Sheru vs Oggy - Part 2",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: TopHeader,DejaVu Sans,48,&H00FFFFFF,&H00000000,&H00050505,&H80000000,-1,0,0,0,100,100,2,0,1,4,3,8,40,40,220,1",
    "Style: BrandPill,DejaVu Sans,30,&H0038E8FF,&H00000000,&H00050505,&HA0000000,-1,0,0,0,100,100,2,0,1,2.5,2,8,40,40,290,1",
    "Style: WatermarkTag,DejaVu Sans,26,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,2,2,3,40,40,650,1",
    "Style: ComedyCaption,DejaVu Sans,64,&H0000FFFF,&H000000FF,&H000A0A0A,&H90000000,-1,0,0,0,100,100,2,0,1,4,4,2,40,40,320,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    # Top Header & Brand Tag (Persistent)
    f"Dialogue: 0,{sec_to_ass(0.2)},{sec_to_ass(32.5)},TopHeader,,0,0,0,,{{\\fade(300,300)}}SHERU VS OGGY  •  PART 2",
    f"Dialogue: 0,{sec_to_ass(0.2)},{sec_to_ass(32.5)},BrandPill,,0,0,0,,{{\\fade(300,300)}}@vynox_00000",
    f"Dialogue: 0,{sec_to_ass(0.2)},{sec_to_ass(32.5)},WatermarkTag,,0,0,0,,{{\\fade(300,300)}}@vynox_00000",
    
    # Dialogue Subtitles
    f"Dialogue: 1,{sec_to_ass(0.3)},{sec_to_ass(4.5)},ComedyCaption,,0,0,0,,{{\\fade(150,150)}}Sun mera beta{{\\c&H00FFFFFF&}} teri school mein nahi padega!",
    f"Dialogue: 1,{sec_to_ass(4.5)},{sec_to_ass(8.2)},ComedyCaption,,0,0,0,,{{\\fade(150,150)}}Ab main banaunga{{\\c&H0000FFFF&}} duniya ka sabse bada school!",
    f"Dialogue: 1,{sec_to_ass(8.2)},{sec_to_ass(12.8)},ComedyCaption,,0,0,0,,{{\\c&H0038E8FF&}}{{\\fade(150,150)}}Beta is shahar mein mera raul hai...",
    f"Dialogue: 1,{sec_to_ass(12.8)},{sec_to_ass(17.5)},ComedyCaption,,0,0,0,,{{\\fade(150,150)}}Mere paas {{\\c&H0000FFFF&}}MULTI-TRILLION DOLLARS{{\\c&H00FFFFFF&}} hain!",
    f"Dialogue: 1,{sec_to_ass(17.5)},{sec_to_ass(23.0)},ComedyCaption,,0,0,0,,{{\\fade(150,150)}}Tere se {{\\c&H0000FFFF&}}TRILLION TIMES{{\\c&H00FFFFFF&}} zyada paise hain!",
    f"Dialogue: 1,{sec_to_ass(23.0)},{sec_to_ass(27.0)},ComedyCaption,,0,0,0,,{{\\c&H003CE0FF&}}{{\\fade(150,150)}}Chal mere joote saaf kar!",
    f"Dialogue: 1,{sec_to_ass(27.0)},{sec_to_ass(32.5)},ComedyCaption,,0,0,0,,{{\\c&H0000FFFF&}}{{\\fade(150,300)}}JACK IS CALLING... TO BE CONTINUED!"
]

ass_file = OUT_DIR / "sheru_subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Clean Subtitle file written: {ass_file}")

final_mp4 = OUT_DIR / "film_sheru_vs_oggy_vynox.mp4"
print(f"🎬 Compiling 9:16 Vertical Reel with ambient background...")

filter_complex = (
    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.15:contrast=1.1[bg];"
    "[0:v]scale=1080:608:flags=lanczos[fg];"
    "[bg][fg]overlay=0:656[composed];"
    f"[composed]ass={ass_file.resolve()}[outv]"
)

cmd = [
    FFMPEG, "-y",
    "-i", str(raw_video),
    "-filter_complex", filter_complex,
    "-map", "[outv]",
    "-map", "0:a",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    str(final_mp4)
]
subprocess.run(cmd, check=True)

cover_jpg = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y",
    "-ss", "00:00:23.500",
    "-i", str(final_mp4),
    "-frames:v", "1",
    "-q:v", "2",
    str(cover_jpg)
], check=True)

print(f"\n🎉 Successfully compiled Sheru vs Oggy Reel: {final_mp4}")
print(f"🖼️ Cover image generated: {cover_jpg}")
