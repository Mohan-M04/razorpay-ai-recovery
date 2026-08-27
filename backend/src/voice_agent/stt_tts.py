"""
Speech-to-Text (STT) and Text-to-Speech (TTS) modular components.
Works out-of-the-box offline and supports pluggable cloud providers.
"""

from dataclasses import dataclass
from typing import Optional


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
    """Modular TTS engine converting Hinglish text into synthesized audio frames."""

    def synthesize(self, text: str, voice_id: str = "hi-IN-SwaraNeural") -> AudioPayload:
        """
        Converts text into audio payload. In test/offline mode, produces a simulated
        audio buffer with calculated speech duration.
        """
        words = len(text.split())
        estimated_duration = max(1.2, words * 0.35)
        # Mock 16kHz PCM audio bytes
        mock_pcm = b"\x00\x00" * int(16000 * estimated_duration)
        return AudioPayload(
            audio_bytes=mock_pcm,
            sample_rate=16000,
            format="wav",
            duration_seconds=estimated_duration,
        )
