from collections import Counter

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.broker_connection import BrokerConnection
from app.models.claim_schema import ClaimSchema
from app.models.integrity_alert import IntegrityAlert
from app.models.trade import Trade


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
    # Integrity
    # ----------------------------------------------------------
    #

    integrity = {

        "total_alerts":

            len(alerts),

        "critical":

            sum(

                a.severity.lower() == "critical"

                for a in alerts

            ),

        "resolved":

            sum(

                getattr(
                    a,
                    "resolved",
                    False,
                )

                for a in alerts

            ),

        "audit_events":

            len(audits),

    }

    integrity_score = max(

        0,

        100 - integrity["total_alerts"] * 5,

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

            trust_score,

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

            (

                "Institutional"

                if trust_score >= 90

                else

                "Excellent"

                if trust_score >= 80

                else

                "Good"

                if trust_score >= 65

                else

                "Needs Improvement"

            ),

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

                round(
                    verification_pct,
                    2,
                ),

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

                status_counter["draft"],

            "verified":

                status_counter["verified"],

            "published":

                status_counter["published"],

            "locked":

                status_counter["locked"],

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