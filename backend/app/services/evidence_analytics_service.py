from sqlalchemy.orm import Session

from app.models.trade import Trade

from app.services.evidence_classification_service import (
    classify_trade,
)


def build_evidence_analytics(
    db: Session,
    workspace_id: int,
):
    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()
    )

    total = len(trades)

    broker_verified = 0
    verified = 0
    self_reported = 0

    tier1 = 0
    tier2 = 0
    tier3 = 0

    fingerprinted = 0
    hash_protected = 0

    feed = []

    exceptions = []

    for trade in trades:

        classification = (
            classify_trade(trade)
        )

        state = (
            classification[
                "verification_state"
            ]
        )

        tier = (
            classification[
                "evidence_trust_tier"
            ]
        )

        integrity = (
            classification[
                "integrity_type"
            ]
        )

        missing_evidence = []

        if not trade.raw_trade_hash:

            missing_evidence.append(
                "missing_hash"
            )

        if not trade.trade_fingerprint:

            missing_evidence.append(
                "missing_fingerprint"
            )

        if state == "broker_verified":
            broker_verified += 1

        elif state == "verified":
            verified += 1

        elif state == "self_reported":
            self_reported += 1

        if tier == "tier_1":
            tier1 += 1

        elif tier == "tier_2":
            tier2 += 1

        elif tier == "tier_3":
            tier3 += 1

        if integrity == "fingerprinted":
            fingerprinted += 1

        elif integrity == "hash_protected":
            hash_protected += 1

        missing_evidence = []

        if not trade.raw_trade_hash:
            missing_evidence.append(
                "missing_hash"
            )

        if not trade.trade_fingerprint:
            missing_evidence.append(
                "missing_fingerprint"
            )

        if missing_evidence:

            exceptions.append({

                "trade_id":
                    trade.id,

                "symbol":
                    trade.symbol,

                "issues":
                    missing_evidence,

            })

        feed.append({
            "trade_id": trade.id,
            "symbol": trade.symbol,
            "verification_state": state,
            "trust_tier": tier,
            "integrity_type": integrity,
        })

    coverage = round(
        (
            (broker_verified + verified)
            / total
        ) * 100,
        2,
    ) if total else 0

    reliability = round(
        (
            tier1
            / total
        ) * 100,
        2,
    ) if total else 0

    protection = round(
        (
            (fingerprinted + hash_protected)
            / total
        ) * 100,
        2,
    ) if total else 0

    unprotected = (
        total
        - fingerprinted
        - hash_protected
    )

    quality_score = 100

    if tier3 > 0:
        quality_score -= min(
            25,
            round(
                (tier3 / total) * 25
            )
        )

    if unprotected > 0:
        quality_score -= min(
            25,
            round(
                (unprotected / total) * 25
            )
        )

    quality_score = max(
        quality_score,
        0,
    )

    verification_quality = coverage

    protection_quality = protection

    completeness_quality = round(
        (
            (total - len(exceptions))
            / total
        ) * 100,
        2,
    ) if total else 0

    import_quality = reliability

    if quality_score >= 90:
        quality_band = "EXCELLENT"

    elif quality_score >= 75:
        quality_band = "GOOD"

    elif quality_score >= 60:
        quality_band = "MONITORING"

    else:
        quality_band = "POOR"

    return {
        "overview": {
            "records": total,
            "coverage": coverage,
            "reliability": reliability,
            "protection": protection,
            "quality_score": quality_score,
            "quality_band": quality_band,
        },

        "verification": {
            "broker_verified":
                broker_verified,

            "verified":
                verified,

            "self_reported":
                self_reported,
        },

        "tiers": {
            "tier_1": tier1,
            "tier_2": tier2,
            "tier_3": tier3,
        },

        "protection": {
            "fingerprinted":
                fingerprinted,

            "hash_protected":
                hash_protected,

            "unprotected":
                unprotected,
        },

        "feed": feed[:20],

        "exceptions":
            exceptions[:50],

        "quality": {

            "verification_quality":
                verification_quality,

            "protection_quality":
                protection_quality,

            "completeness_quality":
                completeness_quality,

            "import_quality":
                import_quality,

            "score":
                quality_score,

            "band":
                quality_band,
        },
    }