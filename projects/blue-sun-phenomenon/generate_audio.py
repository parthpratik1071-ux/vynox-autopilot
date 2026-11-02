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

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/blue-sun-phenomenon")
AUDIO_DIR = PROJECT_DIR / "audio_puck"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

CUES = [
    {"id": "cue_0", "text": "At 12:00 PM tomorrow, the sun will turn neon blue for ten minutes. If you look at it, you will lose your vision forever."},
    {"id": "cue_1", "text": "Scientists call it an extreme ultraviolet flare. It instantly strips the ozone layer, blasting the ground with lethal blue radiation."},
    {"id": "cue_2", "text": "Glass cannot block this wavelength. If you are near a window, you have exactly sixty seconds to cover every opening with foil and heavy blankets."},
    {"id": "cue_3", "text": "Step into the most central, windowless room of your home, and shut off all mirrors. Reflection amplifies the ultraviolet intensity tenfold."},
    {"id": "cue_4", "text": "At minute seven, every street light will shatter, and the sky will hum with a deafening frequency. Do not open the door."},
    {"id": "cue_5", "text": "Then, your phone buzzes with an unreleased NASA satellite alert: The sun never changed."},
    {"id": "cue_6", "text": "A colossal anomaly entered orbit and eclipsed the light. Which is why you must stay silent."},
    {"id": "cue_7", "text": "Timeline secured. Share this to warn someone before twelve o'clock tomorrow."}
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
            "ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
            "-i", str(pcm_file), "-ar", "44100", str(out_wav)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if pcm_file.exists():
            pcm_file.unlink()

print("🎙️ Synthesizing cues with Puck on gemini-2.5-flash-preview-tts...")
durations = []
for i, item in enumerate(CUES):
    out_file = AUDIO_DIR / f"part_{i}.wav"
    if not out_file.exists():
        print(f"[{i+1}/{len(CUES)}] Synthesizing: {item['text'][:40]}...")
        synthesize_cue(item["text"], out_file)
        time.sleep(3.5)
    else:
        print(f"[{i+1}/{len(CUES)}] Cached: {out_file.name}")
    
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_file)]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    durations.append(dur)

print("\nDuration summary:")
for i, d in enumerate(durations):
    print(f"Part {i}: {d:.2f}s")

with open(PROJECT_DIR / "durations.json", "w") as f:
    json.dump({"cues": CUES, "durations": durations}, f, indent=2)

print("✅ Speech synthesis complete!")
