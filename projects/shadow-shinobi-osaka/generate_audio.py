#!/usr/bin/env python3
import asyncio
import json
import subprocess
from pathlib import Path
import edge_tts

PROJECT_DIR = Path("/home/pratik/stickman-video-director/projects/shadow-shinobi-osaka")
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.gemini/antigravity-ide/bin/ffmpeg"
FFPROBE = "/home/pratik/.gemini/antigravity-ide/bin/ffprobe"

VOICE = "en-US-ChristopherNeural"

CUES = [
    {"id": "cue_0", "text": "Osaka Castle, 1598. A thousand imperial guards locked the gates to capture the phantom on the roof."},
    {"id": "cue_1", "text": "The lone shinobi carried the stolen cipher scroll across moonlit tiles without making a single sound."},
    {"id": "cue_2", "text": "Surrounded on the watchtower edge, three smoke bombs shattered the dark before he vanished into thin air."},
    {"id": "cue_3", "text": "Never seen. Never caught. Would you trust a shinobi's oath? Drop your verdict below."}
]

async def synthesize_all():
    durations = []
    print(f"🎙️ Synthesizing Shadow Shinobi with {VOICE}...")
    for i, cue in enumerate(CUES):
        mp3_p = AUDIO_DIR / f"part_{i}.mp3"
        wav_p = AUDIO_DIR / f"part_{i}.wav"
        
        comm = edge_tts.Communicate(cue["text"], VOICE, rate="+5%")
        await comm.save(str(mp3_p))
        
        subprocess.run([
            FFMPEG, "-y", "-i", str(mp3_p),
            "-ar", "44100", str(wav_p)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        mp3_p.unlink(missing_ok=True)
        
        probe = subprocess.run([
            FFPROBE, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(wav_p)
        ], capture_output=True, text=True, check=True)
        dur = float(probe.stdout.strip())
        durations.append(dur)
        print(f"[{i+1}/{len(CUES)}] Generated part_{i}.wav ({dur:.2f}s)")
    
    with open(PROJECT_DIR / "durations.json", "w") as f:
        json.dump({"cues": CUES, "durations": durations}, f, indent=2)
    
    total = sum(durations)
    print(f"\n✅ All 4 audio cues complete! Total: {total:.2f}s")

if __name__ == "__main__":
    asyncio.run(synthesize_all())
