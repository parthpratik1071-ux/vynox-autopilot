#!/usr/bin/env python3
"""
NexoraAI Voice Engine
Handles bidirectional voice communication on Instagram:
1. Understands incoming voice notes (Speech-to-Text in Hindi / Hinglish / English)
2. Generates and sends authentic native Instagram voice notes (Text-to-Speech in natural Indian tone)
"""

import os
import sys
import asyncio
import subprocess
import tempfile
import urllib.request
from pathlib import Path

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

try:
    import speech_recognition as sr
    HAS_SR = True
except Exception:
    HAS_SR = False

try:
    import edge_tts
    HAS_EDGE = True
except Exception:
    HAS_EDGE = False

class VoiceEngine:
    def __init__(self):
        self.default_voice = "hi-IN-MadhurNeural"  # Natural young Indian male voice

    def transcribe_audio(self, audio_src_or_path: str) -> str:
        """
        Transcribes incoming audio file or Instagram audio URL to text.
        """
        if not HAS_SR:
            return ""

        temp_input = None
        temp_wav = None

        try:
            # 1. Download if URL
            if audio_src_or_path.startswith("http://") or audio_src_or_path.startswith("https://"):
                fd, temp_input = tempfile.mkstemp(suffix=".m4a")
                os.close(fd)
                urllib.request.urlretrieve(audio_src_or_path, temp_input)
                input_file = temp_input
            else:
                input_file = audio_src_or_path

            # 2. Convert to 16kHz Mono WAV for speech recognition
            fd, temp_wav = tempfile.mkstemp(suffix=".wav")
            os.close(fd)

            cmd = [
                FFMPEG_EXE, "-y", "-i", str(input_file),
                "-ar", "16000", "-ac", "1",
                str(temp_wav)
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # 3. Transcribe with SpeechRecognition
            r = sr.Recognizer()
            with sr.AudioFile(str(temp_wav)) as source:
                audio = r.record(source)

            # Try Hindi first (covers Hindi & Hinglish), then English fallback
            try:
                text = r.recognize_google(audio, language="hi-IN")
                print(f"🎙️ [Voice-Transcription]: \"{text}\"")
                return text
            except Exception:
                try:
                    text = r.recognize_google(audio, language="en-IN")
                    print(f"🎙️ [Voice-Transcription (en-IN)]: \"{text}\"")
                    return text
                except Exception:
                    return ""

        except Exception as e:
            print(f"⚠️ Voice transcription error: {e}")
            return ""
        finally:
            if temp_input and os.path.exists(temp_input):
                os.unlink(temp_input)
            if temp_wav and os.path.exists(temp_wav):
                os.unlink(temp_wav)

    async def _synthesize_edge(self, text: str, mp3_path: str, voice: str):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(mp3_path)

    def generate_voice_note(self, text: str, voice: str = None) -> Path:
        """
        Generates an authentic spoken voice note and formats it as an Instagram native .m4a.
        """
        if not HAS_EDGE:
            print("⚠️ edge_tts not available for voice generation.")
            return None

        chosen_voice = voice or self.default_voice
        fd_mp3, temp_mp3 = tempfile.mkstemp(suffix=".mp3")
        os.close(fd_mp3)

        fd_m4a, temp_m4a = tempfile.mkstemp(suffix=".m4a")
        os.close(fd_m4a)

        try:
            # 1. Synthesize audio via edge_tts
            asyncio.run(self._synthesize_edge(text, temp_mp3, chosen_voice))

            # 2. Transcode to Instagram-compatible AAC 44.1kHz mono in MP4 container
            cmd = [
                FFMPEG_EXE, "-y", "-i", str(temp_mp3),
                "-c:a", "aac", "-b:a", "64k", "-ar", "44100", "-ac", "1",
                str(temp_m4a)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return Path(temp_m4a)

        except Exception as e:
            print(f"⚠️ Voice note generation error: {e}")
            if os.path.exists(temp_m4a):
                os.unlink(temp_m4a)
            return None
        finally:
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)

voice_engine = VoiceEngine()

