"""Typed data structures used by the audit engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Policy = Literal["prospective", "strain-holdout", "pair-holdout", "cold-both"]
Severity = Literal["error", "warning", "info"]
Outcome = Literal["PASS", "WARN", "FAIL"]


@dataclass(frozen=True)
class ColumnSpec:
    """Column names expected in an input pair table."""

    split: str = "split"
    virus_id: str = "virus_id"
    antiserum_id: str = "antiserum_id"
    virus_year: str = "virus_year"
    antiserum_year: str = "antiserum_year"
    observed: str = "observed"
    predicted: str = "predicted"

    def required(self) -> tuple[str, ...]:
        """Return required columns in their canonical order."""
        return (
            self.split,
            self.virus_id,
            self.antiserum_id,
            self.virus_year,
            self.antiserum_year,
            self.observed,
            self.predicted,
        )


@dataclass(frozen=True)
class PairRecord:
    """One measured/predicted virus-antiserum observation."""

    row_number: int
    split: str
    virus_id: str
    antiserum_id: str
    virus_year: int
    antiserum_year: int
    observed: float
    predicted: float

    @property
    def pair(self) -> tuple[str, str]:
        return (self.virus_id, self.antiserum_id)


@dataclass(frozen=True)
class AuditConfig:
    """Policy and label configuration for an audit."""

    policy: Policy = "prospective"
    train_label: str = "train"
    test_label: str = "test"
    validation_label: str = "validation"
    max_examples: int = 10


@dataclass(frozen=True)
class Issue:
    """One audit finding."""

    code: str
    severity: Severity
    message: str
    count: int
    examples: tuple[str, ...] = ()


@dataclass(frozen=True)
class Metrics:
    """Regression metrics for a group of observations."""

    n: int
    mae: float | None
    rmse: float | None
    spearman_rho: float | None


@dataclass
class AuditReport:
    """Complete deterministic audit result."""

    outcome: Outcome
    policy: Policy
    dataset: dict[str, Any]
    temporal: dict[str, Any]
    leakage: dict[str, Any]
    metrics: dict[str, Any]
    issues: list[Issue] = field(default_factory=list)
    schema_version: str = "antigenic-audit-report/v1"
    generated_by: str = "antigenic-audit 0.1.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert the report to JSON-compatible builtins."""
        return {
            "schema_version": self.schema_version,
            "generated_by": self.generated_by,
            "outcome": self.outcome,
            "policy": self.policy,
            "dataset": self.dataset,
            "temporal": self.temporal,
            "leakage": self.leakage,
            "metrics": self.metrics,
            "issues": [asdict(issue) for issue in self.issues],
        }
