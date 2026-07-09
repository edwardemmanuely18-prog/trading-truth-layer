export interface WorkspaceEntitlements {

    workspace_id: number;

    plan: string;

    commercial_services: Record<string, boolean>;

    features: Record<string, boolean>;

    limits: Record<string, number>;

}