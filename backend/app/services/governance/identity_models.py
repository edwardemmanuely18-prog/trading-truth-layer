from __future__ import annotations

from dataclasses import dataclass, field


# ==========================================================
# PERMISSIONS
# ==========================================================

from dataclasses import dataclass, field

from .capabilities import Capability


@dataclass(slots=True)
class PermissionMatrix:

    capabilities: set[
        Capability
    ] = field(default_factory=set)

    def allows(
        self,
        capability: Capability,
    ) -> bool:

        return capability in self.capabilities


# ==========================================================
# GOVERNANCE PROFILE
# ==========================================================

@dataclass(slots=True)
class IdentityGovernanceProfile:

    user_id: int

    workspace_role: str

    authority: str

    operational_scope: list[str]

    governance_status: str

    permissions: PermissionMatrix


# ==========================================================
# WORKSPACE SNAPSHOT
# ==========================================================

@dataclass(slots=True)
class WorkspaceGovernanceSnapshot:

    workspace_id: int

    member_count: int

    owner_count: int

    operator_count: int

    auditor_count: int

    pending_invites: int

    profiles: list[
        IdentityGovernanceProfile
    ] = field(default_factory=list)

# ==========================================================
# GOVERNANCE HEALTH
# ==========================================================

from dataclasses import dataclass, field


@dataclass(slots=True)
class GovernanceFinding:

    title: str

    description: str

    severity: str


@dataclass(slots=True)
class GovernanceRecommendation:

    title: str

    description: str

    priority: str

    action: str


@dataclass(slots=True)
class GovernanceHealthComponent:

    name: str

    score: float

    healthy: bool

    findings: list[
        GovernanceFinding
    ] = field(default_factory=list)


@dataclass(slots=True)
class GovernanceHealth:

    overall_score: float

    owner: GovernanceHealthComponent

    operator: GovernanceHealthComponent

    auditor: GovernanceHealthComponent

    invitation: GovernanceHealthComponent

    permission: GovernanceHealthComponent

    coverage: GovernanceHealthComponent

    activity: GovernanceHealthComponent

    recommendations: list[
        GovernanceRecommendation
    ] = field(default_factory=list)