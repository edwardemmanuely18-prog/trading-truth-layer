from sqlalchemy.orm import Session

from app.models.trade import Trade

from app.services.evidence_classification_service import (
    classify_trade,
)

from app.services.evidence.calculators.coverage import (
    compute_coverage,
)

from app.services.evidence.calculators.protection import (
    compute_protection,
)

from app.services.evidence.calculators.tiers import (
    compute_tiers,
)

from app.services.evidence.feeds.monitoring_feed import (
    build_monitoring_feed,
)

from app.services.evidence.feeds.exception_feed import (
    build_exception_registry,
)

from app.services.evidence.calculators.quality import (
    compute_quality,
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

    monitoring_feed = build_monitoring_feed(
        feed,
    )

    exception_registry = build_exception_registry(
        exceptions,
    )

    coverage_metrics = compute_coverage(

        total_records=total,

        broker_verified=broker_verified,

        verified=verified,

        self_reported=self_reported,

    )

    coverage = coverage_metrics.coverage

    tier_metrics = compute_tiers(

        total_records=total,

        tier1=tier1,

        tier2=tier2,

        tier3=tier3,

    )

    reliability = (
        tier_metrics.reliability
    )

    protection_metrics = compute_protection(

        total_records=total,

        fingerprinted=fingerprinted,

        hash_protected=hash_protected,

    )

    protection = (
        protection_metrics.protection
    )

    unprotected = (
        protection_metrics.unprotected
    )

    quality_metrics = compute_quality(

        total_records=total,

        coverage=coverage,

        reliability=reliability,

        protection=protection,

        tier3=tier_metrics.tier3,

        unprotected=protection_metrics.unprotected,

        exception_count=len(exceptions),

    )

    return {
        "overview": {
            "records": total,
            "coverage": coverage,
            "reliability": reliability,
            "protection": protection,
            "quality_score":
                quality_metrics.score,

            "quality_band":
                quality_metrics.band,
        },

        "verification": {

            "broker_verified":
                coverage_metrics.broker_verified,

            "verified":
                coverage_metrics.verified,

            "self_reported":
                coverage_metrics.self_reported,

        },

        "tiers": {

            "tier_1":
                tier_metrics.tier1,

            "tier_2":
                tier_metrics.tier2,

            "tier_3":
                tier_metrics.tier3,

        },

        "protection": {

            "fingerprinted":
                protection_metrics.fingerprinted,

            "hash_protected":
                protection_metrics.hash_protected,

            "unprotected":
                protection_metrics.unprotected,

        },

        "feed": monitoring_feed.rows,

        "exceptions":
            exception_registry.rows[:50],

        "quality": {

            "verification_quality":
                quality_metrics.verification_quality,

            "protection_quality":
                quality_metrics.protection_quality,

            "completeness_quality":
                quality_metrics.completeness_quality,

            "import_quality":
                quality_metrics.import_quality,

            "score":
                quality_metrics.score,

            "band":
                quality_metrics.band,
        },
    }