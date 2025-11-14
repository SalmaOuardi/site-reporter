"""Tableau de bord Streamlit pour piloter le MVP Site Reporter."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Callable, Dict, List, Optional

import streamlit as st

from services.api import BackendClient

st.set_page_config(page_title="Rapporteur de Chantier", layout="wide", page_icon=":material/construction:")

client = BackendClient()

DEFAULT_LANGUAGE = "fr"
MANUAL_MODE = "Avec validation humaine"
AUTO_MODE = "Entièrement automatique"
TRANSCRIPT_WIDGET_KEY = "transcript_editor"


def init_state() -> None:
    """Seed session_state with the keys we rely on."""

    defaults = {
        "mode": MANUAL_MODE,
        "transcript": "",
        "template_type": "",
        "fields": {},
        "report_text": "",
        "audio_bytes": None,
        TRANSCRIPT_WIDGET_KEY: "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_workflow() -> None:
    """Clear everything but remember which mode was active."""

    preserved_mode = st.session_state.get("mode", MANUAL_MODE)
    st.session_state.clear()
    init_state()
    st.session_state["mode"] = preserved_mode


def encode_audio(audio_bytes: bytes) -> str:
    """Turn raw audio bytes into the base64 payload FastAPI expects."""

    return base64.b64encode(audio_bytes).decode("utf-8")


def data_editor_rows(fields: Dict[str, str]) -> List[Dict[str, str]]:
    """Convert our field dict into `st.data_editor` rows."""

    return [{"Champ": key, "Valeur": value} for key, value in fields.items()]


def set_transcript_state(value: str) -> None:
    """Keep both transcript stores (state + widget key) aligned."""

    st.session_state["transcript"] = value
    st.session_state[TRANSCRIPT_WIDGET_KEY] = value


def audio_trigger_button(label: str, callback: Callable[[bytes], None]) -> None:
    """Render a CTA that does nothing until we have a recording."""

    stored_audio = st.session_state.get("audio_bytes")
    if st.button(label, disabled=stored_audio is None, use_container_width=True):
        if stored_audio is None:
            st.warning(":material/warning: Veuillez d'abord enregistrer un mémo vocal.")
        else:
            callback(stored_audio)


def inject_theme_overrides() -> None:
    """Drop some CSS to make the Streamlit theme feel like VINCI."""

    st.markdown(
        """
        <style>
            .main {
                background: linear-gradient(180deg, #f1f4fb 0%, #edf1f7 40%, #edf1f7 100%);
            }
            section[data-testid="stSidebar"] {
                background-color: #dfe6f2 !important;
            }
            section[data-testid="stSidebar"] .css-1d391kg,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] label {
                color: #14213d !important;
            }
            .vinci-hero {
                background: linear-gradient(135deg, #f9fbff 0%, #e8f1ff 100%);
                border-radius: 24px;
                padding: 1.5rem;
                border: 1px solid rgba(0, 68, 137, 0.1);
                margin-bottom: 1.5rem;
            }
            .vinci-hero__content {
                display: flex;
                gap: 1.5rem;
                align-items: center;
                flex-wrap: wrap;
            }
            .vinci-hero__text h1 {
                font-size: 2.2rem;
                margin-bottom: 0.3rem;
                color: #0c2c5c;
                font-weight: 700;
            }
            .vinci-hero__text p {
                margin: 0;
                color: #385076;
                font-size: 1rem;
            }
            .vinci-tagline {
                font-weight: 500;
                letter-spacing: 0.6px;
                text-transform: uppercase;
                color: #1e4f93;
            }
            div[data-testid="stExpander"] {
                border: 1px solid rgba(0, 68, 137, 0.15);
                border-radius: 16px !important;
                background-color: #f8f9fc;
            }
            div[data-testid="stExpander"] > details > summary {
                font-size: 1.05rem;
                font-weight: 600;
                color: #0c2c5c;
            }
            div[data-testid="stExpander"] details[open] {
                box-shadow: 0 6px 18px rgba(20, 33, 61, 0.08);
            }
            .step-hint {
                margin-top: 0.3rem;
                color: #4d5c7a;
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Display the VINCI block with logo, title, and tagline."""

    logo_path = Path(__file__).resolve().parent / "assets" / "vinci-logo.png"
    logo_html = ""
    if logo_path.exists():
        encoded_logo = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
        logo_html = (
            f"<img src='data:image/png;base64,{encoded_logo}' alt='VINCI Construction' "
            "style='max-width:180px;'>"
        )

    st.markdown(
        f"""
        <div class="vinci-hero">
            <div class="vinci-hero__content">
                <div>{logo_html}</div>
                <div class="vinci-hero__text">
                    <div class="vinci-tagline">VINCI Construction · MVP</div>
                    <h1>Générateur de Rapports de Chantier</h1>
                    <p>Mémos vocaux → GPT‑4o-mini-transcribe → Mistral → rapport structuré.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def capture_audio() -> Optional[bytes]:
    """Handle microphone capture (no file uploads for now)."""

    if not hasattr(st, "audio_input"):
        st.sidebar.error(
            "La version actuelle de Streamlit ne supporte pas l'enregistrement audio. "
            "Veuillez mettre à jour Streamlit."
        )
        return None

    audio_input = st.sidebar.audio_input(":material/mic: Enregistrer un mémo vocal", key="record_audio")
    if audio_input is not None:
        audio_bytes = audio_input.getvalue()
        st.sidebar.success("Enregistrement capturé.")
        st.sidebar.audio(audio_bytes, format="audio/wav")
        return audio_bytes

    stored_audio = st.session_state.get("audio_bytes")
    if stored_audio:
        st.sidebar.audio(stored_audio, format="audio/wav")
        st.sidebar.caption("Lecture du dernier enregistrement.")
    else:
        st.sidebar.info(":material/info: Réalisez un enregistrement pour activer les étapes suivantes.")
    return None


def handle_transcription(audio_bytes: bytes) -> None:
    """Send the recorded audio to the backend STT endpoint."""

    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner(":material/autorenew: Transcription en cours avec GPT-4o-mini..."):
            response = client.transcribe(encoded, language=DEFAULT_LANGUAGE)
    except Exception as exc:  # noqa: BLE001 - surface network issues in the UI
        st.error(f":material/error: Échec de la transcription: {exc}")
        return
    set_transcript_state(response["text"])
    st.toast("Transcription reçue.", icon=":material/done_all:")
    st.rerun()  # refresh the UI so the transcript shows up


def handle_template_inference() -> None:
    """Ask the backend to pick a template and prefill fields."""

    transcript = st.session_state.get("transcript", "").strip()
    if not transcript:
        st.warning(":material/info: Veuillez d'abord générer ou coller une transcription.")
        return

    try:
        with st.spinner(":material/auto_graph: Analyse du type de rapport..."):
            response = client.infer_template(transcript)
    except Exception as exc:  # noqa: BLE001
        st.error(f":material/error: Échec de l'analyse: {exc}")
        return
    st.session_state["template_type"] = response["template_type"]
    st.session_state["fields"] = response["fields"]
    st.toast(f"Template détecté: {response['template_type']}", icon=":material/insights:")
    st.rerun()  # refresh the UI so the new table renders


def handle_report_generation() -> None:
    """Trigger report synthesis once the structured data looks good."""

    template_type = st.session_state.get("template_type")
    fields = st.session_state.get("fields", {})
    if not template_type or not fields:
        st.warning(":material/info: Veuillez analyser le template et modifier les champs avant de générer.")
        return

    try:
        with st.spinner(":material/article: Génération du rapport..."):
            response = client.generate_report(
                template_type=template_type,
                fields=fields,
                transcript=st.session_state.get("transcript"),
            )
    except Exception as exc:  # noqa: BLE001
        st.error(f":material/error: Échec de la génération: {exc}")
        return
    st.session_state["report_text"] = response["report_text"]
    st.toast("Rapport prêt pour révision.", icon=":material/done_outline:")
    st.rerun()  # refresh the UI so the report preview appears


def handle_auto_pipeline(audio_bytes: bytes) -> None:
    """Let the backend run STT → template → report in one go."""

    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner(":material/bolt: Pipeline automatique en cours..."):
            response = client.run_auto_pipeline(encoded, language=DEFAULT_LANGUAGE)
    except Exception as exc:  # noqa: BLE001
        st.error(f":material/error: Échec du pipeline: {exc}")
        return

    set_transcript_state(response["text"])
    st.session_state["template_type"] = response["template_type"]
    st.session_state["fields"] = response["fields"]
    st.session_state["report_text"] = response["report_text"]
    st.toast("Rapport automatique créé.", icon=":material/robot_2:")
    st.rerun()  # refresh the UI so each result card updates


def rows_to_fields_dict(rows: List[Dict[str, str]]) -> Dict[str, str]:
    """Convert edited rows back into the dict shape our API expects."""

    return {row["Champ"]: row["Valeur"] for row in rows}


def show_report_preview(report_text: str) -> None:
    """Offer a simple preview of the generated report text."""

    st.subheader(":material/description: Rapport Généré")
    st.code(report_text, language="text")


def render_manual_workflow() -> None:
    """Layout the three human-in-loop steps with helpful copy."""

    with st.expander(":material/mic: Étape 1 · Enregistrer et Transcrire", expanded=True):
        st.caption("Enregistrez un mémo vocal en français, puis lancez la transcription.")
        audio_trigger_button(":material/transcribe: Transcrire l'audio", handle_transcription)

        new_transcript = st.text_area(
            "Transcription (modifiable):",
            height=160,
            placeholder="La transcription apparaîtra ici après l'étape 1.",
            key=TRANSCRIPT_WIDGET_KEY,
        )
        if new_transcript != st.session_state.get("transcript"):
            set_transcript_state(new_transcript)

    with st.expander(
        ":material/table_chart: Étape 2 · Template et Données Structurées",
        expanded=bool(st.session_state.get("transcript")),
    ):
        if not st.session_state.get("transcript"):
            st.info("Ajoutez ou éditez une transcription avant d'analyser le template.")
        else:
            st.caption("Détectez automatiquement le bon template puis ajustez les champs.")
            if st.button(":material/stacked_bar_chart: Analyser le type de rapport", use_container_width=True):
                handle_template_inference()

            if st.session_state.get("template_type"):
                st.info(f"**Template détecté:** {st.session_state['template_type']}")
                rows = data_editor_rows(st.session_state.get("fields", {}))
                edited = st.data_editor(
                    rows,
                    use_container_width=True,
                    num_rows="dynamic",
                    key="fields_editor",
                )
                st.session_state["fields"] = rows_to_fields_dict(edited)
            else:
                st.info("Aucun template détecté pour l'instant.")

    with st.expander(":material/description: Étape 3 · Générer le Rapport", expanded=bool(st.session_state.get("fields"))):
        if not st.session_state.get("fields"):
            st.info("Complétez d'abord les champs structurés.")
        else:
            if st.button(":material/picture_as_pdf: Générer le rapport", use_container_width=True):
                handle_report_generation()


def render_auto_workflow() -> None:
    """UI for the single-click automated path."""

    with st.expander(":material/bolt: Pipeline Automatique", expanded=True):
        st.markdown("Ce mode enchaîne transcription → analyse → génération sans validation.")
        audio_trigger_button(":material/robot_2: Lancer le pipeline automatique", handle_auto_pipeline)

        if st.session_state.get("transcript"):
            st.text_area(
                "Transcription générée",
                value=st.session_state["transcript"],
                height=140,
                disabled=True,
            )

        if st.session_state.get("fields"):
            st.caption("Champs détectés (lecture seule)")
            st.json(st.session_state["fields"])


def main() -> None:
    """Streamlit entry point."""

    init_state()
    inject_theme_overrides()
    render_header()

    with st.sidebar:
        st.header(":material/tune: Contrôles")
        st.caption("Langue cible: Français (fixe)")
        st.caption("L'enregistreur du navigateur est requis.")
        if st.button(":material/restart_alt: Réinitialiser", type="secondary", use_container_width=True):
            reset_workflow()

    mode_choice = st.radio(
        "Choisissez le mode de travail:",
        [MANUAL_MODE, AUTO_MODE],
        index=0 if st.session_state["mode"] == MANUAL_MODE else 1,
        horizontal=True,
    )
    st.session_state["mode"] = mode_choice

    audio_bytes = capture_audio()
    if audio_bytes:
        st.session_state["audio_bytes"] = audio_bytes

    if st.session_state["mode"] == MANUAL_MODE:
        render_manual_workflow()
    else:
        render_auto_workflow()

    if st.session_state.get("report_text"):
        show_report_preview(st.session_state["report_text"])


if __name__ == "__main__":
    main()
