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

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/edo-samurai-story")
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

CUES = [
    {"id": "cue_0", "text": "In 1615 Edo Japan, a masterless samurai was ambushed by fifty shadow assassins in a misty bamboo forest."},
    {"id": "cue_1", "text": "He didn't draw his katana. He closed his eyes and whispered: The blade is drawn only when death is accepted."},
    {"id": "cue_2", "text": "In three seconds of blinding steel, every lantern shattered. When the mist cleared, only one sword remained standing."},
    {"id": "cue_3", "text": "Honor is eternal. Would you survive this duel? Drop your answer below."}
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
            "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
            "-i", str(pcm_file), "-ar", "44100", str(out_wav)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if pcm_file.exists():
            pcm_file.unlink()

print("🎙️ Synthesizing samurai narration with Puck...")
durations = []
for i, item in enumerate(CUES):
    out_file = AUDIO_DIR / f"part_{i}.wav"
    print(f"[{i+1}/{len(CUES)}] Synthesizing: {item['text'][:40]}...")
    synthesize_cue(item["text"], out_file)
    time.sleep(2.5)
    
    dur_cmd = ["/home/pratik/.gemini/antigravity-ide/bin/ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_file)]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    durations.append(dur)

print("\nDuration summary:")
for i, d in enumerate(durations):
    print(f"Part {i}: {d:.2f}s")

with open(PROJECT_DIR / "durations.json", "w") as f:
    json.dump({"cues": CUES, "durations": durations}, f, indent=2)

print("✅ Speech synthesis complete!")
