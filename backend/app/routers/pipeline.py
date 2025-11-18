"""REST endpoints driving the transcription → template → report workflow."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from ..core.config import get_settings
from ..models.schemas import (
    AutoPipelineRequest,
    AutoPipelineResponse,
    DocxDownloadRequest,
    ReportGenerationRequest,
    ReportGenerationResponse,
    TemplateInferenceRequest,
    TemplateInferenceResponse,
    TranscriptionRequest,
    TranscriptionResponse,
)
from ..services.docx_generator import generate_incident_docx
from ..services.report import generate_report
from ..services.stt import transcribe_audio
from ..services.template import infer_template

router = APIRouter(prefix="/api", tags=["workflow"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(payload: TranscriptionRequest) -> TranscriptionResponse:
    """Turn the base64 audio sent by Streamlit into text."""

    text = await transcribe_audio(payload.audio_b64, payload.language)
    return TranscriptionResponse(text=text)


@router.post("/report/template", response_model=TemplateInferenceResponse)
async def infer_template_route(
    payload: TemplateInferenceRequest,
) -> TemplateInferenceResponse:
    """Pick the proper template and seed values based on the transcript."""

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
    """Build the formatted report once the fields look good."""

    if not payload.fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required to build the report.",
        )

    report_text = generate_report(payload.template_type, payload.fields, payload.transcript)
    return ReportGenerationResponse(report_text=report_text)


@router.post("/pipeline/auto", response_model=AutoPipelineResponse)
async def auto_pipeline(payload: AutoPipelineRequest) -> AutoPipelineResponse:
    """Run transcription, inference, and report in one go."""

    text = await transcribe_audio(payload.audio_b64, payload.language)
    template, fields = await infer_template(text)
    report_text = generate_report(template, fields, text)
    return AutoPipelineResponse(
        text=text, template_type=template, fields=fields, report_text=report_text
    )


@router.post("/report/download/docx")
async def download_docx(payload: DocxDownloadRequest) -> StreamingResponse:
    """Generate and download a DOCX report from the template."""

    if not payload.fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field is required to generate the DOCX.",
        )

    # Get template path
    settings = get_settings()
    template_path = Path(__file__).resolve().parents[2] / "app" / "assets" / "Template_incident.docx"

    if not template_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template not found at {template_path}",
        )

    # Generate DOCX bytes
    try:
        docx_bytes = generate_incident_docx(payload.fields, template_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX: {str(e)}",
        )

    # Return as downloadable file
    from io import BytesIO
    buffer = BytesIO(docx_bytes)
    buffer.seek(0)

    filename = f"rapport_incident_{payload.fields.get('Date de découverte', 'sans_date').replace('/', '-')}.docx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
