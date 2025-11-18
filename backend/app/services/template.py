"""Decide which template fits a transcript and have the LLM fill the fields."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, Tuple

from .llm import chat_completion
from ..core.config import get_settings

async def infer_template(transcript: str) -> Tuple[str, Dict[str, str]]:
    """Guess the template from keywords and let the LLM pull field values."""

    normalized = transcript.lower()
    settings = get_settings()

    if any(word in normalized for word in ("problème", "problem", "incident", "souci", "défaillance", "panne", "fuite", "casse")):
        template = "probleme_decouverte"
        field_schema = {
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

    elif any(word in normalized for word in ("tour", "sécurité", "security", "inspection", "vendredi", "friday", "fissure", "béton")):
        template = "tour_securite"
        field_schema = {
            "Date": "date mentionnée (format JJ/MM/AAAA)",
            "Heure": "heure mentionnée si disponible",
            "Opérateur": "nom de la personne si mentionné, sinon 'Marie Martin - Responsable sécurité'",
            "Zone inspectée": "bâtiment, étage, ou zone inspectée",
            "Observations": "résumé des observations principales",
            "Non-conformités": "problèmes détectés ou 'Aucune' si tout va bien",
            "Actions correctives": "actions recommandées pour corriger les non-conformités",
        }

    elif any(word in normalized for word in ("tâche", "task", "assigné", "assigned", "mission", "travail")):
        template = "tache_assignee"
        field_schema = {
            "Date": "date mentionnée (format JJ/MM/AAAA)",
            "Heure": "heure mentionnée si disponible",
            "Opérateur": "nom de la personne qui assigne, sinon 'Pierre Leroy - Coordinateur'",
            "Tâche": "nom ou description de la tâche",
            "Assigné à": "personne ou équipe assignée",
            "Échéance": "date limite si mentionnée",
            "Priorité": "niveau de priorité (Faible/Normale/Élevée/Urgente)",
            "Description": "détails de la tâche",
        }

    else:
        template = "rapport_generique"
        field_schema = {
            "Date": "date mentionnée (format JJ/MM/AAAA)",
            "Heure": "heure mentionnée si disponible",
            "Opérateur": "nom de la personne si mentionné, sinon 'Jean Dupont - Chef de chantier'",
            "Problème": "problème ou situation décrite",
            "Domaine": "zone ou domaine concerné",
            "Urgence": "niveau d'urgence estimé",
            "Plan d'action": "actions à prendre",
        }

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
        if "Opérateur" in fields and not fields["Opérateur"]:
            if template == "tour_securite":
                fields["Opérateur"] = "Salma OUARDI - Responsable sécurité"
            elif template == "tache_assignee":
                fields["Opérateur"] = "Pierre Leroy - Coordinateur"
            else:
                fields["Opérateur"] = "Jean Dupont - Chef de chantier"

    # Auto-fill date and time if not mentioned (for all templates)
    now = datetime.now()

    if "Date de découverte" in fields and not fields["Date de découverte"]:
        fields["Date de découverte"] = now.strftime("%d/%m/%Y")

    if "Heure de découverte" in fields and not fields["Heure de découverte"]:
        fields["Heure de découverte"] = now.strftime("%H:%M")

    if "Date" in fields and not fields["Date"]:
        fields["Date"] = now.strftime("%d/%m/%Y")

    if "Heure" in fields and not fields["Heure"]:
        fields["Heure"] = now.strftime("%H:%M")

    return template, fields
