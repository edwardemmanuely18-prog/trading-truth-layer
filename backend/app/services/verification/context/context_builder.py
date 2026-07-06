from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.verification.verification_context import (
    VerificationContext,
)

from .context_queries import (
    load_context_data,
)

from .context_validator import (
    validate_context,
)


def build_verification_context(
    *,
    db: Session,
    claim_schema: ClaimSchema,
) -> VerificationContext:
    """
    Canonical builder used by the Trading
    Verification Engine.

    Loads every object required to verify
    a ClaimSchema.
    """

    data = load_context_data(
        db=db,
        claim_schema=claim_schema,
    )

    #
    # ----------------------------------------------------------
    # Canonical Claim Performance
    # ----------------------------------------------------------
    #

    performance_metrics = compute_trade_metrics(
        data.trades,
    )

    #
    # ----------------------------------------------------------
    # Institutional Evidence Profile
    # ----------------------------------------------------------
    #

    metadata = performance_metrics.get(
        "evidence_profile",
        {},
    )

    evidence_profile = {

        "primary_tier":
            metadata.get(
                "primary_tier",
                "Unknown",
            ),

        "primary_source":
            metadata.get(
                "primary_source",
                "Unknown",
            ),

        "tier1_count":
            metadata.get(
                "tier1_count",
                0,
            ),

        "tier2_count":
            metadata.get(
                "tier2_count",
                0,
            ),

        "tier3_count":
            metadata.get(
                "tier3_count",
                0,
            ),

        "tier1_percent":
            metadata.get(
                "tier1_percent",
                0.0,
            ),

        "tier2_percent":
            metadata.get(
                "tier2_percent",
                0.0,
            ),

        "tier3_percent":
            metadata.get(
                "tier3_percent",
                0.0,
            ),

    }

    context = VerificationContext(

        claim_schema=claim_schema,

        workspace=data.workspace,

        trades=data.trades,

        claim_trade_count=data.claim_trade_count,

        performance_metrics=performance_metrics,

        trade_metrics=performance_metrics,

        evidence_records=data.evidence_records,

        evidence_profile=evidence_profile,

        integrity_scan=data.integrity_scan,

        integrity_alerts=data.integrity_alerts,

        review_statements=data.review_statements,

        disputes=data.disputes,

        audit_events=data.audit_events,

        broker_connections=data.broker_connections,

        identity={

            "claim_id": claim_schema.id,

            "workspace_id": claim_schema.workspace_id,

            "claim_hash": claim_schema.claim_hash,

        },

        metadata={

            "claim_trade_count":
                data.claim_trade_count,

        },

        qr_payload={

            "verification_url":
                getattr(
                    claim_schema,
                    "public_verification_url",
                    "",
                ),

            "claim_hash":
                claim_schema.claim_hash,

        },

    )

    validate_context(
        context
    )

    return context