# Site Reporter MVP

Voice-first assistant for chantier reports: Streamlit records French memos, Azure GPT‑4o-mini-transcribe handles STT, a Mistral deployment extracts structured fields, and FastAPI returns an editable report plus DOCX download.

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

## Tests
```bash
cd backend
uv run pytest ../tests
```

## Contributing
- Use feature branches, run `ruff check` + tests before pushing.
- Keep backend routers under `app/api/routes/` and shared services in `app/services/`.
- Describe manual test steps and Azure dependencies in PRs.
