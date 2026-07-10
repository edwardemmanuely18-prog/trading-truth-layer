export type GovernanceHealth =
    | "healthy"
    | "warning"
    | "critical";

export interface GovernanceSummary {

    workspaceName: string;

    plan: string;

    memberCount: number;

    memberLimit: number;

    ownerCount: number;

    operatorCount: number;

    auditorCount: number;

    pendingInvites: number;

    governanceHealth: GovernanceHealth;

}

export interface RoleCapability {

    surface: string;

    owner: boolean;

    operator: boolean;

    auditor: boolean;

    member: boolean;

}