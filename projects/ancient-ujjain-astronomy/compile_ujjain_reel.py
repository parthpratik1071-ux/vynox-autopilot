#!/usr/bin/env python3
"""
High-Fidelity 1080x1920 Vertical Full HD Reel Compiler
Project: The Astronomer of Ancient Ujjain (Ancient Indian Astronomy)
"""
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/ancient-ujjain-astronomy")
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

# 1. Stitched Audio Verification
voice_stitched = AUDIO_DIR / "voice_stitched.wav"
res = subprocess.run([
    FFPROBE, "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", str(voice_stitched)
], capture_output=True, text=True, check=True)
TOTAL_DUR = round(float(res.stdout.strip()), 2)
print(f"🎙️ High-Fidelity Voice Track: {TOTAL_DUR:.2f}s (Within 20-30s range)")
assert 20.0 <= TOTAL_DUR <= 30.0, f"Duration {TOTAL_DUR}s out of range!"

# 2. Synthesize Cinematic SFX Layers
# SFX 1: Deep Ancient Temple Gong / Chime (t=0.2)
sfx_gong = OUT_DIR / "sfx_gong.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=220:duration=2.5",
    "-af", "afade=t=out:st=0.2:d=2.3,volume=0.35",
    str(sfx_gong)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# SFX 2: Cosmic Shimmer Sparkle (t=8.2)
sfx_sparkle = OUT_DIR / "sfx_sparkle.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=1200:duration=1.2",
    "-af", "afade=t=in:ss=0:d=0.2,afade=t=out:st=0.6:d=0.6,volume=0.18",
    str(sfx_sparkle)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# SFX 3: Low Frequency Eclipse Sweep (t=15.5)
sfx_sweep = OUT_DIR / "sfx_sweep.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=75:duration=1.8",
    "-af", "afade=t=out:st=0.3:d=1.5,volume=0.40",
    str(sfx_sweep)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Master Audio Mix: Voice (1.35x) + BGM (0.22x) + Timed SFX
bgm_source = AUDIO_DIR / "ujjain_bgm.mp3"
master_audio = OUT_DIR / "master_audio.wav"

cmd_audio = [
    FFMPEG, "-y",
    "-i", str(voice_stitched),    # [0] voice
    "-i", str(bgm_source),        # [1] bgm
    "-i", str(sfx_gong),          # [2] gong
    "-i", str(sfx_sparkle),       # [3] sparkle
    "-i", str(sfx_sweep),         # [4] sweep
    "-filter_complex",
    f"[0:a]volume=1.35[v];"
    f"[1:a]volume=0.22,afade=t=in:ss=0:d=1.0,afade=t=out:st={TOTAL_DUR-1.5}:d=1.5[b];"
    f"[2:a]adelay=200|200[sfx1];"
    f"[3:a]adelay=8200|8200[sfx2];"
    f"[4:a]adelay=15500|15500[sfx3];"
    f"[v][b][sfx1][sfx2][sfx3]amix=inputs=5:duration=first[a]",
    "-map", "[a]",
    "-t", str(TOTAL_DUR),
    str(master_audio)
]
subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"🎵 Studio Master Audio Mixed with Procedural SFX ({TOTAL_DUR}s)")

# 3. Generate 1080x1920 ASS Subtitles with Glowing Typography
ass_lines = [
    "[Script Info]",
    "Title: The Blind Astronomer of Ancient Ujjain",
    "ScriptType: v4.00+",
    "WrapStyle: 0",
    "PlayResX: 1080",
    "PlayResY: 1920",
    "",
    "[V4+ Styles]",
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    "Style: Default,Noto Sans Devanagari,54,&H00FFFFFF,&H000000FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0.5,0,1,5.0,3.0,2,50,50,340,1",
    "",
    "[Events]",
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    f"Dialogue: 0,{sec_to_ass(0.30)},{sec_to_ass(8.00)},Default,,0,0,0,,{{\\c&H0000D7FF&}}नासा से 1500 साल पहले...{{\\c&H00FFFFFF&}}\\Nउज्जैन में एक ऋषि ने केवल छड़ी और रेत से ग्रहों की चाल नाप दी थी!\\N{{\\fs34\\c&H00E0E0E0&}}1,500 years before NASA, he mapped planetary orbits with sand!",
    f"Dialogue: 0,{sec_to_ass(8.15)},{sec_to_ass(15.05)},Default,,0,0,0,,आर्यभट ने बिना कंप्यूटर के...\\N{{\\c&H0000D7FF&}}पृथ्वी की परिधि{{\\c&H00FFFFFF&}} और ग्रहों की कक्षा की सटीक गणना कर दी थी!\\N{{\\fs34\\c&H00E0E0E0&}}Aryabhata calculated Earth's circumference without any computers!",
    f"Dialogue: 0,{sec_to_ass(15.20)},{sec_to_ass(22.40)},Default,,0,0,0,,जब दुनिया ग्रहण से डरती थी...\\Nतब उन्होंने साबित किया कि {{\\c&H0033FF33&}}ये केवल पृथ्वी की परछाई है!{{\\c&H00FFFFFF&}}\\N{{\\fs34\\c&H00E0E0E0&}}He proved eclipses are merely the Earth's spherical shadow!",
    f"Dialogue: 0,{sec_to_ass(22.55)},{sec_to_ass(TOTAL_DUR-0.20)},Default,,0,0,0,,ये है हमारे भारत का गौरवशाली विज्ञान!\\N{{\\c&H0000D7FF&}}✨ क्या आप इस प्राचीन प्रतिभा को जानते थे? 👇{{\\c&H00FFFFFF&}}\\N{{\\fs34\\c&H00E0E0E0&}}Ancient Indian astronomy. Did you know about this genius?"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 1080p Subtitles Generated: {ass_file}")

# 4. Render 4 Shots in Native 1080x1920 Full HD with Smooth Pan & Zoom
# Timing breakdown:
# Shot 0: 8.08s
# Shot 1: 7.11s
# Shot 2: 7.37s
# Shot 3: 6.41s
shot_durs = [8.08, 7.11, 7.37, round(TOTAL_DUR - (8.08 + 7.11 + 7.37), 2)]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)

    if i == 0:
        # Scene 1: Ancient Ujjain observatory at night - slow pan up into constellations
        z_expr = "'min(zoom+0.0006,1.14)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = f"'max(0, ih*0.60 - (on/{frames})*ih*0.22)'"
    elif i == 1:
        # Scene 2: Drawing planetary orbits in glowing sand - push into golden geometric orbits
        z_expr = "'min(zoom+0.0010,1.20)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.52-(ih/zoom/2)'"
    elif i == 2:
        # Scene 3: Rational geometry of eclipse - gentle pan across teacher and students
        z_expr = "'min(zoom+0.0007,1.14)'"
        x_expr = f"'max(0, iw*0.35 - (on/{frames})*iw*0.15)'"
        y_expr = "'ih*0.55-(ih/zoom/2)'"
    else:
        # Scene 4: Grand elevation on parapet under Milky Way - pull back revealing cosmos
        z_expr = "'max(1.16 - 0.0007*on, 1.0)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.5-(ih/zoom/2)'"

    cmd_shot = [
        FFMPEG, "-y", "-loop", "1", "-i", str(img_p),
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z={z_expr}:x={x_expr}:y={y_expr}:d={frames}:s=1080x1920:fps=30",
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        str(shot_mp4)
    ]
    subprocess.run(cmd_shot, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tmp_shots.append(shot_mp4)
    print(f"🎬 Rendered Shot {i+1}/4 ({dur}s @ 1080x1920)")

# Concat video shots
shots_concat = OUT_DIR / "shots_concat.txt"
with open(shots_concat, "w") as f:
    for sp in tmp_shots:
        f.write(f"file '{sp.resolve()}'\n")

raw_video = OUT_DIR / "raw_video.mp4"
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0",
    "-i", str(shots_concat),
    "-c", "copy",
    str(raw_video)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 5. Final Master Mux with 1080p CRF 17 High Bitrate & Color Matrix
final_film = OUT_DIR / "film_ancient_ujjain.mp4"
cmd_final = [
    FFMPEG, "-y",
    "-i", str(raw_video),
    "-i", str(master_audio),
    "-vf", f"ass={ass_file}",
    "-c:v", "libx264", "-preset", "slow", "-crf", "17",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-c:a", "aac", "-b:a", "256k",
    "-shortest",
    str(final_film)
]
subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 6. Extract Crisp 1080p Cover Thumbnail (Scene 4 - The astronomer under the Milky Way)
cover_img = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y", "-ss", "00:00:24.000",
    "-i", str(final_film),
    "-vframes", "1", "-q:v", "1",
    str(cover_img)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cleanup temp files
for sp in tmp_shots:
    if sp.exists(): sp.unlink()
if raw_video.exists(): raw_video.unlink()
if shots_concat.exists(): shots_concat.unlink()

print(f"🎉 1080p FULL HD RENDER COMPLETE: {final_film}")
print(f"🖼️ HIGH-RES COVER EXTRACTED: {cover_img}")
