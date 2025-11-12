"""Report generation helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional


def generate_report(
    template_type: str, fields: Dict[str, str], transcript: Optional[str] = None
) -> str:
    """Create a plaintext report using the inferred template structure."""

    header = f"Construction Report · {template_type.replace('_', ' ').title()}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        header,
        f"Generated: {timestamp}",
        "",
        "Key Details:",
    ]

    for key, value in fields.items():
        lines.append(f"  - {key}: {value}")

    if transcript:
        lines.extend(
            [
                "",
                "Transcript Snapshot:",
                f"{transcript[:400]}{'...' if len(transcript) > 400 else ''}",
            ]
        )

    lines.append("")
    lines.append("This is a placeholder output. Replace with PDF generation later.")

    return "\n".join(lines)

