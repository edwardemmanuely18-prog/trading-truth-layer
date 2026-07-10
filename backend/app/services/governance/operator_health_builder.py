from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    GovernanceFinding,
    GovernanceHealthComponent,
)


def build_operator_health(
    context: MembershipContext,
) -> GovernanceHealthComponent:

    findings = []

    score = 100.0

    if context.total_operators == 0:

        findings.append(
            GovernanceFinding(
                title="No Operators Assigned",
                description=(
                    "Operational responsibilities are "
                    "currently concentrated."
                ),
                severity="medium",
            )
        )

        score = 75

    return GovernanceHealthComponent(

        name="Operator Health",

        score=score,

        healthy=score >= 80,

        findings=findings,

    )