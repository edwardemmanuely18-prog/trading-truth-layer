from __future__ import annotations

from app.services.performance.member_models import (
    MemberPerformanceMetrics,
)


def build_member_performance_metrics(
    **kwargs,
) -> MemberPerformanceMetrics:
    """
    Projects already-computed analytics into
    the canonical MemberPerformanceMetrics
    contract.

    Performs no calculations.
    """

    return MemberPerformanceMetrics(
        **kwargs,
    )