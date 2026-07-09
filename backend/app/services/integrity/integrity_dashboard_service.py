from app.models.integrity_alert import IntegrityAlert
from app.models.claim_schema import ClaimSchema

from app.services.integrity_score_service import (
    calculate_integrity_score,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    compute_trade_set_hash,
)

from app.services.integrity.scanner_registry_service import (
    build_scanner_status,
)


def build_integrity_dashboard(
    db,
    workspace_id,
):
    alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .order_by(
            IntegrityAlert.id.desc()
        )
        .all()
    )

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    severity = {
        "warning": 0,
        "high": 0,
        "critical": 0,
        "fatal": 0,
    }

    scanner_status = (
        build_scanner_status(
            db,
            workspace_id,
        )
    )

    alert_distribution = {}

    open_findings = 0
    resolved_findings = 0

    compromised_claims = 0

    for alert in alerts:

        level = (
            str(alert.severity or "")
            .lower()
        )

        if level in severity:
            severity[level] += 1

        if (
            alert.status or ""
        ).lower() == "resolved":
            resolved_findings += 1
        else:
            open_findings += 1

        alert_type = (
            alert.alert_type or ""
        ).upper()

        alert_distribution[
            alert_type
        ] = (
            alert_distribution.get(
                alert_type,
                0
            )
            + 1
        )

    for claim in claims:

        if (
            claim.status != "locked"
            or not claim.locked_trade_set_hash
        ):
            continue

        trades = resolve_schema_trades(
            claim,
            db,
        )

        current_hash = compute_trade_set_hash(
            trades
        )

        if (
            current_hash
            != claim.locked_trade_set_hash
        ):
            compromised_claims += 1

    open_alerts = [
        a
        for a in alerts
        if (
            str(a.status or "")
            .lower()
            != "resolved"
        )
    ]

    score = (
        calculate_integrity_score(
            open_alerts
        )
    )

    return {
        "integrity_score": score,

        "claims_scanned":
            len(claims),

        "compromised_claims":
            compromised_claims,

        "total_alerts":
            len(alerts),

        "open_findings":
            len(
                [
                    a
                    for a in alerts
                    if a.status == "open"
                ]
            ),

        "resolved_findings":
            len(
                [
                    a
                    for a in alerts
                    if a.status == "resolved"
                ]
            ),

        "severity":
            severity,

        "healthy":
            score >= 80,

        "scanner_status": {
            "ledger": {
                "status": "healthy",
                "findings": 0,
            },
            "lifecycle": {
                "status":
                    "warning"
                    if len(alerts) > 0
                    else "healthy",
                "findings":
                    len(alerts),
            },
            "evidence": {
                "status": "healthy",
                "findings": 0,
            },
            "governance": {
                "status": "healthy",
                "findings": 0,
            },
            "verification": {
                "status": "healthy",
                "findings": 0,
            },
            "metrics": {
                "status": "healthy",
                "findings": 0,
            },
            "public": {
                "status": "healthy",
                "findings": 0,
            },
            "authenticity": {
                "status": "healthy",
                "findings": 0,
            },
        },

        "alert_distribution": {
            "open":
                len(
                    [
                        a
                        for a in alerts
                        if a.status == "open"
                    ]
                ),

            "resolved":
                len(
                    [
                        a
                        for a in alerts
                        if a.status == "resolved"
                    ]
                ),
        },

        "recent_findings": [
            {
                "id":
                    alert.id,

                "severity":
                    alert.severity,

                "type":
                    alert.alert_type,

                "status":
                    alert.status,

                "message":
                    alert.message,

                "created_at":
                    alert.created_at.isoformat()
                    if alert.created_at
                    else None,
            }
            for alert in alerts[:10]
        ],
    }