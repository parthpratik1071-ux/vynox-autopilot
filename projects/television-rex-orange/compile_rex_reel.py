#!/usr/bin/env python3
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/television-rex-orange")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

audio_file = AUDIO_DIR / "rex_clip_25s.wav"
total_dur = 25.0

# 1. Generate styled ASS subtitles for Rex Orange County
def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: Television / So Far So Good",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 720",
    "PlayResY: 1280",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,40,40,240,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    f"Dialogue: 0,{sec_to_ass(0.2)},{sec_to_ass(3.2)},Default,,0,0,0,,If you're looking for something new...",
    f"Dialogue: 0,{sec_to_ass(3.2)},{sec_to_ass(6.25)},Default,,0,0,0,,I know somebody that you could choose.",
    f"Dialogue: 0,{sec_to_ass(6.25)},{sec_to_ass(8.2)},Default,,0,0,0,,{{\\c&H0033FFFF&}}What about me?{{\\c&H00FFFFFF&}}",
    f"Dialogue: 0,{sec_to_ass(8.2)},{sec_to_ass(10.2)},Default,,0,0,0,,{{\\c&H0033FFFF&}}What about me?{{\\c&H00FFFFFF&}}",
    f"Dialogue: 0,{sec_to_ass(10.2)},{sec_to_ass(13.5)},Default,,0,0,0,,What about {{\\c&H0033FFFF&}}me and you together?{{\\c&H00FFFFFF&}}",
    f"Dialogue: 0,{sec_to_ass(13.5)},{sec_to_ass(16.5)},Default,,0,0,0,,Something that could {{\\c&H0033FFFF&}}last forever{{\\c&H00FFFFFF&}}...",
    f"Dialogue: 0,{sec_to_ass(16.5)},{sec_to_ass(18.5)},Default,,0,0,0,,{{\\c&H0033FFFF&}}What about me?{{\\c&H00FFFFFF&}}",
    f"Dialogue: 0,{sec_to_ass(18.5)},{sec_to_ass(21.5)},Default,,0,0,0,,What about {{\\c&H0033FFFF&}}me and you together?{{\\c&H00FFFFFF&}}",
    f"Dialogue: 0,{sec_to_ass(21.5)},{sec_to_ass(25.0)},Default,,0,0,0,,{{\\c&H0033FFFF&}}Something that could really last forever{{\\c&H00FFFFFF&}} ✨"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w") as f:
    f.write("\n".join(ass_lines))

# 2. Render 4 aesthetic indie cartoon scenes (6.25s each)
shot_durs = [6.25, 6.25, 6.25, 6.25]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)
    z_expr = "'min(zoom+0.0012,1.2)'" if i % 2 == 0 else "'max(1.2-0.0012*on,1.0)'"
    
    cmd_shot = [
        FFMPEG, "-y", "-loop", "1", "-i", str(img_p),
        "-vf", f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,zoompan=z={z_expr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=720x1280:fps=30",
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(shot_mp4)
    ]
    subprocess.run(cmd_shot, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp_shots.append(shot_mp4)
    print(f"🎬 Rendered scene {i+1}/4 ({dur}s)")

# Concat video
shots_concat = OUT_DIR / "shots_concat.txt"
with open(shots_concat, "w") as f:
    for sp in tmp_shots:
        f.write(f"file '{sp}'\n")

raw_video = OUT_DIR / "raw_video.mp4"
subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(shots_concat), "-c", "copy", str(raw_video)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Final mux with audio and subtitles
final_film = OUT_DIR / "film_rex.mp4"
cmd_final = [
    FFMPEG, "-y",
    "-i", str(raw_video),
    "-i", str(audio_file),
    "-vf", f"ass={ass_file}",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    str(final_film)
]
subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

cover_img = OUT_DIR / "cover.jpg"
subprocess.run([FFMPEG, "-y", "-ss", "00:00:02.000", "-i", str(final_film), "-vframes", "1", "-q:v", "2", str(cover_img)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cleanup temp files
for sp in tmp_shots:
    if sp.exists(): sp.unlink()
if raw_video.exists(): raw_video.unlink()

print(f"🎉 RENDER COMPLETE: {final_film}")
print(f"🖼️ COVER: {cover_img}")
