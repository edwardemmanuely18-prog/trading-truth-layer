from __future__ import annotations

from statistics import mean

from app.services.verification.certificate.certificate_models import (
    VerificationCertificate,
)

from app.services.verification.metric_models import (
    WorkspaceVerificationMetrics,
)

from app.services.verification.verification_models import (
    ComponentResult,
)


def _average_component(
    components: list[ComponentResult],
    *,
    name: str,
) -> ComponentResult:
    """
    Aggregates a verification component across
    multiple claim certificates.

    This performs NO verification.

    It summarizes already-computed TVS results.
    """

    if not components:

        return ComponentResult(
            name=name,
            earned_points=0.0,
            maximum_points=0.0,
            status="Unavailable",
            reason="No verified claims.",
        )

    earned = mean(
        c.earned_points
        for c in components
    )

    maximum = mean(
        c.maximum_points
        for c in components
    )

    percentage = mean(
        c.percentage
        for c in components
    )

    return ComponentResult(

        name=name,

        earned_points=round(
            earned,
            2,
        ),

        maximum_points=round(
            maximum,
            2,
        ),

        status=max(
            components,
            key=lambda c: c.percentage,
        ).status,

        reason=f"Aggregated from {len(components)} verified claims.",

        details={
            "claim_count": len(components),
            "average_percentage": round(
                percentage,
                2,
            ),
        },

    )


def build_workspace_verification_metrics(
    certificates: list[
        VerificationCertificate
    ],
) -> WorkspaceVerificationMetrics:
    """
    Aggregates claim verification certificates
    into canonical workspace verification
    metrics.

    NO verification calculations occur here.

    Every value originates from TVS.
    """

    if not certificates:

        return WorkspaceVerificationMetrics(

            workspace_id=0,

            claim_count=0,

            average_verification_score=0.0,

            verification_band="Unavailable",

            evidence=_average_component(
                [],
                name="Evidence",
            ),

            integrity=_average_component(
                [],
                name="Integrity",
            ),

            governance=_average_component(
                [],
                name="Governance",
            ),

            transparency=_average_component(
                [],
                name="Transparency",
            ),

            stability=_average_component(
                [],
                name="Stability",
            ),

            network=_average_component(
                [],
                name="Network",
            ),

            reviews=_average_component(
                [],
                name="Reviews",
            ),

            disputes=_average_component(
                [],
                name="Disputes",
            ),

        )

    workspace_id = (
        certificates[0]
        .identity
        .workspace_id
    )

    average_score = round(

        mean(

            c.summary.verification_score

            for c

            in certificates

        ),

        2,

    )

    # Highest certification band currently
    # represented in the workspace.
    verification_band = max(

        certificates,

        key=lambda c: (
            c.summary.verification_score
        ),

    ).summary.verification_band

    return WorkspaceVerificationMetrics(

        workspace_id=workspace_id,

        claim_count=len(
            certificates
        ),

        average_verification_score=average_score,

        verification_band=verification_band,

        evidence=_average_component(

            [
                c.component_scores.evidence

                for c

                in certificates
            ],

            name="Evidence",

        ),

        integrity=_average_component(

            [
                c.component_scores.integrity

                for c

                in certificates
            ],

            name="Integrity",

        ),

        governance=_average_component(

            [
                c.component_scores.governance

                for c

                in certificates
            ],

            name="Governance",

        ),

        transparency=_average_component(

            [
                c.component_scores.transparency

                for c

                in certificates
            ],

            name="Transparency",

        ),

        stability=_average_component(

            [
                c.component_scores.stability

                for c

                in certificates
            ],

            name="Stability",

        ),

        network=_average_component(

            [
                c.component_scores.network

                for c

                in certificates
            ],

            name="Network",

        ),

        reviews=_average_component(

            [
                c.component_scores.reviews

                for c

                in certificates
            ],

            name="Reviews",

        ),

        disputes=_average_component(

            [
                c.component_scores.disputes

                for c

                in certificates
            ],

            name="Disputes",

        ),

        metadata={

            "aggregation":

                "Claim Verification Certificates",

            "tvs_version":

                certificates[
                    0
                ].identity.tvs_version,

        },

    )