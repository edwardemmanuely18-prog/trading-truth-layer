"""
============================================================

Trading Truth Layer Verification Standard (TVS)

Version: 1.0

Canonical scoring weights.

This file is the ONLY location where verification
component weights are defined.

Every verification engine imports these values.

============================================================
"""

from dataclasses import dataclass


# ============================================================
# TVS VERSION
# ============================================================

TVS_VERSION = "1.0"


# ============================================================
# VERIFICATION COMPONENT WEIGHTS
# ============================================================

EVIDENCE_AUTHENTICITY = 30

INTEGRITY = 18

GOVERNANCE = 12

TRANSPARENCY = 8

STABILITY = 8

VERIFICATION_NETWORK = 8

INDEPENDENT_REVIEW = 8

DISPUTE_RESOLUTION = 8


TOTAL_SCORE = (

    EVIDENCE_AUTHENTICITY +

    INTEGRITY +

    GOVERNANCE +

    TRANSPARENCY +

    STABILITY +

    VERIFICATION_NETWORK +

    INDEPENDENT_REVIEW +

    DISPUTE_RESOLUTION

)


assert TOTAL_SCORE == 100


# ============================================================
# COMPONENT LABELS
# ============================================================

COMPONENT_LABELS = {

    "evidence":

        "Evidence Authenticity",

    "integrity":

        "Integrity",

    "governance":

        "Governance",

    "transparency":

        "Transparency",

    "stability":

        "Stability",

    "network":

        "Verification Network",

    "reviews":

        "Independent Review",

    "disputes":

        "Dispute Resolution",

}


# ============================================================
# BAND THRESHOLDS
# ============================================================

@dataclass(frozen=True)
class VerificationBand:

    minimum: float

    maximum: float

    label: str

    description: str


VERIFICATION_BANDS = [

    VerificationBand(

        minimum=98,

        maximum=100,

        label="Elite",

        description=(
            "Exceptional institutional-grade "
            "verification."
        ),

    ),

    VerificationBand(

        minimum=90,

        maximum=97.99,

        label="Institutional",

        description=(
            "Strong institutional confidence."
        ),

    ),

    VerificationBand(

        minimum=80,

        maximum=89.99,

        label="Verified",

        description=(
            "Highly credible verified claim."
        ),

    ),

    VerificationBand(

        minimum=65,

        maximum=79.99,

        label="Trusted",

        description=(
            "Good verification confidence."
        ),

    ),

    VerificationBand(

        minimum=50,

        maximum=64.99,

        label="Developing",

        description=(
            "Verification still improving."
        ),

    ),

    VerificationBand(

        minimum=0,

        maximum=49.99,

        label="Limited",

        description=(
            "Limited verification confidence."
        ),

    ),

]