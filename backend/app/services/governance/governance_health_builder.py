from __future__ import annotations

from app.services.governance.identity_models import (
    GovernanceHealth,
)

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from .owner_health_builder import (
    build_owner_health,
)

from .operator_health_builder import (
    build_operator_health,
)

from .auditor_health_builder import (
    build_auditor_health,
)

from .invitation_health_builder import (
    build_invitation_health,
)

from .governance_policy import (
    OWNER_WEIGHT,
    OPERATOR_WEIGHT,
    AUDITOR_WEIGHT,
    INVITATION_WEIGHT,
    PERMISSION_WEIGHT,
    COVERAGE_WEIGHT,
    ACTIVITY_WEIGHT,
)

from .permission_health_builder import (
    build_permission_health,
)

from .coverage_health_builder import (
    build_coverage_health,
)

from .identity_activity_builder import (
    build_identity_activity,
)

from .recommendation_builder import (
    build_recommendations,
)

from app.services.governance.identity_models import (
    GovernanceHealthComponent,
)


# ==========================================================
# PUBLIC API
# ==========================================================

def build_governance_health(
    context: MembershipContext,
) -> GovernanceHealth:

    owner = build_owner_health(context)

    operator = build_operator_health(context)

    auditor = build_auditor_health(context)

    invitation = build_invitation_health(context)

    permission = build_permission_health(
        context
    )

    coverage = build_coverage_health(
        context
    )

    # TODO:
    # Replace the temporary activity health component
    # once activity_health_builder.py is introduced.
    activity_model = build_identity_activity()

    activity = GovernanceHealthComponent(
        name="Activity Health",
        score=100.0,
        healthy=True,
        findings=[],
    )

    overall_score = (

        owner.score * OWNER_WEIGHT +

        operator.score * OPERATOR_WEIGHT +

        auditor.score * AUDITOR_WEIGHT +

        invitation.score * INVITATION_WEIGHT +

        permission.score * PERMISSION_WEIGHT +

        coverage.score * COVERAGE_WEIGHT +

        activity.score * ACTIVITY_WEIGHT

    )

    temporary_health = GovernanceHealth(

        overall_score=0,

        owner=owner,

        operator=operator,

        auditor=auditor,

        invitation=invitation,

        permission=permission,

        coverage=coverage,

        activity=activity,

        recommendations=[],
    )

    recommendations = build_recommendations(
        temporary_health
    )

    return GovernanceHealth(

        overall_score=round(

            overall_score,

            2,

        ),

        owner=owner,

        operator=operator,

        auditor=auditor,

        invitation=invitation,

        permission=permission,

        coverage=coverage,

        activity=activity,

        recommendations=recommendations,

    )