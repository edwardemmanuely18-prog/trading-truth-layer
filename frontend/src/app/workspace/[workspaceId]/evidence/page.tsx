"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, usePathname, useSearchParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import DownloadEvidenceButton from "../../../../components/DownloadEvidenceButton";
import EvidenceCard from "../../../../components/EvidenceCard";
import { useAuth } from "../../../../components/AuthProvider";
import {
  api,
  type AuditEvent,
  type ClaimIntegrityResult,
  type ClaimSchema,
  type EvidenceBundle,
  type EvidencePack,
  type PublicClaim,
} from "../../../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value: unknown, digits = 4) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return value.toFixed(digits);
}

function safeJson(value: unknown) {
  return JSON.stringify(value ?? {}, null, 2);
}

function tryParseJson(value?: string | null) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function truncateMiddle(value?: string | null, start = 12, end = 10) {
  if (!value) return "—";
  if (value.length <= start + end + 3) return value;
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}

function readNumber(value: unknown): number | null {
  return typeof value === "number" && !Number.isNaN(value) ? value : null;
}

function readRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function inferScopeSummary(evidencePack: EvidencePack | null, publicClaim: PublicClaim | null) {
  const pack = readRecord(evidencePack as unknown);
  const publicRecord = readRecord(publicClaim as unknown);

  const candidates: Array<Record<string, unknown> | null> = [
    readRecord(pack?.summary),
    readRecord(pack?.scope_summary),
    readRecord(pack?.claim_scope_summary),
    readRecord(publicRecord?.summary),
    readRecord(publicRecord?.scope_summary),
    readRecord(readRecord(publicRecord?.scope)?.summary),
  ];

  const summary = candidates.find(Boolean) ?? null;
  const breakdown =
    readRecord(summary?.excluded_breakdown) ??
    readRecord(summary?.breakdown) ??
    readRecord(summary?.excluded_reasons) ??
    {};

  return {
    workspaceTradeCount:
      readNumber(summary?.workspace_trade_count) ??
      readNumber(summary?.workspace_trades) ??
      readNumber(summary?.total_workspace_trades) ??
      null,
    includedTradeCount:
      readNumber(summary?.included_trade_count) ??
      readNumber(summary?.included_trades) ??
      readNumber(summary?.in_scope_trade_count) ??
      readNumber(summary?.in_scope_rows) ??
      null,
    excludedTradeCount:
      readNumber(summary?.excluded_trade_count) ??
      readNumber(summary?.excluded_trades) ??
      readNumber(summary?.out_of_scope_trade_count) ??
      null,
    inScopeEvidenceRows:
      readNumber(summary?.in_scope_evidence_rows) ??
      readNumber(summary?.in_scope_rows) ??
      readNumber(summary?.included_trade_count) ??
      readNumber(summary?.included_trades) ??
      null,
    breakdown,
  };
}

function StatusBadge({ status }: { status?: string | null }) {
  const normalized = normalizeText(status);

  const className =
    normalized === "locked"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "published"
        ? "border-blue-200 bg-blue-100 text-blue-800"
        : normalized === "verified"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

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
        : normalized === "auditor"
          ? "border-purple-200 bg-purple-100 text-purple-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      role: {role || "unknown"}
    </span>
  );
}

function CopyButton({
  value,
  label,
}: {
  value?: string | null;
  label: string;
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

function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
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

function ScopeStatCard({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "neutral" | "positive" | "negative";
}) {
  const toneClass =
    tone === "positive"
      ? "bg-green-50 text-green-900"
      : tone === "negative"
        ? "bg-red-50 text-red-900"
        : "bg-slate-50 text-slate-900";

  const labelClass =
    tone === "positive"
      ? "text-green-700"
      : tone === "negative"
        ? "text-red-700"
        : "text-slate-500";

  return (
    <div className={`rounded-xl px-4 py-3 ${toneClass}`}>
      <div className={`text-sm ${labelClass}`}>{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );
}

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <h2 className="text-xl font-semibold">{title}</h2>
      {subtitle ? <div className="mt-2 text-sm text-slate-500">{subtitle}</div> : null}
      <div className="mt-4">{children}</div>
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

export default function WorkspaceEvidencePage() {
  const params = useParams();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user, workspaces, getWorkspaceRole, loading: authLoading } = useAuth();

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

  const claimIdFromQuery = searchParams.get("claimId");

  const resolvedClaimId = useMemo(() => {
    if (!claimIdFromQuery) return null;
    const parsed = Number(claimIdFromQuery);
    return Number.isNaN(parsed) ? null : parsed;
  }, [claimIdFromQuery]);

  const [claimId, setClaimId] = useState<number | null>(null);
  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [evidencePack, setEvidencePack] = useState<EvidencePack | null>(null);
  const [evidenceBundle, setEvidenceBundle] = useState<EvidenceBundle | null>(null);
  const [publicClaim, setPublicClaim] = useState<PublicClaim | null>(null);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!workspaceId || !workspaceMembership) return;

      setLoading(true);
      setError(null);

      try {
        let targetClaimId = resolvedClaimId;

        if (!targetClaimId) {
          const workspaceClaims = await api.getWorkspaceClaims(workspaceId);
          const latestWorkspaceClaim =
            Array.isArray(workspaceClaims) && workspaceClaims.length > 0
              ? [...workspaceClaims].sort((a, b) => b.claim_schema_id - a.claim_schema_id)[0]
              : null;

          if (!latestWorkspaceClaim) {
            throw new Error("No claims found in this workspace.");
          }

          targetClaimId = latestWorkspaceClaim.claim_schema_id;
        }

        const claimRes = await api.getClaimSchema(targetClaimId);

        if (claimRes.workspace_id !== workspaceId) {
          throw new Error("Claim does not belong to the selected workspace.");
        }

        setClaimId(targetClaimId);
        setClaim(claimRes);

        const [evidenceRes, bundleRes, auditRes] = await Promise.all([
          api.getEvidencePack(targetClaimId),
          api.getEvidenceBundle(targetClaimId).catch(() => null),
          api.getAuditEventsForEntity("claim_schema", targetClaimId).catch(() => []),
        ]);

        setEvidencePack(evidenceRes);
        setEvidenceBundle(bundleRes);
        setAuditEvents(Array.isArray(auditRes) ? auditRes : []);

        try {
          const publicRes = await api.getPublicClaim(targetClaimId);
          setPublicClaim(publicRes);
        } catch {
          setPublicClaim(null);
        }

        if (claimRes.status === "locked") {
          try {
            const integrityRes = await api.getClaimIntegrity(targetClaimId);
            setIntegrity(integrityRes);
          } catch {
            setIntegrity(null);
          }
        } else {
          setIntegrity(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load evidence page");
      } finally {
        setLoading(false);
      }
    };

    if (!authLoading && workspaceMembership) {
      void load();
    } else if (!authLoading && !workspaceMembership) {
      setLoading(false);
    }
  }, [resolvedClaimId, workspaceId, workspaceMembership, authLoading]);

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading evidence pack...</div>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            You do not have access to this workspace evidence page.
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading evidence pack...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        </div>
      </div>
    );
  }

  if (!claimId || !claim || !evidencePack) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">No evidence pack available.</div>
      </div>
    );
  }

  const metricsSnapshot = (evidencePack.metrics_snapshot ?? {}) as Record<string, unknown>;
  const schemaSnapshot = (evidencePack.schema_snapshot ?? {}) as Record<string, unknown>;
  const lifecycle = evidencePack.lifecycle ?? {
    status: claim.status,
    verified_at: claim.verified_at,
    published_at: claim.published_at,
    locked_at: claim.locked_at,
    locked_trade_set_hash: claim.locked_trade_set_hash,
  };

  const scopeSummary = inferScopeSummary(evidencePack, publicClaim);
  const breakdownRows = Object.entries(scopeSummary.breakdown)
    .filter(([, value]) => typeof value === "number" && value > 0)
    .sort((a, b) => Number(b[1]) - Number(a[1]));

  const publicRouteReady = Boolean(
    publicClaim &&
      claim.visibility === "public" &&
      (claim.status === "published" || claim.status === "locked")
  );

  const unlistedRouteReady = Boolean(
    claim.visibility === "unlisted" &&
      claim.claim_hash &&
      (claim.status === "published" || claim.status === "locked")
  );

  const internalHref = `/workspace/${workspaceId}/claim/${claimId}`;
  const evidenceHref = `/workspace/${workspaceId}/evidence?claimId=${claimId}`;
  const publicHref = claim.claim_hash ? `/verify/${claim.claim_hash}` : null;

  const isInternalActive = pathname === internalHref;
  const isEvidenceActive = pathname === `/workspace/${workspaceId}/evidence`;

  const exportJsonName = `evidence_pack_claim_${claimId}_${truncateMiddle(
    evidencePack.claim_hash || claim.claim_hash || "",
    12,
    4,
  ).replace(/\.\.\./g, "")}.json`;
  const exportZipName = `evidence_bundle_claim_${claimId}_${truncateMiddle(
    evidencePack.claim_hash || claim.claim_hash || "",
    12,
    4,
  ).replace(/\.\.\./g, "")}.zip`;
  const exportPdfName = `claim_report_${claimId}_${truncateMiddle(
    evidencePack.claim_hash || claim.claim_hash || "",
    12,
    4,
  ).replace(/\.\.\./g, "")}.pdf`;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-10">
        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-4xl">
              <div className="mb-2 text-sm text-slate-500">
                <Link href={`/workspace/${workspaceId}/claims`} className="hover:underline">
                  Claims
                </Link>
                <span className="mx-2">/</span>
                <Link href={`/workspace/${workspaceId}/claim/${claimId}`} className="hover:underline">
                  Claim #{claimId}
                </Link>
                <span className="mx-2">/</span>
                <span>Evidence</span>
              </div>

              <h1 className="text-3xl font-semibold tracking-tight">Evidence Center</h1>

              <div className="mt-3 flex flex-wrap items-center gap-2">
                <StatusBadge status={claim.status} />
                <VisibilityBadge visibility={claim.visibility} />
                <IntegrityBadge integrity={integrity} />
                <RoleBadge role={workspaceRole} />
              </div>

              <div className="mt-3 text-slate-600">{claim.name}</div>
            </div>

            <div className="flex flex-wrap gap-2">
              <PageNavButton href={internalHref} label="Internal View" active={isInternalActive} />
              <PageNavButton href={evidenceHref} label="Evidence" active={isEvidenceActive} />
              {publicHref ? (
                <PageNavButton href={publicHref} label="Public Verify" active={false} />
              ) : (
                <PageNavButton href="#" label="Public Verify Unavailable" active={false} disabled />
              )}
            </div>
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Claim fingerprint</div>
              <div className="mt-2 font-mono text-sm text-slate-800">
                {truncateMiddle(evidencePack.claim_hash || claim.claim_hash || "—")}
              </div>
              <div className="mt-3">
                <CopyButton
                  value={evidencePack.claim_hash || claim.claim_hash}
                  label="Copy Claim Hash"
                />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Trade-set fingerprint</div>
              <div className="mt-2 font-mono text-sm text-slate-800">
                {truncateMiddle(evidencePack.trade_set_hash || claim.locked_trade_set_hash || "—")}
              </div>
              <div className="mt-3">
                <CopyButton
                  value={evidencePack.trade_set_hash || claim.locked_trade_set_hash}
                  label="Copy Trade Set Hash"
                />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-sm text-slate-500">Exposure posture</div>
              <div className="mt-2 text-lg font-semibold text-slate-900">
                {claim.visibility === "private"
                  ? "Internal only"
                  : claim.visibility === "unlisted"
                    ? "Direct-route verification"
                    : "Publicly routable"}
              </div>
              <div className="mt-2 text-sm text-slate-600">
                {claim.visibility === "private"
                  ? "Evidence remains internal."
                  : claim.visibility === "unlisted"
                    ? "External verification uses the claim hash path."
                    : "External users can reach the public trust surface when lifecycle permits."}
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Claim ID" value={String(claimId)} />
          <StatCard
            label="Trade Count"
            value={
              typeof metricsSnapshot.trade_count === "number"
                ? String(metricsSnapshot.trade_count)
                : "—"
            }
          />
          <StatCard label="Net PnL" value={formatNumber(metricsSnapshot.net_pnl, 2)} />
          <StatCard label="Profit Factor" value={formatNumber(metricsSnapshot.profit_factor, 4)} />
        </section>

        <SectionCard
          title="Scope Summary"
          subtitle="Explainability layer for what entered evidence computation and what was left out."
        >
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <ScopeStatCard
              label="Workspace Trades"
              value={
                scopeSummary.workspaceTradeCount !== null
                  ? String(scopeSummary.workspaceTradeCount)
                  : "—"
              }
            />
            <ScopeStatCard
              label="Included Trades"
              value={
                scopeSummary.includedTradeCount !== null
                  ? String(scopeSummary.includedTradeCount)
                  : "—"
              }
              tone="positive"
            />
            <ScopeStatCard
              label="Excluded Trades"
              value={
                scopeSummary.excludedTradeCount !== null
                  ? String(scopeSummary.excludedTradeCount)
                  : "—"
              }
              tone="negative"
            />
            <ScopeStatCard
              label="In-scope Evidence Rows"
              value={
                scopeSummary.inScopeEvidenceRows !== null
                  ? String(scopeSummary.inScopeEvidenceRows)
                  : "—"
              }
            />
          </div>

          <div className="mt-5">
            <div className="mb-2 text-sm font-medium text-slate-700">Excluded breakdown</div>

            {breakdownRows.length === 0 ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                No explicit exclusion breakdown is available in this evidence bundle.
              </div>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {breakdownRows.map(([reason, count]) => (
                  <div key={reason} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">{reason}</div>
                    <div className="mt-1 text-lg font-semibold">{String(count)}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </SectionCard>

        <div className="grid gap-6 lg:grid-cols-2">
          <SectionCard
            title="Evidence Summary"
            subtitle="Portable evidence facts describing what was exported."
          >
            <div className="space-y-4">
              <div>
                <div className="text-sm text-slate-500">Exported At</div>
                <div className="mt-1 font-medium">{formatDateTime(evidencePack.exported_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Export Version</div>
                <div className="mt-1 font-medium">{evidencePack.export_version || "—"}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Claim Hash</div>
                <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                  {evidencePack.claim_hash || "—"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Trade Set Hash</div>
                <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                  {evidencePack.trade_set_hash || "—"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Methodology Notes</div>
                <div className="mt-1 rounded-xl bg-slate-50 p-3 whitespace-pre-wrap text-sm text-slate-700">
                  {evidencePack.methodology_notes || "—"}
                </div>
              </div>
            </div>
          </SectionCard>

          <SectionCard
            title="Lifecycle & Integrity"
            subtitle="Trust-state facts used to decide whether evidence can be externally relied on."
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <div className="text-sm text-slate-500">Status</div>
                <div className="mt-1 font-medium">{lifecycle.status || "—"}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Integrity Status</div>
                <div className="mt-1 font-medium">{integrity?.integrity_status || "not checked"}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Verified At</div>
                <div className="mt-1 font-medium">{formatDateTime(lifecycle.verified_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Published At</div>
                <div className="mt-1 font-medium">{formatDateTime(lifecycle.published_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Locked At</div>
                <div className="mt-1 font-medium">{formatDateTime(lifecycle.locked_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Hash Match</div>
                <div className="mt-1 font-medium">
                  {integrity ? String(integrity.hash_match) : "—"}
                </div>
              </div>
            </div>

            {integrity ? (
              <div className="mt-4 space-y-3">
                <div>
                  <div className="text-sm text-slate-500">Stored Hash</div>
                  <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                    {integrity.stored_hash}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Recomputed Hash</div>
                  <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                    {integrity.recomputed_hash}
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                Integrity result is available after lock state verification.
              </div>
            )}
          </SectionCard>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <EvidenceCard title="Claim Schema Snapshot" value={safeJson(schemaSnapshot)} />
          <EvidenceCard title="Metrics Snapshot" value={safeJson(metricsSnapshot)} />
          <EvidenceCard
            title="Bundle Manifest"
            value={
              evidenceBundle ? safeJson(evidenceBundle.manifest) : "ZIP bundle preview not available."
            }
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <SectionCard
            title="Public Verification Snapshot"
            subtitle="Preview of what external verifiers can reach after lifecycle and visibility gates are satisfied."
          >
            {!publicClaim ? (
              <div className="text-sm text-slate-500">
                Public claim view is not available for this claim yet.
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <div className="text-sm text-slate-500">Public Visibility</div>
                    <div className="mt-1 font-medium">{publicClaim.scope.visibility || "—"}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-500">Public Route Ready</div>
                    <div className="mt-1 font-medium">
                      {publicRouteReady ? "yes" : unlistedRouteReady ? "unlisted route only" : "no"}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Public Claim Payload Preview</div>
                  <pre className="mt-2 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
                    {safeJson(publicClaim)}
                  </pre>
                </div>
              </div>
            )}
          </SectionCard>

          <SectionCard
            title="Audit Timeline Preview"
            subtitle="Recorded evidence actions showing how this claim moved through the lifecycle."
          >
            <div className="mb-4 text-sm text-slate-500">{auditEvents.length} event(s)</div>

            {auditEvents.length === 0 ? (
              <div className="text-sm text-slate-500">No audit events found for this claim.</div>
            ) : (
              <div className="space-y-4">
                {auditEvents.slice(0, 6).map((event) => {
                  const metadata = tryParseJson(event.metadata_json);

                  return (
                    <div key={event.id} className="rounded-xl border border-slate-200 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="font-medium">{event.event_type}</div>
                        <div className="text-xs text-slate-500">
                          {formatDateTime(event.created_at)}
                        </div>
                      </div>

                      <div className="mt-2 text-xs text-slate-500">
                        entity: {event.entity_type} / {event.entity_id}
                      </div>

                      <pre className="mt-3 overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
                        {JSON.stringify(metadata, null, 2)}
                      </pre>
                    </div>
                  );
                })}
              </div>
            )}
          </SectionCard>
        </div>

        <SectionCard
          title="Evidence Exports"
          subtitle="Portable artifacts for storage, dispute-ready handoff, and external review after evidence is understood."
        >
          <DownloadEvidenceButton
            claimSchemaId={claimId}
            claimHash={evidencePack.claim_hash}
            payload={evidencePack}
          />

          <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-medium text-slate-700">Export naming</div>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              <div className="rounded-xl bg-white p-3">
                <div className="text-xs uppercase tracking-wide text-slate-500">JSON</div>
                <div className="mt-1 break-all text-sm text-slate-700">{exportJsonName}</div>
              </div>
              <div className="rounded-xl bg-white p-3">
                <div className="text-xs uppercase tracking-wide text-slate-500">ZIP</div>
                <div className="mt-1 break-all text-sm text-slate-700">{exportZipName}</div>
              </div>
              <div className="rounded-xl bg-white p-3">
                <div className="text-xs uppercase tracking-wide text-slate-500">PDF</div>
                <div className="mt-1 break-all text-sm text-slate-700">{exportPdfName}</div>
              </div>
            </div>
          </div>
        </SectionCard>
      </main>
    </div>
  );
}