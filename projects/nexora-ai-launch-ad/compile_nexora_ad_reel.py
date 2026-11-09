#!/usr/bin/env python3
"""
High-Fidelity 1080x1920 Commercial Product Advertisement Reel Compiler
Product: NexoraAI V14.2 (Sovereign Local AI & Cloud Licensing Platform)
"""
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/nexora-ai-launch-ad")
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
print(f"🎙️ High-Energy Voice Track: {TOTAL_DUR:.2f}s (Within 20-30s range)")
assert 20.0 <= TOTAL_DUR <= 30.0, f"Duration {TOTAL_DUR}s out of range!"

# 2. Synthesize High-Tech Cyber SFX Layers
# SFX 1: Red Alert Glitch Bass Drop (t=0.2)
sfx_drop = OUT_DIR / "sfx_drop.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=65:duration=1.5",
    "-af", "afade=t=out:st=0.2:d=1.3,volume=0.45",
    str(sfx_drop)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# SFX 2: Cybernetic Bootup & Neural Surge (t=7.2)
sfx_surge = OUT_DIR / "sfx_surge.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=950:duration=1.2",
    "-af", "afade=t=in:ss=0:d=0.2,afade=t=out:st=0.6:d=0.6,volume=0.22",
    str(sfx_surge)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# SFX 3: Cloud Verification Chime (t=14.9)
sfx_chime = OUT_DIR / "sfx_chime.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "lavfi",
    "-i", "sine=frequency=1320:duration=0.8",
    "-af", "afade=t=out:st=0.08:d=0.72,volume=0.25",
    str(sfx_chime)
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Master Audio Mix: Voice (1.35x) + Synth BGM (0.22x) + Timed SFX
bgm_source = AUDIO_DIR / "tech_bgm.mp3"
master_audio = OUT_DIR / "master_audio.wav"

cmd_audio = [
    FFMPEG, "-y",
    "-i", str(voice_stitched),    # [0] voice
    "-i", str(bgm_source),        # [1] bgm
    "-i", str(sfx_drop),          # [2] drop
    "-i", str(sfx_surge),         # [3] surge
    "-i", str(sfx_chime),         # [4] chime
    "-filter_complex",
    f"[0:a]volume=1.35[v];"
    f"[1:a]volume=0.22,afade=t=in:ss=0:d=0.8,afade=t=out:st={TOTAL_DUR-1.5}:d=1.5[b];"
    f"[2:a]adelay=200|200[sfx1];"
    f"[3:a]adelay=7200|7200[sfx2];"
    f"[4:a]adelay=14900|14900[sfx3];"
    f"[v][b][sfx1][sfx2][sfx3]amix=inputs=5:duration=first[a]",
    "-map", "[a]",
    "-t", str(TOTAL_DUR),
    str(master_audio)
]
subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"🎵 Studio Commercial Audio Mixed with Procedural SFX ({TOTAL_DUR}s)")

# 3. Generate 1080x1920 ASS Subtitles with Cyberpunk Glowing Typography
ass_lines = [
    "[Script Info]",
    "Title: NexoraAI V14.2 Commercial Launch",
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
    f"Dialogue: 0,{sec_to_ass(0.20)},{sec_to_ass(7.10)},Default,,0,0,0,,AI सब्सक्रिप्शन और डेटा लीक से परेशान हैं?\\N{{\\c&H003333FF&}}क्लाउड कंपनियाँ{{\\c&H00FFFFFF&}} आपका प्राइवेट डेटा देखती हैं!\\N{{\\fs34\\c&H00E0E0E0&}}Tired of costly AI subscriptions and data leak fears?",
    f"Dialogue: 0,{sec_to_ass(7.25)},{sec_to_ass(14.80)},Default,,0,0,0,,मिलिए {{\\c&H00FFFF00&}}NexoraAI V14.2{{\\c&H00FFFFFF&}} से!\\N{{\\c&H0000D7FF&}}100% प्राइवेट AI{{\\c&H00FFFFFF&}} जो बिना इंटरनेट सीधे आपके लैपटॉप पर चलता है!\\N{{\\fs34\\c&H00E0E0E0&}}100% private local AI running on your own CPU!",
    f"Dialogue: 0,{sec_to_ass(14.95)},{sec_to_ass(21.40)},Default,,0,0,0,,{{\\c&H0033FF33&}}जीरो मंथली फीस, जीरो डेटा लीक!{{\\c&H00FFFFFF&}}\\Nक्लाउड लाइसेंसिंग अब {{\\c&H0000D7FF&}}Render पर लाइव तैनात{{\\c&H00FFFFFF&}} है!\\N{{\\fs34\\c&H00E0E0E0&}}Zero subscription. Enterprise licensing live on Render!",
    f"Dialogue: 0,{sec_to_ass(21.55)},{sec_to_ass(TOTAL_DUR-0.20)},Default,,0,0,0,,अपने AI के खुद मालिक बनिए!\\N{{\\c&H00FFFF00&}}🚀 nexora-cloud-licensing.onrender.com 👇{{\\c&H00FFFFFF&}}\\N{{\\fs34\\c&H00E0E0E0&}}Own your AI today. Check link in bio!"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ass_lines))
print(f"📝 1080p Subtitles Generated: {ass_file}")

# 4. Render 4 Shots in Native 1080x1920 Full HD with Smooth Pan & Zoom
# Timing breakdown:
# Shot 0: 7.22s
# Shot 1: 7.73s
# Shot 2: 6.59s
# Shot 3: 6.85s
shot_durs = [7.22, 7.73, 6.59, round(TOTAL_DUR - (7.22 + 7.73 + 6.59), 2)]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)

    if i == 0:
        # Scene 1: Cloud trap & data leak - dramatic zoom in on the red alert screens
        z_expr = "'min(zoom+0.0010,1.20)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.52-(ih/zoom/2)'"
    elif i == 1:
        # Scene 2: Nexora local inference breakthrough - vibrant push into glowing cyan brain
        z_expr = "'min(zoom+0.0012,1.22)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.50-(ih/zoom/2)'"
    elif i == 2:
        # Scene 3: Enterprise cloud licensing display - pan across healthy architecture
        z_expr = "'min(zoom+0.0007,1.14)'"
        x_expr = f"'max(0, iw*0.35 - (on/{frames})*iw*0.16)'"
        y_expr = "'ih*0.55-(ih/zoom/2)'"
    else:
        # Scene 4: Grand launch podium & CTA - epic pull back revealing logo & link
        z_expr = "'max(1.18 - 0.0008*on, 1.0)'"
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
final_film = OUT_DIR / "film_nexora_ad.mp4"
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

# 6. Extract Crisp 1080p Cover Thumbnail (Scene 4 - The grand launch podium)
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

