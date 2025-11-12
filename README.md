# Site Reporter MVP

Minimal FastAPI + Streamlit project for experimenting with audio-first construction site reports.

## Project Layout

```
backend/   FastAPI service (REST API, OpenAI STT placeholder)
frontend/  Streamlit UI (multi-step workflow + session state)
```

## Prerequisites

- Python 3.11+ installed locally.
- [uv](https://github.com/astral-sh/uv) available on your PATH.

## Environment Variables

1. Copy `backend/.env.example` to `backend/.env` and add your `OPENAI_API_KEY` if you plan to hit the real GPT-4o-mini transcription model. Without a key the backend will fall back to a deterministic stub.
2. Copy `frontend/.env.example` to `frontend/.env` and point `BACKEND_URL` at your FastAPI instance (defaults to `http://localhost:8000`).

## Run the Backend

```bash
uv run --project backend uvicorn backend.app.main:app --reload
```

The service exposes its workflow routes under `/api/*` plus a `/health` endpoint for readiness probes.

## Run the Frontend

```bash
uv run --project frontend streamlit run frontend/app.py
```

The Streamlit dashboard lets you:

1. Record or upload audio, then call the transcription endpoint (human-in-loop mode).
2. Trigger template inference, edit the resulting table, and generate a draft report.
3. Switch to automated mode, where the backend runs transcription → inference → report in a single call.

## Notes

- Both sub-projects are standard `pyproject.toml` applications, so you can install dependencies or open shells with `uv pip install` / `uv run --project ...`.
- Report creation and PDF generation are placeholders; extend `backend/app/services/report.py` to emit richer formats when ready.
