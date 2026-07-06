from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class VerificationSnapshot:

    claim_id: int

    workspace_id: int

    verification_standard: str

    verification_score: float

    verification_band: str

    verification_tier: str

    generated_at: datetime

    verification_result: dict[str, Any]

    timeline: list[Any] = field(
        default_factory=list
    )

    decision_record: dict[str, Any] = field(
        default_factory=dict
    )

    lineage_summary: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )