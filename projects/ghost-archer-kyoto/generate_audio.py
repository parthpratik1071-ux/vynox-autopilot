#!/usr/bin/env python3
import os
import json
import base64
import time
import subprocess
import urllib.request
from pathlib import Path

KEY = "AQ.Ab8RN6LPzD2gior2MckDAq_cDi06-rku9CU8O4uM7iRVp2gd8A"
MODEL = "gemini-2.5-flash-preview-tts"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/ghost-archer-kyoto")
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

CUES = [
    {"id": "cue_0", "text": "Kyoto, 1603. Five hundred enemy siege warriors stormed the castle gate under a moonless sky."},
    {"id": "cue_1", "text": "Only one defender guarded the pagoda roof: the legendary Ghost Archer, who could hear an arrow in the dark."},
    {"id": "cue_2", "text": "In silence, whistling black arrows struck through armor before the enemy could draw their swords."},
    {"id": "cue_3", "text": "One bow. One soul. Would you hold the castle gate alone? Comment below."}
]

def synthesize_cue(text, out_wav):
    body = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {"voiceName": "Puck"}
                }
            }
        }
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        audio_b64 = res["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        raw_pcm = base64.b64decode(audio_b64)
        
        tmp_pcm = out_wav.with_suffix(".pcm")
        tmp_pcm.write_bytes(raw_pcm)
        subprocess.run([
            FFMPEG, "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
            "-i", str(tmp_pcm),
            "-ar", "44100", str(out_wav)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tmp_pcm.unlink(missing_ok=True)

durations = []
print("🎙️ Synthesizing Ghost Archer with Puck...")
for i, cue in enumerate(CUES):
    out_w = AUDIO_DIR / f"part_{i}.wav"
    preview = (cue["text"][:40] + '...') if len(cue["text"]) > 40 else cue["text"]
    print(f"[{i+1}/{len(CUES)}] Synthesizing: {preview}")
    synthesize_cue(cue["text"], out_w)
    
    probe = subprocess.run([
        FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(out_w)
    ], capture_output=True, text=True, check=True)
    durations.append(float(probe.stdout.strip()))
    time.sleep(2.0)

with open(PROJECT_DIR / "durations.json", "w") as f:
    json.dump({"cues": CUES, "durations": durations}, f, indent=2)

print("\nDuration summary:")
for i, d in enumerate(durations):
    print(f"Part {i}: {d:.2f}s")
print("✅ Speech synthesis complete!")
