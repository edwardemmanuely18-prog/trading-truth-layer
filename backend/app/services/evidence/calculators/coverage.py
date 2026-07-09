from __future__ import annotations

"""
Trade Evidence System (TES)

Coverage Calculator

Determines institutional evidence coverage.

NO database access.

NO SQL.

Pure computation.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class CoverageMetrics:

    broker_verified: int

    verified: int

    self_reported: int

    coverage: float


def compute_coverage(
    *,
    total_records: int,
    broker_verified: int,
    verified: int,
    self_reported: int,
) -> CoverageMetrics:

    coverage = (
        round(
            (
                broker_verified +
                verified
            )
            / total_records
            * 100,
            2,
        )
        if total_records
        else 0.0
    )

    return CoverageMetrics(

        broker_verified=broker_verified,

        verified=verified,

        self_reported=self_reported,

        coverage=coverage,

    )