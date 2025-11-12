# Site Reporter MVP

Full-stack FastAPI + Streamlit prototype that records French voice memos directly in the browser, transcribes them with Azure OpenAI, infers the best chantier report template, and drafts a structured summary that supervisors can edit or auto-generate.

## Stack & Workflow Highlights

- **FastAPI backend** with async routers, Pydantic schemas, and Azure OpenAI clients (GPT-4o-mini transcription + Mistral-small field extraction).
- **Streamlit frontend** that manages session state for two modes: *Avec validation humaine* (step-by-step editing) and *Entièrement automatique* (fire-and-forget).
- **Live audio capture only** via `st.audio_input` to keep UX focused; everything assumes French input (`fr`) end-to-end.
- **Clean architecture**: dedicated `services/`, `models/`, and `routers/` modules plus matching Streamlit helpers.

## Repository Layout

```
site-reporter/
├── backend/
│   ├── app/
│   │   ├── core/          # Settings & env loading
│   │   ├── models/        # Pydantic schemas
│   │   ├── routers/       # FastAPI routers
│   │   └── services/      # STT, LLM, template, report helpers
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── app.py             # Streamlit UI (FR only)
│   ├── services/api.py    # REST client wrapper
│   └── pyproject.toml
├── tests/                 # Integration fixtures + future unit tests
└── PROJECT_CONTEXT.md     # Extended design notes
```

## Prerequisites

1. Python **3.11+**
2. [uv](https://github.com/astral-sh/uv) ≥ 0.4.0 on your PATH
3. Azure OpenAI resources for GPT-4o-mini transcription and Mistral-small chat completions

## Configure Environment Variables

### Backend (`backend/.env`)

```bash
cp backend/.env.example backend/.env
```

Fill the placeholders with your Azure credentials:

| Variable | Purpose |
| --- | --- |
| `AZURE_OPENAI_KEY` | Primary key for your Azure OpenAI resource |
| `AZURE_ENDPOINT` | Base endpoint (e.g., `https://xxxx.openai.azure.com`) |
| `STT_DEPLOYMENT_NAME`, `STT_API_VERSION` | GPT-4o-mini transcription deployment metadata |
| `MISTRAL_DEPLOYMENT_NAME`, `MISTRAL_API_VERSION` | Mistral-small deployment metadata |
| `DEFAULT_LANGUAGE` | Leave at `fr` to keep the workflow French-only |
| `DEFAULT_TEMPLATE` | Fallback template (`rapport_generique`) |

### Frontend (`frontend/.env`)

Create a `.env` file next to `frontend/app.py` (no example file is tracked):

```env
BACKEND_URL=http://localhost:8000
```

Point it at whatever host/port runs FastAPI (Render, Azure App Service, etc.).

## Install Dependencies with uv

Each side of the stack manages its own virtual environment:

```bash
cd backend
uv sync          # installs backend deps into .venv using pyproject + uv.lock

cd ../frontend
uv sync
```

`uv sync` only needs to run again when `pyproject.toml` changes.

## Run the Apps

### Backend API

```bash
cd backend
uv run uvicorn app.main:app --reload
```

The API lives under `http://127.0.0.1:8000/api/*` with endpoints for transcription, template inference, report generation, and an all-in-one pipeline.

### Streamlit Frontend

```bash
cd frontend
uv run streamlit run app.py
```

Open `http://localhost:8501` and use the microphone widget in the sidebar:

1. **Avec validation humaine** – record audio → transcribe → infer template → tweak fields → generate report.
2. **Entièrement automatique** – record audio → click *Pipeline automatique* to let the backend do every step.

All UI copy, prompts, and templates are in French, and only live recordings are accepted to keep transcripts consistent.

## Testing & Troubleshooting

- Basic integration scenarios (including sample audio fixtures) live under `tests/`. Run them from the backend environment:  
  ```bash
  cd backend
  uv run pytest ../tests
  ```
- If `st.audio_input` is unavailable, upgrade Streamlit (`uv pip install -U streamlit`) because recording is mandatory.
- When running locally without valid Azure credentials, mock the services or stub responses inside `backend/app/services/`.

## Next Steps

- Add PDF export in `backend/app/services/report.py`.
- Persist reports plus transcripts for audit trails.
- Harden error handling + logging before field pilots.

Happy reporting! 🏗️
