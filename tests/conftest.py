"""Shared synthetic antigenicity fixtures."""

from __future__ import annotations

from antigenic_audit.models import PairRecord


def record(
    row: int,
    split: str,
    virus: str,
    antiserum: str,
    virus_year: int,
    antiserum_year: int,
    observed: float,
    predicted: float,
) -> PairRecord:
    """Construct a compact typed test record."""
    return PairRecord(
        row_number=row,
        split=split,
        virus_id=virus,
        antiserum_id=antiserum,
        virus_year=virus_year,
        antiserum_year=antiserum_year,
        observed=observed,
        predicted=predicted,
    )
