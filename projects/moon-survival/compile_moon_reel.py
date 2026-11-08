#!/usr/bin/env python3
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/moon-survival")
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

# 1. Stitch Audio Cues
cues = [AUDIO_DIR / f"cue_{i}.mp3" for i in range(4)]
cue_concat_list = OUT_DIR / "cue_concat.txt"
with open(cue_concat_list, "w") as f:
    for c in cues:
        f.write(f"file '{c.resolve()}'\n")

voice_stitched = AUDIO_DIR / "voice_stitched.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0",
    "-i", str(cue_concat_list),
    "-c:a", "pcm_s16le",
    str(voice_stitched)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

res = subprocess.run([
    FFPROBE, "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", str(voice_stitched)
], capture_output=True, text=True, check=True)
TOTAL_DUR = round(float(res.stdout.strip()), 2)
print(f"🎙️ Hindi Voice Duration: {TOTAL_DUR:.2f}s")
assert 20.0 <= TOTAL_DUR <= 30.0, f"Duration {TOTAL_DUR}s must be between 20.0s and 30.0s!"

# Get individual cue durations
cue_durs = []
for c in cues:
    r = subprocess.run([
        FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(c)
    ], capture_output=True, text=True, check=True)
    cue_durs.append(float(r.stdout.strip()))

print("Cue durations:", cue_durs)

# 2. Mix voice with Sci-Fi ambient BGM
bgm_source = AUDIO_DIR / "space_bgm.mp3"
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
t0 = 0.0
t1 = round(cue_durs[0], 2)
t2 = round(t1 + cue_durs[1], 2)
t3 = round(t2 + cue_durs[2], 2)
t4 = TOTAL_DUR

ass_lines = [
    "[Script Info]",
    "Title: Trapped on the Moon: Only 1 Air Cylinder Left",
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
    f"Dialogue: 0,{sec_to_ass(t0 + 0.15)},{sec_to_ass(t1 - 0.10)},Default,,0,0,0,,{{\\c&H0000D7FF&}}चाँद के अंधेरे हिस्से पर...{{\\c&H00FFFFFF&}}\\Nदो अंतरिक्ष यात्री भाई-बहन का रोवर क्रैश हो गया।\\N{{\\fs26\\c&H00E0E0E0&}}On the dark side of the Moon, sibling astronauts crashed.",
    f"Dialogue: 0,{sec_to_ass(t1 + 0.10)},{sec_to_ass(t2 - 0.10)},Default,,0,0,0,,{{\\c&H003333FF&}}अलार्म बज उठा!{{\\c&H00FFFFFF&}}\\Nहवा सिर्फ दस मिनट की बची थी, और {{\\c&H0000D7FF&}}टैंक केवल एक!{{\\c&H00FFFFFF&}}\\N{{\\fs26\\c&H00E0E0E0&}}Alarm blared! Only 10 mins of air left, and just ONE tank!",
    f"Dialogue: 0,{sec_to_ass(t2 + 0.10)},{sec_to_ass(t3 - 0.10)},Default,,0,0,0,,बड़े भाई ने अपनी सांसें रोक लीं...\\Nऔर {{\\c&H0000D7FF&}}बहन के सूट में वो आखिरी टैंक लॉक कर दिया।{{\\c&H00FFFFFF&}}\\N{{\\fs26\\c&H00E0E0E0&}}The elder brother held his breath and locked the tank in her suit.",
    f"Dialogue: 0,{sec_to_ass(t3 + 0.10)},{sec_to_ass(t4 - 0.20)},Default,,0,0,0,,{{\\c&H0033FF33&}}'तू जी ले मेरी बहना...'{{\\c&H00FFFFFF&}}\\Nशून्य में उसका हाथ छूट गया। क्या आप ये कर पाते?\\N{{\\fs26\\c&H00E0E0E0&}}'Live on, sister'... In the void his hand slipped. Could you do this?"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitles Generated: {ass_file}")

# 4. Render 4 Shots with Dynamic Camera Motion
shot_durs = [t1, round(t2 - t1, 2), round(t3 - t2, 2), round(t4 - t3, 2)]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)
    
    if i == 0:
        # Scene 1: Lunar crash site & Earth in deep cosmos - slow cinematic pan
        z_expr = "'min(zoom+0.0007,1.14)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.5-(ih/zoom/2)'"
    elif i == 1:
        # Scene 2: Critical Alarm HUD & Only 1 O2 Tank - dramatic zoom in on the tank
        z_expr = "'min(zoom+0.0010,1.20)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.58-(ih/zoom/2)'"
    elif i == 2:
        # Scene 3: Brother locks last tank - gentle push into the golden bond
        z_expr = "'min(zoom+0.0008,1.15)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.62-(ih/zoom/2)'"
    else:
        # Scene 4: Heroic Salute on Lunar Ridge - pull back as Earth rises
        z_expr = "'max(1.15 - 0.0006*on, 1.0)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.5-(ih/zoom/2)'"

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
final_film = OUT_DIR / "film_moon_survival.mp4"
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

# 6. Extract Cover Thumbnail (Scene 3 - The golden sacrifice)
cover_img = OUT_DIR / "cover.jpg"
cover_time = t2 + 2.0
subprocess.run([FFMPEG, "-y", "-ss", sec_to_ass(cover_time), "-i", str(final_film), "-vframes", "1", "-q:v", "2", str(cover_img)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cleanup temp files
for sp in tmp_shots:
    if sp.exists(): sp.unlink()
if raw_video.exists(): raw_video.unlink()
if shots_concat.exists(): shots_concat.unlink()
if cue_concat_list.exists(): cue_concat_list.unlink()

print(f"🎉 RENDER COMPLETE: {final_film}")
print(f"🖼️ COVER EXTRACTED: {cover_img}")
