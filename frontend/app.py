"""Interface Streamlit pour le générateur de rapports de chantier MVP."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Callable, Dict, List, Optional

import streamlit as st

from services.api import BackendClient

st.set_page_config(page_title="Rapporteur de Chantier", layout="wide", page_icon="🏗️")

client = BackendClient()

DEFAULT_LANGUAGE = "fr"
MANUAL_MODE = "Avec validation humaine"
AUTO_MODE = "Entièrement automatique"
TRANSCRIPT_WIDGET_KEY = "transcript_editor"


def init_state() -> None:
    """Ensure all workflow keys exist in session_state."""

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
    """Clear all derived values while keeping the selected mode."""

    preserved_mode = st.session_state.get("mode", MANUAL_MODE)
    st.session_state.clear()
    init_state()
    st.session_state["mode"] = preserved_mode


def encode_audio(audio_bytes: bytes) -> str:
    """Convert binary audio into the base64 payload required by the backend."""

    return base64.b64encode(audio_bytes).decode("utf-8")


def data_editor_rows(fields: Dict[str, str]) -> List[Dict[str, str]]:
    """Convert a dict into rows consumable by st.data_editor."""

    return [{"Champ": key, "Valeur": value} for key, value in fields.items()]


def set_transcript_state(value: str) -> None:
    """Keep transcript and widget state synchronized."""

    st.session_state["transcript"] = value
    st.session_state[TRANSCRIPT_WIDGET_KEY] = value


def audio_trigger_button(label: str, callback: Callable[[bytes], None]) -> None:
    """Render a button that requires a recorded audio clip."""

    stored_audio = st.session_state.get("audio_bytes")
    if st.button(label, disabled=stored_audio is None, use_container_width=True):
        if stored_audio is None:
            st.warning("⚠️ Veuillez d'abord enregistrer un mémo vocal.")
        else:
            callback(stored_audio)


def capture_audio() -> Optional[bytes]:
    """Capture live audio recordings only."""

    if not hasattr(st, "audio_input"):
        st.sidebar.error(
            "La version actuelle de Streamlit ne supporte pas l'enregistrement audio. "
            "Veuillez mettre à jour Streamlit."
        )
        return None

    audio_input = st.sidebar.audio_input("🎤 Enregistrer un mémo vocal", key="record_audio")
    if audio_input is not None:
        audio_bytes = audio_input.getvalue()
        st.sidebar.success("✅ Enregistrement capturé.")
        st.sidebar.audio(audio_bytes, format="audio/wav")
        return audio_bytes

    stored_audio = st.session_state.get("audio_bytes")
    if stored_audio:
        st.sidebar.audio(stored_audio, format="audio/wav")
        st.sidebar.caption("Lecture du dernier enregistrement.")
    else:
        st.sidebar.info("Réalisez un enregistrement pour activer les étapes suivantes.")
    return None


def handle_transcription(audio_bytes: bytes) -> None:
    """Call the backend transcription endpoint."""

    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner("🔄 Transcription en cours avec GPT-4o-mini..."):
            response = client.transcribe(encoded, language=DEFAULT_LANGUAGE)
    except Exception as exc:  # noqa: BLE001 - surface network issues in the UI
        st.error(f"❌ Échec de la transcription: {exc}")
        return
    set_transcript_state(response["text"])
    st.toast("✅ Transcription reçue.", icon="✏️")
    st.rerun()  # Force UI refresh to show transcript


def handle_template_inference() -> None:
    """Call backend to infer a template and seed editable fields."""

    transcript = st.session_state.get("transcript", "").strip()
    if not transcript:
        st.warning("⚠️ Veuillez d'abord générer ou coller une transcription.")
        return

    try:
        with st.spinner("🔄 Analyse du type de rapport..."):
            response = client.infer_template(transcript)
    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Échec de l'analyse: {exc}")
        return
    st.session_state["template_type"] = response["template_type"]
    st.session_state["fields"] = response["fields"]
    st.toast(f"✅ Template détecté: {response['template_type']}", icon="🧩")
    st.rerun()  # Force UI refresh to show fields table


def handle_report_generation() -> None:
    """Call backend to build the final textual report."""

    template_type = st.session_state.get("template_type")
    fields = st.session_state.get("fields", {})
    if not template_type or not fields:
        st.warning("⚠️ Veuillez analyser le template et modifier les champs avant de générer.")
        return

    try:
        with st.spinner("🔄 Génération du rapport..."):
            response = client.generate_report(
                template_type=template_type,
                fields=fields,
                transcript=st.session_state.get("transcript"),
            )
    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Échec de la génération: {exc}")
        return
    st.session_state["report_text"] = response["report_text"]
    st.toast("✅ Rapport prêt pour révision.", icon="📄")
    st.rerun()  # Force UI refresh to show report


def handle_auto_pipeline(audio_bytes: bytes) -> None:
    """Run the entire workflow in a single backend call."""

    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner("🔄 Pipeline automatique en cours..."):
            response = client.run_auto_pipeline(encoded, language=DEFAULT_LANGUAGE)
    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Échec du pipeline: {exc}")
        return

    set_transcript_state(response["text"])
    st.session_state["template_type"] = response["template_type"]
    st.session_state["fields"] = response["fields"]
    st.session_state["report_text"] = response["report_text"]
    st.toast("✅ Rapport automatique créé.", icon="⚡️")
    st.rerun()  # Force UI refresh to show all results


def rows_to_fields_dict(rows: List[Dict[str, str]]) -> Dict[str, str]:
    """Convert data_editor rows back to a dict."""

    return {row["Champ"]: row["Valeur"] for row in rows}


def show_report_preview(report_text: str) -> None:
    """Render the final report in a code block."""

    st.subheader("📄 Rapport Généré")
    st.code(report_text, language="text")


def render_manual_workflow() -> None:
    """Render the human-in-the-loop workflow."""

    st.subheader("📝 Étape 1: Enregistrer et Transcrire")
    st.caption("Enregistrez un mémo vocal en français, puis lancez la transcription.")

    audio_trigger_button("📝 Transcrire l'audio", handle_transcription)

    new_transcript = st.text_area(
        "Transcription (modifiable):",
        height=160,
        placeholder="La transcription apparaîtra ici après l'étape 1.",
        key=TRANSCRIPT_WIDGET_KEY,
    )
    if new_transcript != st.session_state.get("transcript"):
        st.session_state["transcript"] = new_transcript

    if st.session_state.get("transcript"):
        st.subheader("🔍 Étape 2: Template et Données Structurées")
        st.caption("Détectez automatiquement le bon template puis ajustez les champs.")
        if st.button("🔍 Analyser le type de rapport", use_container_width=True):
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

    if st.session_state.get("fields"):
        st.subheader("📄 Étape 3: Générer le Rapport")
        if st.button("📄 Générer le rapport", use_container_width=True):
            handle_report_generation()


def render_auto_workflow() -> None:
    """Render the fully automated workflow."""

    st.subheader("⚡ Pipeline Automatique")
    st.markdown("Ce mode enchaîne transcription → analyse → génération sans validation.")

    audio_trigger_button("⚡ Lancer le pipeline automatique", handle_auto_pipeline)


def main() -> None:
    """Application entry point."""

    init_state()

    logo_path = Path(__file__).resolve().parent / "assets" / "vinci-logo.png"
    if logo_path.exists():
        col_logo, col_title = st.columns([1, 5])
        with col_logo:
            st.image(str(logo_path), use_column_width=True)
        with col_title:
            st.title("🏗️ Générateur de Rapports de Chantier")
    else:
        st.title("🏗️ Générateur de Rapports de Chantier")
    st.markdown("*MVP - Audio vers rapport structuré*")
    st.divider()

    with st.sidebar:
        st.header("⚙️ Contrôles")
        st.caption("Langue cible: Français (fixe)")
        st.caption("L'enregistreur du navigateur est requis.")
        if st.button("🔄 Réinitialiser", type="secondary", use_container_width=True):
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

    # Show report if available
    if st.session_state.get("report_text"):
        show_report_preview(st.session_state["report_text"])


if __name__ == "__main__":
    main()
