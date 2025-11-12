"""Pydantic request/response schemas used by FastAPI routers."""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """Payload received from the frontend after an audio recording."""

    audio_b64: str = Field(..., description="Base64-encoded audio bytes.")
    language: Optional[str] = Field(
        default=None, description="Optional BCP-47 language hint for transcription."
    )


class TranscriptionResponse(BaseModel):
    """Response containing the transcript text."""

    text: str = Field(..., description="Raw transcription from the STT model.")


class TemplateInferenceRequest(BaseModel):
    """Payload to infer the best template from a transcript."""

    transcript: str = Field(..., description="Human readable transcript.")


class TemplateInferenceResponse(BaseModel):
    """Response describing the selected template and extracted placeholder fields."""

    template_type: str = Field(..., description="One of the supported template names.")
    fields: Dict[str, str] = Field(
        default_factory=dict, description="Key/value pairs editable by the user."
    )


class ReportGenerationRequest(BaseModel):
    """Request body for generating a final textual report."""

    template_type: str = Field(..., description="Template to fill.")
    fields: Dict[str, str] = Field(..., description="Structured inputs for the template.")
    transcript: Optional[str] = Field(
        default=None, description="Optional transcript for additional context."
    )


class ReportGenerationResponse(BaseModel):
    """Response for report generation."""

    report_text: str = Field(..., description="Plaintext report summary.")


class AutoPipelineRequest(TranscriptionRequest):
    """Request body for the fully automated workflow."""

    autopilot: bool = Field(
        default=True,
        description="Marker used by the frontend to indicate no human validation.",
    )


class AutoPipelineResponse(BaseModel):
    """Aggregated response for the automated workflow."""

    text: str
    template_type: str
    fields: Dict[str, str]
    report_text: str

