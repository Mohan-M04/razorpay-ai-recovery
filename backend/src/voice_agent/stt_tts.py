"""
Speech-to-Text (STT) and Text-to-Speech (TTS) modular components.
Supports offline audio synthesis and non-blocking real-time speaker playback via Windows SAPI.
"""

from dataclasses import dataclass
from typing import Optional
import os
import threading


@dataclass
class AudioPayload:
    audio_bytes: bytes
    sample_rate: int = 16000
    format: str = "wav"
    duration_seconds: float = 2.5


class SpeechToText:
    """Modular STT engine with offline simulation and pluggable API integration."""

    def transcribe(self, input_data: str | AudioPayload) -> str:
        if isinstance(input_data, str):
            return input_data.strip()
        elif isinstance(input_data, AudioPayload):
            return "Payment link bhej do WhatsApp pe, main kar dunga."
        return ""


def _speak_in_background(text: str):
    """Speaks text in a background thread so the terminal never hangs."""
    try:
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        clean = text.replace("https://rzp.io", "razor pay link")
        speaker.Speak(clean)
    except Exception:
        pass
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


class TextToSpeech:
    """Modular TTS engine converting text into synthesized audio frames and real-time playback."""

    def __init__(self, enable_audio_output: bool = True):
        self.enable_audio_output = enable_audio_output

    def speak_audio(self, text: str) -> None:
        """Plays the synthesized voice in background without blocking."""
        if not self.enable_audio_output or "PYTEST_CURRENT_TEST" in os.environ:
            return
        t = threading.Thread(target=_speak_in_background, args=(text,), daemon=True)
        t.start()

    def synthesize(self, text: str, voice_id: str = "hi-IN-SwaraNeural", play_audio: bool = True) -> AudioPayload:
        if play_audio and self.enable_audio_output:
            self.speak_audio(text)

        words = len(text.split())
        estimated_duration = max(1.2, words * 0.35)
        mock_pcm = b"\x00\x00" * int(16000 * estimated_duration)
        return AudioPayload(
            audio_bytes=mock_pcm,
            sample_rate=16000,
            format="wav",
            duration_seconds=estimated_duration,
        )
