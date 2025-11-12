"""Streamlit frontend for the construction site report generator MVP."""

from __future__ import annotations

import base64
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from services.api import BackendClient

st.set_page_config(page_title="Site Reporter MVP", layout="wide")

client = BackendClient()


def init_state() -> None:
    """Ensure all workflow keys exist in session_state."""

    defaults = {
        "mode": "Human in the loop",
        "transcript": "",
        "template_type": "",
        "fields": {},
        "report_text": "",
        "audio_bytes": None,
        "language": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_workflow() -> None:
    """Clear all derived values while keeping the selected mode."""

    preserved_mode = st.session_state.get("mode", "Human in the loop")
    st.session_state.clear()
    init_state()
    st.session_state["mode"] = preserved_mode


def encode_audio(audio_bytes: bytes) -> str:
    """Convert binary audio into the base64 payload required by the backend."""

    return base64.b64encode(audio_bytes).decode("utf-8")


def data_editor_rows(fields: Dict[str, str]) -> List[Dict[str, str]]:
    """Convert a dict into rows consumable by st.data_editor."""

    return [{"Field": key, "Value": value} for key, value in fields.items()]


def capture_audio() -> Optional[bytes]:
    """Handle either direct recording or manual uploads."""

    audio_bytes: Optional[bytes] = None
    audio_input = None

    if hasattr(st, "audio_input"):
        audio_input = st.sidebar.audio_input("Record audio", key="record_audio")

    if audio_input is not None:
        audio_bytes = audio_input.getvalue()
        st.sidebar.success("Live recording captured.")
    else:
        upload = st.sidebar.file_uploader(
            "Upload audio (mp3, wav, m4a)",
            type=["mp3", "wav", "m4a"],
            key="upload_audio",
        )
        if upload is not None:
            audio_bytes = upload.read()
            st.sidebar.success(f"Uploaded {upload.name}.")

    if audio_bytes:
        st.sidebar.audio(audio_bytes, format="audio/wav")

    return audio_bytes


def handle_transcription(audio_bytes: bytes, language: Optional[str]) -> None:
    """Call the backend transcription endpoint."""

    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner("Transcribing with GPT-4o-mini..."):
            response = client.transcribe(encoded, language=language)
    except Exception as exc:  # noqa: BLE001 - surface network issues in the UI
        st.error(f"Transcription failed: {exc}")
        return
    st.session_state["transcript"] = response["text"]
    st.toast("Transcript received.", icon="✏️")


def handle_template_inference() -> None:
    """Call backend to infer a template and seed editable fields."""

    transcript = st.session_state.get("transcript", "").strip()
    if not transcript:
        st.warning("Please generate or paste a transcript first.")
        return

    try:
        with st.spinner("Inferring template..."):
            response = client.infer_template(transcript)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Template inference failed: {exc}")
        return
    st.session_state["template_type"] = response["template_type"]
    st.session_state["fields"] = response["fields"]
    st.toast(f"Template inferred: {response['template_type']}", icon="🧩")


def handle_report_generation() -> None:
    """Call backend to build the final textual report."""

    template_type = st.session_state.get("template_type")
    fields = st.session_state.get("fields", {})
    if not template_type or not fields:
        st.warning("Please infer a template and edit the fields before generating.")
        return

    try:
        with st.spinner("Generating report draft..."):
            response = client.generate_report(
                template_type=template_type,
                fields=fields,
                transcript=st.session_state.get("transcript"),
            )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Report generation failed: {exc}")
        return
    st.session_state["report_text"] = response["report_text"]
    st.toast("Report ready for review.", icon="📄")


def handle_auto_pipeline(audio_bytes: bytes, language: Optional[str]) -> None:
    """Call the one-shot pipeline for the fully automated path."""

    encoded = encode_audio(audio_bytes)
    try:
        with st.spinner("Running automated pipeline..."):
            response = client.run_auto_pipeline(encoded, language=language)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Automated pipeline failed: {exc}")
        return

    st.session_state["transcript"] = response["text"]
    st.session_state["template_type"] = response["template_type"]
    st.session_state["fields"] = response["fields"]
    st.session_state["report_text"] = response["report_text"]
    st.toast("Automatic report created.", icon="⚡️")


def render_fields_editor() -> None:
    """Render editable table for the structured template fields."""

    fields = st.session_state.get("fields", {})
    if not fields:
        return

    st.markdown(f"**Template:** `{st.session_state.get('template_type', 'n/a')}`")
    edited_rows = st.data_editor(
        pd.DataFrame(data_editor_rows(fields)),
        num_rows="dynamic",
        hide_index=True,
        key="fields_editor",
    )
    cleaned = {
        str(row["Field"]).strip(): str(row["Value"]).strip()
        for _, row in edited_rows.iterrows()
        if str(row["Field"]).strip()
    }
    st.session_state["fields"] = cleaned


def render_report_output() -> None:
    """Display the generated report if available."""

    report = st.session_state.get("report_text")
    if not report:
        return

    st.subheader("Generated Report")
    st.text_area("Report preview", value=report, height=220, label_visibility="collapsed")


def main() -> None:
    """Wire all UI sections together."""

    init_state()

    st.title("Construction Site Report Generator")
    st.caption("FastAPI backend · Streamlit frontend · OpenAI transcription placeholder")

    st.session_state["mode"] = st.radio(
        "Choose workflow",
        options=["Human in the loop", "Fully automatic"],
        horizontal=True,
        index=0,
    )

    with st.sidebar:
        st.header("Workflow Controls")
        selected_language = st.selectbox(
            "Language hint (optional)",
            ["auto", "en", "es", "fr"],
            index=0,
        )
        st.session_state["language"] = None if selected_language == "auto" else selected_language
        if st.button("Reset workflow", type="secondary"):
            reset_workflow()

    audio_bytes = capture_audio()
    if audio_bytes:
        st.session_state["audio_bytes"] = audio_bytes

    mode = st.session_state["mode"]

    if mode == "Human in the loop":
        st.subheader("1. Record and Transcribe")
        st.write("Record audio in the sidebar and transcribe it when ready.")
        if st.button("Transcribe Audio", disabled=audio_bytes is None):
            if not audio_bytes:
                st.warning("Please record or upload audio first.")
            else:
                handle_transcription(audio_bytes, st.session_state.get("language"))

        if st.session_state.get("transcript"):
            transcript = st.text_area(
                "Transcript",
                value=st.session_state["transcript"],
                height=150,
            )
            st.session_state["transcript"] = transcript

            st.subheader("2. Template & Structured Data")
            if st.button("Infer Template"):
                handle_template_inference()

            render_fields_editor()

            st.subheader("3. Generate Report")
            if st.button("Generate Report", disabled=not st.session_state.get("fields")):
                handle_report_generation()

            render_report_output()
    else:
        st.subheader("Automated Pipeline")
        st.write(
            "The backend will transcribe the audio, infer a template, populate fields, "
            "and draft a report automatically."
        )
        if st.button("Run automated pipeline", disabled=audio_bytes is None):
            if not audio_bytes:
                st.warning("Please record or upload audio first.")
            else:
                handle_auto_pipeline(audio_bytes, st.session_state.get("language"))

        if st.session_state.get("transcript"):
            st.text_area(
                "Transcript",
                value=st.session_state["transcript"],
                height=150,
            )
        render_fields_editor()
        render_report_output()


if __name__ == "__main__":
    main()
