from sqlalchemy.orm import Session

from app.services.dashboard_service import (
    get_dashboard_overview,
)


def get_dashboard_snapshot(
    db: Session,
    workspace_id: int,
):
    dashboard = get_dashboard_overview(
        db,
        workspace_id,
    )

    integrity = dashboard["integrity"]

    return {

        "health_score":
            integrity["score"],

        "health_state":
            (
                "HEALTHY"
                if integrity["score"] >= 90
                else "WARNING"
            ),

        "trust_state":
            (
                "ACTIVE"
                if dashboard["claims"]["locked"] > 0
                else "BUILDING"
            ),

        "governance_state":
            dashboard["governance"]["status"],

        "active_alerts":
            integrity["total_alerts"],

        "services": {

            "evidence_engine":
                "HEALTHY",

            "verification_engine":
                "HEALTHY",

            "report_engine":
                "HEALTHY",

            "trust_layer":
                "ACTIVE",

            "governance_engine":
                dashboard["governance"]["status"].upper(),

        },

    }