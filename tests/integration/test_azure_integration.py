"""Test script for Azure OpenAI integrations (STT and LLM)."""

import asyncio
import base64
import sys
from pathlib import Path

# Add backend to path (project root -> backend)
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.services.llm import chat_completion
from app.services.stt import transcribe_audio


async def test_llm():
    """Test the Mistral LLM service."""
    print("\n" + "=" * 60)
    print("Testing Azure Mistral LLM Service")
    print("=" * 60)

    try:
        prompt = "What is the capital of France? Answer in one sentence."
        system_message = "You are a helpful assistant that provides concise answers."

        print(f"\n📤 Prompt: {prompt}")
        print("⏳ Waiting for response...")

        response = await chat_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3,
            max_tokens=100,
        )

        print(f"\n✅ Response: {response}")
        print("\n✅ LLM test PASSED!")
        return True

    except Exception as exc:
        print(f"\n❌ LLM test FAILED: {exc}")
        return False


async def test_stt(audio_file_path: str = None):
    """Test the STT service with an audio file."""
    print("\n" + "=" * 60)
    print("Testing Azure STT Service")
    print("=" * 60)

    if not audio_file_path:
        print("\n⚠️  No audio file provided. Skipping STT test.")
        print("To test STT, run: python test_azure_integration.py <path-to-wav-file>")
        return None

    try:
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            print(f"\n❌ Audio file not found: {audio_file_path}")
            return False

        print(f"\n📂 Reading audio file: {audio_path.name}")
        audio_bytes = audio_path.read_bytes()
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        print(f"📊 Audio size: {len(audio_bytes)} bytes")
        print("⏳ Transcribing...")

        transcript = await transcribe_audio(audio_b64, language="en")

        print(f"\n✅ Transcript: {transcript}")
        print("\n✅ STT test PASSED!")
        return True

    except Exception as exc:
        print(f"\n❌ STT test FAILED: {exc}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n🚀 Starting Azure OpenAI Integration Tests")

    # Test LLM
    llm_result = await test_llm()

    # Test STT if audio file provided
    audio_file = sys.argv[1] if len(sys.argv) > 1 else None
    stt_result = await test_stt(audio_file)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"LLM (Mistral):  {'✅ PASS' if llm_result else '❌ FAIL'}")
    if stt_result is not None:
        print(f"STT (GPT-4o):   {'✅ PASS' if stt_result else '❌ FAIL'}")
    else:
        print("STT (GPT-4o):   ⏭️  SKIPPED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
