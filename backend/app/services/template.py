"""Template inference logic based on lightweight keyword heuristics."""

from __future__ import annotations

from typing import Dict, Tuple

from ..core.config import get_settings


def infer_template(transcript: str) -> Tuple[str, Dict[str, str]]:
    """Return a template identifier and stub field values."""

    normalized = transcript.lower()
    settings = get_settings()

    if any(word in normalized for word in ("safety", "incident", "hazard")):
        template = "safety_walk"
        fields = {
            "Site": "Unknown Site",
            "Observation": "No critical issues noted.",
            "Corrective Actions": "Continue standard safety protocol.",
        }
    elif any(word in normalized for word in ("delivery", "material", "equipment")):
        template = "logistics_update"
        fields = {
            "Shipment": "Pending delivery",
            "Materials": "Concrete, rebar",
            "Notes": "Verify inventory upon arrival.",
        }
    else:
        template = settings.default_template
        fields = {
            "Crew Count": "0",
            "Completed Tasks": "Prep work",
            "Roadblocks": "Weather delays",
            "Next Steps": "Resume pour tomorrow morning.",
        }

    return template, fields

