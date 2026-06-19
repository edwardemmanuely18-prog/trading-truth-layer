from app.models.trade import Trade


def classify_trade(trade: Trade):
    """
    Canonical TTL evidence classification engine.

    This service is the single source of truth for:

    - verification_state
    - evidence_trust_tier
    - integrity_type

    All pages must consume this service:
        - Evidence Records
        - Evidence Registry
        - Integrity Registry
        - Claim Operations
        - Public Verification
    """

    verification_state = "verified"
    evidence_trust_tier = "tier_2"

    # Tier 3
    if trade.import_source in [
        "manual_trade",
        "manual_edit",
        "manual_edit_created",
        "edited_trade",
        "manual_created",
    ]:

        verification_state = "self_reported"
        evidence_trust_tier = "tier_3"

    # Tier 1
    elif trade.broker_connection_id:

        verification_state = "broker_verified"
        evidence_trust_tier = "tier_1"

    # Integrity classification
    integrity_type = "none"

    if trade.trade_fingerprint:

        integrity_type = "fingerprinted"

    elif trade.raw_trade_hash:

        integrity_type = "hash_protected"

    return {
        "verification_state":
            verification_state,

        "evidence_trust_tier":
            evidence_trust_tier,

        "integrity_type":
            integrity_type,

        "has_raw_hash":
            bool(trade.raw_trade_hash),

        "has_fingerprint":
            bool(trade.trade_fingerprint),
    }