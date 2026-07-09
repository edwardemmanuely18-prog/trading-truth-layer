from __future__ import annotations

"""
Trade Evidence System (TES)

Tier Calculator

Canonical evidence provenance aggregation.

Pure computation.

No SQL.

No database access.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class TierMetrics:

    tier1: int

    tier2: int

    tier3: int

    reliability: float


def compute_tiers(
    *,
    total_records: int,
    tier1: int,
    tier2: int,
    tier3: int,
) -> TierMetrics:

    reliability = (
        round(
            tier1 / total_records * 100,
            2,
        )
        if total_records
        else 0.0
    )

    return TierMetrics(

        tier1=tier1,

        tier2=tier2,

        tier3=tier3,

        reliability=reliability,

    )