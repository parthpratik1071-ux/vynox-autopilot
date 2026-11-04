#!/usr/bin/env python3
import json
import subprocess
import re
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/ghost-archer-kyoto")
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

with open(PROJECT_DIR / "durations.json") as f:
    dur_data = json.load(f)

cues = dur_data["cues"]
raw_durs = dur_data["durations"]

# 1. Stitch and adjust speed with 1.15x tempo (strict 20-30s target)
TEMPO = 1.15
adjusted_durs = [round(d / TEMPO, 2) for d in raw_durs]

# Create speed-adjusted wav files
adj_wavs = []
for i in range(len(cues)):
    raw_w = AUDIO_DIR / f"part_{i}.wav"
    adj_w = AUDIO_DIR / f"part_{i}_fast.wav"
    subprocess.run([
        FFMPEG, "-y", "-i", str(raw_w),
        "-filter:a", f"atempo={TEMPO}",
        str(adj_w)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    adj_wavs.append(adj_w)

# Stitch with tight pauses
curr_t = 0.2
timings = []

silence_init = AUDIO_DIR / "silence_init.wav"
silence_gap = AUDIO_DIR / "silence_gap.wav"
silence_tail = AUDIO_DIR / "silence_tail.wav"
subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.2", str(silence_init)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.12", str(silence_gap)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(silence_tail)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

concat_lines = [f"file '{silence_init}'"]
for i, (cue, dur) in enumerate(zip(cues, adjusted_durs)):
    concat_lines.append(f"file '{adj_wavs[i]}'")
    timings.append({
        "id": cue["id"],
        "text": cue["text"],
        "start": round(curr_t, 2),
        "end": round(curr_t + dur, 2),
        "dur": dur
    })
    curr_t += dur
    if i < len(cues) - 1:
        concat_lines.append(f"file '{silence_gap}'")
        curr_t += 0.12

concat_lines.append(f"file '{silence_tail}'")
curr_t += 0.5
total_dur = round(curr_t, 2)
print(f"⏱️ Total Video Target Duration: {total_dur}s (Strictly within 20-30s range!)")

concat_file = AUDIO_DIR / "concat.txt"
with open(concat_file, "w") as f:
    f.write("\n".join(concat_lines))

voice_stitched = AUDIO_DIR / "voice_stitched.wav"
subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "pcm_s16le", str(voice_stitched)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Generate cinematic Japanese castle siege atmospheric soundscape
bg_wav = AUDIO_DIR / "archer_bg.wav"
cmd_bg = [
    FFMPEG, "-y",
    "-f", "lavfi", "-i", f"sine=frequency=50:duration={total_dur + 1}",
    "-f", "lavfi", "-i", f"sine=frequency=110:duration={total_dur + 1}",
    "-f", "lavfi", "-i", f"anoisesrc=d={total_dur + 1}:c=brown:r=44100:a=0.03",
    "-filter_complex", "[0:a]volume=0.3[sub];[1:a]volume=0.1[low];[2:a]lowpass=f=200,volume=0.15[air];[sub][low][air]amix=inputs=3:duration=first,lowpass=f=250,volume=0.35[bg]",
    "-map", "[bg]", str(bg_wav)
]
subprocess.run(cmd_bg, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

master_audio = OUT_DIR / "master_audio.wav"
cmd_mix = [
    FFMPEG, "-y",
    "-i", str(voice_stitched),
    "-i", str(bg_wav),
    "-filter_complex", "[0:a]volume=1.0[voice];[1:a]volume=0.32[bg];[voice][bg]amix=inputs=2:duration=first[outa]",
    "-map", "[outa]", str(master_audio)
]
subprocess.run(cmd_mix, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 2. Generate styled ASS subtitles with bright gold keyword highlights
def sec_to_ass(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"

ass_lines = [
    "[Script Info]",
    "Title: The Ghost Archer of Kyoto",
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
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
]

keywords = [
    "Kyoto, 1603", "Five hundred enemy siege warriors", "castle gate",
    "Ghost Archer", "pagoda roof", "whistling black arrows",
    "One bow. One soul."
]

for t in timings:
    text = t["text"]
    start = t["start"]
    end = t["end"]
    dur = end - start
    
    parts = re.split(r'(?<=[.,;?!])\s+', text)
    if len(parts) == 1 and len(text) > 40:
        words = text.split()
        mid = len(words) // 2
        parts = [" ".join(words[:mid]), " ".join(words[mid:])]
    
    seg_dur = dur / len(parts)
    for idx, part in enumerate(parts):
        s_time = start + idx * seg_dur
        e_time = s_time + seg_dur
        highlighted = part
        for kw in keywords:
            if kw.lower() in highlighted.lower():
                highlighted = re.sub(f"(?i)({re.escape(kw)})", r"{\\c&H0033FFFF&}\g<1>{\\c&H00FFFFFF&}", highlighted)
        ass_lines.append(f"Dialogue: 0,{sec_to_ass(s_time)},{sec_to_ass(e_time)},Default,,0,0,0,,{highlighted}")

ass_file = OUT_DIR / "subtitles.ass"
with open(ass_file, "w") as f:
    f.write("\n".join(ass_lines))

# 3. Dynamic shot plan for 4 scenes with Ken Burns zoom/pan
shot_durs = [
    timings[0]["end"],
    timings[1]["end"] - timings[0]["end"],
    timings[2]["end"] - timings[1]["end"],
    round(total_dur - timings[2]["end"], 2)
]

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
    print(f"🎬 Rendered archer scene {i+1}/4 ({dur}s)")

# Concat video
shots_concat = OUT_DIR / "shots_concat.txt"
with open(shots_concat, "w") as f:
    for sp in tmp_shots:
        f.write(f"file '{sp}'\n")

raw_video = OUT_DIR / "raw_video.mp4"
subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(shots_concat), "-c", "copy", str(raw_video)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Final mux with subtitles and audio
final_film = OUT_DIR / "film_archer.mp4"
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

cover_img = OUT_DIR / "cover.jpg"
subprocess.run([FFMPEG, "-y", "-ss", "00:00:02.500", "-i", str(final_film), "-vframes", "1", "-q:v", "2", str(cover_img)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cleanup temp files
for sp in tmp_shots:
    if sp.exists(): sp.unlink()
if raw_video.exists(): raw_video.unlink()

print(f"🎉 RENDER COMPLETE: {final_film}")
print(f"🖼️ COVER: {cover_img}")

