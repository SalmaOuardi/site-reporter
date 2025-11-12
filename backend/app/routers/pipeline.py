"""Workflow endpoints for transcription, template inference, and report generation."""

from fastapi import APIRouter, HTTPException, status

from ..models.schemas import (
    AutoPipelineRequest,
    AutoPipelineResponse,
    ReportGenerationRequest,
    ReportGenerationResponse,
    TemplateInferenceRequest,
    TemplateInferenceResponse,
    TranscriptionRequest,
    TranscriptionResponse,
)
from ..services.report import generate_report
from ..services.stt import transcribe_audio
from ..services.template import infer_template

router = APIRouter(prefix="/api", tags=["workflow"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(payload: TranscriptionRequest) -> TranscriptionResponse:
    """Transcribe a base64 audio payload."""

    text = await transcribe_audio(payload.audio_b64, payload.language)
    return TranscriptionResponse(text=text)


@router.post("/report/template", response_model=TemplateInferenceResponse)
async def infer_template_route(
    payload: TemplateInferenceRequest,
) -> TemplateInferenceResponse:
    """Infer a report template from the transcript text."""

    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transcript cannot be empty.",
        )

    template, fields = await infer_template(transcript)
    return TemplateInferenceResponse(template_type=template, fields=fields)


@router.post("/report/generate", response_model=ReportGenerationResponse)
async def generate_report_route(
    payload: ReportGenerationRequest,
) -> ReportGenerationResponse:
    """Generate the final textual report."""

    if not payload.fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required to build the report.",
        )

    report_text = generate_report(payload.template_type, payload.fields, payload.transcript)
    return ReportGenerationResponse(report_text=report_text)


@router.post("/pipeline/auto", response_model=AutoPipelineResponse)
async def auto_pipeline(payload: AutoPipelineRequest) -> AutoPipelineResponse:
    """Run the full workflow without human intervention."""

    text = await transcribe_audio(payload.audio_b64, payload.language)
    template, fields = await infer_template(text)
    report_text = generate_report(template, fields, text)
    return AutoPipelineResponse(
        text=text, template_type=template, fields=fields, report_text=report_text
    )

