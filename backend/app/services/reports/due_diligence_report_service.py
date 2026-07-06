from app.models.workspace import Workspace
from app.models.claim_schema import ClaimSchema
from app.models.review_statement import (
    ReviewStatement,
)
from app.models.audit_event import (
    AuditEvent,
)
from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.metrics_service import (
    get_workspace_trade_metrics,
)

from app.services.evidence_analytics_service import (
    build_evidence_analytics,
)

from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)

from app.api.routes.claim_schemas import (
    build_public_trust_profile_for_workspace,
)


def build_due_diligence_report_payload(
    workspace_id: int,
    db,
):
    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if not workspace:
        raise ValueError(
            "Workspace not found"
        )

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    reviews = (
        db.query(ReviewStatement)
        .filter(
            ReviewStatement.workspace_id
            == workspace_id
        )
        .all()
    )

    alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
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
        .all()
    )

    trust_profile = (
        build_public_trust_profile_for_workspace(
            workspace_id,
            db,
        )
    )

    integrity = (
        build_integrity_dashboard(
            db,
            workspace_id,
        )
    )

    evidence = (
        build_evidence_analytics(
            db,
            workspace_id,
        )
    )

    risk = (
        get_workspace_trade_metrics(
            db,
            workspace_id,
        )
    )

    claim_count = len(claims)

    published_claims = len(
        [
            c
            for c in claims
            if c.status == "published"
        ]
    )

    locked_claims = len(
        [
            c
            for c in claims
            if c.status == "locked"
        ]
    )

    positive_reviews = len(
        [
            r
            for r in reviews
            if r.review_direction
            == "POSITIVE"
        ]
    )

    negative_reviews = len(
        [
            r
            for r in reviews
            if r.review_direction
            == "NEGATIVE"
        ]
    )

    critical_reviews = len(
        [
            r
            for r in reviews
            if r.review_direction
            == "CRITICAL"
        ]
    )

    average_rating = (
        round(
            sum(
                r.rating or 0
                for r in reviews
            )
            / len(reviews),
            2,
        )
        if reviews
        else 0
    )

    confidence = round(
        (
            trust_profile.get(
                "average_trust_score",
                0,
            )
            + integrity.get(
                "integrity_score",
                0,
            )
            + evidence["quality"][
                "score"
            ]
        )
        / 3,
        2,
    )

    if confidence >= 90:
        grade = "A+"

    elif confidence >= 80:
        grade = "A"

    elif confidence >= 70:
        grade = "B"

    elif confidence >= 60:
        grade = "C"

    else:
        grade = "D"

    recommendation = (
        "LOW RISK"
        if confidence >= 85
        else "MONITOR"
        if confidence >= 70
        else "HIGH RISK"
    )

    governance_score = round(
        (
            locked_claims
            / claim_count
        ) * 100,
        2,
    ) if claim_count else 0

    evidence_exceptions = (
        evidence.get(
            "exceptions",
            [],
        )
    )

    trust_risks = []

    if critical_reviews > 0:
        trust_risks.append(
            "critical_reviews_present"
        )

    if integrity["open_findings"] > 0:
        trust_risks.append(
            "open_integrity_findings"
        )

    if evidence["quality"]["score"] < 70:
        trust_risks.append(
            "low_evidence_quality"
        )

    if trust_profile.get(
        "average_trust_score",
        0,
    ) < 60:
        trust_risks.append(
            "low_trust_score"
        )

    return {

        "workspace": {
            "id":
                workspace.id,

            "name":
                workspace.name,

            "plan":
                workspace.plan_code,
        },

        "overview": {

            "claims":
                claim_count,

            "published_claims":
                published_claims,

            "locked_claims":
                locked_claims,

            "evidence_records":
                evidence["overview"][
                    "records"
                ],

            "audit_events":
                len(audit_events),

            "integrity_alerts":
                len(alerts),
        },

        "trust": {

            "trust_score":
                trust_profile.get(
                    "average_trust_score",
                    0,
                ),

            "network_score":
                trust_profile.get(
                    "average_network_score",
                    0,
                ),

            "trust_band":
                trust_profile.get(
                    "trust_profile_band",
                    "unknown",
                ),
        },

        "verification": {

            "coverage":
                evidence["overview"][
                    "coverage"
                ],

            "broker_verified":
                evidence[
                    "verification"
                ][
                    "broker_verified"
                ],

            "verified":
                evidence[
                    "verification"
                ][
                    "verified"
                ],

            "self_reported":
                evidence[
                    "verification"
                ][
                    "self_reported"
                ],
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

            "recent_findings":
                integrity[
                    "recent_findings"
                ],
        },

        "evidence": evidence,

        "risk": risk,

        "reviews": {

            "count":
                len(reviews),

            "positive":
                positive_reviews,

            "negative":
                negative_reviews,

            "critical":
                critical_reviews,

            "average_rating":
                average_rating,
        },

        "assessment": {

            "grade":
                grade,

            "confidence":
                confidence,

            "recommendation":
                recommendation,
        },

        "governance": {

            "governance_score":
                governance_score,

            "claims":
                claim_count,

            "published":
                published_claims,

            "locked":
                locked_claims,
        },

        "audit": {

            "event_count":
                len(audit_events),

            "latest_event":
                (
                    audit_events[-1].event_type
                    if audit_events
                    else None
                ),
        },

        "exceptions": {

            "count":
                len(
                    evidence_exceptions
                ),

            "items":
                evidence_exceptions[:25],
        },

        "trust_risks": {

            "count":
                len(trust_risks),

            "items":
                trust_risks,
        },

        "verification_links": {

            "workspace":
                workspace_id,

            "verification_route":
                f"/reports/workspace/{workspace_id}/verification",

            "audit_route":
                f"/reports/workspace/{workspace_id}/audit",

            "allocator_route":
                f"/reports/workspace/{workspace_id}/allocator",
        },

        "report_metadata": {

            "report_type":
                "DUE_DILIGENCE",

            "workspace_id":
                workspace_id,

            "workspace_name":
                workspace.name,

            "version":
                "1.0",
        },
    }