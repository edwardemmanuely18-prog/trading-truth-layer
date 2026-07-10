from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class IdentityActivity:

    claims_created: int = 0

    evidence_uploaded: int = 0

    reports_generated: int = 0

    verification_reviews: int = 0

    public_records: int = 0

    recent_events: list[str] = field(
        default_factory=list,
    )


def build_identity_activity():

    """
    Placeholder.

    Future versions consume

    TVS

    TES

    Audit Log

    Claim Events

    Report Events
    """

    return IdentityActivity()