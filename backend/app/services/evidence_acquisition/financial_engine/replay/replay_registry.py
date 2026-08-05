"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Financial Infrastructure Engine

Replay Registry

Canonical registry for Financial Engine replay datasets.
"""

from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path

from typing import Dict
from typing import List
from typing import Optional


# ============================================================================
# Replay Dataset Descriptor
# ============================================================================


@dataclass(slots=True)
class ReplayDataset:
    """
    Describes a replay dataset.
    """

    name: str

    path: Path

    description: str = ""

    enabled: bool = True


# ============================================================================
# Replay Registry
# ============================================================================


class ReplayRegistry:
    """
    Registry of replay datasets.
    """

    def __init__(
        self,
    ) -> None:

        self._datasets: Dict[
            str,
            ReplayDataset,
        ] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        dataset: ReplayDataset,
    ) -> None:

        self._datasets[
            dataset.name
        ] = dataset

    def unregister(
        self,
        dataset: str,
    ) -> None:

        self._datasets.pop(
            dataset,
            None,
        )

    def clear(
        self,
    ) -> None:

        self._datasets.clear()

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def exists(
        self,
        dataset: str,
    ) -> bool:

        return dataset in self._datasets

    def dataset(
        self,
        dataset: str,
    ) -> Optional[ReplayDataset]:

        return self._datasets.get(
            dataset,
        )

    # ------------------------------------------------------------------
    # Enumeration
    # ------------------------------------------------------------------

    def datasets(
        self,
    ) -> List[str]:

        return sorted(
            self._datasets.keys(),
        )

    def enabled(
        self,
    ) -> List[ReplayDataset]:

        return [

            dataset

            for dataset in self._datasets.values()

            if dataset.enabled

        ]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def count(
        self,
    ) -> int:

        return len(
            self._datasets,
        )


# ============================================================================
# Global Registry
# ============================================================================


replay_registry = ReplayRegistry()


# ============================================================================
# Canonical Financial Replay Datasets
# ============================================================================

_REPLAY_ROOT = (
    Path(__file__)
    .resolve()
    .parents[6]
    / "tests"
    / "financial"
    / "swift"
)


for dataset in (

    "MT103",

    "MT202",

    "MT700",

    "MT760",

    "MT767",

    "MT799",

    "MT940",

    "MX",

):

    replay_registry.register(

        ReplayDataset(

            name=dataset,

            path=_REPLAY_ROOT / dataset,

            description=f"Canonical {dataset} replay dataset.",

        )

    )
    

# ============================================================================
# Public Exports
# ============================================================================


__all__ = [
    "ReplayDataset",
    "ReplayRegistry",
    "replay_registry",
]