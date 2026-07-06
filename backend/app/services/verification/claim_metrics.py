from __future__ import annotations

from app.services.verification.certificate.certificate_models import (
    VerificationCertificate,
)

from app.services.verification.metric_models import (
    ClaimVerificationMetrics,
)


def build_claim_verification_metrics(
    certificate: VerificationCertificate,
) -> ClaimVerificationMetrics:
    """
    Projects a VerificationCertificate into the
    canonical ClaimVerificationMetrics contract.

    This function performs NO verification.

    It performs NO database access.

    It performs NO business logic.

    Every single-claim verification surface
    inside Trading Truth Layer should consume
    this object instead of reading directly from
    the certificate.
    """

    return ClaimVerificationMetrics(

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        claim_schema_id=(
            certificate.identity.claim_schema_id
        ),

        workspace_id=(
            certificate.identity.workspace_id
        ),

        claim_hash=(
            certificate.identity.claim_hash
        ),

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        verification_score=(
            certificate.summary.verification_score
        ),

        verification_band=(
            certificate.summary.verification_band
        ),

        verification_tier=(
            certificate.summary.verification_tier
        ),

        verification_status=(
            certificate.summary.verification_status
        ),

        # --------------------------------------------------
        # Institutional Evidence Profile
        # --------------------------------------------------

        primary_tier=(
            certificate.provenance.primary_tier
        ),

        primary_source=(
            certificate.provenance.primary_source
        ),

        tier1_count=(
            certificate.provenance.tier_composition.tier1_count
        ),

        tier2_count=(
            certificate.provenance.tier_composition.tier2_count
        ),

        tier3_count=(
            certificate.provenance.tier_composition.tier3_count
        ),

        tier1_percent=(
            certificate.provenance.tier_composition.tier1_percent
        ),

        tier2_percent=(
            certificate.provenance.tier_composition.tier2_percent
        ),

        tier3_percent=(
            certificate.provenance.tier_composition.tier3_percent
        ),

        # --------------------------------------------------
        # Components
        # --------------------------------------------------

        evidence=(
            certificate.component_scores.evidence
        ),

        integrity=(
            certificate.component_scores.integrity
        ),

        governance=(
            certificate.component_scores.governance
        ),

        transparency=(
            certificate.component_scores.transparency
        ),

        stability=(
            certificate.component_scores.stability
        ),

        network=(
            certificate.component_scores.network
        ),

        reviews=(
            certificate.component_scores.reviews
        ),

        disputes=(
            certificate.component_scores.disputes
        ),

        # --------------------------------------------------
        # Timeline
        # --------------------------------------------------

        verified_at=(
            certificate.timeline.verified_at
        ),

        published_at=(
            certificate.timeline.published_at
        ),

        locked_at=(
            certificate.timeline.locked_at
        ),

        # --------------------------------------------------
        # Decision
        # --------------------------------------------------

        decision=(
            certificate.decision.decision
        ),

        confidence=(
            certificate.decision.confidence
        ),

        warnings=list(
            certificate.decision.warnings
        ),

        recommendations=list(
            certificate.decision.recommendations
        ),

        metadata={

            #
            # Certificate Identity
            #

            "certificate_hash":
                certificate.identity.certificate_hash,

            "certificate_version":
                certificate.identity.certificate_version,

            "tvs_version":
                certificate.identity.tvs_version,

            "verification_id":
                certificate.identity.certificate_id,

            #
            # Claim Identity
            #

            "workspace_id":
                certificate.identity.workspace_id,

            "claim_schema_id":
                certificate.identity.claim_schema_id,

            "claim_hash":
                certificate.identity.claim_hash,

            #
            # Institutional Evidence Profile
            #

            "primary_tier":
                certificate.provenance.primary_tier,

            "primary_source":
                certificate.provenance.primary_source,

            "tier1_count":
                certificate.provenance.tier_composition.tier1_count,

            "tier2_count":
                certificate.provenance.tier_composition.tier2_count,

            "tier3_count":
                certificate.provenance.tier_composition.tier3_count,

            "tier1_percent":
                certificate.provenance.tier_composition.tier1_percent,

            "tier2_percent":
                certificate.provenance.tier_composition.tier2_percent,

            "tier3_percent":
                certificate.provenance.tier_composition.tier3_percent,

        },

        identity={

            "certificate_hash":
                certificate.identity.certificate_hash,

            "claim_hash":
                certificate.identity.claim_hash,

            "certificate_version":
                certificate.identity.certificate_version,

            "tvs_version":
                certificate.identity.tvs_version,

        },

    )