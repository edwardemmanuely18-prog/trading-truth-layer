from __future__ import annotations

import time
import uuid

from datetime import datetime

from app.services.verification.certificate.certificate_hash import (
    generate_certificate_hash,
)

from app.services.verification.certificate.certificate_models import (

    CertificateIdentity,

    IssuerIdentity,

    VerificationSummary,

    VerificationComponentSet,

    ProvenanceSummary,

    LineageSummary,

    TimelineSummary,

    VerificationDecision,

    CertificateMetadata,

    VerificationCertificate,

)


def build_verification_certificate(
    *,
    context,
    tvs_version: str,
    verification_score: float,
    verification_band: str,
    provenance,
    components,
) -> VerificationCertificate:
    """
    Builds the canonical Trading Verification
    Certificate.

    This function performs NO verification
    calculations.

    It assembles the immutable certificate from
    outputs already produced by the Verification
    Engine.
    """

    started = time.perf_counter()

    claim = context.claim_schema
    workspace = context.workspace

    payload = {

        "claim_schema_id": claim.id,

        "workspace_id": workspace.id,

        "claim_hash": claim.claim_hash,

        "scope_hash": claim.scope_hash,

        "lifecycle_hash": claim.lifecycle_hash,

        "evidence_snapshot_hash":
            claim.evidence_snapshot_hash,

        "locked_trade_set_hash":
            claim.locked_trade_set_hash,

        "verification_score":
            verification_score,

        "verification_band":
            verification_band,

        "verification_tier":
            provenance.primary_tier,

        "tvs_version":
            tvs_version,

    }

    certificate_hash = generate_certificate_hash(
        payload
    )

    identity = CertificateIdentity(

        certificate_id=str(uuid.uuid4()),

        certificate_hash=certificate_hash,

        certificate_version=1,

        tvs_version=tvs_version,

        generated_at=datetime.utcnow(),

        generated_by="Trading Verification Engine",

        claim_schema_id=claim.id,

        claim_name=claim.name,

        workspace_id=workspace.id,

        claim_hash=claim.claim_hash,

        scope_hash=claim.scope_hash,

        lifecycle_hash=claim.lifecycle_hash,

        evidence_snapshot_hash=
            claim.evidence_snapshot_hash,

        locked_trade_set_hash=
            claim.locked_trade_set_hash,

    )

    issuer = IssuerIdentity(

        workspace_id=workspace.id,

        workspace_name=getattr(
            workspace,
            "name",
            "Workspace",
        ),

        issuer_status="Active",

        issuer_rating=None,

        verified_claims=0,

        verified_trades=len(context.trades),

        average_verification_score=0.0,

    )

    summary = VerificationSummary(

        verification_score=verification_score,

        verification_band=verification_band,

        verification_tier=provenance.primary_tier,

        evidence_tier=provenance.primary_tier,

        verification_status=claim.status,

        integrity_status=components.integrity.status,

        visibility=claim.visibility,

        trade_count=len(context.trades),

        verified_at=claim.verified_at,

        published_at=claim.published_at,

        locked_at=claim.locked_at,

    )

    component_scores = VerificationComponentSet(

        evidence=components.evidence,

        integrity=components.integrity,

        governance=components.governance,

        transparency=components.transparency,

        stability=components.stability,

        network=components.network,

        reviews=components.reviews,

        disputes=components.disputes,

    )

    provenance_summary = ProvenanceSummary(

        primary_source=provenance.primary_source,

        primary_tier=provenance.primary_tier,

        tier_composition=provenance.tier_composition,

        evidence_records=len(
            context.evidence_records
        ),

        broker_connections=len(
            context.broker_connections
        ),

        verified_evidence=sum(

            1

            for record

            in context.evidence_records

            if getattr(
                record,
                "verification_state",
                "",
            ).lower() == "verified"

        ),

        fingerprints_verified=sum(

            1

            for record

            in context.evidence_records

            if getattr(
                record,
                "fingerprint",
                None,
            )

        ),

    )

    edited_trades = 0

    for event in context.audit_events:

        if (
            getattr(
                event,
                "event_type",
                "",
            ).lower()
            in {
                "trade_updated",
                "trade_edited",
                "trade_modified",
            }
        ):
            edited_trades += 1

    lineage = LineageSummary(

        total_trades=len(
            context.trades
        ),

        tier1_trades=sum(

            1

            for trade

            in context.trades

            if getattr(
                trade,
                "evidence_trust_tier",
                "",
            ) == "tier_1"

        ),

        tier2_trades=sum(

            1

            for trade

            in context.trades

            if getattr(
                trade,
                "evidence_trust_tier",
                "",
            ) == "tier_2"

        ),

        tier3_trades=sum(

            1

            for trade

            in context.trades

            if getattr(
                trade,
                "evidence_trust_tier",
                "",
            ) == "tier_3"

        ),

        manually_modified_trades=edited_trades,

        immutable_trades=sum(

            1

            for trade

            in context.trades

            if getattr(
                trade,
                "verification_state",
                "",
            ).lower() == "verified"

        ),

    )

    timeline = TimelineSummary(

        verified_at=claim.verified_at,

        published_at=claim.published_at,

        locked_at=claim.locked_at,

        latest_activity_at=claim.locked_at
        or claim.published_at
        or claim.verified_at,

        total_events=len(
            context.audit_events
        ),

    )

    decision = VerificationDecision(

        decision=verification_band,

        confidence=verification_score,

        explanation=(

            "Verification certificate generated "

            "by the Trading Verification Engine."

        ),

        strengths=[],

        weaknesses=[],

        recommendations=[

            "Maintain immutable evidence.",

            "Use Broker Synchronization for all future trades.",

            "Keep claims locked after publication.",

        ],

        warnings=[],

    )

    elapsed = round(

        time.perf_counter()
        - started,

        4,

    )

    metadata = CertificateMetadata(

        engine_version="1.0",

        tvs_version=tvs_version,

        generated_in_seconds=elapsed,

        metadata={

            **payload,

            "certificate_hash":

                certificate_hash,

            "certificate_version": 1,

            "watermark":

                "TRADING TRUTH LAYER",

            "verification_url":

                f"https://tradingtruthlayer.com/verify/{certificate_hash}",

            "generated_utc":

                datetime.utcnow().isoformat(),

        },

    )

    return VerificationCertificate(

        identity=identity,

        issuer=issuer,

        summary=summary,

        provenance=provenance_summary,

        component_scores=component_scores,

        lineage=lineage,

        timeline=timeline,

        decision=decision,

        metadata=metadata,

        evidence={

            "records": len(
                context.evidence_records
            ),

        },

        integrity={

            "alerts": len(
                context.integrity_alerts
            ),

        },

        governance={

            "audit_events": len(
                context.audit_events
            ),

        },

        network={

            "broker_connections": len(
                context.broker_connections
            ),

        },

        external_reviews={

            "reviews": len(
                context.review_statements
            ),

        },

        disputes={

            "active": len(
                context.disputes
            ),

        },

        attachments={

            "verification_certificate_pdf": None,

            "evidence_bundle_pdf": None,

            "evidence_archive": None,

        },

        links={

            "verification_url":
                f"https://tradingtruthlayer.com/verify/{certificate_hash}",

            "public_claim":
                (
                    f"https://tradingtruthlayer.com/public/claims/{claim.claim_hash}"
                    if claim.claim_hash
                    else None
                ),

            "certificate_page":
                f"https://tradingtruthlayer.com/certificate/{certificate_hash}",

            "evidence_bundle":
                f"https://tradingtruthlayer.com/evidence/{certificate_hash}",

            "issuer":
                f"https://tradingtruthlayer.com/workspaces/{workspace.id}",

            "qr_payload":
                f"https://tradingtruthlayer.com/verify/{certificate_hash}",

            "qr_caption":
                "Scan to verify this Trading Verification Certificate.",

        },

        custom={

            "certificate_watermark":

                "TRADING TRUTH LAYER",

            "certificate_footer":

                f"Certificate {certificate_hash[:16]}",

        },

    )