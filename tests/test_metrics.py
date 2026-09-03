"""Metric tests, including ties and degenerate inputs."""

from __future__ import annotations

import math

import pytest

from antigenic_audit.metrics import compute_metrics
from tests.conftest import record


def test_metrics_are_correct() -> None:
    rows = [
        record(2, "test", "v1", "s", 2001, 2000, 1.0, 1.0),
        record(3, "test", "v2", "s", 2002, 2000, 2.0, 3.0),
        record(4, "test", "v3", "s", 2003, 2000, 3.0, 2.0),
    ]
    metrics = compute_metrics(rows)
    assert metrics.n == 3
    assert metrics.mae == pytest.approx(2.0 / 3.0)
    assert metrics.rmse == pytest.approx(math.sqrt(2.0 / 3.0))
    assert metrics.spearman_rho == pytest.approx(0.5)


def test_tied_ranks_use_average_rank() -> None:
    rows = [
        record(2, "test", "v1", "s", 2001, 2000, 1.0, 1.0),
        record(3, "test", "v2", "s", 2002, 2000, 1.0, 2.0),
        record(4, "test", "v3", "s", 2003, 2000, 3.0, 3.0),
    ]
    assert compute_metrics(rows).spearman_rho == pytest.approx(math.sqrt(3) / 2)


def test_constant_values_have_undefined_correlation() -> None:
    rows = [
        record(2, "test", "v1", "s", 2001, 2000, 1.0, 4.0),
        record(3, "test", "v2", "s", 2002, 2000, 2.0, 4.0),
    ]
    assert compute_metrics(rows).spearman_rho is None


def test_empty_metrics_are_explicit() -> None:
    metrics = compute_metrics([])
    assert metrics.n == 0
    assert metrics.mae is None
    assert metrics.rmse is None
    assert metrics.spearman_rho is None
