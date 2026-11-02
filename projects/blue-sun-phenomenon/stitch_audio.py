#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/blue-sun-phenomenon")
AUDIO_DIR = PROJECT_DIR / "audio_puck"
TMP_DIR = PROJECT_DIR / "tmp_stitch"
TMP_DIR.mkdir(parents=True, exist_ok=True)

with open(PROJECT_DIR / "durations.json") as f:
    data = json.load(f)

cues = data["cues"]
durs = data["durations"]

# Generate silence files
subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", str(TMP_DIR / "silence_init.wav")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.35", str(TMP_DIR / "silence_gap.wav")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.8", str(TMP_DIR / "silence_tail.wav")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

concat_lines = [f"file '{TMP_DIR / 'silence_init.wav'}'"]
timings = []
current_time = 0.5

for i, (cue, dur) in enumerate(zip(cues, durs)):
    wav_path = AUDIO_DIR / f"part_{i}.wav"
    concat_lines.append(f"file '{wav_path}'")
    timings.append({
        "id": cue["id"],
        "text": cue["text"],
        "start": round(current_time, 2),
        "end": round(current_time + dur, 2),
        "duration": round(dur, 2)
    })
    current_time += dur
    if i < len(cues) - 1:
        concat_lines.append(f"file '{TMP_DIR / 'silence_gap.wav'}'")
        current_time += 0.35

concat_lines.append(f"file '{TMP_DIR / 'silence_tail.wav'}'")
current_time += 0.8
total_duration = round(current_time, 2)

concat_file = TMP_DIR / "concat.txt"
with open(concat_file, "w") as f:
    f.write("\n".join(concat_lines))

voice_wav = PROJECT_DIR / "voice_stitched.wav"
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "pcm_s16le", str(voice_wav)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Generate sub-bass dark ambient tension background track
bg_wav = PROJECT_DIR / "audio_bg.wav"
cmd_bg = [
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"sine=frequency=55:duration={total_duration + 2}",
    "-f", "lavfi", "-i", f"sine=frequency=110:duration={total_duration + 2}",
    "-f", "lavfi", "-i", f"anoisesrc=d={total_duration + 2}:c=brown:r=44100:a=0.04",
    "-filter_complex", "[0:a]volume=0.25[sub];[1:a]volume=0.08[mid];[2:a]lowpass=f=220,volume=0.15[air];[sub][mid][air]amix=inputs=3:duration=first,lowpass=f=280,volume=0.4[bg]",
    "-map", "[bg]", str(bg_wav)
]
subprocess.run(cmd_bg, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Mix voice + tension music
final_audio = PROJECT_DIR / "assets" / "master_audio.wav"
cmd_mix = [
    "ffmpeg", "-y",
    "-i", str(voice_wav),
    "-i", str(bg_wav),
    "-filter_complex", "[0:a]volume=1.0[voice];[1:a]volume=0.3[bg];[voice][bg]amix=inputs=2:duration=first[outa]",
    "-map", "[outa]", str(final_audio)
]
subprocess.run(cmd_mix, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

with open(PROJECT_DIR / "timings.json", "w") as f:
    json.dump({"total_duration": total_duration, "timings": timings}, f, indent=2)

print(f"✅ Master audio created! Total duration: {total_duration}s")
