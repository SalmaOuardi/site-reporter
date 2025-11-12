"""Génération de rapports de chantier en français."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional


# Template headers in French
TEMPLATE_HEADERS = {
    "probleme_decouverte": "RAPPORT D'INCIDENT - Problème Découvert",
    "tour_securite": "RAPPORT DE SÉCURITÉ - Tour de Chantier",
    "tache_assignee": "RAPPORT D'AFFECTATION - Tâche Assignée",
    "rapport_generique": "RAPPORT DE CHANTIER - Générique",
}


def generate_report(
    template_type: str, fields: Dict[str, str], transcript: Optional[str] = None
) -> str:
    """
    Créer un rapport de chantier en français.

    Args:
        template_type: Type de template (probleme_decouverte, tour_securite, etc.)
        fields: Dictionnaire des champs du rapport
        transcript: Transcription audio optionnelle

    Returns:
        Rapport formaté en texte
    """

    # Get French header for template
    header = TEMPLATE_HEADERS.get(
        template_type, f"RAPPORT DE CHANTIER - {template_type.upper()}"
    )

    # Format timestamp in French
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

    # Add all fields
    for key, value in fields.items():
        # Format the field nicely
        field_value = value if value else "Non renseigné"
        lines.append(f"▪ {key}: {field_value}")

    # Add transcript if available
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

    # Footer
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

