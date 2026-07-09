from __future__ import annotations

"""
Trade Evidence System (TES)

Quality Calculator

Computes the institutional quality profile
for workspace evidence.

Pure computation.

No SQL.

No database access.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class QualityMetrics:

    verification_quality: float

    protection_quality: float

    completeness_quality: float

    import_quality: float

    score: float

    band: str


def compute_quality(
    *,
    total_records: int,
    coverage: float,
    reliability: float,
    protection: float,
    tier3: int,
    unprotected: int,
    exception_count: int,
) -> QualityMetrics:

    score = 100.0

    if total_records:

        score -= min(
            25,
            round(
                (tier3 / total_records) * 25,
            ),
        )

        score -= min(
            25,
            round(
                (
                    unprotected /
                    total_records
                ) * 25,
            ),
        )

    score = max(
        score,
        0,
    )

    completeness = (
        round(
            (
                (
                    total_records -
                    exception_count
                )
                / total_records
            ) * 100,
            2,
        )
        if total_records
        else 0.0
    )

    if score >= 90:

        band = "EXCELLENT"

    elif score >= 75:

        band = "GOOD"

    elif score >= 60:

        band = "MONITORING"

    else:

        band = "POOR"

    return QualityMetrics(

        verification_quality=coverage,

        protection_quality=protection,

        completeness_quality=completeness,

        import_quality=reliability,

        score=score,

        band=band,

    )