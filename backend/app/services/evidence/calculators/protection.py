from __future__ import annotations

"""
Trade Evidence System (TES)

Protection Calculator

Determines institutional evidence protection.

Pure computation.

No SQL.

No database access.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ProtectionMetrics:

    fingerprinted: int

    hash_protected: int

    unprotected: int

    protection: float


def compute_protection(
    *,
    total_records: int,
    fingerprinted: int,
    hash_protected: int,
) -> ProtectionMetrics:

    protected = (
        fingerprinted +
        hash_protected
    )

    protection = (
        round(
            (
                protected /
                total_records
            ) * 100,
            2,
        )
        if total_records
        else 0.0
    )

    unprotected = max(

        total_records -
        protected,

        0,

    )

    return ProtectionMetrics(

        fingerprinted=fingerprinted,

        hash_protected=hash_protected,

        unprotected=unprotected,

        protection=protection,

    )