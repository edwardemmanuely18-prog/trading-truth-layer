"""
============================================================

Trading Truth Layer Verification Standard (TVS)

Verification Tier Engine

This module contains the canonical tier definitions
used throughout the platform.

Nothing should hardcode Tier logic outside this file.

============================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.verification.verification_constants import (
    TIER_1,
    TIER_2,
    TIER_3,
)


# ============================================================
# Tier Definition
# ============================================================

@dataclass(frozen=True, slots=True)
class VerificationTier:

    code: str

    label: str

    description: str

    confidence: str

    authenticity_points: int

    institutional_grade: str


# ============================================================
# Canonical Tier Registry
# ============================================================

TIERS = {

    TIER_1:

        VerificationTier(

            code=TIER_1,

            label="Tier I",

            description=(
                "Live Broker Synchronization"
            ),

            confidence="Very High",

            authenticity_points=30,

            institutional_grade="Institutional",

        ),

    TIER_2:

        VerificationTier(

            code=TIER_2,

            label="Tier II",

            description=(
                "Official Broker Statement Import"
            ),

            confidence="High",

            authenticity_points=22,

            institutional_grade="Verified",

        ),

    TIER_3:

        VerificationTier(

            code=TIER_3,

            label="Tier III",

            description=(
                "Manual or Edited Trade Evidence"
            ),

            confidence="Moderate",

            authenticity_points=12,

            institutional_grade="Limited",

        ),

}


# ============================================================
# Helper Functions
# ============================================================

def get_tier(
    tier_code: str,
) -> VerificationTier:

    return TIERS[tier_code]


def authenticity_points(
    tier_code: str,
) -> int:

    return get_tier(
        tier_code
    ).authenticity_points


def confidence_label(
    tier_code: str,
) -> str:

    return get_tier(
        tier_code
    ).confidence


def institutional_grade(
    tier_code: str,
) -> str:

    return get_tier(
        tier_code
    ).institutional_grade