#!/usr/bin/env python3
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/meow-meow-cat")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

audio_file = AUDIO_DIR / "cat_clip_24s.wav"
total_dur = 24.0

# 1. Generate styled ASS subtitles
def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: Meow Meow Kisko Chhodu",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 720",
    "PlayResY: 1280",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: Default,Noto Sans Devanagari,44,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,40,40,240,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    f"Dialogue: 0,{sec_to_ass(0.5)},{sec_to_ass(3.2)},Default,,0,0,0,,{{\\c&H0033FFFF&}}म्याऊँ म्याऊँ... म्याऊँ म्याऊँ...{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Meow Meow... Meow Meow...",
    f"Dialogue: 0,{sec_to_ass(3.2)},{sec_to_ass(6.0)},Default,,0,0,0,,{{\\c&H0033FFFF&}}किसको छोड़ूँ, किसको खाऊँ?{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Kisko chhodu, kisko khau?",
    f"Dialogue: 0,{sec_to_ass(6.0)},{sec_to_ass(9.0)},Default,,0,0,0,,एक तरफ है {{\\c&H0033FFFF&}}दूध मलाई{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Ek taraf hai doodh malai",
    f"Dialogue: 0,{sec_to_ass(9.0)},{sec_to_ass(12.0)},Default,,0,0,0,,एक तरफ है {{\\c&H0033FFFF&}}चुहिया आई!{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Ek taraf hai chuhiya aai!",
    f"Dialogue: 0,{sec_to_ass(12.0)},{sec_to_ass(15.0)},Default,,0,0,0,,एक तरफ है {{\\c&H005555FF&}}मालिक आया{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Ek taraf hai malik aaya",
    f"Dialogue: 0,{sec_to_ass(15.0)},{sec_to_ass(17.5)},Default,,0,0,0,,एक तरफ है {{\\c&H005555FF&}}कुत्ता आया!{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Ek taraf hai kutta aaya!",
    f"Dialogue: 0,{sec_to_ass(17.5)},{sec_to_ass(20.5)},Default,,0,0,0,,{{\\c&H0033FFFF&}}किधर जाऊँ, किधर जाऊँ?!{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Kidhar jau, kidhar jau?!",
    f"Dialogue: 0,{sec_to_ass(20.5)},{sec_to_ass(24.0)},Default,,0,0,0,,{{\\c&H0033FF33&}}दोनों लेके भाग गया!{{\\c&H00FFFFFF&}}\\N{{\\fs32\\c&H00FFFFFF&}}Donon leke bhaag gaya!"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w") as f:
    f.write("\n".join(ass_lines))

# 2. Render 4 scenes (6.0s each)
shot_durs = [6.0, 6.0, 6.0, 6.0]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)
    z_expr = "'min(zoom+0.0015,1.25)'" if i % 2 == 0 else "'max(1.25-0.0015*on,1.0)'"
    
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
final_film = OUT_DIR / "film_cat.mp4"
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
