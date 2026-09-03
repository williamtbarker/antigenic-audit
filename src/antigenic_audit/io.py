"""Input parsing with explicit validation and gzip support."""

from __future__ import annotations

import csv
import gzip
import math
from collections.abc import Iterator
from pathlib import Path
from typing import TextIO

from antigenic_audit.models import ColumnSpec, PairRecord


class InputError(ValueError):
    """Raised when an input table cannot be audited safely."""


def _open_text(path: Path) -> TextIO:
    if path.suffix.casefold() == ".gz":
        return gzip.open(path, mode="rt", encoding="utf-8-sig", newline="")
    return path.open(mode="r", encoding="utf-8-sig", newline="")


def _delimiter(path: Path) -> str:
    name = path.name.casefold()
    if name.endswith((".tsv", ".tsv.gz", ".tab", ".tab.gz")):
        return "\t"
    return ","


def _parse_year(value: str, *, field_name: str, row_number: int) -> int:
    try:
        year = int(value)
    except ValueError as exc:
        raise InputError(f"row {row_number}: {field_name} must be an integer year") from exc
    if not 1800 <= year <= 2200:
        raise InputError(f"row {row_number}: {field_name}={year} is outside 1800..2200")
    return year


def _parse_float(value: str, *, field_name: str, row_number: int) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise InputError(f"row {row_number}: {field_name} must be numeric") from exc
    if not math.isfinite(result):
        raise InputError(f"row {row_number}: {field_name} must be finite")
    return result


def _clean_rows(reader: csv.DictReader[str]) -> Iterator[tuple[int, dict[str, str]]]:
    for row_number, raw in enumerate(reader, start=2):
        if None in raw:
            raise InputError(f"row {row_number}: contains more values than the header")
        row = {key.strip(): (value or "").strip() for key, value in raw.items()}
        if not any(row.values()):
            continue
        yield row_number, row


def load_records(
    path: str | Path,
    columns: ColumnSpec | None = None,
    *,
    allowed_splits: set[str] | None = None,
) -> list[PairRecord]:
    """Load and validate CSV/TSV pair records, optionally gzip-compressed."""
    table_path = Path(path)
    spec = columns or ColumnSpec()
    allowed = {"train", "validation", "test"} if allowed_splits is None else allowed_splits

    if not allowed or "" in allowed:
        raise InputError("allowed split labels must be non-empty")
    if any(not name for name in spec.required()):
        raise InputError("column names must be non-empty")
    if len(set(spec.required())) != len(spec.required()):
        raise InputError("required column names must be distinct")

    if not table_path.is_file():
        raise InputError(f"input file does not exist: {table_path}")

    with _open_text(table_path) as handle:
        reader = csv.DictReader(handle, delimiter=_delimiter(table_path), strict=True)
        if reader.fieldnames is None:
            raise InputError("input has no header")
        normalized_header = [field.strip() for field in reader.fieldnames]
        if len(normalized_header) != len(set(normalized_header)):
            raise InputError("input header contains duplicate column names")
        reader.fieldnames = normalized_header
        missing = [name for name in spec.required() if name not in normalized_header]
        if missing:
            raise InputError(f"missing required columns: {', '.join(missing)}")

        records: list[PairRecord] = []
        for row_number, row in _clean_rows(reader):
            split = row[spec.split].casefold()
            if split not in allowed:
                choices = ", ".join(sorted(allowed))
                raise InputError(
                    f"row {row_number}: unknown split {row[spec.split]!r}; expected {choices}"
                )
            virus_id = row[spec.virus_id]
            antiserum_id = row[spec.antiserum_id]
            if not virus_id:
                raise InputError(f"row {row_number}: {spec.virus_id} is empty")
            if not antiserum_id:
                raise InputError(f"row {row_number}: {spec.antiserum_id} is empty")
            records.append(
                PairRecord(
                    row_number=row_number,
                    split=split,
                    virus_id=virus_id,
                    antiserum_id=antiserum_id,
                    virus_year=_parse_year(
                        row[spec.virus_year],
                        field_name=spec.virus_year,
                        row_number=row_number,
                    ),
                    antiserum_year=_parse_year(
                        row[spec.antiserum_year],
                        field_name=spec.antiserum_year,
                        row_number=row_number,
                    ),
                    observed=_parse_float(
                        row[spec.observed], field_name=spec.observed, row_number=row_number
                    ),
                    predicted=_parse_float(
                        row[spec.predicted], field_name=spec.predicted, row_number=row_number
                    ),
                )
            )

    if not records:
        raise InputError("input contains no data records")
    return records
