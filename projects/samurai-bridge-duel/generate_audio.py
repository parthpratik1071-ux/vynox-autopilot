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

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/samurai-bridge-duel")
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

CUES = [
    {"id": "cue_0", "text": "Midnight in 1616 Edo Japan. A lone blindfolded samurai guarded the Bridge of One Hundred Blades."},
    {"id": "cue_1", "text": "The Shogun offered ten thousand gold coins to any warlord who could cross. Ninety-nine had fallen."},
    {"id": "cue_2", "text": "When the demon executioner stepped forward, the blindfold dropped. In two breaths, lightning struck the water."},
    {"id": "cue_3", "text": "Honor is eternal. Would you dare step onto this bridge? Drop your answer below."}
]

def synthesize_cue(text, out_wav):
    body = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": "Puck"}}}
        }
    }
    req = urllib.request.Request(URL, data=json.dumps(body).encode("utf-8"), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        cand = data.get("candidates", [{}])[0]
        parts = cand.get("content", {}).get("parts", [])
        audio_part = next((p for p in parts if "inlineData" in p and p["inlineData"]["mimeType"].startswith("audio/")), None)
        if not audio_part:
            raise RuntimeError(f"No audio returned for: {text}")
        
        raw_pcm = base64.b64decode(audio_part["inlineData"]["data"])
        pcm_file = out_wav.with_suffix(".pcm")
        with open(pcm_file, "wb") as f:
            f.write(raw_pcm)
        
        cmd = [
            FFMPEG, "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
            "-i", str(pcm_file), "-ar", "44100", str(out_wav)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if pcm_file.exists():
            pcm_file.unlink()

print("🎙️ Synthesizing Samurai Bridge Duel with Puck...")
durations = []
for i, item in enumerate(CUES):
    out_file = AUDIO_DIR / f"part_{i}.wav"
    print(f"[{i+1}/{len(CUES)}] Synthesizing: {item['text'][:40]}...")
    synthesize_cue(item["text"], out_file)
    time.sleep(2.0)
    
    dur_cmd = [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_file)]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    durations.append(dur)

print("\nDuration summary:")
for i, d in enumerate(durations):
    print(f"Part {i}: {d:.2f}s")

with open(PROJECT_DIR / "durations.json", "w") as f:
    json.dump({"cues": CUES, "durations": durations}, f, indent=2)

print("✅ Speech synthesis complete!")

