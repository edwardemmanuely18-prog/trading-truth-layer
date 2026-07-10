from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    GovernanceFinding,
    GovernanceHealthComponent,
)


COMPONENT_NAME = "Owner Health"


def build_owner_health(
    context: MembershipContext,
) -> GovernanceHealthComponent:
    """
    Evaluate workspace ownership health.

    This builder is intentionally isolated from all
    other governance builders.
    """

    findings: list[GovernanceFinding] = []

    score = 100.0

    if context.total_owners == 0:

        findings.append(
            GovernanceFinding(
                title="Workspace has no Owner",
                description=(
                    "Every workspace should have at least "
                    "one Owner."
                ),
                severity="critical",
            )
        )

        score = 0

    elif context.total_owners == 1:

        findings.append(
            GovernanceFinding(
                title="Single Owner",
                description=(
                    "Consider assigning a secondary Owner "
                    "to improve governance resilience."
                ),
                severity="low",
            )
        )

        score = 90

    return GovernanceHealthComponent(

        name=COMPONENT_NAME,

        score=score,

        healthy=score >= 80,

        findings=findings,

    )