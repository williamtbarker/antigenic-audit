"""Role-aware leakage and temporal audit engine."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Any

from antigenic_audit.metrics import compute_metrics
from antigenic_audit.models import (
    AuditConfig,
    AuditReport,
    Issue,
    Outcome,
    PairRecord,
    Severity,
)


def _format_pair(pair: tuple[str, str]) -> str:
    return f"{pair[0]} × {pair[1]}"


def _examples(values: set[str] | set[tuple[str, str]], limit: int) -> tuple[str, ...]:
    rendered = [value if isinstance(value, str) else _format_pair(value) for value in values]
    return tuple(sorted(rendered)[:limit])


def _year_range(records: list[PairRecord], attribute: str) -> list[int] | None:
    years = [int(getattr(record, attribute)) for record in records]
    return [min(years), max(years)] if years else None


def _metric_dict(records: list[PairRecord]) -> dict[str, Any]:
    raw = asdict(compute_metrics(records))
    return {
        key: round(value, 12) if isinstance(value, float) else value for key, value in raw.items()
    }


def _metrics_by_test_year(records: list[PairRecord]) -> dict[str, dict[str, Any]]:
    grouped: dict[int, list[PairRecord]] = defaultdict(list)
    for record in records:
        grouped[record.virus_year].append(record)
    return {str(year): _metric_dict(grouped[year]) for year in sorted(grouped)}


def _lag_bin(record: PairRecord) -> str:
    lag = record.virus_year - record.antiserum_year
    if lag < 0:
        return "future-antiserum"
    if lag == 0:
        return "0"
    if lag <= 2:
        return "1-2"
    if lag <= 5:
        return "3-5"
    if lag <= 10:
        return "6-10"
    return ">10"


def _metrics_by_lag(records: list[PairRecord]) -> dict[str, dict[str, Any]]:
    order = ("future-antiserum", "0", "1-2", "3-5", "6-10", ">10")
    grouped: dict[str, list[PairRecord]] = defaultdict(list)
    for record in records:
        grouped[_lag_bin(record)].append(record)
    return {label: _metric_dict(grouped[label]) for label in order if label in grouped}


def _issue(
    issues: list[Issue],
    *,
    code: str,
    severity: Severity,
    message: str,
    values: set[str] | set[tuple[str, str]],
    limit: int,
) -> None:
    if values:
        issues.append(
            Issue(
                code=code,
                severity=severity,
                message=message,
                count=len(values),
                examples=_examples(values, limit),
            )
        )


def _duplicate_pairs(records: list[PairRecord]) -> set[tuple[str, str]]:
    counts = Counter(record.pair for record in records)
    return {pair for pair, count in counts.items() if count > 1}


def audit_records(records: list[PairRecord], config: AuditConfig | None = None) -> AuditReport:
    """Audit records under a documented deployment policy."""
    cfg = config or AuditConfig()
    if cfg.policy not in {"prospective", "strain-holdout", "pair-holdout", "cold-both"}:
        raise ValueError(f"unknown audit policy: {cfg.policy!r}")
    if cfg.max_examples < 1:
        raise ValueError("max_examples must be at least 1")
    labels = (cfg.train_label, cfg.validation_label, cfg.test_label)
    if not all(labels):
        raise ValueError("train, validation, and test labels must not be empty")
    if any(label != label.strip() for label in labels):
        raise ValueError("train, validation, and test labels must not contain outer whitespace")
    if len(set(labels)) != len(labels):
        raise ValueError("train, validation, and test labels must be distinct")

    train = [record for record in records if record.split == cfg.train_label]
    validation = [record for record in records if record.split == cfg.validation_label]
    test = [record for record in records if record.split == cfg.test_label]
    if not train:
        raise ValueError(f"no records use the training split label {cfg.train_label!r}")
    if not test:
        raise ValueError(f"no records use the test split label {cfg.test_label!r}")

    development = train + validation
    development_pairs = {record.pair for record in development}
    test_pairs = {record.pair for record in test}
    development_viruses = {record.virus_id for record in development}
    development_antisera = {record.antiserum_id for record in development}
    test_viruses = {record.virus_id for record in test}
    test_antisera = {record.antiserum_id for record in test}

    pair_overlap = development_pairs & test_pairs
    target_overlap = development_viruses & test_viruses
    test_target_seen_as_development_antiserum = test_viruses & development_antisera
    antiserum_overlap = development_antisera & test_antisera
    test_antiserum_seen_as_development_virus = test_antisera & development_viruses
    duplicate_development_pairs = _duplicate_pairs(development)
    duplicate_test_pairs = _duplicate_pairs(test)
    future_antiserum_pairs = {
        record.pair for record in test if record.antiserum_year > record.virus_year
    }

    issues: list[Issue] = []
    limit = cfg.max_examples
    _issue(
        issues,
        code="EXACT_PAIR_OVERLAP",
        severity="error",
        message="Exact virus-antiserum pairs occur in both development and test data.",
        values=pair_overlap,
        limit=limit,
    )

    if cfg.policy in {"prospective", "strain-holdout", "cold-both"}:
        _issue(
            issues,
            code="TEST_VIRUS_IN_DEVELOPMENT_TARGET",
            severity="error",
            message="Test viruses also occur as development target viruses.",
            values=target_overlap,
            limit=limit,
        )
        _issue(
            issues,
            code="TEST_VIRUS_IN_DEVELOPMENT_ANTISERUM",
            severity="error",
            message="Test viruses occur in the development data's antiserum role.",
            values=test_target_seen_as_development_antiserum,
            limit=limit,
        )
    else:
        _issue(
            issues,
            code="TEST_VIRUS_REUSED",
            severity="info",
            message="Test viruses occur somewhere in development; pair-holdout permits this.",
            values=target_overlap | test_target_seen_as_development_antiserum,
            limit=limit,
        )

    if cfg.policy == "cold-both":
        _issue(
            issues,
            code="TEST_ANTISERUM_IN_DEVELOPMENT",
            severity="error",
            message="Cold-both evaluation forbids test antisera from appearing in development.",
            values=antiserum_overlap | test_antiserum_seen_as_development_virus,
            limit=limit,
        )
    else:
        _issue(
            issues,
            code="KNOWN_TEST_ANTISERUM",
            severity="info",
            message=(
                "Test antisera also occur in development; this is expected for known-sera "
                "deployment."
            ),
            values=antiserum_overlap,
            limit=limit,
        )
        _issue(
            issues,
            code="TEST_ANTISERUM_SEEN_AS_DEVELOPMENT_VIRUS",
            severity="info",
            message="Test antisera occur as development target viruses.",
            values=test_antiserum_seen_as_development_virus,
            limit=limit,
        )

    _issue(
        issues,
        code="DUPLICATE_TEST_PAIR",
        severity="warning",
        message="Repeated test pairs can overweight selected relationships in aggregate metrics.",
        values=duplicate_test_pairs,
        limit=limit,
    )
    _issue(
        issues,
        code="DUPLICATE_DEVELOPMENT_PAIR",
        severity="info",
        message="Repeated development pairs may be intentional assay replicates.",
        values=duplicate_development_pairs,
        limit=limit,
    )
    _issue(
        issues,
        code="FUTURE_ANTISERUM",
        severity="warning" if cfg.policy == "prospective" else "info",
        message="Some test rows pair a virus with an antiserum strain from a later year.",
        values=future_antiserum_pairs,
        limit=limit,
    )

    development_target_range = _year_range(development, "virus_year")
    test_target_range = _year_range(test, "virus_year")
    assert development_target_range is not None
    assert test_target_range is not None
    temporal_gap = test_target_range[0] - development_target_range[1]
    if cfg.policy == "prospective" and temporal_gap <= 0:
        issues.append(
            Issue(
                code="NON_FORWARD_TIME_SPLIT",
                severity="error",
                message=(
                    "Prospective policy requires every test-virus year to follow every "
                    "development-virus year."
                ),
                count=sum(record.virus_year <= development_target_range[1] for record in test),
                examples=(
                    f"latest development={development_target_range[1]}",
                    f"earliest test={test_target_range[0]}",
                ),
            )
        )

    severity_order = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda item: (severity_order[item.severity], item.code))
    if any(issue.severity == "error" for issue in issues):
        outcome: Outcome = "FAIL"
    elif any(issue.severity == "warning" for issue in issues):
        outcome = "WARN"
    else:
        outcome = "PASS"

    return AuditReport(
        outcome=outcome,
        policy=cfg.policy,
        dataset={
            "records": len(records),
            "train_records": len(train),
            "validation_records": len(validation),
            "development_records": len(development),
            "test_records": len(test),
            "development_unique_viruses": len(development_viruses),
            "test_unique_viruses": len(test_viruses),
            "development_unique_antisera": len(development_antisera),
            "test_unique_antisera": len(test_antisera),
        },
        temporal={
            "development_virus_year_range": development_target_range,
            "test_virus_year_range": test_target_range,
            "test_minus_development_boundary_years": temporal_gap,
            "test_future_antiserum_pairs": len(future_antiserum_pairs),
        },
        leakage={
            "exact_pair_overlap": sorted(_format_pair(pair) for pair in pair_overlap),
            "test_virus_in_development_target": sorted(target_overlap),
            "test_virus_in_development_antiserum": sorted(
                test_target_seen_as_development_antiserum
            ),
            "test_antiserum_in_development_antiserum": sorted(antiserum_overlap),
            "test_antiserum_in_development_target": sorted(
                test_antiserum_seen_as_development_virus
            ),
            "duplicate_development_pairs": sorted(
                _format_pair(pair) for pair in duplicate_development_pairs
            ),
            "duplicate_test_pairs": sorted(_format_pair(pair) for pair in duplicate_test_pairs),
        },
        metrics={
            "train": _metric_dict(train),
            "validation": _metric_dict(validation),
            "development": _metric_dict(development),
            "test": _metric_dict(test),
            "test_by_virus_year": _metrics_by_test_year(test),
            "test_by_virus_antiserum_lag_years": _metrics_by_lag(test),
        },
        issues=issues,
    )
