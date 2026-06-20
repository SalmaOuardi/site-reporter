"""Unit tests for the pure helpers in app.services.template.

These cover the deterministic date/year normalization logic — no Azure
or network access required.
"""

from __future__ import annotations

from datetime import datetime

from app.services.template import (
    _extract_year_from_transcript,
    _normalize_date_field,
)

NOW = datetime(2026, 6, 20)


class TestExtractYear:
    def test_returns_none_when_absent(self) -> None:
        assert _extract_year_from_transcript("rien ici") is None

    def test_returns_last_year_mentioned(self) -> None:
        assert _extract_year_from_transcript("2019 then 2023 then 2021") == 2021

    def test_ignores_non_2000s_numbers(self) -> None:
        assert _extract_year_from_transcript("incident salle 1999 et 2024") == 2024


class TestNormalizeDateField:
    def test_uses_transcript_year_over_spoken(self) -> None:
        assert _normalize_date_field("en 2025", "01/02/2099", NOW) == "01/02/2025"

    def test_falls_back_to_current_year_when_no_transcript_year(self) -> None:
        assert _normalize_date_field("pas d annee", "15/03/2099", NOW) == "15/03/2026"

    def test_leaves_already_correct_date(self) -> None:
        assert _normalize_date_field("en 2025", "10/11/2025", NOW) == "10/11/2025"

    def test_passes_through_empty(self) -> None:
        assert _normalize_date_field("2025", "", NOW) == ""

    def test_passes_through_malformed_date(self) -> None:
        assert _normalize_date_field("2025", "demain", NOW) == "demain"
