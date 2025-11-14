"""Thin wrapper around Azure OpenAI's transcription endpoint."""

from __future__ import annotations

import base64
import io
import logging
from typing import Optional

from openai import AsyncAzureOpenAI
from openai import OpenAIError

from ..core.config import get_settings

logger = logging.getLogger(__name__)


async def transcribe_audio(audio_b64: str, language: Optional[str] = None) -> str:
    """Send the recorded audio to GPT-4o-mini-transcribe and return plain text."""
    audio_bytes = base64.b64decode(audio_b64)
    settings = get_settings()

    if language is None:
        language = settings.default_language

    client = AsyncAzureOpenAI(
        api_key=settings.azure_openai_key,
        api_version=settings.stt_api_version,
        azure_endpoint=settings.azure_endpoint,
    )

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "recording.wav"

    try:
        response = await client.audio.transcriptions.create(
            model=settings.stt_deployment_name,
            file=audio_file,
            language=language,
        )

        text = getattr(response, "text", None)
        if not text and isinstance(response, dict):
            text = response.get("text")

        if not text:
            raise ValueError("Transcription response did not contain text")

        logger.info("Successfully transcribed audio (%d bytes)", len(audio_bytes))
        return text

    except OpenAIError as exc:
        logger.error("Azure OpenAI transcription failed: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error during transcription: %s", exc)
        raise
