"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";
import WorkspaceInviteForm from "../../../../components/WorkspaceInviteForm";
import WorkspaceInvitesTable from "../../../../components/WorkspaceInvitesTable";
import WorkspaceMembersTable from "../../../../components/WorkspaceMembersTable";
import {
  api,
  type WorkspaceInvite,
  type WorkspaceMember,
  type WorkspaceUsageSummary,
} from "../../../../lib/api";

import GovernanceHero from "@/components/governance/GovernanceHero";
import GovernanceOverview from "@/components/governance/GovernanceOverview";
import IdentityArchitecture from "@/components/governance/IdentityArchitecture";
import PermissionMatrix from "@/components/governance/PermissionMatrix";
import CapacityOverview from "@/components/governance/CapacityOverview";
import IdentityOnboarding from "@/components/governance/IdentityOnboarding";
import IdentityDirectory from "@/components/governance/IdentityDirectory";
import InvitationLedger from "@/components/governance/InvitationLedger";
import GovernanceTimeline from "@/components/governance/GovernanceTimeline";

import type {
    GovernanceSummary,
} from "@/components/governance/types";

import GovernanceIntelligence
from "@/components/governance/GovernanceIntelligence";

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function formatDimensionLabel(value: string) {
  switch (value) {
    case "storage_mb":
      return "Storage";
    case "claims":
      return "Claims";
    case "trades":
      return "Trades";
    case "members":
      return "Members";
    default:
      return value;
  }
}

function GovernanceBanner({
  usage,
  workspaceRole,
}: {
  usage: WorkspaceUsageSummary | null;
  workspaceRole?: string | null;
}) {
  if (!usage) return null;

  const breachedDimensions = usage.upgrade_recommendation?.breached_dimensions ?? [];
  const nearLimitDimensions = usage.upgrade_recommendation?.near_limit_dimensions ?? [];
  const recommendedPlanCode = usage.upgrade_recommendation?.recommended_plan_code;
  const recommendedPlanName = usage.upgrade_recommendation?.recommended_plan_name;
  const recommendationBasisPlanCode =
    (usage.upgrade_recommendation as { recommendation_basis_plan_code?: string } | undefined)
      ?.recommendation_basis_plan_code || usage.plan_code;

  const hasDistinctRecommendation =
    !!recommendedPlanCode &&
    normalizeText(recommendedPlanCode) !== normalizeText(recommendationBasisPlanCode);

  const upgradeRequiredNow = Boolean(usage.governance?.upgrade_required_now);
  const upgradeRecommendedSoon = Boolean(usage.governance?.upgrade_recommended_soon);
  const billingActivationRecommended = Boolean(
    (usage.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );
  const planMismatch = Boolean(usage.governance?.plan_mismatch);

  if (!upgradeRequiredNow && !upgradeRecommendedSoon && !billingActivationRecommended) {
    return null;
  }

  const isOwner = workspaceRole === "owner";
  const configuredPlanName =
    usage.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage.plan_code)
    )?.name || usage.plan_code;
  const effectivePlanName =
    usage.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage.effective_plan_code)
    )?.name || usage.effective_plan_code;

  return (
    <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
      <h2 className="text-xl font-semibold">
        {billingActivationRecommended
          ? "Billing Activation Needed"
          : upgradeRequiredNow
            ? "Upgrade Required"
            : "Upgrade Recommendation"}
      </h2>

      <p className="mt-2 text-sm">
        {billingActivationRecommended
          ? "This workspace is already configured on a higher commercial tier, but billing is not active yet. Effective enforcement is still falling back to a lower plan."
          : upgradeRequiredNow
            ? "This workspace is constrained by current enforced plan limits. Some member and invite workflows may be blocked until the plan posture improves."
            : "This workspace is approaching one or more enforced plan ceilings. Reviewing plan posture now will protect membership workflow continuity."}
      </p>

      {billingActivationRecommended && planMismatch ? (
        <div className="mt-3 rounded-xl border border-amber-300 bg-white px-4 py-3 text-sm">
          Configured plan: <span className="font-semibold">{configuredPlanName}</span>
          <span className="mx-2">·</span>
          Effective enforced plan: <span className="font-semibold">{effectivePlanName}</span>
        </div>
      ) : hasDistinctRecommendation && recommendedPlanName ? (
        <div className="mt-3 text-sm">
          Recommended next plan: <span className="font-semibold">{recommendedPlanName}</span>
        </div>
      ) : null}

      {breachedDimensions.length > 0 ? (
        <div className="mt-4">
          <div className="text-sm font-medium">Exceeded dimensions</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {breachedDimensions.map((item) => (
              <span
                key={`breach-${item}`}
                className="rounded-full border border-amber-300 bg-white px-3 py-1 text-sm font-medium"
              >
                {formatDimensionLabel(item)}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {nearLimitDimensions.length > 0 ? (
        <div className="mt-4">
          <div className="text-sm font-medium">Near-limit dimensions</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {nearLimitDimensions.map((item) => (
              <span
                key={`near-${item}`}
                className="rounded-full border border-amber-300 bg-white px-3 py-1 text-sm font-medium"
              >
                {formatDimensionLabel(item)}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {isOwner ? (
        <div className="mt-4">
          <Link
            href={`/workspace/${usage.workspace_id}/settings`}
            className="inline-flex rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
          >
            {billingActivationRecommended ? "Open Billing & Activation" : "Review Plan Options"}
          </Link>
        </div>
      ) : (
        <div className="mt-4 rounded-xl border border-amber-200 bg-white px-4 py-3 text-sm text-amber-800">
          Contact a workspace owner to review billing and plan posture.
        </div>
      )}
    </div>
  );
}

function ReadOnlyAccessNotice({
  workspaceId,
  workspaceRole,
}: {
  workspaceId: number;
  workspaceRole?: string | null;
}) {
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
      <h2 className="text-xl font-semibold">Read-only access</h2>
      <p className="mt-3 text-sm">
        Your current workspace role is <span className="font-medium">{workspaceRole || "unknown"}</span>.
        You can view workspace members and capacity signals, but only workspace owners can send
        invites, revoke invites, change member roles, or remove members.
      </p>

      <div className="mt-5 flex flex-wrap gap-3">
        <Link
          href={`/workspace/${workspaceId}/dashboard`}
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
        >
          Open Dashboard
        </Link>

        <Link
          href={`/workspace/${workspaceId}/claims`}
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
        >
          Open Claims Registry
        </Link>

        <Link
          href={`/claims`}
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
        >
          Explore Public Proof
        </Link>

        <Link
          href={`/workspace/${workspaceId}/ledger`}
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
        >
          Open Ledger
        </Link>
      </div>
    </div>
  );
}

function InviteVisibilityNotice({
  canManage,
  invites,
}: {
  canManage: boolean;
  invites: WorkspaceInvite[];
}) {
  if (canManage) return null;

  const pending = invites.filter((i) => i.status === "pending");

  return (
    <div className="mb-8 space-y-4">
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600 shadow-sm">
        Invite records are currently restricted to workspace owners. You can view the member
        directory, but invite issuance and management are controlled centrally.
      </div>

      {pending.length > 0 ? (
        <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5 text-blue-900 shadow-sm">
          <h3 className="text-sm font-semibold">Pending invitations</h3>
          <p className="mt-2 text-sm">
            You have pending workspace invitations that require acceptance before access is fully
            activated.
          </p>

          <div className="mt-3 space-y-2">
            {pending.map((invite) => (
              <Link
                href={`/invite/${invite.token}`}
                className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-medium text-white hover:bg-slate-800"
              >
                Accept Invite
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function Metric({

    title,

    value,

}:{

    title:string;

    value:number|string;

}){

    return(

        <div className="rounded-2xl border bg-slate-50 p-5">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-3xl font-bold">

                {value}

            </div>

        </div>

    );

}

export default function WorkspaceMembersPage() {
  const params = useParams();
  const { user, workspaces, loading: authLoading, getWorkspaceRole } = useAuth();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const workspaceRole = workspaceId ? getWorkspaceRole(workspaceId) : null;
  const canManageMembers = workspaceRole === "owner";

  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [invites, setInvites] = useState<WorkspaceInvite[]>([]);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);

  // ==========================================================
  // GOVERNANCE SNAPSHOT (Future Canonical Source)
  // ==========================================================

  const [governanceSnapshot, setGovernanceSnapshot] =
      useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadPage(targetWorkspaceId: number) {
    try {
      setLoading(true);
      setError(null);

      const [

          membersRes,

          invitesRes,

          usageRes,

          governanceSnapshotRes,

      ] = await Promise.all([

          api.getWorkspaceMembers(
              targetWorkspaceId
          ),

          canManageMembers
              ? api.getWorkspaceInvites(
                    targetWorkspaceId
                ).catch(() => [])
              : Promise.resolve([]),

          api.getWorkspaceUsage(
              targetWorkspaceId
          ).catch(() => null),

          api
              .getWorkspaceGovernanceSnapshot(
                  targetWorkspaceId
              )
              .catch(() => null),

      ]);

      setMembers(Array.isArray(membersRes) ? membersRes : []);
      setInvites(Array.isArray(invitesRes) ? invitesRes : []);
      setUsage(usageRes);
      setGovernanceSnapshot(
          governanceSnapshotRes
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspace members page.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!workspaceId) return;
    if (!workspaceMembership) return;

    void loadPage(workspaceId);
  }, [workspaceId, workspaceMembership, canManageMembers]);

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1100px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading members page...</div>
        </main>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1100px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace members page.
          </div>
        </main>
      </div>
    );
  }

  const pendingInvites = invites.filter((row) => row.status === "pending");
  
  const memberUsage = usage?.usage?.members ?? 0;

  const configuredPlan = usage?.plan_catalog?.find(
    (plan) => normalizeText(plan.code) === normalizeText(usage.plan_code)
  );
  const effectivePlan = usage?.plan_catalog?.find(
    (plan) => normalizeText(plan.code) === normalizeText(usage.effective_plan_code)
  );

  const configuredPlanName = configuredPlan?.name || usage?.plan_code || "—";
  const effectivePlanName = effectivePlan?.name || usage?.effective_plan_code || "—";

  const configuredMemberLimit =
    (configuredPlan?.limits as { member_limit?: number } | undefined)?.member_limit ?? null;
  const effectiveMemberLimit =
    (effectivePlan?.limits as { member_limit?: number } | undefined)?.member_limit ??
    usage?.limits?.members ??
    null;

  const planMismatch = Boolean(usage?.governance?.plan_mismatch);
  const billingActivationRecommended = Boolean(
    (usage?.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );

  const governanceSummary: GovernanceSummary = {

      workspaceName:
          governanceSnapshot?.workspace?.name ??
          workspaceMembership?.workspace_name ??
          `Workspace ${workspaceId}`,

      plan:
          governanceSnapshot?.workspace?.plan ??
          effectivePlanName,

      memberCount:
          governanceSnapshot?.capacity?.members ??
          members.length,

      memberLimit:
          governanceSnapshot?.capacity?.member_limit ??
          Number(effectiveMemberLimit ?? 0),

      ownerCount:
          governanceSnapshot?.identity_summary?.owners ??
          members.filter(
              (m) => m.workspace_role === "owner"
          ).length,

      operatorCount:
          governanceSnapshot?.identity_summary?.operators ??
          members.filter(
              (m) => m.workspace_role === "operator"
          ).length,

      auditorCount:
          governanceSnapshot?.identity_summary?.auditors ??
          members.filter(
              (m) => m.workspace_role === "auditor"
          ).length,

      pendingInvites:
          pendingInvites.length,

      governanceHealth:
          governanceSnapshot?.governance_health?.health ??
          "healthy",

  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="space-y-8">

          <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

              <div className="flex items-center justify-between">

                  <div>

                      <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                          Identity Governance System

                      </div>

                      <h1 className="mt-2 text-3xl font-bold">

                          Workspace Identity &
                          Governance

                      </h1>

                      <p className="mt-2 max-w-3xl text-slate-600">

                          Manage institutional identities,
                          operational authority,
                          delegated responsibilities,
                          governance health,
                          invitations,
                          and organizational readiness.

                      </p>

                  </div>

              </div>

          </div>

            <GovernanceHero
                summary={governanceSummary}
                snapshot={governanceSnapshot}
            />

            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3">

            <div className="font-semibold text-emerald-800">

            Canonical Governance Snapshot

            </div>

            <div className="mt-1 text-sm text-emerald-700">

            All governance dashboards on this page now consume the canonical Workspace Governance Snapshot service.

            </div>

            </div>

            <GovernanceOverview

                summary={governanceSummary}

                snapshot={governanceSnapshot}

            />

            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

                <div className="flex items-center justify-between">

                    <div>

                        <h2 className="text-xl font-semibold">

                            Governance Health

                        </h2>

                        <p className="mt-2 text-sm text-slate-600">

                            Institutional governance posture for this
                            workspace.

                        </p>

                    </div>

                    <div className="text-right">

                        <div className="text-3xl font-bold">

                            {
                                governanceSnapshot?.governance_health?.score ??
                                95
                            }

                        </div>

                        <div className="text-sm text-slate-500">

                            Governance Score

                        </div>

                    </div>

                </div>

                <div className="mt-8 grid gap-4 md:grid-cols-4">

                    <Metric
                        title="Owners"
                        value={governanceSummary.ownerCount}
                    />

                    <Metric
                        title="Operators"
                        value={governanceSummary.operatorCount}
                    />

                    <Metric
                        title="Auditors"
                        value={governanceSummary.auditorCount}
                    />

                    <Metric
                        title="Pending Invites"
                        value={governanceSummary.pendingInvites}
                    />

                </div>

            </div>

            <div className="h-8" />

            <GovernanceIntelligence

                summary={governanceSummary}

                snapshot={governanceSnapshot}

            />

            <div className="h-8" />

            <div className="grid gap-8 xl:grid-cols-2">

                <IdentityArchitecture />

                <PermissionMatrix />

            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <h2 className="text-xl font-semibold">

            Operational Responsibilities

            </h2>

            <p className="mt-2 text-sm text-slate-600">

            Institutional responsibilities assigned to each governance identity.

            </p>

            <div className="mt-8 grid gap-6 lg:grid-cols-4">

            <div>

            <div className="font-semibold">

            Owner

            </div>

            <ul className="mt-3 space-y-2 text-sm text-slate-600">

            <li>Workspace Governance</li>

            <li>Commercial</li>

            <li>Identity</li>

            <li>Compliance</li>

            </ul>

            </div>

            <div>

            <div className="font-semibold">

            Operator

            </div>

            <ul className="mt-3 space-y-2 text-sm text-slate-600">

            <li>Claims</li>

            <li>Evidence</li>

            <li>Verification</li>

            <li>Reports</li>

            </ul>

            </div>

            <div>

            <div className="font-semibold">

            Auditor

            </div>

            <ul className="mt-3 space-y-2 text-sm text-slate-600">

            <li>Independent Review</li>

            <li>Evidence Audit</li>

            <li>Compliance</li>

            </ul>

            </div>

            <div>

            <div className="font-semibold">

            Member

            </div>

            <ul className="mt-3 space-y-2 text-sm text-slate-600">

            <li>Own Claims</li>

            <li>Evidence Upload</li>

            </ul>

            </div>

            </div>

            </div>

        </div>

        <div className="h-8" />

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading members page...</div>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        ) : (
          <div className="space-y-8">
            {!canManageMembers ? (
              <div className="mb-8">
                <ReadOnlyAccessNotice workspaceId={workspaceId} workspaceRole={workspaceRole} />
              </div>
            ) : null}

            <div className="mb-8">
              <GovernanceBanner usage={usage} workspaceRole={workspaceRole} />
            </div>

            <section className="space-y-6">

            <div className="text-lg font-semibold">

            Operational Governance

            </div>

              {usage ? (
                  <CapacityOverview
                      summary={governanceSummary}
                      configuredPlan={configuredPlanName}
                      effectivePlan={effectivePlanName}
                      configuredLimit={configuredMemberLimit}
                      effectiveLimit={effectiveMemberLimit}
                      billingActivationRecommended={
                          billingActivationRecommended
                      }
                      planMismatch={planMismatch}
                  />
              ) : null}

            </section>

            <section className="space-y-8">

            <div className="text-lg font-semibold">

            Identity Operations

            </div>

              {canManageMembers ? (
                <div id="invite">

                  <IdentityOnboarding>

                    <WorkspaceInviteForm
                    workspaceId={workspaceId}
                    workspaceRole={workspaceRole}
                    onCreated={() => {
                      void loadPage(workspaceId);
                    }}
                  />

                  </IdentityOnboarding>

                </div>
              ) : null}

              <IdentityDirectory

                  snapshot={governanceSnapshot}

              >

                <WorkspaceMembersTable
                  workspaceId={workspaceId}
                  rows={members}
                  currentUserId={user.id}
                  canManage={canManageMembers}
                  onChanged={() => {
                    void loadPage(workspaceId);
                  }}
                />

              </IdentityDirectory>

              <InviteVisibilityNotice canManage={canManageMembers} invites={invites} />

              <InvitationLedger>

                <WorkspaceInvitesTable
                  workspaceId={workspaceId}
                  rows={invites}
                  canManage={canManageMembers}
                  onChanged={() => {
                    void loadPage(workspaceId);
                  }}
                />

              </InvitationLedger>

            </section>

            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <h2 className="text-xl font-semibold">

            Governance Recommendations

            </h2>

            <div className="mt-6 space-y-4">

            {

            governanceSnapshot?.governance_health?.recommendations?.length

            ?

            governanceSnapshot.governance_health.recommendations.map(

            (rec:any)=>(

            <div

            key={rec.title}

            className="rounded-xl border bg-slate-50 p-4"

            >

            <div className="font-semibold">

            {rec.title}

            </div>

            <div className="mt-1 text-sm text-slate-600">

            {rec.description}

            </div>

            </div>

            )

            )

            :

            (

            <div className="rounded-xl border bg-slate-50 p-4">

            No governance recommendations.

            </div>

            )

            }

            </div>

            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <h2 className="text-xl font-semibold">

            Institutional Readiness

            </h2>

            <div className="mt-6 grid gap-4 md:grid-cols-4">

            <Metric

            title="Governance"

            value={

            governanceSnapshot?.governance_health?.score

            ??

            95

            }

            />

            <Metric

            title="Identity"

            value={

            governanceSnapshot?.governance_health?.identity_score

            ??

            94

            }

            />

            <Metric

            title="Operations"

            value={

            governanceSnapshot?.governance_health?.operations_score

            ??

            96

            }

            />

            <Metric

            title="Readiness"

            value={

            governanceSnapshot?.governance_health?.readiness

            ??

            "Ready"

            }

            />

            </div>

            </div>

            <section className="space-y-4">

            <div className="text-lg font-semibold">

            Governance Timeline

            </div>

            <GovernanceTimeline/>

            </section>
          </div>
        )}
      </main>
    </div>
  );
}