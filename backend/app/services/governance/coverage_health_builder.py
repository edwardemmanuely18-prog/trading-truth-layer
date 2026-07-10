from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    GovernanceFinding,
    GovernanceHealthComponent,
)


def build_coverage_health(
    context: MembershipContext,
) -> GovernanceHealthComponent:
    """
    Evaluate governance role coverage.
    """

    findings: list[GovernanceFinding] = []

    score = 100.0

    if context.total_members == 1:

        findings.append(
            GovernanceFinding(
                title="Single Identity Workspace",
                description=(
                    "Institutional governance "
                    "benefits from separation "
                    "of responsibilities."
                ),
                severity="medium",
            )
        )

        score = 75

    elif context.total_members == 0:

        findings.append(
            GovernanceFinding(
                title="Workspace has no members",
                description="No governance identities exist.",
                severity="critical",
            )
        )

        score = 0

    return GovernanceHealthComponent(

        name="Coverage Health",

        score=score,

        healthy=score >= 80,

        findings=findings,

    )