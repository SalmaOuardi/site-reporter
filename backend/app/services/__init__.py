"""Domain services such as STT, LLM, template inference, and report generation."""

from .llm import chat_completion
from .stt import transcribe_audio

__all__ = ["chat_completion", "transcribe_audio"]

