"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, usePathname } from "next/navigation";
import {
  api,
  type AuditEvent,
  type ClaimEquityCurve,
  type ClaimIntegrityResult,
  type ClaimSchema,
  type ClaimSchemaPreview,
  type ClaimTradeEvidence,
  type ClaimTradeScopeReason,
  type ClaimTradeScopeRow,
  type ClaimVersion,
  type ClaimDispute,
  type WorkspaceUsageSummary,
} from "../../../../../lib/api";
import Navbar from "../../../../../components/Navbar";
import ClaimLifecycleActions from "../../../../../components/ClaimLifecycleActions";
import CreateClaimVersionButton from "../../../../../components/CreateClaimVersionButton";
import EditClaimDraftButton from "../../../../../components/EditClaimDraftButton";
import EquityCurveChart from "../../../../../components/EquityCurveChart";
import AuditTimeline from "../../../../../components/AuditTimeline";
import { useAuth } from "../../../../../components/AuthProvider";

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

function formatPercent(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

function truncateMiddle(value?: string | null, start = 12, end = 10) {
  if (!value) return "—";
  if (value.length <= start + end + 3) return value;
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function resolveCanonicalLineage(row: {
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  version_number?: number | null;
}) {
  const rootClaimId =
    typeof row?.root_claim_id === "number" ? row.root_claim_id : null;

  const parentClaimId =
    typeof row?.parent_claim_id === "number" ? row.parent_claim_id : null;

  const versionNumber =
    typeof row?.version_number === "number" ? row.version_number : 1;

  return {
    rootClaimId,
    parentClaimId,
    versionNumber,
  };
}

function resolveClaimOriginType(row: {
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  version_number?: number | null;
}) {
  const lineage = resolveCanonicalLineage(row);

  if (lineage.versionNumber > 1) return "versioned";
  if (lineage.parentClaimId || lineage.rootClaimId) return "derived";
  return "independent";
}

function resolveNetworkLabel(row: {
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  version_number?: number | null;
}) {
  const type = resolveClaimOriginType(row);

  if (type === "versioned") return "Versioned Claim";
  if (type === "derived") return "Derived Claim";
  return "Independent Claim";
}

function networkTone(row: {
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  version_number?: number | null;
}) {
  const type = resolveClaimOriginType(row);

  if (type === "independent") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }

  if (type === "derived") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }

  return "border-sky-200 bg-sky-50 text-sky-800";
}

function buildLineageSummary(row: {
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  version_number?: number | null;
}) {
  const lineage = resolveCanonicalLineage(row);

  return {
    root: lineage.rootClaimId ? `claim#${lineage.rootClaimId}` : "self",
    parent: lineage.parentClaimId ? `claim#${lineage.parentClaimId}` : "none",
    version: String(lineage.versionNumber),
  };
}

function resolveIssuerName(claim: ClaimSchema, workspaceId: number) {
  return `workspace#${workspaceId}`;
}

function emptyTradeEvidence(claimId: number): ClaimTradeEvidence {
  return {
    claim_schema_id: claimId,
    claim_hash: "",
    name: "",
    status: "",
    trade_count: 0,
    trades: [],
    included_trade_count: 0,
    excluded_trade_count: 0,
    included_trades: [],
    excluded_trades: [],
    summary: {
      workspace_trade_count: 0,
      included_trade_count: 0,
      excluded_trade_count: 0,
      excluded_breakdown: {},
    },
  };
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
        : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      visibility: {visibility || "unknown"}
    </span>
  );
}

function IntegrityBadge({ integrity }: { integrity?: ClaimIntegrityResult | null }) {
  if (!integrity) {
    return (
      <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
        not checked
      </span>
    );
  }

  const ok = integrity.hash_match && integrity.integrity_status === "valid";

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${
        ok
          ? "border-green-200 bg-green-100 text-green-800"
          : "border-red-200 bg-red-100 text-red-800"
      }`}
    >
      {ok ? "integrity valid" : "integrity compromised"}
    </span>
  );
}

function RoleBadge({ role }: { role?: string | null }) {
  const normalized = normalizeText(role);

  const className =
    normalized === "owner"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "operator"
        ? "border-blue-200 bg-blue-100 text-blue-800"
        : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      role: {role || "unknown"}
    </span>
  );
}

function CopyButton({
  value,
  label = "Copy",
}: {
  value?: string | null;
  label?: string;
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <button
      type="button"
      onClick={() => void handleCopy()}
      disabled={!value}
      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {copied ? "Copied" : label}
    </button>
  );
}

function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold tracking-tight">{value}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div>
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 font-medium">{value}</div>
    </div>
  );
}

function HashCard({
  title,
  value,
  copyLabel,
}: {
  title: string;
  value?: string | null;
  copyLabel?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold">{title}</h3>
          <div className="mt-1 text-sm text-slate-500">
            Canonical fingerprint used in trust and verification workflows.
          </div>
        </div>
        <CopyButton value={value} label={copyLabel || "Copy"} />
      </div>

      <div className="mt-4 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
        {value || "—"}
      </div>
    </div>
  );
}

function GovernanceCard({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <div className="mt-2 text-sm leading-6 text-slate-600">{body}</div>
    </div>
  );
}

function PageNavButton({
  href,
  label,
  active,
  disabled = false,
}: {
  href: string;
  label: string;
  active: boolean;
  disabled?: boolean;
}) {
  if (disabled) {
    return (
      <span className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-400">
        {label}
      </span>
    );
  }

  return (
    <Link
      href={href}
      className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
        active
          ? "bg-slate-900 text-white"
          : "border border-slate-300 text-slate-700 hover:bg-slate-50"
      }`}
    >
      {label}
    </Link>
  );
}

function VersionCard({
  version,
  workspaceId,
  isCurrent,
}: {
  version: ClaimVersion;
  workspaceId: number;
  isCurrent: boolean;
}) {
  return (
    <Link
      href={`/workspace/${workspaceId}/claim/${version.id}`}
      className={`block rounded-xl border p-3 transition hover:bg-slate-50 ${
        isCurrent ? "border-slate-900 bg-slate-50" : "border-slate-200"
      }`}
    >
      <div className="flex items-center justify-between gap-2">
        <div>
          <div className="font-medium">{version.name}</div>
          <div className="mt-1 text-xs text-slate-500">
            version {version.version_number} · root{" "}
            {version.root_claim_id ? `claim#${version.root_claim_id}` : "self"} · parent{" "}
            {version.parent_claim_id ? `claim#${version.parent_claim_id}` : "none"}
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          {isCurrent ? (
            <span className="rounded-full border border-slate-300 bg-white px-3 py-1 text-[11px] font-semibold text-slate-700">
              current
            </span>
          ) : null}
          <StatusBadge status={version.status} />
        </div>
      </div>
    </Link>
  );
}

function ScopeStatusBadge({ status }: { status?: string | null }) {
  const normalized = normalizeText(status);
  const className =
    normalized === "excluded"
      ? "border-red-200 bg-red-50 text-red-700"
      : "border-green-200 bg-green-50 text-green-700";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function ExclusionReasonBadge({ reason }: { reason?: string | null }) {
  if (!reason) {
    return <span className="text-slate-400">—</span>;
  }

  return (
    <span className="inline-flex rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
      {reason}
    </span>
  );
}

function humanizeReason(reason: ClaimTradeScopeReason | string) {
  switch (reason) {
    case "OUTSIDE_PERIOD":
      return "Outside period";
    case "MEMBER_FILTER":
      return "Member filter";
    case "SYMBOL_FILTER":
      return "Symbol filter";
    case "MANUAL_EXCLUSION":
      return "Manual exclusion";
    default:
      return reason;
  }
}

function GovernanceOverview({
  claim,
  versions,
  auditEvents,
  integrity,
}: {
  claim: ClaimSchema;
  versions: ClaimVersion[];
  auditEvents: AuditEvent[];
  integrity: ClaimIntegrityResult | null;
}) {
  const latestEvent = auditEvents[0] ?? null;
  const lineageDepth = versions.length;
  const lineageSummary = buildLineageSummary(claim);
  const networkLabel = resolveNetworkLabel(claim);
  const networkClassName = networkTone(claim);
  const integrityState = integrity
    ? integrity.integrity_status === "valid" && integrity.hash_match
      ? "Confirmed"
      : "Compromised"
    : claim.status === "locked"
      ? "Pending check"
      : "Pre-lock";

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">Governance Overview</h2>
          <div className="mt-1 text-sm text-slate-500">
            Lineage, lifecycle, integrity, and audit posture for this claim record.
          </div>
        </div>

        <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">
          claim #{claim.id}
        </span>
      </div>

      <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${networkClassName}`}>
        network: {normalizeText(resolveClaimOriginType(claim))}
      </span>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Lifecycle state</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{claim.status}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Integrity posture</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{integrityState}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Network State</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{networkLabel}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Latest audit event</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {latestEvent?.event_type || "—"}
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Root</div>
          <div className="mt-1 text-base font-semibold text-slate-900">{lineageSummary.root}</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Parent</div>
          <div className="mt-1 text-base font-semibold text-slate-900">{lineageSummary.parent}</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Version</div>
          <div className="mt-1 text-base font-semibold text-slate-900">{lineageSummary.version}</div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <div className="font-medium text-slate-900">Version governance</div>
          <div className="mt-2">
            Claim versions should preserve historical states instead of mutating prior records. This
            makes comparison, accountability, and later public verification defensible.
          </div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <div className="font-medium text-slate-900">Audit governance</div>
          <div className="mt-2">
            Every draft edit and lifecycle transition should remain visible in audit history so
            external trust can be supported by internal evidence.
          </div>
        </div>
      </div>
    </div>
  );
}

function ScopeSummaryCard({ evidence }: { evidence: ClaimTradeEvidence | null }) {
  const summary = evidence?.summary;
  const breakdown = summary?.excluded_breakdown ?? {};

  const breakdownRows = (Object.entries(breakdown) as [string, number][])
    .filter(([, value]) => Number(value) > 0)
    .sort((a, b) => Number(b[1]) - Number(a[1]));

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">Scope Summary</h2>
          <div className="mt-1 text-sm text-slate-500">
            Explainability layer for what entered claim computation and what was left out.
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl bg-slate-50 px-4 py-3">
          <div className="text-sm text-slate-500">Workspace Trades</div>
          <div className="mt-1 text-xl font-semibold">{summary?.workspace_trade_count ?? 0}</div>
        </div>
        <div className="rounded-xl bg-green-50 px-4 py-3">
          <div className="text-sm text-green-700">Included Trades</div>
          <div className="mt-1 text-xl font-semibold text-green-900">
            {summary?.included_trade_count ?? 0}
          </div>
        </div>
        <div className="rounded-xl bg-red-50 px-4 py-3">
          <div className="text-sm text-red-700">Excluded Trades</div>
          <div className="mt-1 text-xl font-semibold text-red-900">
            {summary?.excluded_trade_count ?? 0}
          </div>
        </div>
        <div className="rounded-xl bg-slate-50 px-4 py-3">
          <div className="text-sm text-slate-500">In-scope Evidence Rows</div>
          <div className="mt-1 text-xl font-semibold">{evidence?.trade_count ?? 0}</div>
        </div>
      </div>

      <div className="mt-5">
        <div className="mb-2 text-sm font-medium text-slate-700">Excluded breakdown</div>
        {breakdownRows.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
            No excluded trades were found for this claim scope.
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {breakdownRows.map(([reason, count]) => (
              <div key={reason} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">{humanizeReason(reason)}</div>
                <div className="mt-1 text-lg font-semibold">{count}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function ScopeTradesTable({
  title,
  subtitle,
  rows,
  emptyText,
  showExclusionColumns = false,
}: {
  title: string;
  subtitle: string;
  rows?: ClaimTradeScopeRow[] | null;
  emptyText: string;
  showExclusionColumns?: boolean;
}) {
  const safe = Array.isArray(rows) ? rows : [];

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">{title}</h2>
          <div className="mt-2 text-sm text-slate-500">{subtitle}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
          <div className="text-slate-500">Rows</div>
          <div className="mt-1 font-semibold">{safe.length}</div>
        </div>
      </div>

      {safe.length === 0 ? (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
          {emptyText}
        </div>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b text-left text-slate-500">
                <th className="px-3 py-2">#</th>
                <th className="px-3 py-2">Trade ID</th>
                <th className="px-3 py-2">Opened</th>
                <th className="px-3 py-2">Symbol</th>
                <th className="px-3 py-2">Side</th>
                <th className="px-3 py-2">Member</th>
                <th className="px-3 py-2">Entry</th>
                <th className="px-3 py-2">Qty</th>
                <th className="px-3 py-2">PnL</th>
                <th className="px-3 py-2">Cumulative</th>
                <th className="px-3 py-2">Scope</th>
                {showExclusionColumns ? <th className="px-3 py-2">Reason</th> : null}
                {showExclusionColumns ? <th className="px-3 py-2">Detail</th> : null}
                <th className="px-3 py-2">Strategy</th>
                <th className="px-3 py-2">Source</th>
              </tr>
            </thead>
            <tbody>
              {safe.map((row) => (
                <tr
                  key={`${row.trade_id}-${row.index}-${row.scope_status}`}
                  className="border-b last:border-0 align-top"
                >
                  <td className="px-3 py-2">{row.index}</td>
                  <td className="px-3 py-2">{row.trade_id}</td>
                  <td className="px-3 py-2">{formatDateTime(row.opened_at)}</td>
                  <td className="px-3 py-2">{row.symbol}</td>
                  <td className="px-3 py-2">{row.side}</td>
                  <td className="px-3 py-2">{row.member_id}</td>
                  <td className="px-3 py-2">{formatNumber(row.entry_price, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.quantity, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.net_pnl, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.cumulative_pnl, 4)}</td>
                  <td className="px-3 py-2">
                    <ScopeStatusBadge status={row.scope_status} />
                  </td>
                  {showExclusionColumns ? (
                    <td className="px-3 py-2">
                      <div className="flex min-w-[140px]">
                        <ExclusionReasonBadge
                          reason={row.exclusion_reason_label || row.exclusion_reason}
                        />
                      </div>
                    </td>
                  ) : null}
                  {showExclusionColumns ? (
                    <td className="px-3 py-2 text-slate-600">
                      <div className="min-w-[280px] whitespace-normal">
                        {row.exclusion_reason_detail || "—"}
                      </div>
                    </td>
                  ) : null}
                  <td className="px-3 py-2">{row.strategy_tag || "—"}</td>
                  <td className="px-3 py-2">{row.source_system || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function UpgradeContextCard({
  usage,
  claimLimitReached,
  qaOverrideActive,
  workspaceId,
  canManageActions,
}: {
  usage: WorkspaceUsageSummary | null;
  claimLimitReached: boolean;
  qaOverrideActive: boolean;
  workspaceId: number;
  canManageActions: boolean;
}) {
  const claimUsage = usage?.usage?.claims;
  const currentPlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.plan_code)
    )?.name || usage?.plan_code || "—";

  const effectivePlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.effective_plan_code)
    )?.name ||
    usage?.effective_plan_code ||
    currentPlanName;

  const recommendedPlanName =
    usage?.upgrade_recommendation?.recommended_plan_name || "Pro or Team";

  const breachedDimensions = usage?.upgrade_recommendation?.breached_dimensions ?? [];
  const nearLimitDimensions = usage?.upgrade_recommendation?.near_limit_dimensions ?? [];
  const planMismatch =
    normalizeText(usage?.effective_plan_code) &&
    normalizeText(usage?.plan_code) &&
    normalizeText(usage?.effective_plan_code) !== normalizeText(usage?.plan_code);

  const statusChip = qaOverrideActive
    ? "qa override"
    : claimLimitReached
      ? "upgrade required"
      : usage?.governance?.upgrade_recommended_soon
        ? "upgrade recommended"
        : "within plan";

  const statusChipClass = qaOverrideActive
    ? "border-violet-200 bg-violet-50 text-violet-800"
    : claimLimitReached
      ? "border-amber-200 bg-amber-50 text-amber-800"
      : usage?.governance?.upgrade_recommended_soon
        ? "border-blue-200 bg-blue-50 text-blue-800"
        : "border-green-200 bg-green-50 text-green-800";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Claim Capacity & Upgrade</h3>
          <div className="mt-1 text-sm text-slate-500">
            Action gating should feel predictable before users click into blocked workflow steps.
          </div>
        </div>

        <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusChipClass}`}>
          {statusChip}
        </span>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Configured plan</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{currentPlanName}</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Effective plan</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{effectivePlanName}</div>
          <div className="mt-1 text-xs text-slate-500">
            Backend-enforced plan posture for governed actions.
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Claim usage</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {claimUsage ? `${claimUsage.used} / ${claimUsage.limit}` : "—"}
          </div>
          <div className="mt-1 text-xs text-slate-500">
            {claimUsage?.ratio !== null && claimUsage?.ratio !== undefined
              ? `${(Number(claimUsage.ratio) * 100).toFixed(1)}% of current claim capacity`
              : "No usage telemetry available"}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Recommended plan</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{recommendedPlanName}</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
          <div className="text-xs uppercase tracking-wide text-slate-500">Governance signal</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {claimLimitReached
              ? "New versions blocked"
              : usage?.governance?.upgrade_recommended_soon
                ? "Capacity getting tight"
                : "Actions available"}
          </div>
        </div>
      </div>

      {planMismatch ? (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          This workspace is configured on <span className="font-semibold">{currentPlanName}</span>,
          but the current effective enforcement posture is{" "}
          <span className="font-semibold">{effectivePlanName}</span>. Claim action gating should
          follow the effective plan state.
        </div>
      ) : null}

      {breachedDimensions.length > 0 || nearLimitDimensions.length > 0 ? (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          {breachedDimensions.length > 0 ? (
            <div>
              <span className="font-medium text-slate-900">Breached:</span>{" "}
              {breachedDimensions.join(", ")}
            </div>
          ) : null}
          {nearLimitDimensions.length > 0 ? (
            <div className={breachedDimensions.length > 0 ? "mt-1" : ""}>
              <span className="font-medium text-slate-900">Near limit:</span>{" "}
              {nearLimitDimensions.join(", ")}
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        {qaOverrideActive ? (
          <>
            <div className="font-medium text-slate-900">Local QA override active</div>
            <div className="mt-2">
              This workspace is over the normal claim plan limit, but version creation remains
              enabled in this QA environment. Production behavior should route into the paywall
              flow.
            </div>
          </>
        ) : claimLimitReached ? (
          <>
            <div className="font-medium text-slate-900">Why actions are blocked</div>
            <div className="mt-2">
              Claim version creation changes governed capacity, so it is controlled by plan
              entitlements and current usage. Users can still inspect records, but cannot create
              additional claim lineage without upgrading.
            </div>
          </>
        ) : (
          <>
            <div className="font-medium text-slate-900">Action readiness</div>
            <div className="mt-2">
              This workspace is still within current claim capacity. Lifecycle actions and governed
              versioning should remain available subject to role permissions and lifecycle state.
            </div>
          </>
        )}
      </div>

      {canManageActions ? (
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            href={`/workspace/${workspaceId}/settings?tab=billing`}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
          >
            Open Billing & Upgrade
          </Link>

          <Link
            href={`/workspace/${workspaceId}/settings?tab=billing`}
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Review Plan Details
          </Link>
        </div>
      ) : (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          Billing changes are owner/operator workflow surfaces. Members can inspect governance state
          but should not change plan entitlements directly.
        </div>
      )}
    </div>
  );
}

type ClaimGraphNodeRole = "root" | "parent" | "current";

type ClaimGraphNode = {
  id: number;
  label: string;
  role: ClaimGraphNodeRole;
  description: string;
};

function graphNodeTone(role: ClaimGraphNodeRole) {
  if (role === "root") {
    return "border-emerald-200 bg-emerald-50 text-emerald-900";
  }

  if (role === "parent") {
    return "border-amber-200 bg-amber-50 text-amber-900";
  }

  return "border-slate-900 bg-slate-900 text-white";
}

function ClaimGraph({
  workspaceId,
  currentId,
  rootId,
  parentId,
}: {
  workspaceId: number;
  currentId: number;
  rootId?: number | null;
  parentId?: number | null;
}) {
  const nodes: ClaimGraphNode[] = [];

  if (rootId) {
    nodes.push({
      id: rootId,
      label: `Claim #${rootId}`,
      role: "root",
      description: "Origin node",
    });
  }

  if (parentId && parentId !== rootId) {
    nodes.push({
      id: parentId,
      label: `Claim #${parentId}`,
      role: "parent",
      description: "Immediate parent",
    });
  }

  nodes.push({
    id: currentId,
    label: `Claim #${currentId}`,
    role: "current",
    description: "Current node",
  });

  return (
    <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">Graph View</div>
          <div className="mt-1 text-xs text-slate-500">
            Workspace-aware lineage graph for governed claim evolution.
          </div>
        </div>

        <div className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600">
          nodes: {nodes.length}
        </div>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-4">
        {nodes.map((node, idx) => (
          <div key={`${node.role}-${node.id}`} className="flex items-center gap-4">
            <Link
              href={`/workspace/${workspaceId}/claim/${node.id}`}
              className={`min-w-[160px] rounded-2xl border px-4 py-3 shadow-sm transition hover:shadow ${graphNodeTone(
                node.role
              )}`}
            >
              <div className="text-xs uppercase tracking-wide opacity-80">
                {node.role}
              </div>
              <div className="mt-1 text-sm font-semibold">{node.label}</div>
              <div className="mt-1 text-xs opacity-80">{node.description}</div>
            </Link>

            {idx < nodes.length - 1 ? (
              <div className="flex min-w-[72px] flex-col items-center text-slate-400">
                <span className="text-[10px] uppercase tracking-wide">flows to</span>
                <span className="text-xl leading-none">→</span>
              </div>
            ) : null}
          </div>
        ))}
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-600">
          <div className="font-medium text-slate-900">Root</div>
          <div className="mt-1">
            {rootId ? `claim#${rootId}` : "self-originated"}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-600">
          <div className="font-medium text-slate-900">Parent</div>
          <div className="mt-1">
            {parentId ? `claim#${parentId}` : "no direct parent"}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-600">
          <div className="font-medium text-slate-900">Current</div>
          <div className="mt-1">{`claim#${currentId}`}</div>
        </div>
      </div>
    </div>
  );
}

export default function WorkspaceClaimDetailPage() {
  const params = useParams();
  const pathname = usePathname();
  const { getWorkspaceRole, loading: authLoading } = useAuth();

  const workspaceId = useMemo(
    () =>
      Number(Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId),
    [params]
  );
  const idParam = params?.id;
  const claimId = useMemo(() => Number(Array.isArray(idParam) ? idParam[0] : idParam), [idParam]);

  const workspaceRole = useMemo(() => {
    if (!workspaceId || Number.isNaN(workspaceId)) return null;
    return getWorkspaceRole(workspaceId);
  }, [workspaceId, getWorkspaceRole]);

  const isOwner = workspaceRole === "owner";
  const isOperator = workspaceRole === "operator";
  const isMember = workspaceRole === "member";

  const canEditDraft = isOwner || isOperator;
  const canManageClaimActions = isOwner || isOperator;

  const qaOverrideActive =
    process.env.NEXT_PUBLIC_DISABLE_WORKSPACE_LIMITS === "true" ||
    process.env.NEXT_PUBLIC_DISABLE_WORKSPACE_LIMITS === "1";

  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [preview, setPreview] = useState<ClaimSchemaPreview | null>(null);
  const [versions, setVersions] = useState<ClaimVersion[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [equityCurve, setEquityCurve] = useState<ClaimEquityCurve | null>(null);
  const [claimTrades, setClaimTrades] = useState<ClaimTradeEvidence | null>(null);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  // ===============================
  // Phase 9 — Claim Disputes State
  // ===============================
  
  const [disputes, setDisputes] = useState<ClaimDispute[]>([]);
  const [loadingDisputes, setLoadingDisputes] = useState(false);
  const [creatingDispute, setCreatingDispute] = useState(false);

  const [newDisputeSummary, setNewDisputeSummary] = useState("");
  const [newDisputeReason, setNewDisputeReason] = useState("general_review");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [checkingIntegrity, setCheckingIntegrity] = useState(false);
  const [integrityMessage, setIntegrityMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const claimUsage = usage?.usage?.claims;
  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 && (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  const effectivePlanCode = usage?.effective_plan_code || usage?.plan_code || null;

  const isBlockedByPlan = !qaOverrideActive && claimLimitReached;

  const effectivePlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(effectivePlanCode)
    )?.name || effectivePlanCode || "—";

  const configuredPlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.plan_code)
    )?.name || usage?.plan_code || "—";

  const claimStatusNormalized = normalizeText(claim?.status);
  const claimVisibilityNormalized = normalizeText(claim?.visibility);

  const publicRouteReady =
    claimVisibilityNormalized === "public" &&
    (claimStatusNormalized === "published" || claimStatusNormalized === "locked") &&
    !!claim?.claim_hash;

  const unlistedRouteReady =
    claimVisibilityNormalized === "unlisted" &&
    (claimStatusNormalized === "published" || claimStatusNormalized === "locked") &&
    !!claim?.claim_hash;

  const currentVersionIndex = useMemo(() => {
    if (!claim || !versions.length) return -1;
    return versions.findIndex((version) => version.id === claim.id);
  }, [claim, versions]);

  const previousVersion = currentVersionIndex > 0 ? versions[currentVersionIndex - 1] : null;
  const nextVersion =
    currentVersionIndex >= 0 && currentVersionIndex < versions.length - 1
      ? versions[currentVersionIndex + 1]
      : null;

  const internalHref = `/workspace/${workspaceId}/claim/${claimId}`;
  const evidenceHref = `/workspace/${workspaceId}/evidence?claimId=${claimId}`;
  const verifyRouteHref =
  ((claim as ClaimSchema & { verify_path?: string | null })?.verify_path ?? null) ||
  (claim?.claim_hash ? `/verify/${claim.claim_hash}` : null);
  
  const canOpenVerifySurface = Boolean(
    (publicRouteReady || unlistedRouteReady) && verifyRouteHref
  );
  const publicViewHref =
    claimStatusNormalized === "published" || claimStatusNormalized === "locked"
      ? `/claim/${claimId}/public`
      : null;

  const isInternalActive = pathname === internalHref;
  const isEvidenceActive = pathname === `/workspace/${workspaceId}/evidence`;

  const loadClaimPage = useCallback(async () => {
    if (!claimId || Number.isNaN(claimId) || !workspaceId || Number.isNaN(workspaceId)) return;

    setError(null);

    try {
      const [claimRes, previewRes, versionsRes, auditRes, equityRes, tradesRes, usageRes, disputesRes] =
        await Promise.all([
          api.getClaimSchema(claimId),
          api.getClaimPreview(claimId),
          api.getClaimVersions(claimId),
          api.getAuditEventsForEntity("claim_schema", claimId),
          api.getClaimEquityCurve(claimId),
          api.getClaimTrades(claimId).catch(() => emptyTradeEvidence(claimId)),
          api.getWorkspaceUsage(workspaceId).catch(() => null),
          api.getClaimDisputes(claimId).catch(() => []),
        ]);

      setClaim(claimRes);
      setPreview(previewRes);
      setVersions(Array.isArray(versionsRes) ? versionsRes : []);
      setAuditEvents(Array.isArray(auditRes) ? auditRes : []);
      setEquityCurve(equityRes);
      setClaimTrades(tradesRes ?? emptyTradeEvidence(claimId));
      setUsage(usageRes);
      setDisputes(Array.isArray(disputesRes) ? disputesRes : []);

      if (normalizeText(claimRes.status) === "locked") {
        try {
          const integrityRes = await api.getClaimIntegrity(claimId);
          setIntegrity(integrityRes);
        } catch {
          setIntegrity(null);
        }
      } else {
        setIntegrity(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load claim");
    }
  }, [claimId, workspaceId]);

  useEffect(() => {
    let active = true;

    async function initialLoad() {
      setLoading(true);
      try {
        if (active) {
          await loadClaimPage();
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void initialLoad();

    return () => {
      active = false;
    };
  }, [loadClaimPage]);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await loadClaimPage();
    } finally {
      setRefreshing(false);
    }
  }, [loadClaimPage]);

  const handleDraftSaved = useCallback(
    async (updated: ClaimSchema) => {
      setClaim(updated);
      await loadClaimPage();
    },
    [loadClaimPage]
  );

  const handleIntegrityCheck = useCallback(async () => {
    // ===============================
    // Phase 9 — Create Dispute
    // ===============================
    
    if (!claimId) return;
    setCheckingIntegrity(true);
    setError(null);
    setIntegrityMessage(null);

    try {
      const integrityRes = await api.getClaimIntegrity(claimId);
      setIntegrity(integrityRes);

      if (integrityRes.hash_match && integrityRes.integrity_status === "valid") {
        setIntegrityMessage("Integrity verified successfully. Stored and recomputed hashes match.");
      } else {
        setIntegrityMessage("Integrity check completed. Review the result carefully.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Integrity verification failed");
    } finally {
      setCheckingIntegrity(false);
    }
  }, [claimId]);

  const handleCreateDispute = useCallback(async () => {
  if (!claimId || !newDisputeSummary.trim()) return;

  setCreatingDispute(true);

  try {
    await api.createClaimDispute(claimId, {
      summary: newDisputeSummary.trim(),
      reason_code: newDisputeReason,
    });

    setNewDisputeSummary("");
    setNewDisputeReason("general_review");

    await loadClaimPage();
  } catch (err) {
    setError(err instanceof Error ? err.message : "Failed to create dispute");
  } finally {
    setCreatingDispute(false);
  }
}, [claimId, newDisputeSummary, newDisputeReason, loadClaimPage]);

  const handleResolveDispute = useCallback(async (id: number) => {
  try {
    await api.updateClaimDisputeStatus(id, {
      status: "resolved",
      resolution_note: "Resolved via internal review",
    });

    await loadClaimPage();
  } catch {
    setError("Failed to resolve dispute");
  }
}, [loadClaimPage]);

const handleRejectDispute = useCallback(async (id: number) => {
  try {
    await api.updateClaimDisputeStatus(id, {
      status: "rejected",
      resolution_note: "Rejected after review",
    });

    await loadClaimPage();
  } catch {
    setError("Failed to reject dispute");
  }
}, [loadClaimPage]);

  if (!workspaceId || Number.isNaN(workspaceId)) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (!claimId || Number.isNaN(claimId)) {
    return <div className="p-6 text-red-600">Invalid claim id.</div>;
  }

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading claim verification screen...</div>
      </div>
    );
  }

  if (error && !claim && !preview) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
        </div>
      </div>
    );
  }

  const lineageSummary = claim ? buildLineageSummary(claim) : null;
  const networkType = claim ? resolveClaimOriginType(claim) : null;
  const networkLabel = claim ? resolveNetworkLabel(claim) : null;
  const networkClassName = claim
    ? networkTone(claim)
    : "border-slate-200 bg-slate-50 text-slate-700";
  const issuerName = claim ? resolveIssuerName(claim, workspaceId) : "workspace";

  if (!claim || !preview) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Claim not found.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-8">
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-4xl">
              <div className="mb-2 text-sm text-slate-500">
                <Link href={`/workspace/${workspaceId}/claims`} className="hover:underline">
                  Claims
                </Link>
                <span className="mx-2">/</span>
                <span>Claim #{claim.id}</span>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-3xl font-semibold tracking-tight">{claim.name}</h1>
                <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-medium text-slate-700">
                  ID {claim.id}
                </span>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-2">
                <StatusBadge status={claim.status} />
                <VisibilityBadge visibility={claim.visibility} />
                <IntegrityBadge integrity={integrity} />
                <RoleBadge role={workspaceRole} />
              </div>

              <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600">
                Internal claim presentation surface for lifecycle review, evidence inspection,
                lineage tracking, integrity validation, and governed version management.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              {normalizeText(claim.status) === "draft" && canEditDraft ? (
                <EditClaimDraftButton claim={claim} onSaved={handleDraftSaved} />
              ) : null}

              <button
                type="button"
                onClick={() => void handleRefresh()}
                disabled={refreshing}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {refreshing ? "Refreshing..." : "Refresh"}
              </button>

              <button
                type="button"
                onClick={() => void handleIntegrityCheck()}
                disabled={normalizeText(claim.status) !== "locked" || checkingIntegrity}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {checkingIntegrity ? "Checking..." : "Verify Integrity"}
              </button>

              <PageNavButton href={internalHref} label="Internal View" active={isInternalActive} />
              <PageNavButton href={evidenceHref} label="Evidence" active={isEvidenceActive} />
              {publicViewHref ? (
                <PageNavButton href={publicViewHref} label="Public View" active={false} />
              ) : null}
              {verifyRouteHref ? (
                <PageNavButton href={verifyRouteHref} label="Verify Route" active={false} />
              ) : null}
            </div>
          </div>

          {integrityMessage ? (
            <div className="mt-4 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
              {integrityMessage}
            </div>
          ) : null}

          {error ? (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <div className="text-xs uppercase tracking-wide text-slate-500">
              Trust Network Context · Phase 8
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${networkClassName}`}>
                network: {networkType}
              </span>
              <span className="inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                issuer: {issuerName}
              </span>
            </div>

            <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-5 text-sm text-slate-700">
              <div>
                <div className="text-slate-500">Network State</div>
                <div className="font-medium text-slate-900">{networkLabel}</div>
              </div>

              <div>
                <div className="text-slate-500">Issuer</div>
                <div className="font-medium text-slate-900">{issuerName}</div>
              </div>

              <div>
                <div className="text-slate-500">Root</div>
                <div className="font-medium text-slate-900">{lineageSummary?.root ?? "—"}</div>
              </div>

              <div>
                <div className="text-slate-500">Parent</div>
                <div className="font-medium text-slate-900">{lineageSummary?.parent ?? "—"}</div>
              </div>

              <div>
                <div className="text-slate-500">Version</div>
                <div className="font-medium text-slate-900">{lineageSummary?.version ?? "—"}</div>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-[1.5fr_1fr_1fr]">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Claim fingerprint · canonical identity</div>
              <div className="mt-2 font-mono text-sm text-slate-800">
                {truncateMiddle(claim.claim_hash || preview.claim_hash || "—")}
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <CopyButton value={claim.claim_hash || preview.claim_hash} label="Copy Claim Hash" />
                {canOpenVerifySurface && (
                  <Link
                    href={verifyRouteHref as string}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Open Verify Surface
                  </Link>
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Exposure state · distribution posture</div>
              <div className="mt-2 text-lg font-semibold text-slate-900">
                {claim.visibility === "private"
                  ? "Internal only"
                  : claim.visibility === "unlisted"
                    ? "Hash-based access"
                    : "Publicly routable"}
              </div>
              <div className="mt-2 text-sm text-slate-600">
                {claim.visibility === "private"
                  ? "No public verification route should be considered externally accessible."
                  : claim.visibility === "unlisted"
                    ? "Accessible through direct verification path when lifecycle permits."
                    : "Eligible for public credibility and verification surfaces when lifecycle permits."}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Trust state · internal confidence</div>
              <div className="mt-2 text-lg font-semibold text-slate-900">
                {integrity?.integrity_status === "valid"
                  ? "Integrity confirmed"
                  : normalizeText(claim.status) === "locked"
                    ? "Awaiting verification"
                    : "Pre-lock state"}
              </div>
              <div className="mt-2 text-sm text-slate-600">
                Locked claims can be independently checked against the stored trade-set fingerprint.
              </div>
            </div>
          </div>
        </section>

        {isMember ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Read-only lifecycle access</h2>
            <p className="mt-2 text-slate-600">
              Your current workspace role is <span className="font-medium">{workspaceRole}</span>.
              You can inspect claim metrics, evidence, lineage, and audit history, but you cannot
              edit drafts or execute governed lifecycle actions.
            </p>
          </div>
        ) : null}

        <GovernanceOverview
          claim={claim}
          versions={versions}
          auditEvents={auditEvents}
          integrity={integrity}
        />

        {disputes.length > 0 && (
          <div className="rounded-2xl border border-red-300 bg-red-50 p-5 shadow-sm">
            <div className="text-sm font-semibold text-red-900">
              Governance Challenge Active
            </div>

            <div className="mt-2 text-sm text-red-800">
              {disputes.length} dispute(s) detected.
              This claim is in a contested trust state.
            </div>

            <div className="mt-2 text-xs text-red-700">
              Public credibility, leaderboard ranking, and verification trust
              should be treated as degraded until disputes are resolved.
            </div>
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Trade Count"
            value={String(preview.trade_count ?? 0)}
            hint="Total in-scope evidence rows"
          />
          <MetricCard
            label="Net PnL"
            value={formatNumber(preview.net_pnl)}
            hint="Aggregate net result"
          />
          <MetricCard
            label="Profit Factor"
            value={formatNumber(preview.profit_factor, 4)}
            hint="Gross profit ÷ gross loss"
          />
          <MetricCard
            label="Win Rate"
            value={formatPercent(preview.win_rate, 2)}
            hint="Winning trades as percentage"
          />
        </section>

        {/* ===============================
          Phase 9 — Dispute Panel
        ================================ */}
        <section className="rounded-2xl border bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Disputes & Challenges</h2>
          </div>

          {/* Create Dispute */}
          {!isMember && (
            <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm font-medium">Raise a dispute</div>

              <textarea
                value={newDisputeSummary}
                onChange={(e) => setNewDisputeSummary(e.target.value)}
                placeholder="Describe the issue with this claim..."
                className="mt-2 w-full rounded-lg border p-2 text-sm"
              />

              <div className="mt-2 flex gap-2">
                <button
                  onClick={handleCreateDispute}
                  disabled={creatingDispute}
                  className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white"
                >
                  {creatingDispute ? "Submitting..." : "Submit Dispute"}
                </button>
              </div>
            </div>
          )}

          {/* Dispute List */}
          <div className="mt-4 space-y-3">
            {disputes.length === 0 ? (
              <div className="text-sm text-slate-500">
                No disputes raised for this claim.
              </div>
            ) : (
              disputes.map((d) => (
                <div
                  key={d.id}
                  className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="text-sm font-semibold">
                        {d.challenge_type}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {d.reason_code}
                      </div>
                    </div>

                    <span className="text-xs font-medium">
                      {d.status}
                    </span>
                  </div>

                  <div className="mt-2 text-sm text-slate-700">
                    {d.summary}
                  </div>

                  <div className="mt-2 text-xs text-slate-500">
                    {formatDateTime(d.opened_at)}
                  </div>

                  {/* Resolution actions */}
                  {canManageClaimActions && d.status === "open" && (
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => handleResolveDispute(d.id)}
                        className="rounded-lg bg-green-600 px-3 py-1 text-xs text-white"
                      >
                        Resolve
                      </button>

                      <button
                        onClick={() => handleRejectDispute(d.id)}
                        className="rounded-lg bg-red-600 px-3 py-1 text-xs text-white"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
          <HashCard
            title="Claim Hash"
            value={claim.claim_hash || preview.claim_hash || null}
            copyLabel="Copy Claim Hash"
          />
          <HashCard
            title="Locked Trade Set Hash"
            value={claim.locked_trade_set_hash || null}
            copyLabel="Copy Trade Set Hash"
          />
        </section>

        {equityCurve ? (
          <EquityCurveChart title="Internal Equity Curve" points={equityCurve.curve} />
        ) : null}

        <ScopeSummaryCard evidence={claimTrades} />

        <ScopeTradesTable
          title="Included Trades"
          subtitle="Exact in-scope trades used to compute this claim, ordered by trade open time."
          rows={claimTrades?.included_trades ?? []}
          emptyText="No included trades were found for this claim."
        />

        <ScopeTradesTable
          title="Excluded Trades"
          subtitle="Trades excluded from the claim scope, with explicit exclusion reasons."
          rows={claimTrades?.excluded_trades ?? []}
          emptyText="No excluded trades were found for this claim."
          showExclusionColumns={true}
        />

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold">Claim Scope</h2>
                {normalizeText(claim.status) === "draft" && canEditDraft ? (
                  <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700">
                    editable draft
                  </span>
                ) : (
                  <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">
                    read-only
                  </span>
                )}
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <DetailRow label="Period Start" value={claim.period_start} />
                <DetailRow label="Period End" value={claim.period_end} />
                <DetailRow label="Visibility" value={claim.visibility} />
                <DetailRow label="Workspace" value={claim.workspace_id} />
              </div>

              <div className="mt-4">
                <div className="text-sm text-slate-500">Methodology Notes</div>
                <div className="mt-1 whitespace-pre-wrap rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                  {claim.methodology_notes || "—"}
                </div>
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <DetailRow
                  label="Included Members"
                  value={
                    claim.included_member_ids_json.length
                      ? claim.included_member_ids_json.join(", ")
                      : "All in scope"
                  }
                />
                <DetailRow
                  label="Included Symbols"
                  value={
                    claim.included_symbols_json.length
                      ? claim.included_symbols_json.join(", ")
                      : "All in scope"
                  }
                />
                <DetailRow
                  label="Excluded Trade IDs"
                  value={
                    claim.excluded_trade_ids_json.length
                      ? claim.excluded_trade_ids_json.join(", ")
                      : "None"
                  }
                />
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold">Lifecycle & Integrity</h2>

                {!isMember ? (
                  <CreateClaimVersionButton
                    claimSchemaId={claim.id}
                    workspaceId={workspaceId}
                    currentVersionNumber={claim.version_number ?? null}
                    rootClaimId={claim.root_claim_id ?? null}
                    parentClaimId={claim.parent_claim_id ?? null}
                  />
                ) : null}
              </div>

              <div className="mt-5 grid gap-6 xl:grid-cols-[1.1fr_1fr]">
                <UpgradeContextCard
                  usage={usage}
                  claimLimitReached={claimLimitReached}
                  qaOverrideActive={qaOverrideActive}
                  workspaceId={workspaceId}
                  canManageActions={canManageClaimActions}
                />

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <div className="text-sm font-semibold text-slate-900">Action governance note</div>
                  <div className="mt-2 text-sm leading-6 text-slate-600">
                    Draft editing depends on role and draft state. Lifecycle progression depends on
                    role and current claim state. New version creation is additionally controlled by
                    governed capacity and workspace billing posture.
                  </div>

                  <div className="mt-4 grid gap-3">
                    <div className="rounded-xl border border-slate-200 bg-white p-4">
                      <div className="text-xs uppercase tracking-wide text-slate-500">
                        Draft editing
                      </div>
                      <div className="mt-1 text-sm text-slate-700">
                        Available only while the claim is still in draft and the user has workflow
                        authority.
                      </div>
                    </div>

                    <div className="rounded-xl border border-slate-200 bg-white p-4">
                      <div className="text-xs uppercase tracking-wide text-slate-500">
                        Lifecycle progression
                      </div>
                      <div className="mt-1 text-sm text-slate-700">
                        Verify, publish, and lock remain state-driven governance actions with role
                        restrictions.
                      </div>
                    </div>

                    <div className="rounded-xl border border-slate-200 bg-white p-4">
                      <div className="text-xs uppercase tracking-wide text-slate-500">
                        New version creation
                      </div>
                      <div className="mt-1 text-sm text-slate-700">
                        Capacity-changing versioning is controlled by workflow permissions and
                        workspace entitlements.
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {isBlockedByPlan ? (
                <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                  <div className="font-medium">Governed claim capacity reached</div>
                  <div className="mt-1">
                    Effective plan: {effectivePlanName}
                    {configuredPlanName && configuredPlanName !== effectivePlanName
                      ? ` · configured plan: ${configuredPlanName}`
                      : ""}
                  </div>
                  <div className="mt-1">
                    Claim usage: {claimUsage?.used ?? 0} / {claimUsage?.limit ?? 0}
                    {claimUsage?.ratio !== null && claimUsage?.ratio !== undefined
                      ? ` · ${(Number(claimUsage.ratio) * 100).toFixed(1)}%`
                      : ""}
                  </div>
                  <div className="mt-2">
                    New governed versions are blocked until the workspace plan state is upgraded or
                    billing posture is corrected. Lifecycle review remains available, but
                    capacity-changing actions should route into billing and paywall flow.
                  </div>
                </div>
              ) : claimLimitReached ? (
                <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                  <div className="font-medium">Local QA override active</div>
                  <div className="mt-1">
                    Claim usage: {claimUsage?.used ?? 0} / {claimUsage?.limit ?? 0}
                    {claimUsage?.ratio !== null && claimUsage?.ratio !== undefined
                      ? ` · ${(Number(claimUsage.ratio) * 100).toFixed(1)}%`
                      : ""}
                  </div>
                  <div className="mt-2">
                    This workspace is over the normal claim plan limit, but version creation
                    remains enabled in this local QA environment.
                  </div>
                </div>
              ) : null}

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <DetailRow label="Status" value={claim.status} />
                <DetailRow label="Network State" value={networkLabel ?? "—"} />
                <DetailRow label="Verified At" value={formatDateTime(claim.verified_at)} />
                <DetailRow label="Published At" value={formatDateTime(claim.published_at)} />
                <DetailRow label="Locked At" value={formatDateTime(claim.locked_at)} />
                <DetailRow label="Root Claim" value={lineageSummary?.root ?? "—"} />
                <DetailRow label="Parent Claim" value={lineageSummary?.parent ?? "—"} />
                <DetailRow label="Version Number" value={lineageSummary?.version ?? "—"} />
              </div>

              {integrity ? (
                <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="mb-3 text-sm font-semibold">Integrity Verification Result</div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <DetailRow label="Integrity Status" value={integrity.integrity_status} />
                    <DetailRow label="Hash Match" value={String(integrity.hash_match)} />
                    <DetailRow label="Trade Count" value={integrity.trade_count} />
                    <DetailRow label="Verified At" value={formatDateTime(integrity.verified_at)} />
                  </div>

                  <div className="mt-4 grid gap-4 sm:grid-cols-2">
                    <div>
                      <div className="text-sm text-slate-500">Stored Hash</div>
                      <div className="mt-1 break-all rounded-xl bg-white p-3 font-mono text-xs text-slate-700">
                        {integrity.stored_hash}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-500">Recomputed Hash</div>
                      <div className="mt-1 break-all rounded-xl bg-white p-3 font-mono text-xs text-slate-700">
                        {integrity.recomputed_hash}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                  {normalizeText(claim.status) === "locked"
                    ? "Integrity can be checked from the locked state."
                    : "Integrity verification becomes meaningful after the claim reaches locked state."}
                </div>
              )}

              <div className="mt-5">
                <ClaimLifecycleActions
                  claimSchemaId={claim.id}
                  workspaceId={workspaceId}
                  status={claim.status}
                />
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Leaderboard</h2>
              {preview.leaderboard.length === 0 ? (
                <div className="mt-4 text-sm text-slate-500">No leaderboard data available.</div>
              ) : (
                <div className="mt-4 overflow-x-auto">
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
                      {preview.leaderboard.map((row) => (
                        <tr key={`${row.member}-${row.rank}`} className="border-b last:border-0">
                          <td className="px-3 py-2">{row.rank}</td>
                          <td className="px-3 py-2">{row.member}</td>
                          <td className="px-3 py-2">{formatNumber(row.net_pnl)}</td>
                          <td className="px-3 py-2">{formatPercent(row.win_rate, 2)}</td>
                          <td className="px-3 py-2">{formatNumber(row.profit_factor, 4)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <AuditTimeline events={auditEvents} />
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Lineage & Claim Graph</h2>

              <div className="mt-2 text-sm text-slate-500">
                Visual lineage map for root, parent, and current claim nodes inside the governed claim network.
              </div>

              <ClaimGraph
                workspaceId={workspaceId}
                currentId={claim.id}
                rootId={claim.root_claim_id}
                parentId={claim.parent_claim_id}
              />

              <div className="mt-4 flex flex-wrap gap-2">
                <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${networkClassName}`}>
                  {networkLabel}
                </span>
                <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">
                  issuer: {issuerName}
                </span>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {claim.root_claim_id ? (
                  <Link
                    href={`/workspace/${workspaceId}/claim/${claim.root_claim_id}`}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Open Root Node
                  </Link>
                ) : null}

                {claim.parent_claim_id ? (
                  <Link
                    href={`/workspace/${workspaceId}/claim/${claim.parent_claim_id}`}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Open Parent Node
                  </Link>
                ) : null}

                <Link
                  href={`/workspace/${workspaceId}/claim/${claim.id}`}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Re-center Current Node
                </Link>
              </div>

              <div className="mt-4 space-y-3 text-sm">
                <DetailRow label="Claim ID" value={claim.id} />
                <DetailRow label="Root Claim" value={lineageSummary?.root ?? "—"} />
                <DetailRow label="Parent Claim" value={lineageSummary?.parent ?? "—"} />
                <DetailRow label="Version Number" value={lineageSummary?.version ?? "—"} />
              </div>

              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                This claim participates in a governed claim graph. New versions preserve historical
                states, support defensible public verification, and prevent silent mutation of prior
                evidence-bearing records.
              </div>

              <div className="mt-4 grid gap-3">
                <div className="rounded-xl border border-slate-200 bg-white p-3">
                  <div className="text-xs text-slate-500">Previous version</div>
                  <div className="mt-1 font-medium">
                    {previousVersion ? previousVersion.name : "No earlier version"}
                  </div>
                  {previousVersion ? (
                    <Link
                      href={`/workspace/${workspaceId}/claim/${previousVersion.id}`}
                      className="mt-2 inline-flex text-xs font-medium text-slate-700 hover:underline"
                    >
                      Open previous version
                    </Link>
                  ) : null}
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-3">
                  <div className="text-xs text-slate-500">Current position in lineage</div>
                  <div className="mt-1 font-medium">
                    {currentVersionIndex >= 0 ? `${currentVersionIndex + 1} of ${versions.length}` : "—"}
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-3">
                  <div className="text-xs text-slate-500">Next version</div>
                  <div className="mt-1 font-medium">
                    {nextVersion ? nextVersion.name : "No later version"}
                  </div>
                  {nextVersion ? (
                    <Link
                      href={`/workspace/${workspaceId}/claim/${nextVersion.id}`}
                      className="mt-2 inline-flex text-xs font-medium text-slate-700 hover:underline"
                    >
                      Open next version
                    </Link>
                  ) : null}
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Exposure Controls</h2>
              <div className="mt-4 space-y-4 text-sm text-slate-700">
                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Private</div>
                  <div className="mt-1 text-slate-600">Internal-only claim visibility.</div>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Unlisted</div>
                  <div className="mt-1 text-slate-600">
                    Non-directory exposure through direct verification path.
                  </div>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Public</div>
                  <div className="mt-1 text-slate-600">
                    Public directory and verification-ready exposure when lifecycle permits.
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Governance Guidance</h2>
              <div className="mt-4 space-y-4 text-sm text-slate-700">
                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Version before changing claim meaning</div>
                  <div className="mt-1 text-slate-600">
                    Create a new governed version whenever scope, methodology, exclusions, or trust
                    posture changes. Preserve the prior claim node instead of mutating history.
                  </div>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Audit before exposure</div>
                  <div className="mt-1 text-slate-600">
                    Review audit events, lineage position, and integrity posture before routing a
                    claim into public or unlisted verification surfaces.
                  </div>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Lock only after final trust review</div>
                  <div className="mt-1 text-slate-600">
                    Locking finalizes the claim as a trust-bearing node in the network. Treat it as
                    the point where external verification and dispute readiness become durable.
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Claim Versions</h2>
              <div className="mt-4 space-y-3">
                {versions.length === 0 ? (
                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                    No governed versions found.
                  </div>
                ) : (
                  versions.map((version) => (
                    <VersionCard
                      key={version.id}
                      version={version}
                      workspaceId={workspaceId}
                      isCurrent={version.id === claim.id}
                    />
                  ))
                )}
              </div>
            </div>

            <GovernanceCard
              title="Trust network principle"
              body="A trustworthy claim is not only a metric summary. It is a governed network node with preserved lineage, visible audit events, explainable scope, controlled exposure, and verifiable integrity."
            />
          </div>
        </div>
      </main>
    </div>
  );
}