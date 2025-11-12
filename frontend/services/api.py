"""Wrapper around the FastAPI backend endpoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)


class BackendClient:
    """Simple REST client used by the Streamlit UI."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        env_url = base_url or os.getenv("BACKEND_URL", "http://localhost:8000")
        self.base_url = env_url.rstrip("/")

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = self._url(path)
        response = requests.post(url, json={k: v for k, v in payload.items() if v is not None}, timeout=60)
        response.raise_for_status()
        return response.json()

    def transcribe(self, audio_b64: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Call the transcription endpoint."""

        return self._post("/api/transcribe", {"audio_b64": audio_b64, "language": language})

    def infer_template(self, transcript: str) -> Dict[str, Any]:
        """Call the template inference endpoint."""

        return self._post("/api/report/template", {"transcript": transcript})

    def generate_report(
        self, template_type: str, fields: Dict[str, str], transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call the report generation endpoint."""

        payload = {"template_type": template_type, "fields": fields, "transcript": transcript}
        return self._post("/api/report/generate", payload)

    def run_auto_pipeline(self, audio_b64: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Execute the automated pipeline endpoint."""

        return self._post(
            "/api/pipeline/auto",
            {
                "audio_b64": audio_b64,
                "language": language,
                "autopilot": True,
            },
        )
