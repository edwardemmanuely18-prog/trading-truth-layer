"""
Trading Truth Layer Verification Band Engine
"""

from __future__ import annotations

from app.services.verification.scoring_weights import (
    VERIFICATION_BANDS,
)


def determine_verification_band(
    score: float,
):

    for band in VERIFICATION_BANDS:

        if (
            band.minimum
            <= score
            <= band.maximum
        ):

            return band

    return VERIFICATION_BANDS[-1]