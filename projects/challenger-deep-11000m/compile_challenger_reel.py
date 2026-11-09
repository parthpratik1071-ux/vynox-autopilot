#!/usr/bin/env python3
"""
High-Fidelity 1080x1920 Vertical Full HD Reel Compiler
Project: Challenger Deep (Mariana Trench 11,000M)
"""
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/challenger-deep-11000m")
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
print(f"🎙️ High-Fidelity Voice Track: {TOTAL_DUR:.2f}s (Within 20-30s sweet spot)")
assert 20.0 <= TOTAL_DUR <= 30.0, f"Duration {TOTAL_DUR}s out of range!"

# 2. Synthesize Cinematic SFX Layers
# SFX 1: Deep Submarine Bass Boom (t=0.0)
sfx_boom = OUT_DIR / "sfx_boom.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=50:duration=1.8",
    "-af", "afade=t=out:st=0.3:d=1.5,volume=0.45",
    str(sfx_boom)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# SFX 2: Sonar Ping (t=6.7)
sfx_sonar = OUT_DIR / "sfx_sonar.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=880:duration=0.8",
    "-af", "afade=t=out:st=0.05:d=0.75,volume=0.20",
    str(sfx_sonar)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# SFX 3: Hydrothermal Hiss (t=14.0)
sfx_hiss = OUT_DIR / "sfx_hiss.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "anoisesrc=d=2.0:c=white:r=44100:a=0.06",
    "-af", "bandpass=f=2200:w=600,afade=t=in:ss=0:d=0.3,afade=t=out:st=1.2:d=0.8,volume=0.30",
    str(sfx_hiss)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Master Audio Mix: Voice (1.35x) + BGM (0.22x) + Timed SFX
bgm_source = AUDIO_DIR / "trench_bgm.mp3"
master_audio = OUT_DIR / "master_audio.wav"

cmd_audio = [
    FFMPEG, "-y",
    "-i", str(voice_stitched),    # [0] voice
    "-i", str(bgm_source),        # [1] bgm
    "-i", str(sfx_boom),          # [2] boom
    "-i", str(sfx_sonar),         # [3] sonar
    "-i", str(sfx_hiss),          # [4] hiss
    "-filter_complex",
    f"[0:a]volume=1.35[v];"
    f"[1:a]volume=0.22,afade=t=in:ss=0:d=1.0,afade=t=out:st={TOTAL_DUR-1.5}:d=1.5[b];"
    f"[2:a]adelay=100|100[sfx1];"
    f"[3:a]adelay=6700|6700[sfx2];"
    f"[4:a]adelay=14000|14000[sfx3];"
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
    "Title: The Mariana Trench at 11000M: Challenger Deep",
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
    f"Dialogue: 0,{sec_to_ass(0.30)},{sec_to_ass(6.60)},Default,,0,0,0,,{{\\c&H0000D7FF&}}चाँद पर बारह लोग गए...{{\\c&H00FFFFFF&}}\\Nलेकिन मारियाना ट्रेंच की अतल गहराई में सिर्फ कुछ लोग!\\N{{\\fs34\\c&H00E0E0E0&}}12 walked on Moon, but only a few reached Mariana Trench!",
    f"Dialogue: 0,{sec_to_ass(6.75)},{sec_to_ass(13.90)},Default,,0,0,0,,11,000 मीटर नीचे, दबाव इतना है...\\Nजैसे सिर पर {{\\c&H003333FF&}}पचास बोइंग विमान{{\\c&H00FFFFFF&}} खड़े हों!\\N{{\\fs34\\c&H00E0E0E0&}}At 11,000m, pressure is like 50 Boeing jets on your skull!",
    f"Dialogue: 0,{sec_to_ass(14.05)},{sec_to_ass(19.60)},Default,,0,0,0,,पर इस स्याह अंधेरे में भी...\\Nखौलते वेंट्स के पास {{\\c&H0000D7FF&}}जीवन की अनोखी दुनिया{{\\c&H00FFFFFF&}} मिली!\\N{{\\fs34\\c&H00E0E0E0&}}Yet in pitch darkness, an alien world thrives near boiling vents!",
    f"Dialogue: 0,{sec_to_ass(19.75)},{sec_to_ass(TOTAL_DUR-0.20)},Default,,0,0,0,,असली रहस्य अंतरिक्ष में नहीं, महासागर में है।\\N{{\\c&H0033FF33&}}🌊 क्या आप यहाँ उतरेंगे? 👇{{\\c&H00FFFFFF&}}\\N{{\\fs34\\c&H00E0E0E0&}}Earth's deepest mystery. Would you dare dive here?"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 1080p Subtitles Generated: {ass_file}")

# 4. Render 4 Shots in Native 1080x1920 Full HD with Smooth Pan & Zoom
# Timing breakdown:
# Shot 0: 6.70s
# Shot 1: 7.33s
# Shot 2: 5.67s
# Shot 3: 6.94s
shot_durs = [6.70, 7.33, 5.67, round(TOTAL_DUR - (6.70 + 7.33 + 5.67), 2)]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)

    if i == 0:
        # Scene 1: Submersible descending into abyss - slow cinematic push
        z_expr = "'min(zoom+0.0007,1.14)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.5-(ih/zoom/2)'"
    elif i == 1:
        # Scene 2: Cockpit red alert pressure HUD - intense push in on the gauges
        z_expr = "'min(zoom+0.0011,1.22)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.52-(ih/zoom/2)'"
    elif i == 2:
        # Scene 3: Hydrothermal vents & robotic claw discovery - gentle pan across floor
        z_expr = "'min(zoom+0.0008,1.15)'"
        x_expr = f"'max(0, iw*0.35 - (on/{frames})*iw*0.16)'"
        y_expr = "'ih*0.55-(ih/zoom/2)'"
    else:
        # Scene 4: Grand colossal scale - slow majestic pull back
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
final_film = OUT_DIR / "film_challenger_deep.mp4"
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

# 6. Extract Crisp 1080p Cover Thumbnail (Scene 3 - The alien seabed discovery)
cover_img = OUT_DIR / "cover.jpg"
subprocess.run([
    FFMPEG, "-y", "-ss", "00:00:16.000",
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
