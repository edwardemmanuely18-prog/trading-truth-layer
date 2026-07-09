from __future__ import annotations

import hashlib
from datetime import datetime
from uuid import uuid4

from app.services.verification.certificate.workspace_certificate_models import (
    WorkspaceCertificateIdentity,
    WorkspaceVerificationSummary,
    WorkspaceProvenance,
    WorkspaceVerificationDecision,
    WorkspaceCertificateMetadata,
    WorkspaceVerificationCertificate,
)

from app.services.verification.workspace_verification_context import (
    WorkspaceVerificationContext,
)


def build_workspace_verification_certificate(
    *,
    context: WorkspaceVerificationContext,
    tvs_version: str,
    verification_score: float,
    verification_band: str,
    provenance,
    components,
):
    """
    Canonical Workspace Verification Certificate Builder.

    No verification mathematics belong here.

    This builder simply assembles the immutable
    WorkspaceVerificationCertificate consumed by every
    workspace-level verification surface.
    """

    workspace = context.workspace

    now = datetime.utcnow()

    certificate_id = str(uuid4())

    certificate_hash = hashlib.sha256(

        (
            f"{workspace.id}"
            f"{verification_score}"
            f"{verification_band}"
            f"{now.isoformat()}"
        ).encode()

    ).hexdigest()

    identity = WorkspaceCertificateIdentity(

        certificate_id=certificate_id,

        certificate_hash=certificate_hash,

        certificate_version=1,

        tvs_version=tvs_version,

        generated_at=now,

        generated_by="Trading Truth Layer",

        workspace_id=workspace.id,

    )

    summary = WorkspaceVerificationSummary(

        verification_score=verification_score,

        verification_band=verification_band,

        verification_tier=verification_band,

        verification_status="verified",

        workspace_name=workspace.name,

        total_trades=len(context.trades),

        total_claims=len(context.claims),

        locked_claims=len(context.locked_claims),

        verified_claims=len(context.published_claims),

    )

    performance = context.performance_metrics

    risk = context.risk_metrics

    allocator = context.allocator_metrics

    decision = WorkspaceVerificationDecision(

        decision="VERIFIED",

        confidence=verification_score,

        explanation=(
            "Workspace verification completed successfully."
        ),

    )

    metadata = WorkspaceCertificateMetadata(

        engine_version=tvs_version,

        tvs_version=tvs_version,

        generated_in_seconds=0.0,

    )

    return WorkspaceVerificationCertificate(

        identity=identity,

        summary=summary,

        performance=performance,

        risk=risk,

        allocator=allocator,

        component_scores=components,

        provenance=WorkspaceProvenance(

            primary_source=provenance.primary_source,

            primary_tier=provenance.primary_tier,

            tier_composition=provenance.tier_composition,

            verified_evidence=provenance.verified_evidence,

            evidence_records=provenance.evidence_records,

            broker_connections=provenance.broker_connections,

        ),

        decision=decision,

        metadata=metadata,

        evidence=context.analytics_result,

        integrity=context.integrity_dashboard,

        governance={},

        network=context.network_result,

        reviews={},

        disputes={},

        analytics=context.analytics_result,

        custom=context.metadata,

    )