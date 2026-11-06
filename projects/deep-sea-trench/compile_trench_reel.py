#!/usr/bin/env python3
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/deep-sea-trench")
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

# 1. Re-encode all fast cues to 44.1kHz mono to prevent concat corruption
cues_44k = []
for i in range(4):
    inp = AUDIO_DIR / f"cue_{i}.mp3"
    out = AUDIO_DIR / f"cue_{i}_44k.wav"
    subprocess.run([
        FFMPEG, "-y", "-i", str(inp),
        "-filter:a", "atempo=1.15",
        "-ar", "44100", "-ac", "1",
        str(out)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cues_44k.append(out)

silence_init = AUDIO_DIR / "silence_init.wav"
silence_gap = AUDIO_DIR / "silence_gap.wav"
silence_tail = AUDIO_DIR / "silence_tail.wav"
subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.20", str(silence_init)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.15", str(silence_gap)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.60", str(silence_tail)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

concat_list = AUDIO_DIR / "voice_concat.txt"
with open(concat_list, "w") as f:
    f.write(f"file '{silence_init.resolve()}'\n")
    f.write(f"file '{cues_44k[0].resolve()}'\n")
    f.write(f"file '{silence_gap.resolve()}'\n")
    f.write(f"file '{cues_44k[1].resolve()}'\n")
    f.write(f"file '{silence_gap.resolve()}'\n")
    f.write(f"file '{cues_44k[2].resolve()}'\n")
    f.write(f"file '{silence_gap.resolve()}'\n")
    f.write(f"file '{cues_44k[3].resolve()}'\n")
    f.write(f"file '{silence_tail.resolve()}'\n")

voice_stitched = AUDIO_DIR / "voice_stitched.wav"
subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(voice_stitched)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Measure exact voice duration
res = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(voice_stitched)], capture_output=True, text=True)
TOTAL_DUR = round(float(res.stdout.strip()), 2)
print(f"🎙️ Master Voice Duration: {TOTAL_DUR:.2f}s")

# 2. Mix with ambient BGM
bgm_source = Path("/home/pratik/stickman-video-director/projects/future-message-reel/assets/bgm.mp3")
master_audio = OUT_DIR / "master_audio.wav"
cmd_audio = [
    FFMPEG, "-y",
    "-i", str(voice_stitched),
    "-i", str(bgm_source),
    "-filter_complex",
    f"[0:a]volume=1.35[v];[1:a]volume=0.22,afade=t=in:ss=0:d=1.0,afade=t=out:st={TOTAL_DUR-1.2}:d=1.2[b];[v][b]amix=inputs=2:duration=first[a]",
    "-map", "[a]",
    "-t", str(TOTAL_DUR),
    str(master_audio)
]
subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"🎵 Master Audio Rendered ({TOTAL_DUR:.2f}s)")

# 3. Generate ASS Subtitles
ass_lines = [
    "[Script Info]",
    "Title: The 3-Second Trench Rule",
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
    f"Dialogue: 0,{sec_to_ass(0.20)},{sec_to_ass(3.40)},Default,,0,0,0,,{{\\c&H0033FFFF&}}At 8,000 meters deep{{\\c&H00FFFFFF&}}, the sub hull cracked.",
    f"Dialogue: 0,{sec_to_ass(3.40)},{sec_to_ass(6.44)},Default,,0,0,0,,{{\\c&H000033FF&}}Rule one:{{\\c&H00FFFFFF&}} you have {{\\c&H0033FFFF&}}three seconds{{\\c&H00FFFFFF&}} to eject.",
    f"Dialogue: 0,{sec_to_ass(6.59)},{sec_to_ass(9.10)},Default,,0,0,0,,His hand reached the emergency switch.",
    f"Dialogue: 0,{sec_to_ass(9.10)},{sec_to_ass(11.96)},Default,,0,0,0,,In cargo sat the {{\\c&H00FFFF33&}}only cure{{\\c&H00FFFFFF&}} for his sick daughter.",
    f"Dialogue: 0,{sec_to_ass(12.11)},{sec_to_ass(14.80)},Default,,0,0,0,,He could not save both.",
    f"Dialogue: 0,{sec_to_ass(14.80)},{sec_to_ass(17.98)},Default,,0,0,0,,Touching her drawing on the dial, he locked the {{\\c&H00FFFF33&}}cure into the pod{{\\c&H00FFFFFF&}} instead.",
    f"Dialogue: 0,{sec_to_ass(18.13)},{sec_to_ass(21.80)},Default,,0,0,0,,His last radio whisper: {{\\c&H0033FFFF&}}'Tell her, daddy kept his promise.'{{\\c&H00FFFFFF&}}",
    f"Dialogue: 0,{sec_to_ass(21.80)},{sec_to_ass(TOTAL_DUR)},Default,,0,0,0,,{{\\c&H0033FF33&}}Could you make this sacrifice?{{\\c&H00FFFFFF&}} 👇"
]

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w") as f:
    f.write("\n".join(ass_lines))
print(f"📝 Subtitles Generated: {ass_file}")

# 4. Render 4 Shots with Dynamic Camera Motion
# Shot 0: 6.52s
# Shot 1: 5.51s
# Shot 2: 6.02s
# Shot 3: remaining (TOTAL_DUR - 18.05s)
shot_durs = [6.52, 5.51, 6.02, round(TOTAL_DUR - 18.05, 2)]
tmp_shots = []

for i, dur in enumerate(shot_durs):
    img_p = ASSETS_DIR / f"scene-{i+1}.jpg"
    shot_mp4 = OUT_DIR / f"shot_{i}.mp4"
    frames = int(dur * 30)
    if i == 0:
        z_expr = "'min(zoom+0.0012,1.20)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih/2-(ih/zoom/2)'"
    elif i == 1:
        z_expr = "'min(zoom+0.0015,1.25)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.6-(ih/zoom/2)'"
    elif i == 2:
        z_expr = "'max(1.22-0.0012*on,1.0)'"
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih*0.4-(ih/zoom/2)'"
    else:
        # Scene 4: dramatic vertical pan upward following the rising pod
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
final_film = OUT_DIR / "film_trench.mp4"
cmd_final = [
    FFMPEG, "-y",
    "-i", str(raw_video),
    "-i", str(master_audio),
    "-vf", f"ass={ass_file}",
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    str(final_film)
]
subprocess.run(cmd_final, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 6. Extract Cover Thumbnail (Scene 3 - the drawing & sacrifice)
cover_img = OUT_DIR / "cover.jpg"
subprocess.run([FFMPEG, "-y", "-ss", "00:00:15.000", "-i", str(final_film), "-vframes", "1", "-q:v", "2", str(cover_img)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cleanup temp files
for sp in tmp_shots:
    if sp.exists(): sp.unlink()
if raw_video.exists(): raw_video.unlink()

print(f"🎉 RENDER COMPLETE: {final_film}")
print(f"🖼️ COVER EXTRACTED: {cover_img}")
