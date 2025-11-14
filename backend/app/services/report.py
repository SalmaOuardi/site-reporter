"""Build human-friendly French reports from the extracted fields."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional


TEMPLATE_HEADERS = {
    "probleme_decouverte": "RAPPORT D'INCIDENT - Problème Découvert",
    "tour_securite": "RAPPORT DE SÉCURITÉ - Tour de Chantier",
    "tache_assignee": "RAPPORT D'AFFECTATION - Tâche Assignée",
    "rapport_generique": "RAPPORT DE CHANTIER - Générique",
}


def generate_report(
    template_type: str, fields: Dict[str, str], transcript: Optional[str] = None
) -> str:
    """Assemble a French report body from the selected template and data."""

    header = TEMPLATE_HEADERS.get(
        template_type, f"RAPPORT DE CHANTIER - {template_type.upper()}"
    )

    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y à %H:%M")

    lines = [
        "=" * 60,
        header,
        "=" * 60,
        f"Généré le: {timestamp}",
        "",
        "─" * 60,
        "DÉTAILS DU RAPPORT",
        "─" * 60,
        "",
    ]

    for key, value in fields.items():
        field_value = value if value else "Non renseigné"
        lines.append(f"▪ {key}: {field_value}")

    if transcript:
        lines.extend(
            [
                "",
                "─" * 60,
                "TRANSCRIPTION AUDIO",
                "─" * 60,
                "",
                f"{transcript}",
                "",
            ]
        )

    lines.extend(
        [
            "",
            "─" * 60,
            "Rapport généré automatiquement par Site Reporter MVP",
            "Note: La génération PDF sera ajoutée prochainement",
            "─" * 60,
        ]
    )

    return "\n".join(lines)
