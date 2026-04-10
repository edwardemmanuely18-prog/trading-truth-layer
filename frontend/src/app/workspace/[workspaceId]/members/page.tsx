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

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
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

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
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
                key={invite.id}
                href={`/invite/${invite.token}`}
                className="block rounded-xl border border-blue-300 bg-white px-4 py-2 text-sm font-medium hover:bg-blue-100"
              >
                Accept invite → {invite.email}
              </Link>
            ))}
          </div>
        </div>
      ) : null}
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadPage(targetWorkspaceId: number) {
    try {
      setLoading(true);
      setError(null);

      const [membersRes, invitesRes, usageRes] = await Promise.all([
        api.getWorkspaceMembers(targetWorkspaceId),
        canManageMembers ? api.getWorkspaceInvites(targetWorkspaceId).catch(() => []) : Promise.resolve([]),
        api.getWorkspaceUsage(targetWorkspaceId).catch(() => null),
      ]);

      setMembers(Array.isArray(membersRes) ? membersRes : []);
      setInvites(Array.isArray(invitesRes) ? invitesRes : []);
      setUsage(usageRes);
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
  const acceptedInvites = invites.filter((row) => row.status === "accepted");
  const memberUsage = usage?.usage.members;

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
    memberUsage?.limit ??
    null;

  const planMismatch = Boolean(usage?.governance?.plan_mismatch);
  const billingActivationRecommended = Boolean(
    (usage?.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Access Control</div>
            <h1 className="mt-2 text-4xl font-bold">
              Workspace Access & Identity Control
            </h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Govern membership, identity access, invitation lifecycle, and capacity enforcement
              for workspace {workspaceId}.
            </p>
          </div>

          <div className="rounded-2xl border bg-white px-5 py-4 shadow-sm">

            {canManageMembers ? (
              <Link
                href={`/workspace/${workspaceId}/members#invite`}
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Invite Member
              </Link>
            ) : null}
            <div className="text-sm text-slate-500">Workspace Role</div>
            <div className="mt-2 text-xl font-semibold">{workspaceRole || "unknown"}</div>
          </div>
        </div>

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading members page...</div>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        ) : (
          <>
            {!canManageMembers ? (
              <div className="mb-8">
                <ReadOnlyAccessNotice workspaceId={workspaceId} workspaceRole={workspaceRole} />
              </div>
            ) : null}

            <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-lg font-semibold">Invitation Lifecycle</h2>
              <p className="mt-2 text-sm text-slate-600">
                Workspace membership is governed through a controlled invitation system.
                Invitations define identity onboarding into the workspace and enforce role,
                capacity, and verification boundaries.
              </p>

              <div className="mt-4 grid gap-3 md:grid-cols-3 text-sm">
                <div className="rounded-xl border bg-slate-50 p-4">
                  <div className="font-semibold">Issued</div>
                  <div className="mt-1 text-slate-600">
                    Invitation is created and sent to a target identity.
                  </div>
                </div>

                <div className="rounded-xl border bg-slate-50 p-4">
                  <div className="font-semibold">Pending</div>
                  <div className="mt-1 text-slate-600">
                    Awaiting acceptance via secure invite token.
                  </div>
                </div>

                <div className="rounded-xl border bg-slate-50 p-4">
                  <div className="font-semibold">Accepted</div>
                  <div className="mt-1 text-slate-600">
                    Identity is bound to workspace with enforced role permissions.
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <SummaryCard
                label="Members"
                value={members.length}
                hint={
                  memberUsage
                    ? `${memberUsage.used} / ${effectiveMemberLimit ?? memberUsage.limit} enforced`
                    : "Current directory size"
                }
              />
              <SummaryCard
                label="Invites Total"
                value={canManageMembers ? invites.length : "Restricted"}
                hint={canManageMembers ? "All invite records" : "Owner-only ledger"}
              />
              <SummaryCard
                label="Pending Invites"
                value={canManageMembers ? pendingInvites.length : "Restricted"}
                hint={canManageMembers ? "Awaiting acceptance" : "Owner-only ledger"}
              />
              <SummaryCard
                label="Accepted Invites"
                value={canManageMembers ? acceptedInvites.length : "Restricted"}
                hint={canManageMembers ? "Completed acceptances" : "Owner-only ledger"}
              />
              <SummaryCard
                label="Configured Plan"
                value={configuredPlanName}
                hint={
                  planMismatch
                    ? `Enforcement currently falling back to ${effectivePlanName}`
                    : "Workspace commercial tier"
                }
              />
            </div>

            <div className="mb-8">
              <GovernanceBanner usage={usage} workspaceRole={workspaceRole} />
            </div>

            {memberUsage ? (
              <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-semibold">Member Capacity</h2>
                    <div className="mt-1 text-sm text-slate-500">
                      Membership should distinguish configured commercial posture from currently enforced limits.
                    </div>
                  </div>

                  <Link
                    href={`/workspace/${workspaceId}/settings`}
                    className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                  >
                    Open Settings & Billing
                  </Link>
                </div>

                {planMismatch ? (
                  <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                    Configured plan: <span className="font-semibold">{configuredPlanName}</span>
                    <span className="mx-2">·</span>
                    Effective enforced plan: <span className="font-semibold">{effectivePlanName}</span>
                    <div className="mt-2">
                      Billing is not fully active, so invitation and member-capacity enforcement may
                      temporarily follow the lower effective plan.
                    </div>
                  </div>
                ) : null}

                <div className="mt-4 grid gap-4 md:grid-cols-4">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">Members Used</div>
                    <div className="mt-1 text-2xl font-semibold">{memberUsage.used}</div>
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">Configured Member Limit</div>
                    <div className="mt-1 text-2xl font-semibold">
                      {configuredMemberLimit ?? "—"}
                    </div>
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">Effective Member Limit</div>
                    <div className="mt-1 text-2xl font-semibold">
                      {effectiveMemberLimit ?? memberUsage.limit}
                    </div>
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">Utilization</div>
                    <div className="mt-1 text-2xl font-semibold">
                      {formatPercent(memberUsage.ratio)}
                    </div>
                    <div className="mt-2 text-xs text-slate-500">Against effective enforcement</div>
                  </div>
                </div>

                {billingActivationRecommended ? (
                  <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
                    This workspace is already configured on a higher tier. The next operational step
                    is billing activation, not selecting a lower replacement plan.
                  </div>
                ) : null}
              </div>
            ) : null}

            {canManageMembers ? (
              <div id="invite">
                <WorkspaceInviteForm
                  workspaceId={workspaceId}
                  workspaceRole={workspaceRole}
                  onCreated={() => {
                    void loadPage(workspaceId);
                  }}
                />
              </div>
            ) : null}

            <div className="mb-8">
              <WorkspaceMembersTable
                workspaceId={workspaceId}
                rows={members}
                currentUserId={user.id}
                canManage={canManageMembers}
                onChanged={() => {
                  void loadPage(workspaceId);
                }}
              />
            </div>

            <InviteVisibilityNotice canManage={canManageMembers} invites={invites} />

            <WorkspaceInvitesTable
              workspaceId={workspaceId}
              rows={invites}
              canManage={canManageMembers}
              onChanged={() => {
                void loadPage(workspaceId);
              }}
            />
          </>
        )}
      </main>
    </div>
  );
}