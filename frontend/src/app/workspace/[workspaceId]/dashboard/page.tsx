"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";
import {
  api,
  type DashboardResponse,
  type PublicClaimDirectoryItem,
  type WorkspaceUsageSummary,
} from "../../../../lib/api";

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
      <div className="mt-2 text-3xl font-bold">{value}</div>
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
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-bold">{formatPercent(ratio)}</div>
      <div className="mt-2 text-xs text-slate-500">
        {formatNumber(used)} used of {formatNumber(limit)}
        {suffix}
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
        Your current workspace role is <span className="font-semibold">{workspaceRole || "member"}</span>.
        You can review dashboard metrics, ledger evidence, claims, and settings visibility, but
        claim creation and trade import remain restricted to owner/operator roles.
      </p>

      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href={`/workspace/${workspaceId}/claims`}
          className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
        >
          Open Claims Registry
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

  const upgradeRequiredNow = Boolean(usage?.governance?.upgrade_required_now);
  const upgradeRecommendedSoon = Boolean(usage?.governance?.upgrade_recommended_soon);
  const recommendedPlanName = usage?.upgrade_recommendation?.recommended_plan_name;
  const breachedDimensions = usage?.upgrade_recommendation?.breached_dimensions ?? [];
  const nearLimitDimensions = usage?.upgrade_recommendation?.near_limit_dimensions ?? [];

  if (!hasAnyAtOrOverLimit && !upgradeRequiredNow && !upgradeRecommendedSoon) {
    return null;
  }

  return (
    <div className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
      <h2 className="text-xl font-semibold">
        {upgradeRequiredNow || hasAnyAtOrOverLimit
          ? "Workspace At / Over Plan Limits"
          : "Workspace Upgrade Recommendation"}
      </h2>

      <p className="mt-2 text-sm">
        {upgradeRequiredNow || hasAnyAtOrOverLimit
          ? "This workspace has reached or exceeded one or more plan limits. Some write actions may now be blocked until the workspace is upgraded or usage is reduced."
          : "This workspace is approaching one or more plan ceilings. Upgrading early will protect operational continuity."}
      </p>

      {recommendedPlanName ? (
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
                {item}
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
                {item}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-4">
        <Link
          href={`/workspace/${workspaceId}/settings`}
          className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
        >
          Review Plan & Billing
        </Link>
      </div>
    </div>
  );
}

export default function WorkspaceDashboardPage() {
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
  const canCreateClaim = workspaceRole === "owner" || workspaceRole === "operator";
  const canImportTrades = workspaceRole === "owner" || workspaceRole === "operator";

  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [claims, setClaims] = useState<PublicClaimDirectoryItem[]>([]);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
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

  const lockedClaims = claims.filter(
    (c) => normalizeText(c?.verification_status) === "locked"
  ).length;

  const publicClaims = claims.filter(
    (c) =>
      normalizeText(c?.scope?.visibility) === "public" &&
      ["published", "locked"].includes(normalizeText(c?.verification_status))
  ).length;

  const recentClaims = [...claims]
    .sort((a, b) => (b?.claim_schema_id ?? 0) - (a?.claim_schema_id ?? 0))
    .slice(0, 5);

  const membersUsage = usage?.usage?.members ?? { used: 0, limit: 0, ratio: 0 };
  const tradesUsage = usage?.usage?.trades ?? { used: 0, limit: 0, ratio: 0 };
  const claimsUsage = usage?.usage?.claims ?? { used: 0, limit: 0, ratio: 0 };
  const storageUsage = usage?.usage?.storage_mb ?? { used: 0, limit: 0, ratio: 0 };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Operations</div>
          <h1 className="mt-2 text-4xl font-bold">Workspace Dashboard</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Control center for workspace {workspaceId}, including claim activity, ledger volume,
            plan usage, and quick access to creation, evidence, and verification workflows.
          </p>
        </div>

        <RoleBanner workspaceId={workspaceId} workspaceRole={workspaceRole} />
        <GovernanceBanner workspaceId={workspaceId} usage={usage} />

        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <SummaryCard
            label="Workspace Members"
            value={formatNumber(dashboard.member_count)}
            hint={`${formatNumber(membersUsage.used)} / ${formatNumber(membersUsage.limit)} · ${formatPercent(membersUsage.ratio)}`}
          />
          <SummaryCard
            label="Total Trades"
            value={formatNumber(dashboard.trade_count)}
            hint={`${formatNumber(tradesUsage.used)} / ${formatNumber(tradesUsage.limit)} · ${formatPercent(tradesUsage.ratio)}`}
          />
          <SummaryCard
            label="Total Claims"
            value={formatNumber(dashboard.claim_count)}
            hint={`${formatNumber(claimsUsage.used)} / ${formatNumber(claimsUsage.limit)} · ${formatPercent(claimsUsage.ratio)}`}
          />
          <SummaryCard
            label="Locked / Public"
            value={`${lockedClaims} / ${publicClaims}`}
            hint={`Plan: ${usage?.plan_code || "—"} · Billing: ${usage?.billing_status || "—"}`}
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

        <div className="mb-8 grid gap-6 lg:grid-cols-[1.3fr_1fr]">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Recent Claims</h2>

            {recentClaims.length === 0 ? (
              <div className="mt-4 text-slate-500">No claims available yet.</div>
            ) : (
              <div className="mt-4 space-y-3">
                {recentClaims.map((claim) => (
                  <div
                    key={claim?.claim_schema_id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4"
                  >
                    <div>
                      <div className="font-medium">{claim?.name || "Unnamed claim"}</div>
                      <div className="mt-1 text-sm text-slate-500">
                        claim #{claim?.claim_schema_id} · {claim?.verification_status} ·{" "}
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
            <h2 className="text-2xl font-semibold">Quick Actions</h2>

            <div className="mt-4 space-y-3">
              {canCreateClaim ? (
                <ActionLink href={`/workspace/${workspaceId}/schema`} label="Create Draft Claim" />
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
              <ActionLink href={`/workspace/${workspaceId}/claims`} label="Open Claims Registry" />
              <ActionLink href={`/workspace/${workspaceId}/settings`} label="Open Settings & Billing" />
            </div>

            {!canCreateClaim || !canImportTrades ? (
              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                Your current role is <span className="font-medium">{workspaceRole}</span>. Some
                workspace write actions are restricted by role.
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}