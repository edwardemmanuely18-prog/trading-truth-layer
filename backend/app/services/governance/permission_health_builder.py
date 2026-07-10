from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    GovernanceFinding,
    GovernanceHealthComponent,
)


def build_permission_health(
    context: MembershipContext,
) -> GovernanceHealthComponent:
    """
    Evaluate permission health.

    Current implementation validates
    governance consistency.

    Future versions will evaluate:

    • Delegated authority
    • Permission overrides
    • Policy violations
    • Enterprise IAM
    """

    findings: list[GovernanceFinding] = []

    score = 100.0

    role = context.membership.role.lower()

    if role not in (
        "owner",
        "operator",
        "auditor",
        "member",
    ):

        findings.append(
            GovernanceFinding(
                title="Unknown Workspace Role",
                description=(
                    "Workspace member uses an "
                    "unrecognized governance role."
                ),
                severity="high",
            )
        )

        score = 50

    return GovernanceHealthComponent(

        name="Permission Health",

        score=score,

        healthy=score >= 80,

        findings=findings,

    )