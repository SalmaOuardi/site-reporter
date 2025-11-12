# Site Reporter MVP - Project Context & Current Status

## 📋 Project Overview

**Goal:** Create a minimal but functional full-stack Python project (FastAPI + Streamlit) for a construction-site report generator MVP that converts French audio recordings into structured reports.

**Tech Stack:**
- Backend: FastAPI (Python 3.11+)
- Frontend: Streamlit
- STT: Azure OpenAI GPT-4o-mini-transcribe
- LLM: Azure OpenAI Mistral-small-2503
- Dependency Management: UV (not pip)
- Language: French (all UI, reports, and transcriptions)

---

## 🏗️ Project Structure

```
site-reporter/
├── backend/
│   ├── .env                        # Azure API keys
│   ├── .env.example
│   ├── pyproject.toml              # Backend dependencies
│   └── app/
│       ├── main.py                 # FastAPI app
│       ├── core/
│       │   └── config.py           # Azure OpenAI configuration
│       ├── models/
│       │   └── schemas.py          # Pydantic models
│       ├── routers/
│       │   └── pipeline.py         # API endpoints
│       └── services/
│           ├── llm.py              # Azure Mistral LLM service
│           ├── stt.py              # Azure STT service
│           ├── template.py         # LLM-powered field extraction
│           └── report.py           # French report generation
│
├── frontend/
│   ├── app.py                      # Streamlit app (French UI)
│   ├── pyproject.toml
│   └── services/
│       └── api.py                  # Backend API client
│
└── tests/
    ├── conftest.py
    ├── integration/
    │   └── test_azure_integration.py
    └── fixtures/
        └── audio/
            └── test_audio.wav
```

---

## ✅ What We've Completed

### 1. Azure OpenAI Integration ✅
- **STT Service:** Uses Azure GPT-4o-mini-transcribe for French audio transcription
- **LLM Service:** Uses Azure Mistral-small-2503 for intelligent field extraction
- **Configuration:**
  - Endpoint: `https://draftspeechtotext.cognitiveservices.azure.com`
  - STT API Version: `2025-03-01-preview`
  - Mistral API Version: `2024-05-01-preview`
  - Default Language: French (`fr`)

### 2. French Language Implementation ✅
- All UI elements translated to French
- French report templates
- French keyword detection
- French LLM prompts for field extraction

### 3. Template System ✅
Four French report templates implemented:

**Template 1: `probleme_decouverte` (Problem/Incident)**
- Keywords: problème, incident, souci, défaillance, panne, fuite, casse
- Fields: Date, Heure, Opérateur, Problème, Domaine, Urgence, Plan d'action

**Template 2: `tour_securite` (Security Tour)**
- Keywords: tour, sécurité, inspection, vendredi, fissure, béton
- Fields: Date, Heure, Opérateur, Zone inspectée, Observations, Non-conformités, Actions correctives

**Template 3: `tache_assignee` (Task Assignment)**
- Keywords: tâche, assigné, mission, travail
- Fields: Date, Heure, Opérateur, Tâche, Assigné à, Échéance, Priorité, Description

**Template 4: `rapport_generique` (Generic - Default)**
- Fields: Date, Heure, Opérateur, Problème, Domaine, Urgence, Plan d'action

### 4. LLM-Powered Field Extraction ✅
- Template detection uses French keywords
- Mistral LLM extracts structured data from transcript
- Low temperature (0.1) for factual extraction
- JSON response parsing with markdown cleanup
- Fallback handling for LLM failures

### 5. Two Workflow Modes ✅
**Mode 1: Avec validation humaine (Human-in-loop)**
1. Record/upload audio
2. Transcribe audio
3. Infer template and extract fields
4. Edit fields in interactive table
5. Generate final report

**Mode 2: Entièrement automatique (Fully automatic)**
1. Record/upload audio
2. Click "Lancer le pipeline automatique"
3. Everything happens automatically

### 6. Auto-Reload Configured ✅
- Backend: `--reload` flag enabled
- Frontend: Streamlit watches for file changes

### 7. Project Cleanup ✅
- Removed duplicate `backend/backend/` directory
- Moved tests to proper `tests/` structure
- Enhanced `.gitignore`
- Standardized Python version to 3.11+
- Added pytest configuration

---

## 🔧 Current Configuration

### Backend Environment Variables (`.env`)
```env
# Azure OpenAI Configuration
AZURE_OPENAI_KEY="<your-key>"
AZURE_ENDPOINT="https://draftspeechtotext.cognitiveservices.azure.com"

# Speech-to-Text Configuration
STT_DEPLOYMENT_NAME="gpt-4o-mini-transcribe"
STT_API_VERSION="2025-03-01-preview"
DEFAULT_LANGUAGE="fr"

# LLM Configuration (Mistral)
MISTRAL_DEPLOYMENT_NAME="mistral-small-2503"
MISTRAL_API_VERSION="2024-05-01-preview"

# Application Configuration
DEFAULT_TEMPLATE="rapport_generique"
```

### API Endpoints
- `POST /api/transcribe` - Transcribe audio
- `POST /api/report/template` - Infer template and extract fields
- `POST /api/report/generate` - Generate final report
- `POST /api/pipeline/auto` - Full automatic pipeline
- `GET /health` - Health check

---

## 🎯 How It Should Work

### Expected Workflow (Avec validation humaine)

**Input Example:**
> "Aujourd'hui, le 12 novembre 2025, je fais l'inspection du bâtiment A. Je me trouve actuellement au troisième étage devant l'entrée principale. J'ai remarqué trois fissures importantes sur le mur est. Les fissures mesurent environ 15 à 20 cm de longueur. L'état du béton armé semble préoccupant. Je recommande une inspection détaillée par un ingénieur structure."

**Expected Output:**
1. **Template Detection:** `tour_securite` (detected via keywords: "inspection", "fissure", "béton")
2. **Extracted Fields:**
   - Date: `12/11/2025`
   - Heure: *(empty if not mentioned)*
   - Opérateur: `Marie Martin - Responsable sécurité`
   - Zone inspectée: `Bâtiment A, troisième étage, entrée principale`
   - Observations: `Trois fissures importantes sur le mur est, 15-20 cm de longueur`
   - Non-conformités: `État du béton armé préoccupant`
   - Actions correctives: `Inspection détaillée par un ingénieur structure recommandée`

3. **Generated Report:**
```
============================================================
RAPPORT DE SÉCURITÉ - Tour de Chantier
============================================================
Généré le: 12/11/2025 à 16:54

────────────────────────────────────────────────────────────
DÉTAILS DU RAPPORT
────────────────────────────────────────────────────────────

▪ Date: 12/11/2025
▪ Heure: Non renseigné
▪ Opérateur: Marie Martin - Responsable sécurité
▪ Zone inspectée: Bâtiment A, troisième étage, entrée principale
▪ Observations: Trois fissures importantes sur le mur est, 15-20 cm
▪ Non-conformités: État du béton armé préoccupant
▪ Actions correctives: Inspection détaillée par un ingénieur structure

────────────────────────────────────────────────────────────
TRANSCRIPTION AUDIO
────────────────────────────────────────────────────────────

Aujourd'hui, le 12 novembre 2025, je fais l'inspection...
```

---

## ❌ Current Problem

### Issue: "Avec validation humaine" Mode - Transcript Not Displaying

**Symptoms:**
1. User records audio ✅
2. User clicks "📝 Transcrire l'audio" button
3. Toast notification appears: "✅ Transcription reçue" ✅
4. **But the transcript text does NOT appear in the text area** ❌
5. If user switches to "Entièrement automatique" mode and clicks "Lancer le pipeline", everything works perfectly ✅
6. After that, if user returns to "Avec validation humaine", the transcript suddenly appears ✅

**What Works:**
- ✅ "Entièrement automatique" mode works perfectly
- ✅ Audio recording/upload works
- ✅ Backend transcription service works (confirmed by automatic mode)
- ✅ Session state is being updated (confirmed by mode switching behavior)
- ✅ LLM field extraction works
- ✅ Report generation works

**What Doesn't Work:**
- ❌ UI doesn't refresh/update after transcription in "Avec validation humaine" mode
- ❌ Transcript text area remains empty immediately after transcription
- ❌ User has to switch modes or trigger another action to see the transcript

### What We've Tried

**Attempt 1: Added `st.rerun()` to force UI refresh**
```python
def handle_transcription(audio_bytes: bytes, language: Optional[str]) -> None:
    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner("🔄 Transcription en cours avec GPT-4o-mini..."):
            response = client.transcribe(encoded, language=language)
    except Exception as exc:
        st.error(f"❌ Échec de la transcription: {exc}")
        return
    st.session_state["transcript"] = response["text"]
    st.toast("✅ Transcription reçue.", icon="✏️")
    st.rerun()  # Force UI refresh to show transcript
```

**Attempt 2: Use session_state audio instead of local variable**
```python
# Before (didn't work after rerun):
if st.button("📝 Transcrire l'audio", disabled=audio_bytes is None):
    handle_transcription(audio_bytes, ...)

# After (to persist audio across reruns):
stored_audio = st.session_state.get("audio_bytes")
if st.button("📝 Transcrire l'audio", disabled=stored_audio is None):
    handle_transcription(stored_audio, ...)
```

**Result:** Problem persists ❌

### Technical Details

**Transcript Storage:**
```python
st.session_state["transcript"] = response["text"]  # Confirmed working
```

**Transcript Display:**
```python
new_transcript = st.text_area(
    "Transcription (modifiable):",
    value=st.session_state.get("transcript", ""),  # Should show transcript
    height=120,
    key="transcript_editor",
)
```

**Hypothesis:**
The issue might be related to:
1. Streamlit widget state management across reruns
2. Text area not re-rendering with new value
3. Race condition between session_state update and widget rendering
4. Button click consuming the rerun before text area updates

### Code Location

**Frontend file:** `frontend/app.py`
- Line 83-95: `handle_transcription()` function
- Line 207-221: "Avec validation humaine" mode UI
- Line 211-216: Transcription button and handler

**Backend files (working correctly):**
- `backend/app/services/stt.py` - STT service
- `backend/app/services/template.py` - LLM field extraction
- `backend/app/routers/pipeline.py` - API endpoints

---

## 🚀 How to Run

### Terminal 1 - Backend
```bash
cd backend
uv run uvicorn app.main:app --reload
```
Server runs at: `http://127.0.0.1:8000`

### Terminal 2 - Frontend
```bash
cd frontend
uv run streamlit run app.py
```
App opens at: `http://localhost:8501`

### Testing Azure Integration
```bash
uv run --directory backend python tests/integration/test_azure_integration.py tests/fixtures/audio/test_audio.wav
```

---

## 📝 Next Steps After Fixing Current Issue

1. **Enhance LLM field extraction prompts** for better accuracy
2. **Add PDF generation** (currently placeholder)
3. **Add persistence layer** (database for reports)
4. **Add authentication**
5. **Add unit tests**
6. **Improve error handling and user feedback**
7. **Add logging and monitoring**

---

## 🔑 Key Files for Reference

### Frontend State Management
**File:** `frontend/app.py`
```python
def init_state() -> None:
    defaults = {
        "mode": "Avec validation humaine",
        "transcript": "",
        "template_type": "",
        "fields": {},
        "report_text": "",
        "audio_bytes": None,
        "language": "fr",
    }
```

### Backend LLM Extraction
**File:** `backend/app/services/template.py`
- Uses 2-step process: keyword detection → LLM extraction
- French prompts with low temperature (0.1)
- Async function returning `Tuple[str, Dict[str, str]]`

### API Client
**File:** `frontend/services/api.py`
```python
class BackendClient:
    def transcribe(self, audio_b64: str, language: str = None) -> dict
    def infer_template(self, transcript: str) -> dict
    def generate_report(self, template_type: str, fields: dict, transcript: str = None) -> dict
    def run_auto_pipeline(self, audio_b64: str, language: str = None) -> dict
```

---

## 🐛 Debug Information

**Streamlit Version:** `>=1.36.0`
**Python Version:** `3.11+`
**UV Version:** Latest

**Session State Keys:**
- `mode`: Current workflow mode
- `transcript`: Transcribed text
- `template_type`: Detected template
- `fields`: Extracted field dictionary
- `report_text`: Generated report
- `audio_bytes`: Raw audio data
- `language`: Selected language (default: "fr")

**Known Working Flows:**
1. ✅ Automatic mode → Complete success
2. ✅ Manual mode → Switch to auto → Switch back → Shows transcript
3. ❌ Manual mode → Transcribe → (empty text area)

---

## 📞 Contact & Context

This document was created to provide context for debugging the Streamlit UI refresh issue in the "Avec validation humaine" workflow mode. The backend is working correctly, Azure integration is functional, and the automatic mode works perfectly. The issue is isolated to the frontend UI state management after transcription.

**Date:** November 12, 2025
**Status:** MVP functional except for UI refresh bug in manual mode
