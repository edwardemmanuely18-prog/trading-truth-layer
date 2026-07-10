from __future__ import annotations

from app.services.governance.identity_models import (
    GovernanceHealth,
    GovernanceRecommendation,
)


def build_recommendations(
    health: GovernanceHealth,
) -> list[GovernanceRecommendation]:

    recommendations = []

    for component in [

        health.owner,

        health.operator,

        health.auditor,

        health.invitation,

        health.permission,

        health.coverage,

        health.activity,

    ]:

        for finding in component.findings:

            recommendations.append(

                GovernanceRecommendation(

                    title=finding.title,

                    description=finding.description,

                    priority=finding.severity,

                    action="Review governance policy.",

                )

            )

    return recommendations