from __future__ import annotations

"""
Trading Truth Layer

Trade Evidence System (TES)

Workspace Evidence Builder

Projects already-computed evidence analytics
into the canonical WorkspaceEvidenceMetrics
contract.

NO calculations occur here.

NO SQL occurs here.
"""

from app.services.evidence.evidence_models import (
    WorkspaceEvidenceMetrics,
    EvidenceComponent,
)


def build_workspace_evidence_metrics(
    *,
    workspace_id: int,
    analytics: dict,
) -> WorkspaceEvidenceMetrics:
    """
    Projects evidence analytics into the
    canonical TES model.

    This function performs NO evidence
    calculations.

    It only maps the canonical analytics
    payload into the institutional
    WorkspaceEvidenceMetrics contract.
    """

    analytics = analytics or {}

    overview = analytics.get(
        "overview",
        {},
    )

    verification = analytics.get(
        "verification",
        {},
    )

    tiers = analytics.get(
        "tiers",
        {},
    )

    protection = analytics.get(
        "protection",
        {},
    )

    quality = analytics.get(
        "quality",
        {},
    )

    return WorkspaceEvidenceMetrics(

        #
        # Identity
        #

        workspace_id=workspace_id,

        trade_count=int(
            overview.get(
                "records",
                0,
            )
        ),

        #
        # Verification
        #

        broker_verified=int(
            verification.get(
                "broker_verified",
                0,
            )
        ),

        verified=int(
            verification.get(
                "verified",
                0,
            )
        ),

        self_reported=int(
            verification.get(
                "self_reported",
                0,
            )
        ),

        coverage=float(
            overview.get(
                "coverage",
                0,
            )
        ),

        #
        # Provenance
        #

        tier1=int(
            tiers.get(
                "tier_1",
                0,
            )
        ),

        tier2=int(
            tiers.get(
                "tier_2",
                0,
            )
        ),

        tier3=int(
            tiers.get(
                "tier_3",
                0,
            )
        ),

        reliability=float(
            overview.get(
                "reliability",
                0,
            )
        ),

        #
        # Protection
        #

        fingerprinted=int(
            protection.get(
                "fingerprinted",
                0,
            )
        ),

        hash_protected=int(
            protection.get(
                "hash_protected",
                0,
            )
        ),

        unprotected=int(
            protection.get(
                "unprotected",
                0,
            )
        ),

        protection=float(
            overview.get(
                "protection",
                0,
            )
        ),

        #
        # Quality
        #

        quality_score=float(
            overview.get(
                "quality_score",
                0,
            )
        ),

        quality_band=overview.get(
            "quality_band",
            "Unknown",
        ),

        verification_quality=float(
            quality.get(
                "verification_quality",
                0,
            )
        ),

        protection_quality=float(
            quality.get(
                "protection_quality",
                0,
            )
        ),

        completeness_quality=float(
            quality.get(
                "completeness_quality",
                0,
            )
        ),

        import_quality=float(
            quality.get(
                "import_quality",
                0,
            )
        ),

        #
        # Institutional Components
        #

        evidence=EvidenceComponent(

            name="Evidence Coverage",

            value=float(
                overview.get(
                    "coverage",
                    0,
                )
            ),

            maximum=100,

            percentage=float(
                overview.get(
                    "coverage",
                    0,
                )
            ),

            status="Computed",

            reason="Projected from canonical evidence analytics.",
        ),

        provenance=EvidenceComponent(

            name="Evidence Provenance",

            value=float(
                overview.get(
                    "reliability",
                    0,
                )
            ),

            maximum=100,

            percentage=float(
                overview.get(
                    "reliability",
                    0,
                )
            ),

            status="Computed",

            reason="Projected from canonical evidence analytics.",
        ),

        protection_component=EvidenceComponent(

            name="Evidence Protection",

            value=float(
                overview.get(
                    "protection",
                    0,
                )
            ),

            maximum=100,

            percentage=float(
                overview.get(
                    "protection",
                    0,
                )
            ),

            status="Computed",

            reason="Projected from canonical evidence analytics.",
        ),

        quality=EvidenceComponent(

            name="Evidence Quality",

            value=float(
                overview.get(
                    "quality_score",
                    0,
                )
            ),

            maximum=100,

            percentage=float(
                overview.get(
                    "quality_score",
                    0,
                )
            ),

            status=overview.get(
                "quality_band",
                "Unknown",
            ),

            reason="Projected from canonical evidence analytics.",
        ),

        #
        # Monitoring
        #

        monitoring_feed=list(
            analytics.get(
                "feed",
                [],
            )
        ),

        exception_registry=list(
            analytics.get(
                "exceptions",
                [],
            )
        ),

        metadata={

            "tes_version": "1.0",

            "engine":

                "Trade Evidence System",

            "projection":

                "Workspace Evidence Metrics",

        },

    )