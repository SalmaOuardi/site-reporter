"""Small helper around Azure's Mistral deployment."""

from __future__ import annotations

import logging
from typing import Optional

from openai import AsyncAzureOpenAI
from openai import OpenAIError

from ..core.config import get_settings

logger = logging.getLogger(__name__)


async def chat_completion(
    prompt: str,
    system_message: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> str:
    """Send a chat prompt to Mistral and return the assistant text."""
    settings = get_settings()

    client = AsyncAzureOpenAI(
        api_key=settings.azure_openai_key,
        api_version=settings.mistral_api_version,
        azure_endpoint=settings.azure_endpoint,
    )

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=settings.mistral_deployment_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not response.choices:
            raise ValueError("LLM response did not contain any choices")

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM response choice did not contain content")

        logger.info(
            "Successfully generated LLM response (%d tokens)",
            response.usage.total_tokens if response.usage else 0,
        )
        return content

    except OpenAIError as exc:
        logger.error("Azure OpenAI chat completion failed: %s", exc)
        raise
    except Exception as exc:
        logger.error("Unexpected error during chat completion: %s", exc)
        raise
