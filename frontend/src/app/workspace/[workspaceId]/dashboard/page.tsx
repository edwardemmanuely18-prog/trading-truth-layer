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
} from "../../../../lib/api";
import PaywallModal from "../../../../components/PaywallModal";
import { useWorkspaceGate } from "../../../../hooks/useWorkspaceGate";

function formatNumber(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString();
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
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
  const membersUsage = usage?.usage?.members;
  const tradesUsage = usage?.usage?.trades;
  const claimsUsage = usage?.usage?.claims;
  const storageUsage = usage?.usage?.storage_mb;

  const membersAtOrOverLimit = isAtOrOverLimit(membersUsage?.used, membersUsage?.limit);
  const tradesAtOrOverLimit = isAtOrOverLimit(tradesUsage?.used, tradesUsage?.limit);
  const claimsAtOrOverLimit = isAtOrOverLimit(claimsUsage?.used, claimsUsage?.limit);
  const storageAtOrOverLimit = isAtOrOverLimit(storageUsage?.used, storageUsage?.limit);

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
  claims,
  usage,
  canCreateClaim,
  canImportTrades,
}: {
  workspaceId: number;
  dashboard: DashboardResponse;
  claims: PublicClaimDirectoryItem[];
  usage: WorkspaceUsageSummary;
  canCreateClaim: boolean;
  canImportTrades: boolean;
}) {
  const draftClaims = claims.filter((claim) => normalizeText(claim?.verification_status) === "draft");
  const lockedClaims = claims.filter((claim) => normalizeText(claim?.verification_status) === "locked");
  const publishedClaims = claims.filter((claim) =>
    ["published", "locked"].includes(normalizeText(claim?.verification_status))
  );

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
      tone: draftClaims.length > 0 ? "warning" : claimCount > 0 ? "good" : "neutral",
      summary:
        draftClaims.length > 0
          ? `${draftClaims.length} draft ${draftClaims.length === 1 ? "claim requires" : "claims require"} action`
          : claimCount > 0
            ? `${formatNumber(claimCount)} governed claims available`
            : canCreateClaim
              ? "No claims yet · create your first record"
              : "No claims available yet",
    },
    {
      label: "Verification",
      tone: lockedClaims.length > 0 ? "good" : publishedClaims.length > 0 ? "warning" : "neutral",
      summary:
        lockedClaims.length > 0
          ? `${lockedClaims.length} locked verification ${lockedClaims.length === 1 ? "record" : "records"}`
          : publishedClaims.length > 0
            ? `${publishedClaims.length} public ${publishedClaims.length === 1 ? "record" : "records"} not yet locked`
            : "No externally finalized records yet",
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
            Workspace status
          </div>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">System state overview</h2>
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
    lockedCount > 0 ? "complete" : publishedCount > 0 ? "active" : "pending";

  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Workflow progress
      </div>
      <h2 className="mt-2 text-2xl font-semibold text-slate-950">Import → verify → publish</h2>
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
        <WorkflowStage label="Publish / Lock" status={publishStatus} />
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
}: {
  workspaceId: number;
  canCreateClaim: boolean;
  canImportTrades: boolean;
  createChecking: boolean;
  onCreateDraft: () => void;
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
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <div className="text-sm font-semibold text-slate-900">Step 1 · Import trades</div>
          <div className="mt-2 text-sm leading-6 text-slate-600">
            Bring in CSV, MT5, IBKR, or webhook data to establish the canonical trade ledger.
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <div className="text-sm font-semibold text-slate-900">Step 2 · Create claim</div>
          <div className="mt-2 text-sm leading-6 text-slate-600">
            Define scope, methodology, participants, and included evidence for the record you want
            to verify.
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <div className="text-sm font-semibold text-slate-900">Step 3 · Verify and publish</div>
          <div className="mt-2 text-sm leading-6 text-slate-600">
            Generate auditable metrics, integrity fingerprints, and public verification surfaces.
          </div>
        </div>
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
  const [claims, setClaims] = useState<PublicClaimDirectoryItem[]>([]);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [createChecking, setCreateChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!workspaceId || !workspaceMembership) return;

      try {
        setLoading(true);
        setError(null);

        const [dashboardRes, claimsRes, usageRes] = await Promise.all([
          api.getDashboard(workspaceId),
          api.getWorkspaceClaims(workspaceId),
          api.getWorkspaceUsage(workspaceId),
        ]);

        setDashboard(dashboardRes ?? null);
        setClaims(Array.isArray(claimsRes) ? claimsRes : []);
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

  const lockedClaims = claims.filter((c) => normalizeText(c?.verification_status) === "locked").length;
  const verifiedClaims = claims.filter((c) =>
    ["verified", "published", "locked"].includes(normalizeText(c?.verification_status))
  ).length;
  const publishedClaims = claims.filter(
    (c) =>
      normalizeText(c?.scope?.visibility) === "public" &&
      ["published", "locked"].includes(normalizeText(c?.verification_status))
  ).length;
  const draftClaims = claims.filter((c) => normalizeText(c?.verification_status) === "draft");

  const recentClaims = [...claims]
    .sort((a, b) => {
      const rankDiff =
        getLifecyclePriorityRank(b?.verification_status) - getLifecyclePriorityRank(a?.verification_status);
      if (rankDiff !== 0) return rankDiff;
      return (b?.claim_schema_id ?? 0) - (a?.claim_schema_id ?? 0);
    })
    .slice(0, 6);

  const activeDraft = [...draftClaims].sort(
    (a, b) => (b?.claim_schema_id ?? 0) - (a?.claim_schema_id ?? 0)
  )[0];

  const latestLockedClaim = [...claims]
    .filter((c) => normalizeText(c?.verification_status) === "locked")
    .sort((a, b) => (b?.claim_schema_id ?? 0) - (a?.claim_schema_id ?? 0))[0];

  const membersUsage = usage?.usage?.members ?? { used: 0, limit: 0, ratio: 0 };
  const tradesUsage = usage?.usage?.trades ?? { used: 0, limit: 0, ratio: 0 };
  const claimsUsage = usage?.usage?.claims ?? { used: 0, limit: 0, ratio: 0 };
  const storageUsage = usage?.usage?.storage_mb ?? { used: 0, limit: 0, ratio: 0 };

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
    if (tradeCount === 0) {
      return {
        title: "Import trades",
        description:
          "Your workspace has no canonical trading activity yet. Import data first to activate the verification workflow.",
        primaryLabel: "Import Trades",
        primaryHref: `/workspace/${workspaceId}/import`,
      };
    }

    if (!activeDraft && claimCount === 0) {
      return {
        title: "Create your first claim",
        description:
          "Trade data is available. Define a claim scope so the system can compute governed metrics and produce evidence-backed records.",
        primaryLabel: "Create First Claim",
        primaryAction: "create",
      };
    }

    if (activeDraft) {
      return {
        title: "Continue draft claim",
        description:
          "A draft claim is waiting for completion. Finalize scope and methodology so it can move into verification.",
        primaryLabel: "Open Draft Claim",
        primaryHref: `/workspace/${workspaceId}/claim/${activeDraft.claim_schema_id}`,
        secondaryLabel: "Open Evidence",
        secondaryHref: `/workspace/${workspaceId}/evidence?claimId=${activeDraft.claim_schema_id}`,
      };
    }

    if (verifiedClaims > lockedClaims) {
      return {
        title: "Lock verified output",
        description:
          "Verified claims exist but not all finalized records are locked yet. Locking strengthens public trust and integrity posture.",
        primaryLabel: "Open Claim Library",
        primaryHref: `/workspace/${workspaceId}/claims`,
      };
    }

    return {
      title: "Review governed output",
      description:
        "The workspace is producing governed claims successfully. Review current records, evidence, and public trust surfaces.",
      primaryLabel: "Open Claim Library",
      primaryHref: `/workspace/${workspaceId}/claims`,
      secondaryLabel: "Open Latest Record",
      secondaryHref: latestLockedClaim
        ? `/workspace/${workspaceId}/claim/${latestLockedClaim.claim_schema_id}`
        : undefined,
    };
  })();

  return (
    <>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />

        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="mb-8">
            <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Operations</div>
            <h1 className="mt-2 text-4xl font-bold">Workspace Dashboard</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Control center for workspace {workspaceId}, including claim activity, ledger volume,
              plan usage, and direct access to governed creation, evidence, and verification
              workflows.
            </p>
          </div>

          <RoleBanner workspaceId={workspaceId} workspaceRole={workspaceRole} />
          <GovernanceBanner workspaceId={workspaceId} usage={usage} />

          <DashboardStatusPanel
            workspaceId={workspaceId}
            dashboard={dashboard}
            claims={claims}
            usage={usage}
            canCreateClaim={canCreateClaim}
            canImportTrades={canImportTrades}
          />

          <WorkflowProgressPanel
            tradeCount={tradeCount}
            claimCount={claimCount}
            draftCount={draftClaims.length}
            verifiedCount={verifiedClaims}
            publishedCount={publishedClaims}
            lockedCount={lockedClaims}
          />

          <div className="mb-8 grid gap-4 md:grid-cols-4">
            <SummaryCard
              label="Workspace Members"
              value={formatNumber(dashboard.member_count)}
              hint={`${formatNumber(membersUsage.used)} / ${formatNumber(
                membersUsage.limit
              )} · ${formatPercent(membersUsage.ratio)}`}
            />
            <SummaryCard
              label="Total Trades"
              value={formatNumber(dashboard.trade_count)}
              hint={`${formatNumber(tradesUsage.used)} / ${formatNumber(
                tradesUsage.limit
              )} · ${formatPercent(tradesUsage.ratio)}`}
            />
            <SummaryCard
              label="Total Claims"
              value={formatNumber(dashboard.claim_count)}
              hint={`${formatNumber(claimsUsage.used)} / ${formatNumber(
                claimsUsage.limit
              )} · ${formatPercent(claimsUsage.ratio)}`}
            />
            <SummaryCard
              label="Locked / Public"
              value={`${lockedClaims} / ${publishedClaims}`}
              hint={`Configured: ${configuredPlanName} · Effective: ${effectivePlanName}`}
            />
          </div>

          <div className="mb-8 grid gap-4 md:grid-cols-4">
            <CapacityCard
              label="Member Capacity"
              ratio={membersUsage.ratio}
              used={membersUsage.used}
              limit={membersUsage.limit}
            />
            <CapacityCard
              label="Trade Capacity"
              ratio={tradesUsage.ratio}
              used={tradesUsage.used}
              limit={tradesUsage.limit}
            />
            <CapacityCard
              label="Claim Capacity"
              ratio={claimsUsage.ratio}
              used={claimsUsage.used}
              limit={claimsUsage.limit}
            />
            <CapacityCard
              label="Storage Capacity"
              ratio={storageUsage.ratio}
              used={storageUsage.used}
              limit={storageUsage.limit}
              suffix=" MB"
            />
          </div>

          {isEmptyWorkspace ? (
            <EmptyWorkspacePanel
              workspaceId={workspaceId}
              canCreateClaim={canCreateClaim}
              canImportTrades={canImportTrades}
              createChecking={createChecking}
              onCreateDraft={() => void handleCreateDraftClick()}
            />
          ) : (
            <div className="mb-8 grid gap-6 lg:grid-cols-[1.3fr_1fr]">
              <div className="rounded-2xl border bg-white p-6 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                      Claim activity
                    </div>
                    <h2 className="mt-2 text-2xl font-semibold">Recent Claims</h2>
                    <p className="mt-2 max-w-2xl text-sm leading-7 text-slate-600">
                      Claims are prioritized by operational relevance so active drafts, finalized
                      records, and recent working items are easier to review.
                    </p>
                  </div>

                  <Link
                    href={`/workspace/${workspaceId}/claims`}
                    className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50"
                  >
                    Open Claim Library
                  </Link>
                </div>

                {activeDraft ? (
                  <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-5">
                    <div className="text-xs font-semibold uppercase tracking-[0.16em] text-amber-700">
                      Active claim · needs action
                    </div>
                    <div className="mt-2 text-lg font-semibold text-amber-950">
                      {activeDraft.name || "Unnamed draft claim"}
                    </div>
                    <div className="mt-2 text-sm text-amber-800">
                      claim #{activeDraft.claim_schema_id} · status:{" "}
                      {activeDraft.verification_status || "draft"} · visibility:{" "}
                      {activeDraft.scope?.visibility || "private"}
                    </div>

                    <div className="mt-4 flex flex-wrap gap-3">
                      <Link
                        href={`/workspace/${workspaceId}/claim/${activeDraft.claim_schema_id}`}
                        className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
                      >
                        Continue Draft
                      </Link>
                      <Link
                        href={`/workspace/${workspaceId}/evidence?claimId=${activeDraft.claim_schema_id}`}
                        className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-semibold text-amber-900 hover:bg-amber-100"
                      >
                        Open Evidence
                      </Link>
                    </div>
                  </div>
                ) : null}

                {latestLockedClaim ? (
                  <div className="mt-4 rounded-2xl border border-green-200 bg-green-50 p-5">
                    <div className="text-xs font-semibold uppercase tracking-[0.16em] text-green-700">
                      Latest finalized record
                    </div>
                    <div className="mt-2 text-lg font-semibold text-green-950">
                      {latestLockedClaim.name || "Unnamed locked claim"}
                    </div>
                    <div className="mt-2 text-sm text-green-800">
                      claim #{latestLockedClaim.claim_schema_id} · locked · visibility:{" "}
                      {latestLockedClaim.scope?.visibility || "private"}
                    </div>
                  </div>
                ) : null}

                {recentClaims.length === 0 ? (
                  <div className="mt-4 text-slate-500">No claims available yet.</div>
                ) : (
                  <div className="mt-5 space-y-3">
                    {recentClaims.map((claim) => (
                      <div
                        key={claim?.claim_schema_id}
                        className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4"
                      >
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <div className="font-medium">
                              {claim?.name || "Unnamed claim"}
                            </div>
                            <span
                              className={`rounded-full border px-2.5 py-1 text-[11px] font-semibold ${getClaimStatusBadgeClass(
                                claim?.verification_status
                              )}`}
                            >
                              {String(claim?.verification_status || "unknown").toUpperCase()}
                            </span>
                          </div>

                          <div className="mt-1 text-sm text-slate-500">
                            claim #{claim?.claim_schema_id} · visibility:{" "}
                            {claim?.scope?.visibility || "private"}
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <Link
                            href={`/workspace/${workspaceId}/claim/${claim?.claim_schema_id}`}
                            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                          >
                            Open
                          </Link>

                          <Link
                            href={`/workspace/${workspaceId}/evidence?claimId=${claim?.claim_schema_id}`}
                            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                          >
                            Evidence
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="rounded-2xl border bg-white p-6 shadow-sm">
                <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Operational guidance
                </div>
                <h2 className="mt-2 text-2xl font-semibold">Next Actions</h2>

                <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-5">
                  <div className="text-sm font-semibold text-blue-900">{nextAction.title}</div>
                  <div className="mt-2 text-sm leading-7 text-blue-800">
                    {nextAction.description}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-3">
                    {nextAction.primaryAction === "create" ? (
                      <ActionButton
                        onClick={() => void handleCreateDraftClick()}
                        label={nextAction.primaryLabel}
                        loading={createChecking}
                        disabled={!canCreateClaim}
                      />
                    ) : nextAction.primaryHref ? (
                      <ActionLink href={nextAction.primaryHref} label={nextAction.primaryLabel} active />
                    ) : null}

                    {nextAction.secondaryHref && nextAction.secondaryLabel ? (
                      <ActionLink href={nextAction.secondaryHref} label={nextAction.secondaryLabel} />
                    ) : null}
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  {canCreateClaim ? (
                    <ActionButton
                      onClick={() => void handleCreateDraftClick()}
                      label="Create Draft Claim"
                      loading={createChecking}
                    />
                  ) : (
                    <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-3 text-center text-sm font-medium text-slate-500">
                      Claim creation available to owner/operator only
                    </div>
                  )}

                  {canImportTrades ? (
                    <ActionLink href={`/workspace/${workspaceId}/import`} label="Import Trades" />
                  ) : (
                    <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-3 text-center text-sm font-medium text-slate-500">
                      Trade import available to owner/operator only
                    </div>
                  )}

                  <ActionLink href={`/workspace/${workspaceId}/ledger`} label="Open Ledger" />
                  <ActionLink href={`/workspace/${workspaceId}/claims`} label="Open Claim Library" />
                  <ActionLink href={`/workspace/${workspaceId}/settings`} label="Open Settings & Billing" />
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