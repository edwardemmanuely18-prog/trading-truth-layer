"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";
import {
    api,
    type DashboardResponse,
    type PublicClaimDirectoryItem,
    type WorkspaceUsageSummary,
    type DashboardSummary,
    type WorkspaceSnapshot,
} from "../../../../lib/api";
import PaywallModal from "../../../../components/PaywallModal";
import { useWorkspaceGate } from "../../../../hooks/useWorkspaceGate";



function formatNumber(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString();
}

function formatPercent(value?: number | null) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(1)}%`;
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function isAtOrOverLimit(used?: number, limit?: number) {
  if (used === undefined || limit === undefined) return false;
  if (limit <= 0) return false;
  return used >= limit;
}

function isNearLimit(ratio?: number | null) {
  if (ratio === null || ratio === undefined || Number.isNaN(Number(ratio))) return false;
  return Number(ratio) >= 0.8;
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

function getPlanName(usage?: WorkspaceUsageSummary | null, planCode?: string | null) {
  const normalized = normalizeText(planCode);
  const matched = usage?.plan_catalog?.find((plan) => normalizeText(plan.code) === normalized);
  return matched?.name || planCode || "current plan";
}

function getClaimStatusBadgeClass(status?: string | null) {
  const normalized = normalizeText(status);

  if (normalized === "locked") {
    return "border-green-200 bg-green-50 text-green-800";
  }

  if (normalized === "published") {
    return "border-blue-200 bg-blue-50 text-blue-800";
  }

  if (normalized === "verified") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }

  if (normalized === "draft") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }

  return "border-slate-200 bg-slate-50 text-slate-700";
}

function getCapacityTone(ratio?: number | null) {
  if (ratio === null || ratio === undefined || Number.isNaN(Number(ratio))) {
    return {
      tone: "neutral",
      wrapper: "border-slate-200 bg-white",
      badge: "border-slate-200 bg-slate-50 text-slate-700",
      summary: "Usage unavailable",
    };
  }

  const value = Number(ratio);

  if (value >= 1) {
    return {
      tone: "critical",
      wrapper: "border-red-200 bg-red-50",
      badge: "border-red-200 bg-white text-red-700",
      summary: "At or over governed limit",
    };
  }

  if (value >= 0.8) {
    return {
      tone: "warning",
      wrapper: "border-amber-200 bg-amber-50",
      badge: "border-amber-200 bg-white text-amber-700",
      summary: "Approaching plan ceiling",
    };
  }

  if (value <= 0.1) {
    return {
      tone: "healthy-low",
      wrapper: "border-slate-200 bg-white",
      badge: "border-slate-200 bg-slate-50 text-slate-700",
      summary: "Healthy capacity headroom",
    };
  }

  return {
    tone: "healthy",
    wrapper: "border-slate-200 bg-white",
    badge: "border-slate-200 bg-slate-50 text-slate-700",
    summary: "Within governed capacity",
  };
}

function getLifecyclePriorityRank(status?: string | null) {
  const normalized = normalizeText(status);

  switch (normalized) {
    case "draft":
      return 4;
    case "verified":
      return 3;
    case "published":
      return 2;
    case "locked":
      return 1;
    default:
      return 0;
  }
}

function getOnboardingStageState(completed: boolean, unlocked: boolean) {
  if (completed) {
    return {
      badge: "complete",
      className: "border-green-200 bg-green-50 text-green-800",
      summary: "Completed",
    };
  }

  if (unlocked) {
    return {
      badge: "active",
      className: "border-blue-200 bg-blue-50 text-blue-800",
      summary: "Current step",
    };
  }

  return {
    badge: "pending",
    className: "border-slate-200 bg-slate-50 text-slate-600",
    summary: "Locked until prior step is complete",
  };
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
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">{value}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

function OnboardingStageCard({
  step,
  title,
  description,
  completed,
  unlocked,
}: {
  step: number;
  title: string;
  description: string;
  completed: boolean;
  unlocked: boolean;
}) {
  const state = getOnboardingStageState(completed, unlocked);

  return (
    <div className={`rounded-2xl border p-5 ${state.className}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em]">
            Step {step}
          </div>
          <div className="mt-2 text-sm font-semibold">{title}</div>
        </div>

        <span className="rounded-full border border-current/20 bg-white px-3 py-1 text-[11px] font-semibold">
          {state.summary}
        </span>
      </div>

      <div className="mt-3 text-sm leading-6">{description}</div>
    </div>
  );
}

function CapacityCard({
  label,
  ratio,
  used,
  limit,
  suffix = "",
}: {
  label: string;
  ratio?: number | null;
  used?: number | null;
  limit?: number | null;
  suffix?: string;
}) {
  const tone = getCapacityTone(ratio);

  return (
    <div className={`rounded-2xl border p-6 shadow-sm ${tone.wrapper}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm text-slate-500">{label}</div>
          <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
            {formatPercent(ratio)}
          </div>
          <div className="mt-2 text-xs text-slate-500">
            {formatNumber(used)} used of {formatNumber(limit)}
            {suffix}
          </div>
        </div>

        <span className={`rounded-full border px-3 py-1 text-[11px] font-semibold ${tone.badge}`}>
          {tone.summary}
        </span>
      </div>
    </div>
  );
}

function ActionLink({
  href,
  label,
  active = false,
}: {
  href: string;
  label: string;
  active?: boolean;
}) {
  return (
    <Link
      href={href}
      className={
        active
          ? "block rounded-xl bg-slate-900 px-5 py-3 text-center text-sm font-semibold text-white hover:bg-slate-800"
          : "block rounded-xl border border-slate-300 px-5 py-3 text-center text-sm font-semibold text-slate-900 hover:bg-slate-50"
      }
    >
      {label}
    </Link>
  );
}

function ActionButton({
  onClick,
  label,
  loading = false,
  disabled = false,
}: {
  onClick: () => void;
  label: string;
  loading?: boolean;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="block w-full rounded-xl border border-slate-300 px-5 py-3 text-center text-sm font-semibold text-slate-900 hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
    >
      {loading ? "Checking Access..." : label}
    </button>
  );
}

function RoleBanner({
  workspaceId,
  workspaceRole,
}: {
  workspaceId: number;
  workspaceRole?: string | null;
}) {
  const normalizedRole = normalizeText(workspaceRole);

  if (normalizedRole === "owner" || normalizedRole === "operator") {
    return null;
  }

  return (
    <div className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
      <h2 className="text-xl font-semibold">Read-only operational access</h2>
      <p className="mt-2 text-sm">
        Your current workspace role is{" "}
        <span className="font-semibold">{workspaceRole || "member"}</span>. You can review
        dashboard metrics, ledger evidence, claims, and settings visibility, but claim creation
        and trade import remain restricted to owner/operator roles.
      </p>

      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href={`/workspace/${workspaceId}/claims`}
          className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
        >
          Open Claim Library
        </Link>

        <Link
          href={`/workspace/${workspaceId}/ledger`}
          className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
        >
          Open Ledger
        </Link>

        <Link
          href={`/workspace/${workspaceId}/evidence`}
          className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
        >
          Open Evidence Center
        </Link>

        <Link
          href={`/workspace/${workspaceId}/members`}
          className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
        >
          Open Members & Invites
        </Link>
      </div>
    </div>
  );
}

function GovernanceBanner({
  workspaceId,
  usage,
}: {
  workspaceId: number;
  usage: WorkspaceUsageSummary;
}) {
  const membersUsed = Number(usage?.usage?.members ?? 0);
  const tradesUsed = Number(usage?.usage?.trades ?? 0);
  const claimsUsed = Number(usage?.usage?.claims ?? 0);
  const storageUsed = Number(usage?.usage?.storage_mb ?? 0);

  const membersLimit = Number(usage?.limits?.members ?? 0);
  const tradesLimit = Number(usage?.limits?.trades ?? 0);
  const claimsLimit = Number(usage?.limits?.claims ?? 0);
  const storageLimit = Number(usage?.limits?.storage_mb ?? 0);

  const membersAtOrOverLimit =
    isAtOrOverLimit(membersUsed, membersLimit);

  const tradesAtOrOverLimit =
    isAtOrOverLimit(tradesUsed, tradesLimit);

  const claimsAtOrOverLimit =
    isAtOrOverLimit(claimsUsed, claimsLimit);

  const storageAtOrOverLimit =
    isAtOrOverLimit(storageUsed, storageLimit);

  const hasAnyAtOrOverLimit =
    membersAtOrOverLimit || tradesAtOrOverLimit || claimsAtOrOverLimit || storageAtOrOverLimit;

  const governance = usage?.governance;
  const upgrade = usage?.upgrade_recommendation;

  const upgradeRequiredNow = Boolean(governance?.upgrade_required_now);
  const upgradeRecommendedSoon = Boolean(governance?.upgrade_recommended_soon);
  const billingActivationRecommended = Boolean(governance?.billing_activation_recommended);

  const configuredPlanName = getPlanName(
    usage,
    governance?.configured_plan_code || usage?.plan_code
  );
  const effectivePlanName = getPlanName(
    usage,
    governance?.effective_plan_code || usage?.effective_plan_code
  );
  const recommendedPlanName = upgrade?.recommended_plan_name;
  const breachedDimensions = upgrade?.breached_dimensions ?? [];
  const nearLimitDimensions = upgrade?.near_limit_dimensions ?? [];

  if (
    !hasAnyAtOrOverLimit &&
    !upgradeRequiredNow &&
    !upgradeRecommendedSoon &&
    !billingActivationRecommended
  ) {
    return null;
  }

  return (
    <div className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
      <h2 className="text-xl font-semibold">
        {billingActivationRecommended
          ? "Billing Activation Needed"
          : upgradeRequiredNow || hasAnyAtOrOverLimit
            ? "Workspace At / Over Plan Limits"
            : "Workspace Upgrade Recommendation"}
      </h2>

      <p className="mt-2 text-sm">
        {billingActivationRecommended
          ? `This workspace is already configured on ${configuredPlanName}, but billing is not active yet. Effective enforcement is still falling back to ${effectivePlanName}.`
          : upgradeRequiredNow || hasAnyAtOrOverLimit
            ? "This workspace has reached or exceeded one or more plan limits. Some write actions may now be blocked until billing is activated or the workspace is upgraded."
            : "This workspace is approaching one or more plan ceilings. Upgrading early will protect operational continuity."}
      </p>

      {recommendedPlanName && !billingActivationRecommended ? (
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
                key={`breached-${item}`}
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

      <div className="mt-4">
        <Link
          href={`/workspace/${workspaceId}/settings?tab=billing`}
          className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
        >
          {billingActivationRecommended ? "Activate Billing" : "Review Plan & Billing"}
        </Link>
      </div>
    </div>
  );
}

function WorkflowStage({
  label,
  status,
}: {
  label: string;
  status: "complete" | "active" | "pending";
}) {
  const className =
    status === "complete"
      ? "border-green-200 bg-green-50 text-green-800"
      : status === "active"
        ? "border-blue-200 bg-blue-50 text-blue-800"
        : "border-slate-200 bg-white text-slate-600";

  return (
    <div className={`rounded-full border px-4 py-2 text-sm font-semibold ${className}`}>
      {label}
    </div>
  );
}

function DashboardStatusPanel({
    workspaceId,
    dashboard,
    usage,
    verifiedClaims,
    publishedClaims,
    lockedClaims,
    draftClaims,
    canCreateClaim,
    canImportTrades,
}: {
    workspaceId: number;
    dashboard: DashboardResponse;
    usage: WorkspaceUsageSummary;
    verifiedClaims: number;
    publishedClaims: number;
    lockedClaims: number;
    draftClaims: number;
    canCreateClaim: boolean;
    canImportTrades: boolean;
}) {
  
  const tradeCount = Number(dashboard.trade_count ?? 0);
  const claimCount = Number(dashboard.claim_count ?? 0);
  const memberCount = Number(dashboard.member_count ?? 0);
  const billingActivationRecommended = Boolean(usage?.governance?.billing_activation_recommended);
  const configuredPlanName = getPlanName(
    usage,
    usage?.governance?.configured_plan_code || usage?.plan_code
  );

  const statusLines = [
    {
      label: "Ledger",
      tone: tradeCount > 0 ? "good" : "neutral",
      summary:
        tradeCount > 0
          ? `Active · ${formatNumber(tradeCount)} trades ingested`
          : canImportTrades
            ? "No trades ingested yet · import required"
            : "No trade activity available yet",
    },
    {
        label: "Claims",

        tone:
            draftClaims > 0
                ? "warning"
                : claimCount > 0
                ? "good"
                : "neutral",

        summary:
            draftClaims > 0
                ? `${draftClaims} draft ${
                    draftClaims === 1
                        ? "claim requires"
                        : "claims require"
                  } action`

                : claimCount > 0
                ? `${formatNumber(claimCount)} governed claims available`

                : canCreateClaim
                ? "No claims yet - create your first record"

                : "No claims available yet",
    },
    {
        label: "Verification",

        tone:
            lockedClaims > 0
                ? "good"
                : publishedClaims > 0
                ? "warning"
                : verifiedClaims > 0
                ? "warning"
                : "neutral",

        summary:
            lockedClaims > 0
                ? `${lockedClaims} locked verification record${lockedClaims === 1 ? "" : "s"}`

            : publishedClaims > 0
                ? `${publishedClaims} published record${publishedClaims === 1 ? "" : "s"} awaiting lock`

            : verifiedClaims > 0
                ? `${verifiedClaims} verified record${verifiedClaims === 1 ? "" : "s"} awaiting publication`

            : draftClaims > 0
                ? `${draftClaims} draft claim${draftClaims === 1 ? "" : "s"} pending verification`

            : "Verification workflow not started",
    },
    {
      label: "Plan",
      tone: billingActivationRecommended ? "warning" : "good",
      summary: billingActivationRecommended
        ? `${configuredPlanName} configured · billing activation still needed`
        : `${configuredPlanName} plan posture active`,
    },
    {
      label: "Members",
      tone: memberCount > 0 ? "good" : "neutral",
      summary:
        memberCount > 0
          ? `${formatNumber(memberCount)} workspace ${memberCount === 1 ? "member" : "members"} tracked`
          : "No members assigned yet",
    },
  ];

  function toneClass(tone: string) {
    switch (tone) {
      case "good":
        return "border-green-200 bg-green-50 text-green-800";
      case "warning":
        return "border-amber-200 bg-amber-50 text-amber-800";
      default:
        return "border-slate-200 bg-white text-slate-700";
    }
  }

  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Executive overview
          </div>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Portfolio Overview</h2>
          <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600">
            This workspace status panel highlights current ingestion posture, claim workflow
            readiness, verification output, and billing or capacity signals that may affect
            operational continuity.
          </p>
        </div>

        <Link
          href={`/workspace/${workspaceId}/settings?tab=billing`}
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50"
        >
          Review workspace posture
        </Link>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {statusLines.map((item) => (
          <div key={item.label} className={`rounded-2xl border p-4 ${toneClass(item.tone)}`}>
            <div className="text-xs font-semibold uppercase tracking-[0.16em]">{item.label}</div>
            <div className="mt-2 text-sm leading-6">{item.summary}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrustOverviewPanel({
  lockedClaims,
  publishedClaims,
  verifiedClaims,
}: {
  lockedClaims: number;
  publishedClaims: number;
  verifiedClaims: number;
}) {
  const trustCoverage =
    publishedClaims + lockedClaims > 0
      ? Math.round(
          (lockedClaims /
            (publishedClaims + lockedClaims)) *
            100
        )
      : 0;

  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Trust Overview
      </div>

      <h2 className="mt-2 text-2xl font-semibold">
        Verification Coverage
      </h2>

      <div className="mt-5 grid gap-4 md:grid-cols-4">
        <SummaryCard
          label="Verified Claims"
          value={verifiedClaims}
        />

        <SummaryCard
          label="Published Claims"
          value={publishedClaims}
        />

        <SummaryCard
          label="Locked Claims"
          value={lockedClaims}
        />

        <SummaryCard
          label="Trust Coverage"
          value={`${trustCoverage}%`}
        />
      </div>
    </div>
  );
}

function IntegrityHealthPanel({
  activeAlerts,
  verificationCoverage,
}: {
  activeAlerts: number;
  verificationCoverage: number;
}) {
  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Integrity Health
      </div>

      <h2 className="mt-2 text-2xl font-semibold">
        Verification Integrity Status
      </h2>

      <div className="mt-5 grid gap-4 md:grid-cols-4">

        <SummaryCard
          label="Integrity Score"
          value={
            activeAlerts === 0
              ? "100%"
              : "WARNING"
          }
        />

        <SummaryCard
          label="Hash Failures"
          value={activeAlerts}
        />

        <SummaryCard
          label="Verification Gaps"
          value="0"
        />

        <SummaryCard
          label="Evidence Coverage"
          value={`${verificationCoverage.toFixed(0)}%`}
        />

      </div>
    </div>
  );
}

function WorkflowProgressPanel({
  tradeCount,
  claimCount,
  draftCount,
  verifiedCount,
  publishedCount,
  lockedCount,
}: {
  tradeCount: number;
  claimCount: number;
  draftCount: number;
  verifiedCount: number;
  publishedCount: number;
  lockedCount: number;
}) {
  const importStatus: "complete" | "active" | "pending" = tradeCount > 0 ? "complete" : "pending";
  const ledgerStatus: "complete" | "active" | "pending" = tradeCount > 0 ? "complete" : "pending";
  const claimStatus: "complete" | "active" | "pending" =
    draftCount > 0 ? "active" : claimCount > 0 ? "complete" : "pending";
  const verifyStatus: "complete" | "active" | "pending" =
    verifiedCount > 0 || publishedCount > 0 || lockedCount > 0
      ? lockedCount > 0
        ? "complete"
        : "active"
      : "pending";
  const publishStatus: "complete" | "active" | "pending" =
    publishedCount > 0 || lockedCount > 0
      ? "complete"
      : verifiedCount > 0
        ? "active"
        : "pending";

  const lockStatus: "complete" | "active" | "pending" =
    lockedCount > 0 ? "complete" : "pending";
  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Verification Lifecycle
      </div>
      <h2 className="mt-2 text-2xl font-semibold text-slate-950">
        Verification Chain
      </h2>
      <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600">
        Trading Truth Layer operates as a governed workflow. This strip shows where the workspace
        currently sits across ingestion, claim construction, verification, and public trust
        distribution.
      </p>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <WorkflowStage label="Import" status={importStatus} />
        <div className="text-slate-300">→</div>
        <WorkflowStage label="Ledger" status={ledgerStatus} />
        <div className="text-slate-300">→</div>
        <WorkflowStage label="Claim" status={claimStatus} />
        <div className="text-slate-300">→</div>
        <WorkflowStage label="Verify" status={verifyStatus} />
        <div className="text-slate-300">→</div>
        <WorkflowStage label="Publish" status={publishStatus} />
        <div className="text-slate-300">→</div>
        <WorkflowStage label="Lock" status={lockStatus} />
      </div>
    </div>
  );
}

function EmptyWorkspacePanel({
  workspaceId,
  canCreateClaim,
  canImportTrades,
  createChecking,
  onCreateDraft,
  tradeCount,
  claimCount,
  verifiedCount,
}: {
  workspaceId: number;
  canCreateClaim: boolean;
  canImportTrades: boolean;
  createChecking: boolean;
  onCreateDraft: () => void;
  tradeCount: number;
  claimCount: number;
  verifiedCount: number;
}) {
  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="max-w-3xl">
        <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          First-run guidance
        </div>
        <h2 className="mt-2 text-3xl font-semibold text-slate-950">
          Start your first governed verification workflow
        </h2>
        <p className="mt-3 text-sm leading-7 text-slate-600">
          This workspace is still empty. The fastest route to value is to import trade activity,
          define your first claim, and then move into verification and public proof.
        </p>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <OnboardingStageCard
          step={1}
          title="Import canonical trade activity"
          description="Bring in CSV, MT5, IBKR, or webhook data so the workspace has a canonical ledger to govern."
          completed={tradeCount > 0}
          unlocked={true}
        />

        <OnboardingStageCard
          step={2}
          title="Author the first governed claim"
          description="Define scope, methodology, participants, exclusions, and evidence posture for the first verifiable record."
          completed={claimCount > 0}
          unlocked={tradeCount > 0}
        />

        <OnboardingStageCard
          step={3}
          title="Verify and activate public proof"
          description="Move the record into evidence-backed verification, integrity validation, and public trust distribution."
          completed={verifiedCount > 0}
          unlocked={tradeCount > 0 && claimCount > 0}
        />
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        {canImportTrades ? (
          <ActionLink href={`/workspace/${workspaceId}/import`} label="Import Trades" active />
        ) : (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-3 text-sm text-slate-500">
            Trade import available to owner/operator only
          </div>
        )}

        {canCreateClaim ? (
          <ActionButton
            onClick={onCreateDraft}
            label="Create First Claim"
            loading={createChecking}
          />
        ) : (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-3 text-sm text-slate-500">
            Claim creation available to owner/operator only
          </div>
        )}

        <ActionLink href={`/workspace/${workspaceId}/members`} label="Invite Collaborators" />
        <ActionLink href={`/claims`} label="Explore Public Proof" />
        <ActionLink href={`/how-it-works`} label="How It Works" />
      </div>
    </div>
  );
}

export default function WorkspaceDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const { user, workspaces, loading: authLoading, getWorkspaceRole } = useAuth();
  const { paywallState, closePaywall, gateAndExecute } = useWorkspaceGate();

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
  const canCreateClaim = workspaceRole === "owner" || workspaceRole === "operator";
  const canImportTrades = workspaceRole === "owner" || workspaceRole === "operator";

  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [
    dashboardSummary,
    setDashboardSummary,
  ] = useState<DashboardSummary | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [createChecking, setCreateChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!workspaceId || !workspaceMembership) return;

      try {
        setLoading(true);
        setError(null);

        const [
            dashboardSummary,
            usageRes,
            snapshot,
        ] = await Promise.all([
            api.getDashboardSummary(workspaceId),
            api.getWorkspaceUsage(workspaceId),
            api.getWorkspaceSnapshot(workspaceId),
        ]);

        setDashboardSummary(dashboardSummary);

        setDashboard({
          workspace_id:
            Number(workspaceId),
          workspace_name: "",
          member_count:
            dashboardSummary.member_count,

          trade_count:
            dashboardSummary.trade_count,

          claim_count:
            dashboardSummary.claim_count,
        });

        setUsage(usageRes ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load workspace dashboard.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [workspaceId, workspaceMembership]);

  async function handleCreateDraftClick() {
    if (!workspaceId) return;

    try {
      setCreateChecking(true);

      await gateAndExecute(
        {
          action: "create_claim_version",
          usage,
          workspaceRole,
        },
        async () => {
          router.push(`/workspace/${workspaceId}/schema`);
        }
      );
    } finally {
      setCreateChecking(false);
    }
  }

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading dashboard...</div>
        </main>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace dashboard.
          </div>
        </main>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading dashboard...</div>
        </main>
      </div>
    );
  }

  if (error || !dashboard || !usage) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error || "Failed to load workspace dashboard."}
          </div>
        </main>
      </div>
    );
  }

 const lockedClaims =
    dashboardSummary?.locked_claims ?? 0;

  const verifiedClaims =
    dashboardSummary?.verified_claims ?? 0;

  const publishedClaims =
    dashboardSummary?.published_claims ?? 0;

  const draftClaimsCount =
    dashboardSummary?.draft_claims ?? 0;

  const membersUsage: {
    used: number;
    limit: number;
    ratio: number;
  } = {
    used: Number(usage?.usage?.members ?? 0),
    limit: Number(usage?.limits?.members ?? 0),
    ratio: 0,
  };

  membersUsage.ratio =
    membersUsage.used / Math.max(1, membersUsage.limit);

  const tradesUsage: {
    used: number;
    limit: number;
    ratio: number;
  } = {
    used: Number(usage?.usage?.trades ?? 0),
    limit: Number(usage?.limits?.trades ?? 0),
    ratio: 0,
  };

  tradesUsage.ratio =
    tradesUsage.used / Math.max(1, tradesUsage.limit);

  const claimsUsage: {
    used: number;
    limit: number;
    ratio: number;
  } = {
    used: Number(usage?.usage?.claims ?? 0),
    limit: Number(usage?.limits?.claims ?? 0),
    ratio: 0,
  };

  claimsUsage.ratio =
    claimsUsage.used / Math.max(1, claimsUsage.limit);

  const storageUsage: {
    used: number;
    limit: number;
    ratio: number;
  } = {
    used: Number(usage?.usage?.storage_mb ?? 0),
    limit: Number(usage?.limits?.storage_mb ?? 0),
    ratio: 0,
  };

  storageUsage.ratio =
    storageUsage.used / Math.max(1, storageUsage.limit);

  const configuredPlanName = getPlanName(
    usage,
    usage?.governance?.configured_plan_code || usage?.plan_code
  );
  const effectivePlanName = getPlanName(
    usage,
    usage?.governance?.effective_plan_code || usage?.effective_plan_code
  );
  const billingActivationRecommended = Boolean(usage?.governance?.billing_activation_recommended);
  const recommendedPlanName =
    usage?.upgrade_recommendation?.recommended_plan_name || configuredPlanName;

  const tradeCount = Number(dashboard.trade_count ?? 0);
  const claimCount = Number(dashboard.claim_count ?? 0);
  const isEmptyWorkspace = tradeCount === 0 && claimCount === 0;

    const nextAction = (() => {
    const actionCandidates = [
      tradeCount === 0
        ? {
            priority: 100,
            title: "Import canonical trade activity",
            description:
              "This workspace does not yet have canonical trading data. Import activity first so claim computation, evidence generation, and downstream verification can begin.",
            primaryLabel: "Import Trades",
            primaryHref: `/workspace/${workspaceId}/import`,
          }
        : null,

      tradeCount > 0 && claimCount === 0
        ? {
            priority: 80,
            title: "Create the first governed claim",
            description:
              "Trade data is already available. Define the first governed record so the workspace can produce reproducible metrics, evidence, and lifecycle outputs.",
            primaryLabel: "Create First Claim",
            primaryAction: "create",
          }
        : null,

      verifiedClaims > lockedClaims
        ? {
            priority: 70,
            title: "Finalize verified output",
            description:
              "Verified claims exist but not all externally important records are locked. Finalizing them improves integrity posture and public trust readiness.",
            primaryLabel: "Open Claim Library",
            primaryHref: `/workspace/${workspaceId}/claims`,
          }
        : null,

      {
        priority: 10,
        title: "Review governed output",
        description:
          "The workspace is already producing governed records. Review claims, evidence, and public proof surfaces to maintain operational confidence.",
        primaryLabel: "Open Claim Library",
        primaryHref: `/workspace/${workspaceId}/claims`,
      }
    ].filter(Boolean) as Array<{
      priority: number;
      title: string;
      description: string;
      primaryLabel: string;
      primaryHref?: string;
      primaryAction?: string;
      secondaryLabel?: string;
      secondaryHref?: string;
    }>;

    return [...actionCandidates].sort((a, b) => b.priority - a.priority)[0];
  })();

  const governanceUsage = {
    members: Number(usage?.usage?.members ?? 0),
    trades: Number(usage?.usage?.trades ?? 0),
    claims: Number(usage?.usage?.claims ?? 0),
    storage_mb: Number(usage?.usage?.storage_mb ?? 0),
  };

  const governanceLimits = {
    members: Number(usage?.limits?.members ?? 0),
    trades: Number(usage?.limits?.trades ?? 0),
    claims: Number(usage?.limits?.claims ?? 0),
    storage_mb: Number(usage?.limits?.storage_mb ?? 0),
  };

  return (
    <>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />

        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="mb-8">
            <div className="text-sm text-slate-500">
              Trading Truth Layer · Executive Dashboard
            </div>
            <h1 className="mt-2 text-4xl font-bold">
              Executive Dashboard
            </h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Executive command center for evidence governance,
              claim operations, trust intelligence,
              verification coverage, and institutional oversight
              for workspace {workspaceId}.
            </p>
          </div>

          <RoleBanner workspaceId={workspaceId} workspaceRole={workspaceRole} />
          <GovernanceBanner workspaceId={workspaceId} usage={usage} />

          <DashboardStatusPanel
              workspaceId={workspaceId}
              dashboard={{
                  ...dashboard,
                  trade_count: Number(
                      usage?.usage?.trades ?? 0
                  ),
              }}
              usage={usage}

              verifiedClaims={verifiedClaims}

              publishedClaims={publishedClaims}

              lockedClaims={lockedClaims}

              draftClaims={draftClaimsCount}

              canCreateClaim={canCreateClaim}

              canImportTrades={canImportTrades}
          />

          <TrustOverviewPanel
            lockedClaims={lockedClaims}
            publishedClaims={publishedClaims}
            verifiedClaims={verifiedClaims}
          />

          <IntegrityHealthPanel
            activeAlerts={
              dashboardSummary?.active_alerts ?? 0
            }
            verificationCoverage={
              claimCount > 0
                ? ((publishedClaims + lockedClaims) / claimCount) * 100
                : 0
            }
          />

          <WorkflowProgressPanel
            tradeCount={tradeCount}
            claimCount={claimCount}
            draftCount={draftClaimsCount}
            verifiedCount={verifiedClaims}
            publishedCount={publishedClaims}
            lockedCount={lockedClaims}
          />

          <div className="mb-8 grid gap-4 md:grid-cols-4">
            <SummaryCard
              label="Workspace Members"
              value={formatNumber(governanceUsage.members)}
              hint={`${formatNumber(governanceUsage.members)} / ${formatNumber(
                governanceLimits.members
              )} · ${formatPercent(
                governanceLimits.members > 0
                  ? governanceUsage.members / governanceLimits.members
                  : 0
              )}`}
            />
            <SummaryCard
              label="Evidence Records"
              value={formatNumber(tradesUsage.used)}
              hint={`${formatNumber(tradesUsage.used)} / ${formatNumber(
                tradesUsage.limit
              )} · ${formatPercent(tradesUsage.ratio)}`}
            />
            <SummaryCard
                label="Governed Claims"
                value={formatNumber(claimCount)}
                hint={`${formatNumber(claimCount)} governed verification records`}
            />
            <SummaryCard
                label="Public Trust Records"
                value={formatNumber(
                    lockedClaims + publishedClaims
                )}
                hint={`${lockedClaims} Locked • ${publishedClaims} Published`}
            />
          </div>

          <div className="mb-8 grid gap-4 md:grid-cols-4">
            <CapacityCard
              label="Member Capacity"
              ratio={
                governanceLimits.members > 0
                  ? governanceUsage.members / governanceLimits.members
                  : 0
              }
              used={governanceUsage.members}
              limit={governanceLimits.members}
            />

            <CapacityCard
              label="Trade Capacity"
              ratio={
                governanceLimits.trades > 0
                  ? governanceUsage.trades / governanceLimits.trades
                  : 0
              }
              used={governanceUsage.trades}
              limit={governanceLimits.trades}
            />

            <CapacityCard
              label="Claim Capacity"
              ratio={
                  governanceLimits.claims > 0
                      ? claimCount /
                        governanceLimits.claims
                      : 0
              }
              used={claimCount}
              limit={governanceLimits.claims}
            />

            <CapacityCard
              label="Storage Capacity"
              ratio={
                governanceLimits.storage_mb > 0
                  ? governanceUsage.storage_mb / governanceLimits.storage_mb
                  : 0
              }
              used={governanceUsage.storage_mb}
              limit={governanceLimits.storage_mb}
              suffix="MB"
            />
          </div>

          {isEmptyWorkspace ? (
            <EmptyWorkspacePanel
              workspaceId={workspaceId}
              canCreateClaim={canCreateClaim}
              canImportTrades={canImportTrades}
              createChecking={createChecking}
              onCreateDraft={() => void handleCreateDraftClick()}
              tradeCount={tradeCount}
              claimCount={claimCount}
              verifiedCount={verifiedClaims}
            />
          ) : (
            <div className="mb-8">
              <div className="rounded-2xl border bg-white p-6 shadow-sm">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Executive Workspace Center
                </div>
                <h2 className="mt-2 text-2xl font-semibold">Operational Command Center</h2>

                <div className="text-sm font-semibold text-blue-900">
                    {nextAction.title}
                </div>

                <div className="mt-2 text-sm leading-7 text-blue-800">
                    {nextAction.description}
                </div>

                <div className="mt-8 grid gap-5 md:grid-cols-2">

                    {/* ======================================================= */}
                    {/* Live Workflow */}
                    {/* ======================================================= */}

                    <div className="rounded-xl border border-slate-200 bg-white p-5 md:col-span-2">

                        <div className="text-xs uppercase tracking-[0.18em] text-slate-500">

                            Live Workflow

                        </div>

                        <div className="mt-5 space-y-3">

                            <div className="flex justify-between">

                                <span>Evidence Intake</span>

                                <span>{tradeCount > 0 ? "✓" : "•"}</span>

                            </div>

                            <div className="flex justify-between">

                                <span>Claim Production</span>

                                <span>{claimCount > 0 ? "✓" : "•"}</span>

                            </div>

                            <div className="flex justify-between">

                                <span>Verification</span>

                                <span>{verifiedClaims > 0 ? "✓" : "•"}</span>

                            </div>

                            <div className="flex justify-between">

                                <span>Public Trust</span>

                                <span>{lockedClaims > 0 ? "✓" : "•"}</span>

                            </div>

                        </div>

                    </div>

                    <div className="rounded-xl border border-slate-200 bg-white p-5 md:col-span-2">

                        <div className="text-xs uppercase tracking-[0.18em] text-slate-500">

                            Executive Readiness

                        </div>

                        <div className="mt-5 space-y-3 text-sm">

                            <div className="flex justify-between">
                                <span>Verification Stage</span>
                                <strong>
                                    {lockedClaims > 0
                                         ? "Locked"

                                     : publishedClaims > 0
                                         ? "Published"

                                     : verifiedClaims > 0
                                         ? "Verified"

                                     : claimCount > 0
                                         ? "Draft"

                                     : "No Claims"}
                                </strong>
                            </div>

                            <div className="flex justify-between">
                                <span>Verification Coverage</span>
                                <strong>
                                    {lockedClaims > 0
                                         ? "READY"

                                     : publishedClaims > 0
                                         ? "PUBLIC"

                                     : verifiedClaims > 0
                                         ? "VERIFIED"

                                     : claimCount > 0
                                         ? "CLAIM CREATED"

                                     : "NOT STARTED"}
                                </strong>
                            </div>

                            <div className="flex justify-between">
                                <span>Verification Coverage</span>

                                <strong>
                                    {claimCount > 0
                                        ? `${Math.round(
                                            ((publishedClaims + lockedClaims) / claimCount) * 100
                                          )}%`
                                        : "0%"}
                                </strong>
                            </div>

                            <div className="flex justify-between">
                                <span>Governed Claims</span>

                                <strong>
                                    {claimCount}
                                </strong>
                            </div>

                            <div className="flex justify-between">
                                <span>Next Executive Action</span>
                                <strong>
                                    {nextAction.title}
                                </strong>
                            </div>

                        </div>

                    </div>             

                </div>

                {billingActivationRecommended ? (
                  <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
                    This workspace is already configured on{" "}
                    <span className="font-semibold">{configuredPlanName}</span>, but billing is not
                    active yet. Effective claim enforcement still follows{" "}
                    <span className="font-semibold">{effectivePlanName}</span>.
                  </div>
                ) : null}

                {Boolean(usage?.governance?.upgrade_required_now) ? (
                  <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                    Governed capacity is currently constrained. Review billing and{" "}
                    <span className="font-semibold">{recommendedPlanName}</span> to protect workflow
                    continuity.
                  </div>
                ) : null}

                {!canCreateClaim || !canImportTrades ? (
                  <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    Your current role is <span className="font-medium">{workspaceRole}</span>. Some
                    workspace write actions are restricted by role.
                  </div>
                ) : null}
              </div>
            </div>
          )}
        </main>
      </div>

      <PaywallModal
        open={paywallState.open}
        onClose={closePaywall}
        reason={paywallState.reason}
        actionLabel={paywallState.actionLabel || "Create draft claim"}
        message={paywallState.message}
        currentPlanName={configuredPlanName}
        currentPlanCode={usage?.plan_code || null}
        usageLabel={`${formatNumber(claimsUsage.used)} / ${formatNumber(
          claimsUsage.limit
        )} · ${formatPercent(claimsUsage.ratio)}`}
        recommendedPlanName={billingActivationRecommended ? configuredPlanName : recommendedPlanName}
        onUpgrade={() => {
          router.push(`/workspace/${workspaceId}/settings?tab=billing`);
        }}
      />
    </>
  );
}