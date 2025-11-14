"""Typed payloads passed between the Streamlit UI and FastAPI."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """What the UI sends after recording audio."""

    audio_b64: str = Field(..., description="Base64-encoded audio bytes.")
    language: Optional[str] = Field(
        default=None, description="Optional BCP-47 language hint for transcription."
    )


class TranscriptionResponse(BaseModel):
    """Plain transcription result."""

    text: str = Field(..., description="Raw transcription from the STT model.")


class TemplateInferenceRequest(BaseModel):
    """Request for template inference once we have text."""

    transcript: str = Field(..., description="Human readable transcript.")


class TemplateInferenceResponse(BaseModel):
    """Template choice plus the raw fields we inferred."""

    template_type: str = Field(..., description="One of the supported template names.")
    fields: Dict[str, str] = Field(
        default_factory=dict, description="Key/value pairs editable by the user."
    )


class ReportGenerationRequest(BaseModel):
    """Everything needed to build the final report text."""

    template_type: str = Field(..., description="Template to fill.")
    fields: Dict[str, str] = Field(..., description="Structured inputs for the template.")
    transcript: Optional[str] = Field(
        default=None, description="Optional transcript for additional context."
    )


class ReportGenerationResponse(BaseModel):
    """Final report text blob."""

    report_text: str = Field(..., description="Plaintext report summary.")


class AutoPipelineRequest(TranscriptionRequest):
    """Fire-and-forget payload when we skip human validation."""

    autopilot: bool = Field(
        default=True,
        description="Marker used by the frontend to indicate no human validation.",
    )


class AutoPipelineResponse(BaseModel):
    """Transcription, template, and report returned together."""

    text: str
    template_type: str
    fields: Dict[str, str]
    report_text: str
