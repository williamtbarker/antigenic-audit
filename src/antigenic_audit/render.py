"""Stable JSON and Markdown renderers."""

from __future__ import annotations

import json
from typing import Any

from antigenic_audit.models import AuditReport, Metrics


def render_json(report: AuditReport) -> str:
    """Render a stable machine-readable report."""
    return json.dumps(report.to_dict(), allow_nan=False, indent=2, sort_keys=True) + "\n"


def _number(value: float | None) -> str:
    return "NA" if value is None else f"{value:.4f}"


def _metrics_row(label: str, raw: dict[str, Any]) -> str:
    metrics = Metrics(**raw)
    return (
        f"| {label} | {metrics.n} | {_number(metrics.mae)} | "
        f"{_number(metrics.rmse)} | {_number(metrics.spearman_rho)} |"
    )


def render_markdown(report: AuditReport) -> str:
    """Render a concise human-reviewable report."""
    data = report.to_dict()
    dataset = data["dataset"]
    temporal = data["temporal"]
    metrics = data["metrics"]
    lines = [
        "# Antigenic evaluation audit",
        "",
        f"- **Outcome:** `{report.outcome}`",
        f"- **Policy:** `{report.policy}`",
        f"- **Records:** {dataset['records']} "
        f"({dataset['train_records']} train, {dataset['validation_records']} validation, "
        f"{dataset['test_records']} test)",
        "",
        "## Temporal boundary",
        "",
        f"- Development virus years: `{temporal['development_virus_year_range'][0]}`–"
        f"`{temporal['development_virus_year_range'][1]}`",
        f"- Test virus years: `{temporal['test_virus_year_range'][0]}`–"
        f"`{temporal['test_virus_year_range'][1]}`",
        "- Earliest-test minus latest-development boundary: "
        f"`{temporal['test_minus_development_boundary_years']}` years",
        "",
        "## Metrics",
        "",
        "| Group | n | MAE | RMSE | Spearman ρ |",
        "|---|---:|---:|---:|---:|",
        _metrics_row("Train", metrics["train"]),
        _metrics_row("Validation", metrics["validation"]),
        _metrics_row("Development", metrics["development"]),
        _metrics_row("Test", metrics["test"]),
        "",
        "### Test metrics by virus year",
        "",
        "| Virus year | n | MAE | RMSE | Spearman ρ |",
        "|---|---:|---:|---:|---:|",
    ]
    for year, values in metrics["test_by_virus_year"].items():
        lines.append(_metrics_row(year, values))

    lines.extend(
        [
            "",
            "### Test metrics by virus–antiserum lag",
            "",
            "| Lag (years) | n | MAE | RMSE | Spearman ρ |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for lag, values in metrics["test_by_virus_antiserum_lag_years"].items():
        lines.append(_metrics_row(lag, values))

    lines.extend(["", "## Findings", ""])
    if not report.issues:
        lines.append("No findings.")
    else:
        for issue in report.issues:
            lines.append(f"### {issue.severity.upper()} · `{issue.code}` ({issue.count})")
            lines.extend(["", issue.message])
            if issue.examples:
                examples = "; ".join(f"`{item}`" for item in issue.examples)
                lines.extend(["", "Examples: " + examples])
            lines.append("")

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "This report audits table structure, entity reuse, temporal direction, and supplied "
            "predictions. It does not establish biological validity, assay comparability, "
            "sequence independence, or prospective clinical utility.",
            "",
        ]
    )
    return "\n".join(lines)
