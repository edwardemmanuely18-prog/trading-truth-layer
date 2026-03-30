"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  api,
  type WorkspaceInvite,
  type WorkspaceMemberRole,
  type WorkspaceUsageSummary,
} from "../lib/api";

type Props = {
  workspaceId: number;
  workspaceRole?: string | null;
  onCreated?: (invite: WorkspaceInvite) => void | Promise<void>;
};

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

export default function WorkspaceInviteForm({
  workspaceId,
  workspaceRole,
  onCreated,
}: Props) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<WorkspaceMemberRole>("member");
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);

  const [loadingUsage, setLoadingUsage] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const canManage = normalizeText(workspaceRole) === "owner";

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      try {
        setLoadingUsage(true);
        const result = await api.getWorkspaceUsage(workspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setLoadingUsage(false);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId]);

  const memberUsage = usage?.usage?.members;

  const configuredPlan = useMemo(() => {
    return usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.plan_code)
    );
  }, [usage]);

  const effectivePlan = useMemo(() => {
    return usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.effective_plan_code)
    );
  }, [usage]);

  const configuredPlanName = configuredPlan?.name || usage?.plan_code || "—";
  const effectivePlanName = effectivePlan?.name || usage?.effective_plan_code || "—";

  const configuredMemberLimit =
    (configuredPlan?.limits as { member_limit?: number } | undefined)?.member_limit ?? null;
  const effectiveMemberLimit =
    (effectivePlan?.limits as { member_limit?: number } | undefined)?.member_limit ??
    memberUsage?.limit ??
    null;

  const configuredMemberRatio =
    configuredMemberLimit && configuredMemberLimit > 0 && memberUsage
      ? memberUsage.used / configuredMemberLimit
      : null;

  const recommendedPlanCode = usage?.upgrade_recommendation?.recommended_plan_code;
  const recommendedPlanName = usage?.upgrade_recommendation?.recommended_plan_name;
  const recommendationBasisPlanCode =
    (usage?.upgrade_recommendation as { recommendation_basis_plan_code?: string } | undefined)
      ?.recommendation_basis_plan_code || usage?.plan_code;

  const hasDistinctRecommendation =
    !!recommendedPlanCode &&
    normalizeText(recommendedPlanCode) !== normalizeText(recommendationBasisPlanCode);

  const billingActivationRecommended = Boolean(
    (usage?.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );
  const planMismatch = Boolean(usage?.governance?.plan_mismatch);

  const memberStatus = memberUsage?.status || "ok";
  const memberAtLimit = memberStatus === "at_limit";
  const memberOverLimit = memberStatus === "over_limit";
  const memberNearLimit = memberStatus === "near_limit";

  const inviteBlockedByCapacity = memberAtLimit || memberOverLimit;
  const inviteBlocked = !canManage || inviteBlockedByCapacity || submitting || loadingUsage;

  async function refreshUsage() {
    try {
      const result = await api.getWorkspaceUsage(workspaceId);
      setUsage(result);
    } catch {
      // keep current snapshot
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!canManage) {
      setError("Only workspace owners can send invites.");
      return;
    }

    if (!email.trim()) {
      setError("Invite email is required.");
      return;
    }

    if (inviteBlockedByCapacity) {
      setError(
        memberOverLimit
          ? "Workspace member limit has already been exceeded. Upgrade the plan before sending another invite."
          : "Workspace member limit has been reached. Upgrade the plan before sending another invite."
      );
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      const created = await api.createWorkspaceInvite(workspaceId, {
        email: email.trim(),
        role,
      });

      setSuccess("Workspace invite created successfully.");
      setEmail("");
      setRole("member");

      await refreshUsage();

      if (onCreated) {
        await onCreated(created);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create workspace invite.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="rounded-3xl border bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-sm text-slate-500">Invitation Control</div>
          <h2 className="mt-2 text-2xl font-semibold">Invite Workspace Member</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            Send a controlled invite into this workspace. Member capacity enforcement follows the
            currently effective workspace plan, which may differ from the configured commercial tier
            when billing is not yet active.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
          <div className="text-slate-500">Workspace Role</div>
          <div className="mt-1 font-semibold">{workspaceRole || "unknown"}</div>
        </div>
      </div>

      {usage ? (
        <>
          {planMismatch ? (
            <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
              <div className="text-lg font-semibold">Configured vs effective plan</div>
              <div className="mt-2 text-sm">
                Configured plan: <span className="font-semibold">{configuredPlanName}</span>
                <span className="mx-2">·</span>
                Effective enforced plan: <span className="font-semibold">{effectivePlanName}</span>
              </div>
              <p className="mt-3 text-sm">
                Billing is not fully active, so invite blocking and capacity enforcement currently
                follow the effective plan.
              </p>
            </div>
          ) : null}

          <div className="mt-6 grid gap-4 md:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Configured Plan</div>
              <div className="mt-1 text-xl font-semibold">{configuredPlanName}</div>
              {planMismatch ? (
                <div className="mt-2 text-xs text-slate-500">
                  Enforcement currently falling back to {effectivePlanName}
                </div>
              ) : null}
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Members Used</div>
              <div className="mt-1 text-xl font-semibold">{memberUsage?.used ?? 0}</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Configured Member Limit</div>
              <div className="mt-1 text-xl font-semibold">{configuredMemberLimit ?? "—"}</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Effective Member Limit</div>
              <div className="mt-1 text-xl font-semibold">
                {effectiveMemberLimit ?? memberUsage?.limit ?? "—"}
              </div>
              <div className="mt-2 text-xs text-slate-500">Invite blocking uses this limit</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 md:col-span-2">
              <div className="text-sm text-slate-500">Effective Utilization</div>
              <div className="mt-1 text-xl font-semibold">{formatPercent(memberUsage?.ratio)}</div>
              <div className="mt-2 text-xs text-slate-500">
                Calculated against effective enforcement, not the configured commercial tier.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 md:col-span-2">
              <div className="text-sm text-slate-500">Configured Utilization</div>
              <div className="mt-1 text-xl font-semibold">{formatPercent(configuredMemberRatio)}</div>
              <div className="mt-2 text-xs text-slate-500">
                Calculated against the configured commercial tier headroom.
              </div>
            </div>
          </div>
        </>
      ) : null}

      {billingActivationRecommended ? (
        <div className="mt-6 rounded-2xl border border-blue-200 bg-blue-50 p-5 text-blue-900">
          <div className="text-lg font-semibold">Billing activation needed</div>
          <p className="mt-2 text-sm">
            This workspace is already configured on a higher tier. The next operational step is to
            activate billing so invite capacity enforcement can match the configured plan.
          </p>

          <div className="mt-4">
            <Link
              href={`/workspace/${workspaceId}/settings`}
              className="inline-flex rounded-xl border border-blue-300 bg-white px-5 py-3 text-sm font-semibold text-blue-900 hover:bg-blue-100"
            >
              Open Settings & Billing
            </Link>
          </div>
        </div>
      ) : null}

      {usage?.governance?.upgrade_required_now && !billingActivationRecommended ? (
        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-5 text-amber-900">
          <div className="text-lg font-semibold">Upgrade Required</div>
          <p className="mt-2 text-sm">
            This workspace is constrained by one or more current enforced plan limits. Member
            invitation workflows may be blocked until plan capacity is increased.
          </p>

          {usage.upgrade_recommendation?.breached_dimensions?.length ? (
            <div className="mt-4">
              <div className="text-sm font-medium">Exceeded dimensions</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {usage.upgrade_recommendation.breached_dimensions.map((item) => (
                  <span
                    key={`breached-${item}`}
                    className="rounded-full border border-amber-300 bg-white px-3 py-1 text-sm font-medium"
                  >
                    {formatDimensionLabel(item)}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          {hasDistinctRecommendation && recommendedPlanName ? (
            <div className="mt-4 text-sm">
              Recommended next plan: <span className="font-semibold">{recommendedPlanName}</span>
            </div>
          ) : null}

          <div className="mt-4">
            <Link
              href={`/workspace/${workspaceId}/settings`}
              className="inline-flex rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
            >
              Review Plan Options
            </Link>
          </div>
        </div>
      ) : null}

      {!usage?.governance?.upgrade_required_now &&
      !billingActivationRecommended &&
      usage?.governance?.upgrade_recommended_soon ? (
        <div className="mt-6 rounded-2xl border border-blue-200 bg-blue-50 p-5 text-blue-900">
          <div className="text-lg font-semibold">Upgrade Recommended Soon</div>
          <p className="mt-2 text-sm">
            This workspace is nearing one or more effective plan ceilings. Upgrading now will reduce
            the risk of interruption in member-management workflows.
          </p>

          {usage.upgrade_recommendation?.near_limit_dimensions?.length ? (
            <div className="mt-4">
              <div className="text-sm font-medium">Near-limit dimensions</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {usage.upgrade_recommendation.near_limit_dimensions.map((item) => (
                  <span
                    key={`near-${item}`}
                    className="rounded-full border border-blue-300 bg-white px-3 py-1 text-sm font-medium text-blue-800"
                  >
                    {formatDimensionLabel(item)}
                  </span>
                ))}
              </div>
            </div>
          ) : null}

          {hasDistinctRecommendation && recommendedPlanName ? (
            <div className="mt-4 text-sm">
              Recommended next plan: <span className="font-semibold">{recommendedPlanName}</span>
            </div>
          ) : null}

          <div className="mt-4">
            <Link
              href={`/workspace/${workspaceId}/settings`}
              className="inline-flex rounded-xl border border-blue-300 bg-white px-5 py-3 text-sm font-semibold text-blue-900 hover:bg-blue-100"
            >
              Open Settings & Billing
            </Link>
          </div>
        </div>
      ) : null}

      {!canManage ? (
        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Only workspace owners can send invites.
        </div>
      ) : null}

      {memberNearLimit && !inviteBlockedByCapacity ? (
        <div className="mt-6 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
          Member capacity is nearing the currently enforced ceiling. You can still invite now, but
          plan posture should be reviewed soon.
        </div>
      ) : null}

      {memberAtLimit ? (
        <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Member capacity is fully used under the current effective plan. New invites are blocked
          until the workspace billing or plan posture improves.
        </div>
      ) : null}

      {memberOverLimit ? (
        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          Member usage is already above the allowed effective plan ceiling. Improve billing or plan
          posture before inviting more users.
        </div>
      ) : null}

      {success ? (
        <div className="mt-6 rounded-2xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
          {success}
        </div>
      ) : null}

      {error ? (
        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div className="grid gap-4 md:grid-cols-[1.5fr_0.9fr]">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Invite Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={inviteBlocked}
              placeholder="newmember@example.com"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">Workspace Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as WorkspaceMemberRole)}
              disabled={inviteBlocked}
              className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-100"
            >
              <option value="member">member</option>
              <option value="operator">operator</option>
              <option value="auditor">auditor</option>
            </select>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={inviteBlocked}
            className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {submitting ? "Sending Invite..." : "Send Invite"}
          </button>

          <Link
            href={`/workspace/${workspaceId}/settings`}
            className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
          >
            Settings & Billing
          </Link>
        </div>
      </form>
    </section>
  );
}