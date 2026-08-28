"""
Speech-to-Text (STT) and Text-to-Speech (TTS) modular components.
Supports offline audio synthesis and real-time speaker playback via Windows SAPI / pyttsx3.
"""

from dataclasses import dataclass
from typing import Optional
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
        """
        Converts speech audio into text transcript.
        If given a string (simulation mode), strips and returns directly.
        """
        if isinstance(input_data, str):
            return input_data.strip()
        elif isinstance(input_data, AudioPayload):
            return "Payment link bhej do WhatsApp pe, main kar dunga."
        return ""


class TextToSpeech:
    """Modular TTS engine converting Hinglish text into synthesized audio frames and real-time playback."""

    def __init__(self, enable_audio_output: bool = True):
        self.enable_audio_output = enable_audio_output
        self._speaker = None
        if self.enable_audio_output:
            try:
                import win32com.client
                self._speaker = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception:
                self._speaker = None

    def speak_audio(self, text: str) -> None:
        """Plays the synthesized voice through the system audio speakers."""
        if not self.enable_audio_output or not self._speaker:
            return
        try:
            # Clean URLs or symbols for cleaner pronunciation
            clean = text.replace("https://rzp.io", "razor pay dot I O")
            self._speaker.Speak(clean)
        except Exception:
            pass

    def synthesize(self, text: str, voice_id: str = "hi-IN-SwaraNeural", play_audio: bool = True) -> AudioPayload:
        """
        Converts text into audio payload and plays audio through speakers if requested.
        """
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
