"""Small dependency-free regression metric implementations."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from antigenic_audit.models import Metrics, PairRecord


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values)


def _rank(values: Sequence[float]) -> list[float]:
    """Return one-based average ranks with deterministic tie handling."""
    indexed = sorted(enumerate(values), key=lambda pair: pair[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(indexed):
        end = start + 1
        while end < len(indexed) and indexed[end][1] == indexed[start][1]:
            end += 1
        average_rank = ((start + 1) + end) / 2.0
        for position in range(start, end):
            ranks[indexed[position][0]] = average_rank
        start = end
    return ranks


def _pearson(left: Sequence[float], right: Sequence[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean = _mean(left)
    right_mean = _mean(right)
    numerator = math.fsum(
        (a - left_mean) * (b - right_mean) for a, b in zip(left, right, strict=True)
    )
    left_ss = math.fsum((value - left_mean) ** 2 for value in left)
    right_ss = math.fsum((value - right_mean) ** 2 for value in right)
    denominator = math.sqrt(left_ss * right_ss)
    if denominator == 0:
        return None
    return numerator / denominator


def compute_metrics(records: Iterable[PairRecord]) -> Metrics:
    """Compute MAE, RMSE, and Spearman rho for records."""
    materialized = list(records)
    if not materialized:
        return Metrics(n=0, mae=None, rmse=None, spearman_rho=None)
    observed = [record.observed for record in materialized]
    predicted = [record.predicted for record in materialized]
    errors = [prediction - truth for truth, prediction in zip(observed, predicted, strict=True)]
    return Metrics(
        n=len(materialized),
        mae=math.fsum(abs(error) for error in errors) / len(errors),
        rmse=math.sqrt(math.fsum(error**2 for error in errors) / len(errors)),
        spearman_rho=_pearson(_rank(observed), _rank(predicted)),
    )
