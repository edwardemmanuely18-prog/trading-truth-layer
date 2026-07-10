from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    GovernanceFinding,
    GovernanceHealthComponent,
)


def build_invitation_health(
    context: MembershipContext,
) -> GovernanceHealthComponent:

    findings = []

    score = 100.0

    if context.pending_invites > 10:

        findings.append(
            GovernanceFinding(
                title="High Pending Invitation Count",
                description=(
                    "Large numbers of pending invitations "
                    "may indicate governance friction."
                ),
                severity="medium",
            )
        )

        score = 80

    return GovernanceHealthComponent(

        name="Invitation Health",

        score=score,

        healthy=score >= 80,

        findings=findings,

    )