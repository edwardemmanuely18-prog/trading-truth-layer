from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.workspace_membership import WorkspaceMembership
from app.models.import_batch import ImportBatch

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.metrics_service import (
    get_workspace_trade_metrics,
)

from app.services.analytics_service import (
    get_strategy_performance,
)

from app.services.integrity_score_service import (
    calculate_integrity_score,
)

from app.services.verification.verification_service import (
    get_workspace_verification_context,
)


def get_dashboard_overview(
    db: Session,
    workspace_id: int,
):
    """
    Canonical institutional dashboard intelligence layer.
    """

    # =====================================================
    # CORE COUNTS
    # =====================================================

    trade_count = (
        db.query(func.count(Trade.id))
        .filter(Trade.workspace_id == workspace_id)
        .scalar()
        or 0
    )

    member_count = (
        db.query(func.count(WorkspaceMembership.user_id))
        .filter(
            WorkspaceMembership.workspace_id == workspace_id
        )
        .scalar()
        or 0
    )

    claim_count = (
        db.query(func.count(ClaimSchema.id))
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .scalar()
        or 0
    )

    # =====================================================
    # CLAIM LIFECYCLE
    # =====================================================

    draft_claims = (
        db.query(func.count(ClaimSchema.id))
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "draft",
        )
        .scalar()
        or 0
    )

    verified_claims = (
        db.query(func.count(ClaimSchema.id))
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "verified",
        )
        .scalar()
        or 0
    )

    published_claims = (
        db.query(func.count(ClaimSchema.id))
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "published",
        )
        .scalar()
        or 0
    )

    locked_claims = (
        db.query(func.count(ClaimSchema.id))
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .scalar()
        or 0
    )

    # =====================================================
    # IMPORT HEALTH
    # =====================================================

    import_batches = (
        db.query(ImportBatch)
        .filter(
            ImportBatch.workspace_id == workspace_id
        )
        .all()
    )

    rows_received = 0
    rows_imported = 0
    rows_rejected = 0
    rows_duplicates = 0

    for batch in import_batches:
        rows_received += (
            batch.rows_received or 0
        )

        rows_imported += (
            batch.rows_imported or 0
        )

        rows_rejected += (
            batch.rows_rejected or 0
        )

        rows_duplicates += (
            batch.rows_skipped_duplicates or 0
        )

    duplicate_ratio = (
        rows_duplicates / rows_received
        if rows_received > 0
        else 0
    )

    rejection_ratio = (
        rows_rejected / rows_received
        if rows_received > 0
        else 0
    )

    # =====================================================
    # STRATEGY ANALYTICS
    # =====================================================

    strategies = get_strategy_performance(
        db,
        workspace_id,
    )

    best_strategy = (
        strategies[0]
        if strategies
        else None
    )

    # =====================================================
    # WORKSPACE METRICS
    # =====================================================

    metrics = get_workspace_trade_metrics(
        db,
        workspace_id,
    )

    verification = (
        get_workspace_verification_context(
            db=db,
            workspace_id=workspace_id,
            include_draft=False,
        )
    )

    # =====================================================
    # WORKFLOW STATE
    # =====================================================

    workflow = {
        "import_complete": trade_count > 0,
        "claim_created": claim_count > 0,
        "verification_started": (
            verified_claims > 0
            or published_claims > 0
            or locked_claims > 0
        ),
        "published": (
            published_claims > 0
            or locked_claims > 0
        ),
        "locked": locked_claims > 0,
    }

    # =====================================================
    # GOVERNANCE HEALTH
    # =====================================================

    utilization = metrics.get(
        "utilization",
        0,
    )

    governance_status = "healthy"

    if utilization >= 100:
        governance_status = "critical"

    elif utilization >= 80:
        governance_status = "warning"

    active_alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id,

            IntegrityAlert.status
            == "open",
        )
        .count()
    )

    open_alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id,

            IntegrityAlert.status
            == "open",
        )
        .all()
    )

    fatal_alerts = len([
        a for a in open_alerts
        if str(a.severity).upper() == "FATAL"
    ])

    critical_alerts = len([
        a for a in open_alerts
        if str(a.severity).upper() == "CRITICAL"
    ])

    high_alerts = len([
        a for a in open_alerts
        if str(a.severity).upper() == "HIGH"
    ])

    warning_alerts = len([
        a for a in open_alerts
        if str(a.severity).upper() == "WARNING"
    ])

    integrity_score = (
        calculate_integrity_score(
            open_alerts
        )
    )

    operational_services = {

        "evidence_engine": "ONLINE",

        "verification_engine": "ONLINE",

        "institutional_reporting": "ONLINE",

        "trust_layer": "ONLINE",

        "governance": "ONLINE",
    }

    # =====================================================
    # FINAL PAYLOAD
    # =====================================================

    return {
        "workspace_id": workspace_id,

        "workspace": {
            "member_count": member_count,
            "trade_count": trade_count,
            "claim_count": claim_count,
        },

        "claims": {
            "draft": draft_claims,
            "verified": verified_claims,
            "published": published_claims,
            "locked": locked_claims,
        },

        "workflow": workflow,

        "governance": {
            "utilization": utilization,
            "status": governance_status,
            "effective_plan_code": metrics.get(
                "effective_plan_code"
            ),
        },

        "trading_metrics": metrics,

        "import_health": {
            "rows_received": rows_received,
            "rows_imported": rows_imported,
            "rows_rejected": rows_rejected,
            "rows_duplicates": rows_duplicates,

            "duplicate_ratio": round(
                duplicate_ratio,
                4,
            ),

            "rejection_ratio": round(
                rejection_ratio,
                4,
            ),
        },

        "strategy_analytics": {
            "strategy_count": len(strategies),
            "best_strategy": best_strategy,
            "strategies": strategies,
        },

        "executive": {

            "active_alerts": active_alerts,

            "integrity_health": (
                "healthy"
                if active_alerts == 0
                else "warning"
            ),

            "integrity_score": integrity_score,

            "verification": {

                "coverage":
                    verification.metrics.coverage,

                "score":
                    verification.metrics.verification_score,

                "band":
                    verification.metrics.band,

                "verified_claims":
                    verification.metrics.verified_claims,

                "published_claims":
                    verification.metrics.published_claims,

                "locked_claims":
                    verification.metrics.locked_claims,
            },
        },

        "integrity": {
            "score": integrity_score,

            "total_alerts": active_alerts,

            "fatal_alerts": fatal_alerts,

            "critical_alerts": critical_alerts,

            "high_alerts": high_alerts,

            "warning_alerts": warning_alerts,
        },

        "operational": {

            "services":
                operational_services,

            "stage": {

                "import":
                    workflow["import_complete"],

                "claims":
                    workflow["claim_created"],

                "verification":
                    workflow["verification_started"],

                "public_trust":
                    workflow["published"],

                "locked":
                    workflow["locked"],
            },
        },
    }