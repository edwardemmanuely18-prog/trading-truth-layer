from collections import Counter

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.broker_connection import BrokerConnection
from app.models.claim_schema import ClaimSchema
from app.models.integrity_alert import IntegrityAlert
from app.models.trade import Trade

from app.services.verification.verification_service import (
    get_workspace_verification_context,
)

from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)


def get_verification_network(
    db: Session,
    workspace_id: int,
):
    """
    Institutional Verification Network

    Executive
    Coverage
    Broker Network
    Integrity
    Claim Registry
    """

    #
    # ----------------------------------------------------------
    # Canonical TVS Workspace Context
    # ----------------------------------------------------------
    #

    tvs = get_workspace_verification_context(
        db=db,
        workspace_id=workspace_id,
    )

    verification_metrics = tvs.metrics

    #
    # ----------------------------------------------------------
    # Load Workspace Data
    # ----------------------------------------------------------
    #

    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()
    )

    alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id == workspace_id
        )
        .all()
    )

    audits = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id == str(workspace_id)
        )
        .all()
    )

    brokers = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.workspace_id == workspace_id
        )
        .all()
    )

    #
    # ----------------------------------------------------------
    # Lifecycle Counters
    # ----------------------------------------------------------
    #

    status_counter = Counter()

    visibility_counter = Counter()

    for schema in schemas:

        status_counter[
            (schema.status or "draft").lower()
        ] += 1

        visibility_counter[
            (schema.visibility or "private").lower()
        ] += 1

    total_claims = len(schemas)

    verification_pct = (
        (
            status_counter["verified"]
            + status_counter["published"]
            + status_counter["locked"]
        )
        / total_claims
        * 100
        if total_claims
        else 0
    )

    publication_pct = (
        (
            status_counter["published"]
            + status_counter["locked"]
        )
        / total_claims
        * 100
        if total_claims
        else 0
    )

    lock_pct = (
        status_counter["locked"]
        / total_claims
        * 100
        if total_claims
        else 0
    )

    #
    # ----------------------------------------------------------
    # Broker Network
    # ----------------------------------------------------------
    #

    broker_network = {

        "total_accounts":

            len(brokers),

        "verified":

            sum(

                b.verification_status == "verified"

                for b in brokers

            ),

        "live":

            sum(

                b.connection_status == "connected"

                for b in brokers

            ),

        "providers":

            sorted(

                {

                    b.provider

                    for b in brokers

                    if b.provider

                }

            ),

    }

    broker_score = (
        (
            broker_network["verified"]
            / broker_network["total_accounts"]
        )
        * 100
        if broker_network["total_accounts"]
        else 100
    )

    #
    # ----------------------------------------------------------
    # Canonical Integrity Dashboard
    # ----------------------------------------------------------
    #

    integrity_dashboard = (

        build_integrity_dashboard(
            db,
            workspace_id,
        )

    )

    integrity = {

        "integrity_score":

            integrity_dashboard.get(
                "integrity_score",
                0,
            ),

        "open_findings":

            integrity_dashboard.get(
                "open_findings",
                0,
            ),

        "resolved":

            integrity_dashboard.get(
                "resolved_findings",
                0,
            ),

        "claims_scanned":

            integrity_dashboard.get(
                "claims_scanned",
                0,
            ),

        "critical":

            integrity_dashboard.get(
                "critical",
                0,
            ),

        "high":

            integrity_dashboard.get(
                "high",
                0,
            ),

        "warning":

            integrity_dashboard.get(
                "warning",
                0,
            ),

        "fatal":

            integrity_dashboard.get(
                "fatal",
                0,
            ),

        "total_alerts":

            integrity_dashboard.get(
                "total_alerts",
                0,
            ),

        "audit_events":

            len(audits),

    }

    integrity_score = (

        integrity["integrity_score"]

    )


    audit_score = min(

        100,

        len(audits) * 2,

    )

    #
    # ----------------------------------------------------------
    # Institutional Trust Score
    # ----------------------------------------------------------
    #

    trust_score = round(

        verification_pct * 0.35 +

        publication_pct * 0.20 +

        lock_pct * 0.15 +

        broker_score * 0.10 +

        integrity_score * 0.10 +

        audit_score * 0.10,

        1,

    )

    executive = {

        "workspace_trust_score":

            verification_metrics.average_verification_score,

        "allocator_ready":

            (

                trust_score >= 85

                and lock_pct >= 75

            ),

        "network_health":

            (

                "Healthy"

                if trust_score >= 85

                else

                "Warning"

                if trust_score >= 60

                else

                "Critical"

            ),

        "verification_band":

            verification_metrics.verification_band,

    }

    #
    # ----------------------------------------------------------
    # Claim Registry
    # ----------------------------------------------------------
    #

    claims = []

    for schema in schemas:

        claims.append(

            {

                "id":

                    schema.id,

                "name":

                    schema.name,

                "status":

                    schema.status,

                "visibility":

                    schema.visibility,

                "claim_hash":

                    schema.claim_hash,

                "verified_at":

                    schema.verified_at,

                "published_at":

                    schema.published_at,

                "locked_at":

                    schema.locked_at,

                "network_state":

                    (

                        "Allocator Ready"

                        if (

                            (schema.status or "").lower() == "locked"

                            and

                            (schema.visibility or "").lower() == "public"

                        )

                        else

                        "Internal"

                    ),

            }

        )

    #
    # ----------------------------------------------------------
    # Response
    # ----------------------------------------------------------
    #

    return {

        "executive":

            executive,

        "coverage": {

            "verification":

                verification_metrics.verification_coverage,

            "publication":

                round(
                    publication_pct,
                    2,
                ),

            "lock":

                round(
                    lock_pct,
                    2,
                ),

        },

        "broker_network":

            broker_network,

        "integrity":

            integrity,

        "lifecycle": {

            "draft":

                verification_metrics.draft_claim_count,

            "verified":

                verification_metrics.verified_claim_count,

            "published":

                verification_metrics.published_claim_count,

            "locked":

                verification_metrics.locked_claim_count,

        },

        "visibility": {

            "private":

                visibility_counter["private"],

            "public":

                visibility_counter["public"],

            "unlisted":

                visibility_counter["unlisted"],

        },

        "claims":

            claims,

    }