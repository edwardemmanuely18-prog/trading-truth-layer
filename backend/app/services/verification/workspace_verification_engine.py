from __future__ import annotations

from app.services.verification.workspace_verification_context import (
    WorkspaceVerificationContext,
)

from app.services.verification.verification_constants import (
    TVS_VERSION,
)

# ------------------------------------------------------------
# Evidence
# ------------------------------------------------------------

from app.services.verification.evidence.evidence_engine import (
    compute_evidence_score,
)

from app.services.verification.evidence.integrity_engine import (
    compute_integrity_score,
)

from app.services.verification.evidence.broker_provenance_engine import (
    build_claim_provenance,
)

# ------------------------------------------------------------
# Governance
# ------------------------------------------------------------

from app.services.verification.governance.governance_engine import (
    compute_governance_score,
)

from app.services.verification.governance.transparency_engine import (
    compute_transparency_score,
)

from app.services.verification.governance.stability_engine import (
    compute_stability_score,
)

from app.services.verification.governance.dispute_engine import (
    compute_dispute_score,
)

# ------------------------------------------------------------
# Intelligence
# ------------------------------------------------------------

from app.services.verification.intelligence.network_engine import (
    compute_network_score,
)

from app.services.verification.intelligence.review_engine import (
    compute_review_score,
)

from app.services.verification.intelligence.verification_band import (
    determine_verification_band,
)

# ------------------------------------------------------------
# Workspace Certificate
# ------------------------------------------------------------

from app.services.verification.certificate.workspace_certificate_builder import (
    build_workspace_verification_certificate,
)

from app.services.verification.certificate.workspace_certificate_models import (
    WorkspaceVerificationComponentSet,
)


def compute_workspace_verification_certificate(
    context: WorkspaceVerificationContext,
):
    """
    Canonical Workspace Verification Engine.

    Every workspace-level verification consumer
    inside Trading Truth Layer must call ONLY
    this engine through
    compute_workspace_certificate().

    No dashboard.

    No report.

    No allocator.

    No public page.

    computes verification independently.
    """

    evidence = compute_evidence_score(
        context
    )

    integrity = compute_integrity_score(
        context
    )

    governance = compute_governance_score(
        context
    )

    transparency = compute_transparency_score(
        context
    )

    stability = compute_stability_score(
        context
    )

    network = compute_network_score(
        context
    )

    reviews = compute_review_score(
        context
    )

    disputes = compute_dispute_score(
        context
    )

    components = (
        WorkspaceVerificationComponentSet(

            evidence=evidence,

            integrity=integrity,

            governance=governance,

            transparency=transparency,

            stability=stability,

            network=network,

            reviews=reviews,

            disputes=disputes,

        )
    )

    verification_score = (
        components.total_score
    )

    verification_band = (
        determine_verification_band(
            verification_score
        )
    )

    provenance = (
        build_claim_provenance(
            context.trades
        )
    )

    certificate = (
        build_workspace_verification_certificate(

            context=context,

            metrics=workspace_metrics,

            provenance=provenance,

            components=component_set,

            verification_score=verification_score,

            verification_band=verification_band.label,

            tvs_version=TVS_VERSION,

        )
    )

    return certificate