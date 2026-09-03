"""Policy behavior and report structure tests."""

from __future__ import annotations

from typing import cast

import pytest

from antigenic_audit.audit import audit_records
from antigenic_audit.models import AuditConfig, PairRecord, Policy
from tests.conftest import record


def clean_records() -> list[PairRecord]:
    """A forward split with novel targets and known reference antisera."""
    return [
        record(2, "train", "v1", "s1", 2000, 1999, 1.0, 1.1),
        record(3, "train", "v2", "s2", 2001, 2000, 2.0, 1.9),
        record(4, "test", "v3", "s1", 2002, 1999, 3.0, 2.8),
        record(5, "test", "v4", "s2", 2003, 2000, 4.0, 4.2),
    ]


def test_prospective_clean_split_passes() -> None:
    report = audit_records(clean_records())
    assert report.outcome == "PASS"
    assert report.temporal["test_minus_development_boundary_years"] == 1
    assert report.leakage["test_antiserum_in_development_antiserum"] == ["s1", "s2"]
    assert [finding.severity for finding in report.issues] == ["info"]


def test_target_and_time_leakage_fail() -> None:
    rows = clean_records()
    rows[-1] = record(5, "test", "v2", "s2", 2001, 2000, 4.0, 4.2)
    report = audit_records(rows)
    codes = {finding.code for finding in report.issues}
    assert report.outcome == "FAIL"
    assert "EXACT_PAIR_OVERLAP" in codes
    assert "TEST_VIRUS_IN_DEVELOPMENT_TARGET" in codes
    assert "NON_FORWARD_TIME_SPLIT" in codes


def test_cross_role_target_leak_fails() -> None:
    rows = clean_records()
    rows[-1] = record(5, "test", "s1", "s2", 2003, 2000, 4.0, 4.2)
    report = audit_records(rows, AuditConfig(policy="strain-holdout"))
    assert report.outcome == "FAIL"
    assert "TEST_VIRUS_IN_DEVELOPMENT_ANTISERUM" in {finding.code for finding in report.issues}


def test_pair_holdout_permits_entity_reuse() -> None:
    rows = clean_records()
    rows[-1] = record(5, "test", "v1", "s2", 2003, 2000, 4.0, 4.2)
    report = audit_records(rows, AuditConfig(policy="pair-holdout"))
    assert report.outcome == "PASS"
    assert "TEST_VIRUS_REUSED" in {finding.code for finding in report.issues}


def test_cold_both_rejects_known_antiserum() -> None:
    report = audit_records(clean_records(), AuditConfig(policy="cold-both"))
    assert report.outcome == "FAIL"
    assert "TEST_ANTISERUM_IN_DEVELOPMENT" in {finding.code for finding in report.issues}


def test_validation_is_treated_as_development_data() -> None:
    rows = clean_records()
    rows.insert(2, record(4, "validation", "v3", "s2", 2002, 2000, 3.0, 3.1))
    report = audit_records(rows)
    assert report.outcome == "FAIL"
    assert "TEST_VIRUS_IN_DEVELOPMENT_TARGET" in {finding.code for finding in report.issues}
    assert report.dataset["development_records"] == 3


def test_duplicate_test_pair_warns() -> None:
    rows = clean_records()
    rows.append(record(6, "test", "v3", "s1", 2002, 1999, 3.2, 2.9))
    report = audit_records(rows)
    assert report.outcome == "WARN"
    assert "DUPLICATE_TEST_PAIR" in {finding.code for finding in report.issues}


def test_future_antiserum_warns_under_prospective_policy() -> None:
    rows = clean_records()
    rows[-1] = record(5, "test", "v4", "s_future", 2003, 2004, 4.0, 4.2)
    report = audit_records(rows)
    assert report.outcome == "WARN"
    assert report.temporal["test_future_antiserum_pairs"] == 1


def test_nonprospective_future_antiserum_is_informational() -> None:
    rows = clean_records()
    rows[-1] = record(5, "test", "v4", "s_future", 2003, 2004, 4.0, 4.2)
    report = audit_records(rows, AuditConfig(policy="strain-holdout"))
    assert report.outcome == "PASS"
    finding = next(item for item in report.issues if item.code == "FUTURE_ANTISERUM")
    assert finding.severity == "info"


def test_cross_role_antiserum_leak_fails_for_cold_both() -> None:
    rows = clean_records()
    rows[-1] = record(5, "test", "v4", "v1", 2003, 2000, 4.0, 4.2)
    report = audit_records(rows, AuditConfig(policy="cold-both"))
    finding = next(item for item in report.issues if item.code == "TEST_ANTISERUM_IN_DEVELOPMENT")
    assert "v1" in finding.examples


@pytest.mark.parametrize(
    "config",
    [
        AuditConfig(max_examples=0),
        AuditConfig(train_label="same", validation_label="validation", test_label="same"),
        AuditConfig(train_label="", validation_label="validation", test_label="test"),
        AuditConfig(train_label=" train", validation_label="validation", test_label="test"),
        AuditConfig(policy=cast(Policy, "unknown")),
    ],
)
def test_invalid_config_is_rejected(config: AuditConfig) -> None:
    with pytest.raises(ValueError):
        audit_records(clean_records(), config)


@pytest.mark.parametrize("missing", ["train", "test"])
def test_required_split_must_exist(missing: str) -> None:
    rows = [row for row in clean_records() if row.split != missing]
    with pytest.raises(ValueError, match=f"no records use the {missing}ing split|no records use"):
        audit_records(rows)
