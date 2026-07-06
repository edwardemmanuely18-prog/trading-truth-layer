from __future__ import annotations

from app.services.verification.verification_context import (
    VerificationContext,
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
# Certificate
# ------------------------------------------------------------

from app.services.verification.certificate.certificate_builder import (
    build_verification_certificate,
)

from app.services.verification.certificate.certificate_registry import (
    certificate_registry,
)

from app.services.verification.certificate.certificate_models import (
    VerificationComponentSet,
)


def compute_verification_certificate(
    context: VerificationContext,
):
    """
    Canonical Verification Engine.

    Every verification surface inside
    Trading Truth Layer must call ONLY
    this function.

    No page should compute trust
    independently.
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

    component_set = VerificationComponentSet(

        evidence=evidence,

        integrity=integrity,

        governance=governance,

        transparency=transparency,

        stability=stability,

        network=network,

        reviews=reviews,

        disputes=disputes,

    )

    verification_score = (
        component_set.total_score
    )

    verification_band = (
        determine_verification_band(
            verification_score
        )
    )

    provenance = build_claim_provenance(
        context.trades
    )

    print("\n===== TVS SCORE BREAKDOWN =====")
    print("Claim:", context.claim_schema.id)

    print("Evidence:", evidence.earned_points)
    print("Integrity:", integrity.earned_points)
    print("Governance:", governance.earned_points)
    print("Transparency:", transparency.earned_points)
    print("Stability:", stability.earned_points)
    print("Network:", network.earned_points)
    print("Reviews:", reviews.earned_points)
    print("Disputes:", disputes.earned_points)

    print("TOTAL:", component_set.total_score)
    print("===============================\n")

    print("Trades:", len(context.trades))
    print("Members:", context.claim_schema.included_member_ids_json)
    print("Symbols:", context.claim_schema.included_symbols_json)
    print("Period:", context.claim_schema.period_start, "->", context.claim_schema.period_end)
    print()

    certificate = (
        build_verification_certificate(

            context=context,

            tvs_version=TVS_VERSION,

            verification_score=
                verification_score,

            verification_band=
                verification_band.label,

            provenance=provenance,

            components=component_set,

        )
    )

    certificate_registry.store(
        certificate
    )

    return certificate