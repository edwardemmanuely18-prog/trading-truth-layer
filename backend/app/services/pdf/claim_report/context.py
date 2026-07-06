from __future__ import annotations

"""
Trading Truth Layer
Claim Report Context

Canonical data context for the institutional
Claim Report.

This module is the ONLY place responsible for
assembling the report state consumed by the PDF.

No PDF section should:

    • Query the database

    • Compute verification metrics

    • Traverse VerificationCertificate

    • Build business objects

Every section consumes this context.
"""

from sqlalchemy.orm import Session

from datetime import datetime, UTC

from app.models.claim_schema import ClaimSchema

from app.services.verification.verification_service import (
    get_claim_verification_certificate,
    get_claim_verification_metrics,
)

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
)


# ==========================================================
# PRESENTATION HELPERS
# ==========================================================

def safe(value, default="Not Available"):
    if value is None:
        return default

    if isinstance(value, str):
        value = value.strip()

        if value == "":
            return default

    return value


def short_hash(value: str | None):
    value = safe(value, "")

    if len(value) <= 24:
        return value

    return f"{value[:12]}...{value[-12:]}"


def percent(value):
    if value is None:
        return "0.0%"

    return f"{float(value):.1f}%"

def present(value, default="Not Available"):
    """
    Converts missing presentation values into
    institutional-friendly output.
    """

    if value is None:
        return default

    if isinstance(value, str):

        if value.strip() == "":
            return default

        return value

    return value


# ==========================================================
# CONTEXT BUILDER
# ==========================================================

def build_claim_report_context(
    schema: ClaimSchema,
    db: Session,
) -> dict:
    """
    Canonical Claim Report Context.

    Returns every dataset required by the
    institutional Claim Report.

    All verification information originates
    from the canonical Trading Verification
    System (TVS).
    """

    #
    # ------------------------------------------------------
    # Canonical Verification Certificate
    # ------------------------------------------------------
    #

    certificate = get_claim_verification_certificate(
        db=db,
        claim=schema,
    )

    verification = get_claim_verification_metrics(
        db=db,
        claim=schema,
    )


    #
    # ------------------------------------------------------
    # Canonical Claim Trades
    # ------------------------------------------------------
    #

    trades = resolve_schema_trades(
        schema=schema,
        db=db,
    )

    performance = compute_trade_metrics(
        trades,
    )

    #
    # ------------------------------------------------------
    # Evidence Profile
    # ------------------------------------------------------
    #

    tier_profile = {

        "primary_tier":
            verification.primary_tier,

        "primary_source":
            verification.primary_source,

        "tier1_count":
            verification.tier1_count,

        "tier2_count":
            verification.tier2_count,

        "tier3_count":
            verification.tier3_count,

        "tier1_percent":
            verification.tier1_percent,

        "tier2_percent":
            verification.tier2_percent,

        "tier3_percent":
            verification.tier3_percent,

    }

    #
    # ------------------------------------------------------
    # Cover
    # ------------------------------------------------------
    #

    cover = {

        "title": schema.name,

        "verification_score": (
            verification.verification_score
        ),

        "verification_band": (
            verification.verification_band
        ),

        "verification_tier": (
            verification.verification_tier
        ),

        "verification_status": (
            verification.verification_status
        ),

    }

    claim = {

        "id": schema.id,

        "name": schema.name,

        "status": schema.status,

        "workspace_id": verification.workspace_id,

        "workspace_name": (
            getattr(schema.workspace, "name", "-")
            if getattr(schema, "workspace", None)
            else "-"
        ),

        "claim_hash": verification.claim_hash,

        "verification_score": verification.verification_score,

        "verification_band": verification.verification_band,

        "verification_tier": verification.verification_tier,

    }

    metadata = {

        "claim_name":
            safe(schema.name),

        "claim_status":
            safe(schema.status),

        "claim_hash":
            short_hash(
                verification.claim_hash,
            ),

        "workspace_id":
            verification.workspace_id,

        "claim_schema_id":
            verification.claim_schema_id,

        "workspace_name":
            safe(
                getattr(
                    getattr(schema, "workspace", None),
                    "name",
                    None,
                )
            ),

        "verification_url":
            safe(
                getattr(
                    schema,
                    "public_verification_url",
                    None,
                )
            ),

        "certificate_hash":
            short_hash(
                certificate.identity.certificate_hash,
            ),

        "certificate_version":
            safe(
                certificate.identity.certificate_version,
            ),

        "tvs_version":
            safe(
                certificate.identity.tvs_version,
            ),

        "generated_at":
            datetime.now(UTC).strftime(
                "%Y-%m-%d %H:%M UTC"
            )

    }

    report = {

        "generated":
            metadata["generated_at"],

        "generator":
            "Trading Truth Layer",

        "framework":
            "Institutional Verification Framework",

        "tvs":
            metadata["tvs_version"],

    }

    # ------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------

    lifecycle = {

        "verified_at":
            present(
                verification.verified_at,
            ),

        "published_at":
            present(
                verification.published_at,
            ),

        "locked_at":
            present(
                verification.locked_at,
            ),

    }

    performance_payload = {

        "summary": performance,

        "risk": performance,

        "assessment": performance,

        "trade_count":
            present(
                performance.get(
                    "trade_count",
                )
            ),

        "net_profit":
            present(
                performance.get(
                    "net_profit",
                )
            ),

        "gross_profit":
            present(
                performance.get(
                    "gross_profit",
                )
            ),

        "gross_loss":
            present(
                performance.get(
                    "gross_loss",
                )
            ),

        "profit_factor":
            present(
                performance.get(
                    "profit_factor",
                )
            ),

        "performance_band":
            present(
                performance.get(
                    "performance_band",
                )
            ),

    }

    #
    # ------------------------------------------------------
    # Final Context
    # ------------------------------------------------------
    #

    context = {

        #
        # Identity
        #

        "schema": schema,

        "claim": claim,

        #
        # Canonical TVS
        #

        "certificate": certificate,

        "verification": verification,

        #
        # Cover
        #

        "cover": cover,

        #
        # Report Sections
        #

        "report": report,

        "summary": {

            "score": verification.verification_score,

            "band": verification.verification_band,

            "tier": verification.verification_tier,

            "status": verification.verification_status,

        },

        "executive": verification,

        "performance": performance_payload,

        "governance": {
            "verification": verification,
            "certificate": certificate,
        },

        "evidence": {

            "verification": verification,

            "certificate": certificate,

            "tier_profile": tier_profile,

        },

        "audit": {
            "verification": verification,
            "certificate": certificate,
            "lifecycle": lifecycle,
        },

        "verdict": {
            "verification": verification,
            "certificate": certificate,
        },

        "metadata": metadata,

        "identity": {

            "certificate_hash":
                metadata["certificate_hash"],

            "claim_hash":
                metadata["claim_hash"],

            "verification_url":
                metadata["verification_url"],

            "certificate_version":
                metadata["certificate_version"],

            "tvs_version":
                metadata["tvs_version"],

        },

        "qr": {

            "verification_url":
                metadata["verification_url"],

            "claim_hash":
                verification.claim_hash,

        },

        "lifecycle": lifecycle,

    }

    return context