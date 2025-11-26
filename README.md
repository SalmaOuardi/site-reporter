# Site Reporter MVP

Voice-first assistant for chantier reports: Streamlit records French memos, Azure GPT‑4o-mini-transcribe handles STT, a Mistral deployment extracts structured fields, and FastAPI returns an editable report plus DOCX download.

## Architecture (what lives where)
- Frontend: Streamlit app (`frontend/app.py`) with a REST client (`frontend/services/api.py`) that calls the backend.
- Backend: FastAPI (`backend/app/main.py`) exposes the workflow routes in `backend/app/api/routes/workflow.py`.
- Services: STT wrapper (`backend/app/services/stt.py`), LLM wrapper (`backend/app/services/llm.py`), template extraction and date normalization (`backend/app/services/template.py`), report rendering (`backend/app/services/report.py`), DOCX generation (`backend/app/services/docx_generator.py`).
- Config: central settings in `backend/app/core/config.py`; STT temperature is a fixed constant in `backend/app/services/stt.py` (kept at 0.0 for deterministic transcripts).
- Schemas: Pydantic payloads live in `backend/app/models/schemas.py`.

## Requirements
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (manages virtualenvs)
- Azure OpenAI deployments for GPT‑4o-mini-transcribe + Mistral

## Setup
```bash
git clone <repo>
cd site-reporter
```

### Backend env
```bash
cd backend
cp .env.example .env  # fill Azure keys, deployments, endpoints
uv sync
```

### Frontend env
```bash
cd ../frontend
echo "BACKEND_URL=http://localhost:8000" > .env
uv sync
```

### Demo audio override (optional)
To always transcribe the bundled noisy clip instead of live mic input, add to `frontend/.env`:
```bash
echo "DEMO_AUDIO_MODE=true" >> .env
# optional custom file
# echo "DEMO_AUDIO_PATH=/full/path/to/audio.wav" >> .env
```
By default the app uses `frontend/assets/audio_noisy.wav`.

## Run
```bash
# Terminal 1 – FastAPI
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2 – Streamlit dashboard
cd frontend
uv run streamlit run app.py
```
Visit `http://localhost:8501` for the UI, `http://localhost:8000/docs` for the API explorer.

## API Surface
Base URL `http://localhost:8000/api`
- `POST /transcribe`
- `POST /report/template`
- `POST /report/generate`
- `POST /pipeline/auto`
- `POST /report/download/docx`

Health probe: `GET /health`.

## End-to-end flow
1) Streamlit records audio and can optionally swap in demo audio (`frontend/assets/audio_noisy.wav`).
2) Audio is base64-encoded and POSTed to `/api/transcribe`; Azure GPT-4o-mini-transcribe returns text at temperature 0.0.
3) `/api/report/template` asks the Mistral deployment to extract fields; missing dates default to “today” but keep transcript-stated years.
4) Users can edit fields, then call `/api/report/generate` for plaintext or `/api/report/download/docx` for a Word file.
5) `/api/pipeline/auto` chains all steps without human validation.

## Tests
```bash
cd backend
uv run pytest ../tests
```

## Contributing
- Use feature branches, run `ruff check` + tests before pushing.
- Keep backend routers under `app/api/routes/` and shared services in `app/services/`.
- Describe manual test steps and Azure dependencies in PRs.
