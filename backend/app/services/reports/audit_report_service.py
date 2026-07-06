from app.models.claim_schema import (
    ClaimSchema,
)

from app.models.audit_event import (
    AuditEvent,
)

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)


def build_audit_report_payload(
    workspace_id: int,
    db,
):
    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    audit_events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id
            == str(workspace_id)
        )
        .order_by(
            AuditEvent.id.desc()
        )
        .all()
    )

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

    integrity = (
        build_integrity_dashboard(
            db,
            workspace_id,
        )
    )

    draft_claims = 0
    verified_claims = 0
    published_claims = 0
    locked_claims = 0

    for claim in claims:

        status = (
            claim.status or ""
        ).lower()

        if status == "draft":
            draft_claims += 1

        elif status == "verified":
            verified_claims += 1

        elif status == "published":
            published_claims += 1

        elif status == "locked":
            locked_claims += 1

    audit_feed = []

    for event in audit_events[:250]:

        audit_feed.append(
            {
                "id":
                    event.id,

                "event_type":
                    event.event_type,

                "entity_type":
                    event.entity_type,

                "entity_id":
                    event.entity_id,

                "actor_id":
                    event.actor_id,

                "created_at":
                    event.created_at,

                "workspace_id":
                    event.workspace_id,
            }
        )

    integrity_findings = []

    for alert in alerts[:250]:

        integrity_findings.append(
            {
                "id":
                    alert.id,

                "severity":
                    alert.severity,

                "alert_type":
                    alert.alert_type,

                "entity_type":
                    alert.entity_type,

                "entity_id":
                    alert.entity_id,

                "status":
                    alert.status,

                "message":
                    alert.message,

                "created_at":
                    alert.created_at,

                "resolved_at":
                    alert.resolved_at,
            }
        )

    governance_score = 100

    governance_score -= min(
        integrity["open_findings"],
        40,
    )

    governance_score = max(
        governance_score,
        0,
    )

    audit_risks = []

    if integrity["open_findings"] > 0:
        audit_risks.append(
            "open_integrity_findings"
        )

    if governance_score < 80:
        audit_risks.append(
            "governance_degradation"
        )

    if len(alerts) > 0:
        audit_risks.append(
            "active_integrity_alerts"
        )

    return {

        "summary": {

            "claims":
                len(claims),

            "audit_events":
                len(audit_events),

            "integrity_findings":
                len(alerts),

            "governance_score":
                governance_score,
        },

        "lifecycle": {

            "draft":
                draft_claims,

            "verified":
                verified_claims,

            "published":
                published_claims,

            "locked":
                locked_claims,
        },

        "integrity": {

            "integrity_score":
                integrity[
                    "integrity_score"
                ],

            "open_findings":
                integrity[
                    "open_findings"
                ],

            "resolved_findings":
                integrity[
                    "resolved_findings"
                ],

            "severity":
                integrity[
                    "severity"
                ],

            "scanner_status":
                integrity[
                    "scanner_status"
                ],
        },

        "audit_events":
            audit_feed,

        "integrity_findings":
            integrity_findings,

        "audit_risks": {

            "count":
                len(audit_risks),

            "items":
                audit_risks,
        },

        "report_metadata": {

            "report_type":
                "AUDIT",

            "workspace_id":
                workspace_id,

            "version":
                "1.0",
        },

        "verification_links": {

            "audit_route":
                f"/reports/workspace/{workspace_id}/audit",

            "verification_route":
                f"/reports/workspace/{workspace_id}/verification",
        },
    }