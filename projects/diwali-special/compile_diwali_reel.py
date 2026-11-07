#!/usr/bin/env python3
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/diwali-special")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

# 1. Verify voice stitched duration
voice_stitched = AUDIO_DIR / "voice_stitched.wav"
res = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(voice_stitched)], capture_output=True, text=True, check=True)
TOTAL_DUR = round(float(res.stdout.strip()), 2)
print(f"🎙️ Master Voice Duration: {TOTAL_DUR:.2f}s")
assert 20.0 <= TOTAL_DUR <= 30.0, f"Duration {TOTAL_DUR}s must be between 20.0s and 30.0s!"

# 2. Mix voice with festive Indian BGM
bgm_source = AUDIO_DIR / "diwali_bgm.mp3"
master_audio = OUT_DIR / "master_audio.wav"
cmd_audio = [
    FFMPEG, "-y",
    "-i", str(voice_stitched),
    "-i", str(bgm_source),
    "-filter_complex",
    f"[0:a]volume=1.35[v];[1:a]volume=0.22,afade=t=in:ss=0:d=1.0,afade=t=out:st={TOTAL_DUR-1.5}:d=1.5[b];[v][b]amix=inputs=2:duration=first[a]",
    "-map", "[a]",
    "-t", str(TOTAL_DUR),
    str(master_audio)
]
subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"🎵 Master Audio Mixed: {master_audio} ({TOTAL_DUR}s)")

# 3. Generate ASS Subtitles (Bilingual Hindi + English)
ass_lines = [
    "[Script Info]",
    "Title: The Legend of the First Diya",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 720",
    "PlayResY: 1280",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: Default,Noto Sans Devanagari,38,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0.5,0,1,3.5,2,2,40,40,240,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    f"Dialogue: 0,{sec_to_ass(0.20)},{sec_to_ass(5.20)},Default,,0,0,0,,{{\\c&H0000D7FF&}}कार्तिक की सबसे घनेरी अमावस...{{\\c&H00FFFFFF&}}\\Nजब अयोध्या में घोर अंधेरा छाया था।\\N{{\\fs26\\c&H00E0E0E0&}}On the darkest night, deep darkness covered ancient Ayodhya.",
    f"Dialogue: 0,{sec_to_ass(5.30)},{sec_to_ass(10.80)},Default,,0,0,0,,{{\\c&H00FFFFFF&}}एक बालक ने हवा के बीच,\\N{{\\c&H0000D7FF&}}पहला मिट्टी का दीया जलाया।{{\\c&H00FFFFFF&}}\\N{{\\fs26\\c&H00E0E0E0&}}A lone child cupped his hands, and lit the first lamp.",
    f"Dialogue: 0,{sec_to_ass(10.90)},{sec_to_ass(16.45)},Default,,0,0,0,,उस एक लौ से {{\\c&H0000D7FF&}}लाखों दीये जाग उठे...{{\\c&H00FFFFFF&}}\\Nमर्यादा पुरुषोत्तम प्रभु राम का स्वागत हुआ!\\N{{\\fs26\\c&H00E0E0E0&}}From that spark, a million golden lamps welcomed Lord Rama.",
    f"Dialogue: 0,{sec_to_ass(16.55)},{sec_to_ass(TOTAL_DUR-0.20)},Default,,0,0,0,,{{\\c&H0033FF33&}}कोई भी अंधेरा इस रोशनी को नहीं बुझा सकता।{{\\c&H00FFFFFF&}}\\N{{\\c&H0000D7FF&}}✨ शुभ दीपावली! 🪔{{\\c&H00FFFFFF&}}\\N{{\\fs26\\c&H00E0E0E0&}}No darkness can extinguish your light. Happy Diwali! ✨"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitles Generated: {ass_file}")

# 4. Render 4 Shots with Dynamic Camera Motion
# Shot 0: 5.25s
# Shot 1: 5.60s
# Shot 2: 5.65s
# Shot 3: remaining (TOTAL_DUR - 16.50s)
shot_durs = [5.25, 5.60, 5.65, round(TOTAL_DUR - 16.50, 2)]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)
    
    if i == 0:
        # Scene 1: Dark Ayodhya - slow cinematic push-in towards the balcony
        z_expr = "'min(zoom+0.0008,1.15)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih/2-(ih/zoom/2)'"
    elif i == 1:
        # Scene 2: The Sacred Diya Flame - intimate focus on the glowing wick
        z_expr = "'min(zoom+0.0010,1.18)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.55-(ih/zoom/2)'"
    elif i == 2:
        # Scene 3: The Ocean of Lights - gentle pan across the Sarayu ghats
        z_expr = "'1.10'"
        x_expr = f"'min(iw*0.05 + (on/{frames})*iw*0.08, iw-iw/zoom)'"
        y_expr = "'ih*0.45-(ih/zoom/2)'"
    else:
        # Scene 4: Fireworks & Sky Lanterns - upward pan following rising lanterns
        z_expr = "'1.10'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = f"'max(0, ih*0.35 - (on/{frames})*ih*0.35)'"

    cmd_shot = [
        FFMPEG, "-y", "-loop", "1", "-i", str(img_p),
        "-vf", f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,zoompan=z={z_expr}:x={x_expr}:y={y_expr}:d={frames}:s=720x1280:fps=30",
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(shot_mp4)
    ]
    subprocess.run(cmd_shot, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp_shots.append(shot_mp4)
    print(f"🎬 Rendered Shot {i+1}/4 ({dur}s)")

# Concat video shots
shots_concat = OUT_DIR / "shots_concat.txt"
with open(shots_concat, "w") as f:
    for sp in tmp_shots:
        f.write(f"file '{sp.resolve()}'\n")

raw_video = OUT_DIR / "raw_video.mp4"
subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(shots_concat), "-c", "copy", str(raw_video)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 5. Final Mux with Master Audio & Subtitles
final_film = OUT_DIR / "film_diwali.mp4"
cmd_final = [
    FFMPEG, "-y",
    "-i", str(raw_video),
    "-i", str(master_audio),
    "-vf", f"ass={ass_file}",
    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    str(final_film)
]
subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 6. Extract Cover Thumbnail (Scene 3 - the illuminated golden ghats of Ayodhya)
cover_img = OUT_DIR / "cover.jpg"
# Extract at ~13.5s which is right in the middle of Scene 3
subprocess.run([FFMPEG, "-y", "-ss", "00:00:13.500", "-i", str(final_film), "-vframes", "1", "-q:v", "2", str(cover_img)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cleanup temp files
for sp in tmp_shots:
    if sp.exists(): sp.unlink()
if raw_video.exists(): raw_video.unlink()
if shots_concat.exists(): shots_concat.unlink()

print(f"🎉 RENDER COMPLETE: {final_film}")
print(f"🖼️ COVER EXTRACTED: {cover_img}")
