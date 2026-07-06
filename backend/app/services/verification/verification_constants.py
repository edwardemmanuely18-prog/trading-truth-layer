"""
============================================================

Trading Truth Layer Verification Standard (TVS)

Canonical Verification Constants

Everything in the Verification Engine should
import values from this file instead of
hardcoding strings.

============================================================
"""

# ============================================================
# TVS
# ============================================================

TVS_VERSION = "1.0"


# ============================================================
# VERIFICATION TIERS
# ============================================================

TIER_1 = "tier_1"

TIER_2 = "tier_2"

TIER_3 = "tier_3"


TIER_LABELS = {

    TIER_1: "Tier 1",

    TIER_2: "Tier 2",

    TIER_3: "Tier 3",

}


TIER_DESCRIPTIONS = {

    TIER_1:
        (
            "Live Broker Synchronization"
        ),

    TIER_2:
        (
            "Broker Statement Import"
        ),

    TIER_3:
        (
            "Manual or Edited Evidence"
        ),

}


# ============================================================
# EVIDENCE SOURCES
# ============================================================

SOURCE_MT5_LIVE = "mt5_live"

SOURCE_IBKR_LIVE = "ibkr_live"

SOURCE_CTRADER_LIVE = "ctrader_live"

SOURCE_DXTRADE_LIVE = "dxtrade_live"

SOURCE_BROKER_CSV = "broker_csv"

SOURCE_BROKER_FLEX = "broker_flex"

SOURCE_MANUAL = "manual"

SOURCE_IMPORTED = "imported"


LIVE_SOURCES = {

    SOURCE_MT5_LIVE,

    SOURCE_IBKR_LIVE,

    SOURCE_CTRADER_LIVE,

    SOURCE_DXTRADE_LIVE,

}


CSV_SOURCES = {

    SOURCE_BROKER_CSV,

    SOURCE_BROKER_FLEX,

}


# ============================================================
# CLAIM LIFECYCLE
# ============================================================

CLAIM_DRAFT = "draft"

CLAIM_VERIFIED = "verified"

CLAIM_PUBLISHED = "published"

CLAIM_LOCKED = "locked"


# ============================================================
# INTEGRITY
# ============================================================

INTEGRITY_VALID = "valid"

INTEGRITY_WARNING = "warning"

INTEGRITY_COMPROMISED = "compromised"


# ============================================================
# DISPUTES
# ============================================================

DISPUTE_NONE = "none"

DISPUTE_OPEN = "open"

DISPUTE_RESOLVED = "resolved"

DISPUTE_REJECTED = "rejected"


# ============================================================
# REVIEW STATUS
# ============================================================

REVIEW_PENDING = "pending"

REVIEW_APPROVED = "approved"

REVIEW_REJECTED = "rejected"


# ============================================================
# SCORE COMPONENT KEYS
# ============================================================

COMPONENT_EVIDENCE = "evidence"

COMPONENT_INTEGRITY = "integrity"

COMPONENT_GOVERNANCE = "governance"

COMPONENT_TRANSPARENCY = "transparency"

COMPONENT_STABILITY = "stability"

COMPONENT_NETWORK = "network"

COMPONENT_REVIEWS = "reviews"

COMPONENT_DISPUTES = "disputes"