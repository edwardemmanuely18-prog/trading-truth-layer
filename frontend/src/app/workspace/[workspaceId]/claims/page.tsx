"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";
import {
  api,
  type PublicClaimDirectoryItem,
  type WorkspaceUsageSummary,
} from "../../../../lib/api";
import PaywallModal from "../../../../components/PaywallModal";
import { useWorkspaceGate } from "../../../../hooks/useWorkspaceGate";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function normalizeText(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function safeLeaderboard(claim: PublicClaimDirectoryItem) {
  return Array.isArray(claim?.leaderboard) ? claim.leaderboard : [];
}

function safeScope(claim: PublicClaimDirectoryItem) {
  return claim?.scope ?? {
    period_start: "",
    period_end: "",
    included_members: [],
    included_symbols: [],
    methodology_notes: "",
    visibility: "",
  };
}

function safeLifecycle(claim: PublicClaimDirectoryItem) {
  return claim?.lifecycle ?? {
    status: "",
    verified_at: null,
    published_at: null,
    locked_at: null,
    locked_trade_set_hash: null,
  };
}

function getPlanName(usage?: WorkspaceUsageSummary | null, planCode?: string | null) {
  const normalized = normalizeText(planCode);
  const matched = usage?.plan_catalog?.find(
    (plan) => normalizeText(plan.code) === normalized
  );
  return matched?.name || planCode || "current plan";
}

function StatusBadge({ status }: { status?: string | null }) {
  const normalized = normalizeText(status);

  const className =
    normalized === "locked"
      ? "bg-green-100 text-green-800 border-green-200"
      : normalized === "published"
        ? "bg-blue-100 text-blue-800 border-blue-200"
        : normalized === "verified"
          ? "bg-amber-100 text-amber-800 border-amber-200"
          : "bg-slate-100 text-slate-800 border-slate-200";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function VisibilityBadge({ visibility }: { visibility?: string | null }) {
  const normalized = normalizeText(visibility);

  const className =
    normalized === "public"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : normalized === "unlisted"
        ? "border-violet-200 bg-violet-50 text-violet-800"
        : "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {visibility || "unknown"}
    </span>
  );
}

function ExposureBadge({ accessible }: { accessible: boolean }) {
  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${
        accessible
          ? "border-green-200 bg-green-50 text-green-700"
          : "border-slate-200 bg-slate-50 text-slate-700"
      }`}
    >
      {accessible ? "public route ready" : "internal only"}
    </span>
  );
}

function FilterChip({
  onClick,
  label,
  active,
}: {
  onClick: () => void;
  label: string;
  active: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex rounded-full border px-4 py-2 text-sm transition ${
        active
          ? "border-slate-900 bg-slate-900 text-white"
          : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
      }`}
    >
      {label}
    </button>
  );
}

function ActionLink({
  href,
  label,
  tone = "neutral",
}: {
  href: string;
  label: string;
  tone?: "neutral" | "disabled";
}) {
  if (tone === "disabled") {
    return (
      <span className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-400">
        {label}
      </span>
    );
  }

  return (
    <Link
      href={href}
      className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
    >
      {label}
    </Link>
  );
}

function sortClaims(claims: PublicClaimDirectoryItem[], sort: string) {
  const items = [...claims];

  switch (sort) {
    case "net_pnl_desc":
      return items.sort((a, b) => (b.net_pnl ?? 0) - (a.net_pnl ?? 0));
    case "net_pnl_asc":
      return items.sort((a, b) => (a.net_pnl ?? 0) - (b.net_pnl ?? 0));
    case "profit_factor_desc":
      return items.sort((a, b) => (b.profit_factor ?? 0) - (a.profit_factor ?? 0));
    case "win_rate_desc":
      return items.sort((a, b) => (b.win_rate ?? 0) - (a.win_rate ?? 0));
    case "name_asc":
      return items.sort((a, b) => a.name.localeCompare(b.name));
    case "oldest":
      return items.sort((a, b) => a.claim_schema_id - b.claim_schema_id);
    case "newest":
    default:
      return items.sort((a, b) => b.claim_schema_id - a.claim_schema_id);
  }
}

function filterClaims(
  claims: PublicClaimDirectoryItem[],
  q: string,
  status: string,
  visibility: string
) {
  const query = normalizeText(q);

  return claims.filter((claim) => {
    const scope = safeScope(claim);

    const matchesQuery =
      !query ||
      normalizeText(claim.name).includes(query) ||
      normalizeText(claim.claim_hash).includes(query) ||
      normalizeText(claim.claim_schema_id).includes(query) ||
      normalizeText(scope.methodology_notes).includes(query) ||
      normalizeText(scope.period_start).includes(query) ||
      normalizeText(scope.period_end).includes(query);

    const matchesStatus =
      status === "all" || normalizeText(claim.verification_status) === normalizeText(status);

    const matchesVisibility =
      visibility === "all" || normalizeText(scope.visibility) === normalizeText(visibility);

    return matchesQuery && matchesStatus && matchesVisibility;
  });
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

function ClaimCard({
  claim,
  workspaceId,
}: {
  claim: PublicClaimDirectoryItem;
  workspaceId: number;
}) {
  const scope = safeScope(claim);
  const lifecycle = safeLifecycle(claim);
  const leaderboard = safeLeaderboard(claim);
  const isPubliclyAccessible = Boolean(claim.is_publicly_accessible);

  return (
    <div className="rounded-3xl border bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="mb-2 text-sm text-slate-500">Workspace Claim Record</div>
          <h2 className="text-2xl font-semibold tracking-tight">{claim.name}</h2>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={claim.verification_status} />
            <VisibilityBadge visibility={scope.visibility} />
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
              claim #{claim.claim_schema_id}
            </span>
            <ExposureBadge accessible={isPubliclyAccessible} />
          </div>

          <div className="mt-4 text-sm text-slate-600">
            Internal registry view for lifecycle-governed claim inspection, evidence routing,
            lineage-aware review, and public exposure control.
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {isPubliclyAccessible ? (
            <ActionLink href={`/verify/${claim.claim_hash}`} label="Public Verify" />
          ) : (
            <ActionLink href="#" label="Public Verify Unavailable" tone="disabled" />
          )}

          <ActionLink
            href={`/workspace/${workspaceId}/claim/${claim.claim_schema_id}`}
            label="Internal View"
          />

          <ActionLink
            href={`/workspace/${workspaceId}/evidence?claimId=${claim.claim_schema_id}`}
            label="Evidence"
          />
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Trade Count</div>
          <div className="mt-1 text-2xl font-semibold">{claim.trade_count ?? 0}</div>
        </div>

        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Net PnL</div>
          <div className="mt-1 text-2xl font-semibold">{formatNumber(claim.net_pnl)}</div>
        </div>

        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Profit Factor</div>
          <div className="mt-1 text-2xl font-semibold">
            {formatNumber(claim.profit_factor, 4)}
          </div>
        </div>

        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Win Rate</div>
          <div className="mt-1 text-2xl font-semibold">{formatNumber(claim.win_rate, 4)}</div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div>
          <div className="text-sm text-slate-500">Verification Scope</div>
          <div className="mt-1 font-medium">
            {scope.period_start || "—"} → {scope.period_end || "—"}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Included Members</div>
              <div className="mt-1 text-sm font-medium">
                {Array.isArray(scope.included_members) && scope.included_members.length > 0
                  ? scope.included_members.join(", ")
                  : "All in scope"}
              </div>
            </div>

            <div className="rounded-xl bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Included Symbols</div>
              <div className="mt-1 text-sm font-medium">
                {Array.isArray(scope.included_symbols) && scope.included_symbols.length > 0
                  ? scope.included_symbols.join(", ")
                  : "All in scope"}
              </div>
            </div>
          </div>

          <div className="mt-4 text-sm text-slate-500">Methodology</div>
          <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm whitespace-pre-wrap text-slate-700">
            {scope.methodology_notes || "—"}
          </div>
        </div>

        <div>
          <div className="text-sm text-slate-500">Lifecycle</div>
          <div className="mt-2 space-y-2 rounded-xl bg-slate-50 p-4 text-sm">
            <div>verified: {formatDateTime(lifecycle.verified_at)}</div>
            <div>published: {formatDateTime(lifecycle.published_at)}</div>
            <div>locked: {formatDateTime(lifecycle.locked_at)}</div>
          </div>

          <div className="mt-4 text-sm text-slate-500">Claim Hash</div>
          <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
            {claim.claim_hash || "—"}
          </div>

          <div className="mt-4 text-sm text-slate-500">Trade Set Hash</div>
          <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
            {claim.trade_set_hash || "—"}
          </div>
        </div>
      </div>

      {leaderboard.length > 0 ? (
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium text-slate-700">Top Leaderboard Entries</div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="px-3 py-2">Rank</th>
                  <th className="px-3 py-2">Member</th>
                  <th className="px-3 py-2">Net PnL</th>
                  <th className="px-3 py-2">Win Rate</th>
                  <th className="px-3 py-2">Profit Factor</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.slice(0, 5).map((row) => (
                  <tr
                    key={`${claim.claim_schema_id}-${row.rank}-${row.member}`}
                    className="border-b last:border-0"
                  >
                    <td className="px-3 py-2">{row.rank}</td>
                    <td className="px-3 py-2">{row.member}</td>
                    <td className="px-3 py-2">{formatNumber(row.net_pnl)}</td>
                    <td className="px-3 py-2">{formatNumber(row.win_rate, 4)}</td>
                    <td className="px-3 py-2">{formatNumber(row.profit_factor, 4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function WorkspaceClaimsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, workspaces, loading: authLoading, getWorkspaceRole } = useAuth();
  const { paywallState, closePaywall, openPaywall, gateAndExecute } = useWorkspaceGate();

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

  const [claims, setClaims] = useState<PublicClaimDirectoryItem[]>([]);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [usageLoading, setUsageLoading] = useState(true);
  const [createLoading, setCreateLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const q = searchParams.get("q") || "";
  const sort = searchParams.get("sort") || "newest";
  const status = searchParams.get("status") || "all";
  const visibility = searchParams.get("visibility") || "all";

  useEffect(() => {
    async function loadClaims() {
      if (!workspaceId || !workspaceMembership) return;

      try {
        setLoading(true);
        setError(null);
        const rows = await api.getWorkspaceClaims(workspaceId);
        setClaims(Array.isArray(rows) ? rows : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load workspace claims.");
      } finally {
        setLoading(false);
      }
    }

    if (!authLoading && workspaceMembership) {
      void loadClaims();
    } else if (!authLoading && !workspaceMembership) {
      setLoading(false);
    }
  }, [workspaceId, workspaceMembership, authLoading]);

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      if (!workspaceId || !workspaceMembership) {
        setUsageLoading(false);
        return;
      }

      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(workspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setUsageLoading(false);
      }
    }

    if (!authLoading && workspaceMembership) {
      void loadUsage();
    }

    return () => {
      active = false;
    };
  }, [workspaceId, workspaceMembership, authLoading]);

  const filtered = useMemo(() => {
    return sortClaims(filterClaims(claims, q, status, visibility), sort);
  }, [claims, q, sort, status, visibility]);

  const draftCount = claims.filter((claim) => normalizeText(claim.verification_status) === "draft").length;
  const verifiedCount = claims.filter((claim) => normalizeText(claim.verification_status) === "verified").length;
  const publishedOrLockedCount = claims.filter((claim) => {
    const statusText = normalizeText(claim.verification_status);
    return statusText === "published" || statusText === "locked";
  }).length;
  const publicRouteReadyCount = claims.filter((claim) => Boolean(claim.is_publicly_accessible)).length;

  const claimUsage = usage?.usage?.claims;
  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 && (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);
  const billingActivationRecommended = Boolean(usage?.governance?.billing_activation_recommended);

  const configuredPlanName = getPlanName(
    usage,
    usage?.governance?.configured_plan_code || usage?.plan_code
  );
  const effectivePlanName = getPlanName(
    usage,
    usage?.governance?.effective_plan_code || usage?.effective_plan_code
  );
  const recommendedPlanName =
    usage?.upgrade_recommendation?.recommended_plan_name || configuredPlanName;

  function setFilters(next: {
    q?: string;
    sort?: string;
    status?: string;
    visibility?: string;
  }) {
    if (!workspaceId) return;

    const query = new URLSearchParams({
      q: next.q ?? q,
      sort: next.sort ?? sort,
      status: next.status ?? status,
      visibility: next.visibility ?? visibility,
    });

    router.push(`/workspace/${workspaceId}/claims?${query.toString()}`);
  }

  function resetFilters() {
    if (!workspaceId) return;
    router.push(`/workspace/${workspaceId}/claims?q=&sort=newest&status=all&visibility=all`);
  }

  async function handleCreateDraftClick() {
    if (!workspaceId) return;

    try {
      setCreateLoading(true);

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
    } catch (err) {
      if (err instanceof Error) {
        openPaywall({
          reason: claimLimitReached ? "claim_limit_reached" : "feature_locked",
          actionLabel: "Create draft claim",
          message: err.message,
        });
      }
    } finally {
      setCreateLoading(false);
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
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading claims...</div>
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
            You do not have access to this workspace claims registry.
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
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading claims...</div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        </main>
      </div>
    );
  }

  return (
    <>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />

        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="mb-8">
            <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Registry</div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Workspace Claims</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Internal registry for lifecycle-governed claim records in workspace {workspaceId}, with
              evidence access, public exposure status, and operator-grade verification routing.
            </p>
          </div>

          <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <SummaryCard label="Total Claims" value={claims.length} hint="All records in this workspace" />
            <SummaryCard
              label="Draft / Verified"
              value={`${draftCount} / ${verifiedCount}`}
              hint="Pre-public lifecycle inventory"
            />
            <SummaryCard
              label="Published / Locked"
              value={publishedOrLockedCount}
              hint="Externally presentable records"
            />
            <SummaryCard
              label="Public Route Ready"
              value={publicRouteReadyCount}
              hint="Public or unlisted + lifecycle-gated"
            />
          </div>

          <div className="mb-6 rounded-3xl border bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-lg font-semibold text-slate-950">Claim Creation Capacity</div>
                <div className="mt-2 text-sm text-slate-600">
                  Governed claim creation should reflect the current effective plan posture and route blocked
                  creation into billing recovery cleanly.
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
                <div className="text-slate-500">Claim usage</div>
                <div className="mt-1 font-semibold text-slate-900">
                  {usageLoading
                    ? "Loading..."
                    : `${claimUsage?.used ?? 0} / ${claimUsage?.limit ?? "—"} · ${formatPercent(
                        claimUsage?.ratio
                      )}`}
                </div>
              </div>
            </div>

            {claimLimitReached ? (
              <div
                className={`mt-4 rounded-2xl border p-4 text-sm ${
                  billingActivationRecommended
                    ? "border-blue-200 bg-blue-50 text-blue-900"
                    : "border-amber-200 bg-amber-50 text-amber-900"
                }`}
              >
                <div className="font-medium">
                  {billingActivationRecommended ? "Billing activation needed" : "Claim capacity reached"}
                </div>
                <div className="mt-2">
                  {billingActivationRecommended
                    ? `This workspace is already configured on ${configuredPlanName}, but billing is not active yet. Effective enforcement still follows ${effectivePlanName}. Activate billing to continue governed claim creation.`
                    : `This workspace has reached governed claim capacity under the current enforced plan posture. Review billing and ${recommendedPlanName} to continue creating draft claims.`}
                </div>
              </div>
            ) : (
              <div className="mt-4 rounded-2xl border border-green-200 bg-green-50 p-4 text-sm text-green-800">
                Claim creation capacity is currently available under the effective workspace plan posture.
              </div>
            )}
          </div>

          <div className="mb-8 rounded-3xl border bg-white p-5 shadow-sm">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                const form = new FormData(event.currentTarget);
                setFilters({
                  q: String(form.get("q") || ""),
                  sort: String(form.get("sort") || "newest"),
                  status: String(form.get("status") || "all"),
                  visibility: String(form.get("visibility") || "all"),
                });
              }}
              className="space-y-4"
            >
              <div className="grid gap-4 lg:grid-cols-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Search</label>
                  <input
                    type="text"
                    name="q"
                    defaultValue={q}
                    placeholder="Search by name, claim id, hash, notes..."
                    className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                  />
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Sort By</label>
                  <select
                    name="sort"
                    defaultValue={sort}
                    className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                  >
                    <option value="newest">Newest</option>
                    <option value="oldest">Oldest</option>
                    <option value="net_pnl_desc">Net PnL High → Low</option>
                    <option value="net_pnl_asc">Net PnL Low → High</option>
                    <option value="profit_factor_desc">Best Profit Factor</option>
                    <option value="win_rate_desc">Best Win Rate</option>
                    <option value="name_asc">Name A → Z</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Status</label>
                  <select
                    name="status"
                    defaultValue={status}
                    className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                  >
                    <option value="all">All statuses</option>
                    <option value="draft">Draft</option>
                    <option value="verified">Verified</option>
                    <option value="published">Published</option>
                    <option value="locked">Locked</option>
                  </select>
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">Visibility</label>
                  <select
                    name="visibility"
                    defaultValue={visibility}
                    className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                  >
                    <option value="all">All visibility</option>
                    <option value="public">Public</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="private">Private</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="submit"
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                >
                  Apply Filters
                </button>

                <button
                  type="button"
                  onClick={resetFilters}
                  className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
                >
                  Reset
                </button>

                <button
                  type="button"
                  onClick={() => void handleCreateDraftClick()}
                  disabled={createLoading || usageLoading}
                  className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
                >
                  {createLoading ? "Checking Access..." : "Create Draft Claim"}
                </button>

                <div className="text-sm text-slate-500">
                  Showing {filtered.length} of {claims.length} workspace claim
                  {claims.length === 1 ? "" : "s"}.
                </div>
              </div>
            </form>

            <div className="mt-4 flex flex-wrap gap-2">
              <FilterChip
                onClick={() => setFilters({ sort: "newest" })}
                label="Newest"
                active={sort === "newest"}
              />
              <FilterChip
                onClick={() => setFilters({ sort: "net_pnl_desc" })}
                label="Best Net PnL"
                active={sort === "net_pnl_desc"}
              />
              <FilterChip
                onClick={() => setFilters({ sort: "profit_factor_desc" })}
                label="Best Profit Factor"
                active={sort === "profit_factor_desc"}
              />
              <FilterChip
                onClick={() => setFilters({ sort: "win_rate_desc" })}
                label="Best Win Rate"
                active={sort === "win_rate_desc"}
              />
              <FilterChip
                onClick={() => setFilters({ status: "locked" })}
                label="Locked Only"
                active={status === "locked"}
              />
              <FilterChip
                onClick={() => setFilters({ visibility: "public" })}
                label="Public Only"
                active={visibility === "public"}
              />
              <FilterChip
                onClick={() => setFilters({ visibility: "private" })}
                label="Private Only"
                active={visibility === "private"}
              />
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="text-slate-600">No claims match the selected filters.</div>
            </div>
          ) : (
            <div className="space-y-6">
              {filtered.map((claim) => (
                <ClaimCard
                  key={`${claim.claim_schema_id}-${claim.claim_hash}`}
                  claim={claim}
                  workspaceId={workspaceId}
                />
              ))}
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
        usageLabel={
          claimUsage
            ? `${claimUsage.used} / ${claimUsage.limit}${
                claimUsage.ratio !== null && claimUsage.ratio !== undefined
                  ? ` · ${formatPercent(claimUsage.ratio)}`
                  : ""
              }`
            : `Effective plan: ${effectivePlanName}`
        }
        recommendedPlanName={billingActivationRecommended ? configuredPlanName : recommendedPlanName}
        onUpgrade={() => {
          router.push(`/workspace/${workspaceId}/settings?tab=billing`);
        }}
      />
    </>
  );
}