"""
ElevenLabs-powered Speech-to-Text and Text-to-Speech.

STT: ElevenLabs Scribe model  →  returns transcribed text
TTS: ElevenLabs multilingual model  →  returns MP3 bytes
"""

import asyncio
import io
from typing import Optional

from .config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    ELEVENLABS_TTS_MODEL,
    ELEVENLABS_STT_MODEL,
)

# Voice is only available when an API key is provided
VOICE_ENABLED: bool = bool(ELEVENLABS_API_KEY)


class VoiceClient:
    """Wraps ElevenLabs STT and TTS in a single client."""

    def __init__(self) -> None:
        self.enabled = VOICE_ENABLED
        if self.enabled:
            from elevenlabs.client import ElevenLabs
            self._client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    # ── STT ───────────────────────────────────────────────────────────────────
    async def transcribe(self, audio_bytes: bytes, filename: str = "recording.wav") -> str:
        """
        Convert audio bytes to text via ElevenLabs Scribe STT.

        Parameters
        ----------
        audio_bytes : raw audio data (WAV, MP3, WebM, etc.)
        filename    : hint for the MIME type; keep the correct extension.

        Returns the transcribed text, or empty string on failure.
        """
        if not self.enabled:
            return ""

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        try:
            result = await asyncio.to_thread(
                self._client.speech_to_text.convert,
                file=audio_file,
                model_id=ELEVENLABS_STT_MODEL,
            )
            # result is a SpeechToTextChunkResponseModel; .text holds the transcript
            return (result.text or "").strip()
        except Exception as exc:
            import streamlit as st
            st.warning(f"STT error: {exc}")
            return ""

    # ── TTS ───────────────────────────────────────────────────────────────────
    async def synthesize(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech via ElevenLabs.

        Returns MP3 bytes, or None when voice is disabled / on error.
        """
        if not self.enabled or not text.strip():
            return None

        try:
            audio_gen = await asyncio.to_thread(
                self._client.text_to_speech.convert,
                voice_id=ELEVENLABS_VOICE_ID,
                text=text,
                model_id=ELEVENLABS_TTS_MODEL,
                output_format="mp3_44100_128",
            )
            # convert the generator returned by the SDK into raw bytes
            return b"".join(audio_gen)
        except Exception as exc:
            print(f"TTS error: {exc}")
            return None
