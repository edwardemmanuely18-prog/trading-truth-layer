from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    GovernanceFinding,
    GovernanceHealthComponent,
)


def build_auditor_health(
    context: MembershipContext,
) -> GovernanceHealthComponent:

    findings = []

    score = 100.0

    if context.total_auditors == 0:

        findings.append(
            GovernanceFinding(
                title="Independent Auditor Missing",
                description=(
                    "Assign an Auditor to improve "
                    "independent governance."
                ),
                severity="high",
            )
        )

        score = 60

    return GovernanceHealthComponent(

        name="Auditor Health",

        score=score,

        healthy=score >= 80,

        findings=findings,

    )