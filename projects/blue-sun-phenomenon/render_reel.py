#!/usr/bin/env python3
import json
import subprocess
import re
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/blue-sun-phenomenon")
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(PROJECT_DIR / "timings.json") as f:
    timing_data = json.load(f)

total_dur = timing_data["total_duration"]
timings = timing_data["timings"]

# 1. Generate ASS subtitle file
def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: Blue Sun Phenomenon",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 720",
    "PlayResY: 1280",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,40,40,240,1",
    "Style: Highlight,DejaVu Sans,46,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,3,2,40,40,240,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
]

# Split longer cues into short punchy subtitle lines
for t in timings:
    text = t["text"]
    start = t["start"]
    end = t["end"]
    dur = end - start
    
    # Split sentences by comma, period, or natural break
    parts = re.split(r'(?<=[.,;?!])\s+', text)
    if len(parts) == 1 and len(text) > 40:
        words = text.split()
        mid = len(words) // 2
        parts = [" ".join(words[:mid]), " ".join(words[mid:])]
    
    seg_dur = dur / len(parts)
    for idx, part in enumerate(parts):
        s_time = start + idx * seg_dur
        e_time = s_time + seg_dur
        # Highlight trigger words
        highlighted = part
        for kw in ["12:00 PM", "neon blue", "radiation", "sixty seconds", "mirrors", "shatter", "NASA", "anomaly", "eclipsed", "Timeline secured"]:
            if kw.lower() in highlighted.lower():
                highlighted = re.sub(f"(?i)({re.escape(kw)})", r"{\\c&H0000FFFF&}\\1{\\c&H00FFFFFF&}", highlighted)
        ass_lines.append(f"Dialogue: 0,{sec_to_ass(s_time)},{sec_to_ass(e_time)},Default,,0,0,0,,{highlighted}")

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w") as f:
    f.write("\n".join(ass_lines))

print("📝 Generated styled ASS subtitles")

# 2. Shot plan (6 visual scenes covering 72.76s)
shots = [
    {"img": ASSETS_DIR / "scene-1.jpg", "start": 0.0, "dur": 10.0, "zoom": "in"},
    {"img": ASSETS_DIR / "scene-2.jpg", "start": 10.0, "dur": 11.0, "zoom": "out"},
    {"img": ASSETS_DIR / "scene-3.jpg", "start": 21.0, "dur": 22.0, "zoom": "in"},
    {"img": ASSETS_DIR / "scene-4.jpg", "start": 43.0, "dur": 10.0, "zoom": "out"},
    {"img": ASSETS_DIR / "scene-5.jpg", "start": 53.0, "dur": 14.0, "zoom": "in"},
    {"img": ASSETS_DIR / "scene-6.jpg", "start": 67.0, "dur": round(total_dur - 67.0, 2), "zoom": "out"}
]

tmp_shots = []
for i, s in enumerate(shots):
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(s["dur"] * 30)
    if s["zoom"] == "in":
        z_expr = f"'min(zoom+0.0008,1.15)'"
    else:
        z_expr = f"'max(1.15-0.0008*on,1.0)'"
    
    cmd_shot = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(s["img"]),
        "-vf", f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,zoompan=z={z_expr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps=30",
        "-t", str(s["dur"]),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(shot_mp4)
    ]
    subprocess.run(cmd_shot, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp_shots.append(shot_mp4)
    print(f"🎬 Rendered camera shot {i+1}/{len(shots)} ({s['dur']}s)")

# Concat video shots
concat_list = OUT_DIR / "shots_concat.txt"
with open(concat_list, "w") as f:
    for sp in tmp_shots:
        f.write(f"file '{sp}'\n")

raw_video = OUT_DIR / "raw_visual.mp4"
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(raw_video)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 3. Final Render: Burn subtitles & mux with master audio
final_film = OUT_DIR / "film_cinematic.mp4"
master_audio = ASSETS_DIR / "master_audio.wav"

cmd_final = [
    "ffmpeg", "-y",
    "-i", str(raw_video),
    "-i", str(master_audio),
    "-vf", f"ass={ass_file}",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    str(final_film)
]
print("🚀 Compiling final cinematic film with subtitles & tension audio...")
subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Extract cover thumbnail
cover_img = OUT_DIR / "cover.jpg"
subprocess.run(["ffmpeg", "-y", "-ss", "00:00:03.000", "-i", str(final_film), "-vframes", "1", "-q:v", "2", str(cover_img)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Clean intermediate shots
for sp in tmp_shots:
    if sp.exists():
        sp.unlink()
if raw_video.exists():
    raw_video.unlink()

print(f"🎉 FINAL FILM RENDERED: {final_film}")
print(f"🖼️ COVER IMAGE: {cover_img}")
