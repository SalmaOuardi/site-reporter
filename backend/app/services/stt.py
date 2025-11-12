"""Speech-to-text service that talks to OpenAI or falls back to a stub."""

from __future__ import annotations

import base64
import io
import logging
from typing import Optional

from openai import AsyncOpenAI
from openai import OpenAIError

from ..core.config import get_settings

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_b64: str, language: Optional[str] = None) -> str:
    """Transcribe audio bytes using GPT-4o-mini-transcribe or a deterministic stub."""

    audio_bytes = base64.b64decode(audio_b64)
    settings = get_settings()

    if settings.openai_api_key:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "recording.wav"

        try:
            response = await client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file,
                language=language,
            )
            text = getattr(response, "text", None)
            if not text and isinstance(response, dict):
                text = response.get("text")
            if text:
                return text
        except OpenAIError as exc:
            logger.warning("OpenAI transcription failed, using stub: %s", exc)

    # Deterministic fallback keeps the app functional during local development.
    approx_seconds = max(len(audio_bytes) // 32000, 1)
    return (
        "Placeholder transcript generated locally. "
        f"Audio length approximately {approx_seconds} seconds."
    )

