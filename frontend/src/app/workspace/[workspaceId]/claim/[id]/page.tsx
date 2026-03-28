"use client";

import { useEffect, useMemo, useState } from "react";
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
            version {version.version_number} · root {version.root_claim_id ?? "—"} · parent{" "}
            {version.parent_claim_id ?? "—"}
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
          <div className="text-xs uppercase tracking-wide text-slate-500">Lineage depth</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">{lineageDepth}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Latest audit event</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {latestEvent?.event_type || "—"}
          </div>
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
                <tr key={`${row.trade_id}-${row.index}-${row.scope_status}`} className="border-b last:border-0 align-top">
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
                        <ExclusionReasonBadge reason={row.exclusion_reason_label || row.exclusion_reason} />
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

export default function WorkspaceClaimDetailPage() {
  const params = useParams();
  const pathname = usePathname();
  const { getWorkspaceRole, loading: authLoading } = useAuth();

  const workspaceId = useMemo(
    () => Number(Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId),
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
  const [loading, setLoading] = useState(true);
  const [checkingIntegrity, setCheckingIntegrity] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const claimUsage = usage?.usage?.claims;
  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 &&
    (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  const publicRouteReady =
    claim?.visibility === "public" &&
    (claim?.status === "published" || claim?.status === "locked") &&
    !!claim?.claim_hash;

  const unlistedRouteReady =
    claim?.visibility === "unlisted" &&
    (claim?.status === "published" || claim?.status === "locked") &&
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
  const publicHref = claim?.claim_hash ? `/verify/${claim.claim_hash}` : null;

  const isInternalActive = pathname === internalHref;
  const isEvidenceActive = pathname === `/workspace/${workspaceId}/evidence`;

  const loadClaimPage = async () => {
    if (!claimId || Number.isNaN(claimId) || !workspaceId || Number.isNaN(workspaceId)) return;

    setLoading(true);
    setError(null);

    try {
      const [claimRes, previewRes, versionsRes, auditRes, equityRes, tradesRes, usageRes] =
        await Promise.all([
          api.getClaimSchema(claimId),
          api.getClaimPreview(claimId),
          api.getClaimVersions(claimId),
          api.getAuditEventsForEntity("claim_schema", claimId),
          api.getClaimEquityCurve(claimId),
          api.getClaimTrades(claimId).catch(() => emptyTradeEvidence(claimId)),
          api.getWorkspaceUsage(workspaceId).catch(() => null),
        ]);

      setClaim(claimRes);
      setPreview(previewRes);
      setVersions(Array.isArray(versionsRes) ? versionsRes : []);
      setAuditEvents(Array.isArray(auditRes) ? auditRes : []);
      setEquityCurve(equityRes);
      setClaimTrades(tradesRes ?? emptyTradeEvidence(claimId));
      setUsage(usageRes);

      if (claimRes.status === "locked") {
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
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadClaimPage();
  }, [claimId, workspaceId]);

  const handleRefresh = async () => {
    await loadClaimPage();
  };

  const handleDraftSaved = async (updated: ClaimSchema) => {
    setClaim(updated);
    await loadClaimPage();
  };

  const handleIntegrityCheck = async () => {
    if (!claimId) return;
    setCheckingIntegrity(true);
    try {
      const integrityRes = await api.getClaimIntegrity(claimId);
      setIntegrity(integrityRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Integrity verification failed");
    } finally {
      setCheckingIntegrity(false);
    }
  };

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

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
        </div>
      </div>
    );
  }

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
                lineage tracking, integrity validation, and version governance.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <EditClaimDraftButton claim={claim} onSaved={handleDraftSaved} />

              <button
                onClick={handleRefresh}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Refresh
              </button>

              <button
                onClick={handleIntegrityCheck}
                disabled={claim.status !== "locked" || checkingIntegrity}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {checkingIntegrity ? "Checking..." : "Verify Integrity"}
              </button>

              <PageNavButton href={internalHref} label="Internal View" active={isInternalActive} />
              <PageNavButton href={evidenceHref} label="Evidence" active={isEvidenceActive} />
              {publicHref ? (
                <PageNavButton href={publicHref} label="Public Verify" active={false} />
              ) : null}
            </div>
          </div>

          <div className="mt-6 grid gap-4 lg:grid-cols-[1.5fr_1fr_1fr]">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Claim fingerprint</div>
              <div className="mt-2 font-mono text-sm text-slate-800">
                {truncateMiddle(claim.claim_hash || preview.claim_hash || "—")}
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <CopyButton value={claim.claim_hash || preview.claim_hash} label="Copy Claim Hash" />
                {publicRouteReady || unlistedRouteReady ? (
                  <Link
                    href={`/verify/${claim.claim_hash}`}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Open Verify Surface
                  </Link>
                ) : null}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Exposure state</div>
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
              <div className="text-sm text-slate-500">Trust state</div>
              <div className="mt-2 text-lg font-semibold text-slate-900">
                {integrity?.integrity_status === "valid"
                  ? "Integrity confirmed"
                  : claim.status === "locked"
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
              edit drafts or run lifecycle transitions.
            </p>
          </div>
        ) : null}

        <GovernanceOverview
          claim={claim}
          versions={versions}
          auditEvents={auditEvents}
          integrity={integrity}
        />

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
                {claim.status === "draft" && canEditDraft ? (
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

              {claimLimitReached ? (
                <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                  <div className="font-medium">
                    {qaOverrideActive ? "Local QA override active" : "Claim plan limit reached"}
                  </div>

                  <div className="mt-1">
                    Claim usage: {claimUsage?.used ?? 0} / {claimUsage?.limit ?? 0}
                    {claimUsage?.ratio !== null && claimUsage?.ratio !== undefined
                      ? ` · ${(Number(claimUsage.ratio) * 100).toFixed(1)}%`
                      : ""}
                  </div>

                  <div className="mt-2">
                    {qaOverrideActive
                      ? "This workspace is over the normal claim plan limit, but version creation remains enabled in this local QA environment."
                      : "This workspace is over the claim plan limit, so new version creation is blocked until the plan is upgraded."}
                  </div>
                </div>
              ) : null}

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <DetailRow label="Status" value={claim.status} />
                <DetailRow label="Version Number" value={claim.version_number ?? "—"} />
                <DetailRow label="Verified At" value={formatDateTime(claim.verified_at)} />
                <DetailRow label="Published At" value={formatDateTime(claim.published_at)} />
                <DetailRow label="Locked At" value={formatDateTime(claim.locked_at)} />
                <DetailRow label="Parent Claim" value={claim.parent_claim_id ?? "—"} />
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
                  {claim.status === "locked"
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
              <h2 className="text-xl font-semibold">Lineage</h2>
              <div className="mt-4 space-y-3 text-sm">
                <DetailRow label="Claim ID" value={claim.id} />
                <DetailRow label="Root Claim ID" value={claim.root_claim_id ?? "—"} />
                <DetailRow label="Parent Claim ID" value={claim.parent_claim_id ?? "—"} />
                <DetailRow label="Version Number" value={claim.version_number ?? "—"} />
              </div>

              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                This claim participates in a governed lineage. New versions preserve history instead
                of silently overwriting the prior record.
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
                  <div className="font-medium">Version before changing meaning</div>
                  <div className="mt-1 text-slate-600">
                    Create a new governed version when scope, methodology, or exclusion logic changes.
                  </div>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Audit before exposure</div>
                  <div className="mt-1 text-slate-600">
                    Review the audit timeline before public distribution to confirm the record tells a defensible story.
                  </div>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <div className="font-medium">Lock only after final review</div>
                  <div className="mt-1 text-slate-600">
                    Locking should be treated as finalization of the trust surface and associated evidence fingerprint.
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
              title="Governance principle"
              body="A trustworthy claim is not just a metric summary. It is a lifecycle-governed record with preserved versions, visible audit events, explainable scope, and verifiable integrity."
            />
          </div>
        </div>
      </main>
    </div>
  );
}