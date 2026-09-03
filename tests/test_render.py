"""Stable human- and machine-readable report tests."""

from __future__ import annotations

import json
from pathlib import Path

from antigenic_audit.audit import audit_records
from antigenic_audit.io import load_records
from antigenic_audit.render import render_json, render_markdown
from tests.conftest import record
from tests.test_audit import clean_records


def test_json_is_stable_and_parseable() -> None:
    report = audit_records(clean_records())
    rendered = render_json(report)
    assert rendered.endswith("\n")
    parsed = json.loads(rendered)
    assert parsed["schema_version"] == "antigenic-audit-report/v1"
    assert parsed["outcome"] == "PASS"
    assert "000000000000000" not in rendered


def test_markdown_contains_decision_information() -> None:
    rendered = render_markdown(audit_records(clean_records()))
    assert "**Outcome:** `PASS`" in rendered
    assert "## Temporal boundary" in rendered
    assert "| Test | 2 |" in rendered
    assert "KNOWN_TEST_ANTISERUM" in rendered
    assert "does not establish biological validity" in rendered


def test_markdown_handles_report_without_findings() -> None:
    rows = [
        record(2, "train", "v1", "s1", 2000, 1999, 1.0, 1.0),
        record(3, "test", "v2", "s2", 2002, 2001, 2.0, 2.0),
    ]
    rendered = render_markdown(audit_records(rows))
    assert "No findings." in rendered
    assert "| Validation | 0 | NA | NA | NA |" in rendered


def test_checked_in_example_reports_are_current() -> None:
    examples = Path(__file__).parents[1] / "examples"
    clean = audit_records(load_records(examples / "clean_pairs.csv"))
    leaky = audit_records(load_records(examples / "leaky_pairs.csv"))
    assert (examples / "clean_report.md").read_text(encoding="utf-8") == render_markdown(clean)
    assert (examples / "leaky_report.json").read_text(encoding="utf-8") == render_json(leaky)
