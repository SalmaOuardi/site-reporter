"""Extract incident template fields from the transcript using the LLM."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

from .llm import chat_completion

INCIDENT_TEMPLATE_TYPE = "probleme_decouverte"
INCIDENT_FIELD_SCHEMA: Dict[str, str] = {
    "Nom du chantier": "nom du chantier ou projet si mentionné",
    "Nom de l'incident": "titre ou nom court de l'incident",
    "Emetteur du signalement": "nom de la personne qui signale l'incident",
    "Date de découverte": "date de découverte de l'incident (format JJ/MM/AAAA)",
    "Heure de découverte": "heure de découverte de l'incident (format HH:MM)",
    "Adresse": "adresse ou localisation précise de l'incident",
    "Nature de l'incident": "type ou catégorie de l'incident (électricité, plomberie, structure, etc.)",
    "Description de l'incident": "description détaillée de l'incident observé",
    "Risques identifiés": "risques potentiels liés à cet incident",
    "Actions à réaliser": "actions correctives ou mesures à prendre",
    "Niveau d'urgence": "niveau d'urgence (Faible/Moyen/Élevé/Critique)",
    "Personnes prévenues": "liste des personnes ou services informés",
}


def _extract_year_from_transcript(transcript: str) -> Optional[int]:
    """Return the latest 4-digit year mentioned in the transcript, if any."""

    matches = re.findall(r"\b(20\d{2})\b", transcript)
    if not matches:
        return None

    try:
        return int(matches[-1])
    except ValueError:
        return None


def _normalize_date_field(transcript: str, date_str: str, now: datetime) -> str:
    """Favor the transcript's year (or current year) when none is spoken."""

    if not date_str:
        return date_str

    parts = date_str.strip().split("/")
    if len(parts) != 3:
        return date_str

    try:
        day, month, year = (int(part) for part in parts)
    except ValueError:
        return date_str

    transcript_year = _extract_year_from_transcript(transcript)
    target_year = transcript_year or now.year

    if year != target_year:
        try:
            normalized = datetime(target_year, month, day)
        except ValueError:
            return date_str
        return normalized.strftime("%d/%m/%Y")

    return date_str


async def infer_template(transcript: str) -> Tuple[str, Dict[str, str]]:
    """Fill the single incident template with values extracted from the transcript."""

    template = INCIDENT_TEMPLATE_TYPE
    field_schema = INCIDENT_FIELD_SCHEMA.copy()

    system_prompt = """Tu es un assistant IA spécialisé dans l'extraction d'informations de rapports de chantier en français.
Tu dois extraire les informations pertinentes d'une transcription audio et les structurer selon un schéma donné.

Règles importantes:
- Extrais uniquement les informations explicitement mentionnées dans la transcription
- Si une information n'est pas mentionnée, laisse le champ vide
- Pour les dates, utilise le format JJ/MM/AAAA
- Sois précis et factuel
- Réponds UNIQUEMENT avec un objet JSON valide, sans texte additionnel"""

    user_prompt = f"""Transcription audio:
{transcript}

Schéma des champs à extraire:
{json.dumps(field_schema, ensure_ascii=False, indent=2)}

Extrais les informations de la transcription et retourne un objet JSON avec ces champs.
Pour chaque champ, extrais la valeur appropriée de la transcription.
Si une valeur n'est pas mentionnée, mets une chaîne vide "".

Réponds UNIQUEMENT avec l'objet JSON, sans markdown ni texte additionnel."""

    try:
        llm_response = await chat_completion(
            prompt=user_prompt,
            system_message=system_prompt,
            temperature=0.1,  # keep answers grounded
            max_tokens=1000,
        )

        cleaned_response = llm_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        fields = json.loads(cleaned_response)

        for field_name in field_schema.keys():
            if field_name not in fields:
                fields[field_name] = ""

    except Exception as e:
        print(f"LLM extraction failed: {e}, using empty fields")
        fields = {field_name: "" for field_name in field_schema.keys()}

    # Auto-fill date and time if not mentioned (for all templates)
    now = datetime.now()

    if "Date de découverte" in fields and fields["Date de découverte"]:
        fields["Date de découverte"] = _normalize_date_field(
            transcript, fields["Date de découverte"], now
        )

    if "Date" in fields and fields["Date"]:
        fields["Date"] = _normalize_date_field(transcript, fields["Date"], now)

    if "Date de découverte" in fields and not fields["Date de découverte"]:
        fields["Date de découverte"] = now.strftime("%d/%m/%Y")

    if "Heure de découverte" in fields and not fields["Heure de découverte"]:
        fields["Heure de découverte"] = now.strftime("%H:%M")

    if not fields.get("Nom du chantier"):
        fields["Nom du chantier"] = "Y154.2433150000 – BEX Lucien Faure / Bd Daney"

    if not fields.get("Emetteur du signalement"):
        fields["Emetteur du signalement"] = "Valentin ALLANT"

    if not fields.get("Adresse"):
        fields["Adresse"] = "91 rue Lucien Faure 33000 Bordeaux"

    if not fields.get("Niveau d'urgence"):
        fields["Niveau d'urgence"] = "Haute"

    if not fields.get("Personnes prévenues"):
        fields["Personnes prévenues"] = "Arthur Brunet"

    if "Date" in fields and not fields["Date"]:
        fields["Date"] = now.strftime("%d/%m/%Y")

    if "Heure" in fields and not fields["Heure"]:
        fields["Heure"] = now.strftime("%H:%M")

    return template, fields
