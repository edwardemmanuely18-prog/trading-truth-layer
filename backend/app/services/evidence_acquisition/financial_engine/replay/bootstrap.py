"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Financial Infrastructure Engine

Replay Bootstrap

Registers canonical replay datasets.
"""

from __future__ import annotations

from pathlib import Path

from .replay_registry import (
    ReplayDataset,
    replay_registry,
)


# ============================================================================
# Dataset Registration
# ============================================================================


def register_replay_datasets(
    root: Path,
) -> None:
    """
    Register every replay dataset.
    """

    datasets = [

        (
            "MT103",
            "SWIFT MT103 Customer Credit Transfer",
        ),

        (
            "MT202",
            "SWIFT MT202 Financial Institution Transfer",
        ),

        (
            "MT700",
            "SWIFT MT700 Documentary Credit",
        ),

        (
            "MT760",
            "SWIFT MT760 Bank Guarantee",
        ),

        (
            "MT767",
            "SWIFT MT767 Guarantee Amendment",
        ),

        (
            "MT799",
            "SWIFT MT799 Free Format Message",
        ),

        (
            "MT940",
            "SWIFT MT940 Customer Statement",
        ),

        (
            "MX",
            "ISO 20022 Messages",
        ),

    ]

    for name, description in datasets:

        replay_registry.register(

            ReplayDataset(

                name=name,

                path=root / name,

                description=description,

            )

        )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "register_replay_datasets",
]