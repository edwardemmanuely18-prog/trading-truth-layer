"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  api,
  type ClaimTradeEvidence,
  type ClaimTradeScopeRow,
  type PublicVerifyResult,
  type VerifyPayloadV7,
  resolveVerificationExposureLevel,
} from "../../../lib/api";
import ClaimVerificationSignature from "../../../components/ClaimVerificationSignature";
import EquityCurveChart from "../../../components/EquityCurveChart";

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

function normalizeText(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function shortHash(value?: string | null, head = 16, tail = 10) {
  const text = String(value ?? "").trim();
  if (!text) return "—";
  if (text.length <= head + tail + 3) return text;
  return `${text.slice(0, head)}...${text.slice(-tail)}`;
}

function resolveLineageCanonical(lineage: any) {
  const rootClaimId =
    typeof lineage?.root_claim_id === "number" ? lineage.root_claim_id : null;

  const parentClaimId =
    typeof lineage?.parent_claim_id === "number" ? lineage.parent_claim_id : null;

  const versionNumber =
    typeof lineage?.version_number === "number" ? lineage.version_number : 1;

  return {
    rootClaimId,
    parentClaimId,
    versionNumber,
  };
}

function resolveClaimOriginType(lineage: any) {
  const l = resolveLineageCanonical(lineage);

  if (l.versionNumber > 1) return "versioned";
  if (l.parentClaimId || l.rootClaimId) return "derived";
  return "independent";
}

function resolveNetworkLabel(lineage: any) {
  const type = resolveClaimOriginType(lineage);

  if (type === "versioned") return "Versioned Claim";
  if (type === "derived") return "Derived Claim";
  return "Independent Claim";
}

function networkTone(lineage: any) {
  const type = resolveClaimOriginType(lineage);

  if (type === "independent") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }

  if (type === "derived") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }

  return "border-sky-200 bg-sky-50 text-sky-800";
}

function resolveIssuerSafe(result: any, v7Payload: any) {
  return (
    v7Payload?.issuer?.name ||
    result?.issuer?.name ||
    result?.issuer_name ||
    result?.workspace_name ||
    "Unknown Issuer"
  );
}

function buildLineageSummary(lineage: any) {
  const l = resolveLineageCanonical(lineage);

  return {
    root: l.rootClaimId ? `claim#${l.rootClaimId}` : "self",
    parent: l.parentClaimId ? `claim#${l.parentClaimId}` : "none",
    version: String(l.versionNumber),
  };
}

async function copyToClipboard(value: string) {
  if (typeof window === "undefined") {
    throw new Error("Clipboard is not available in this environment.");
  }

  const nav = window.navigator;
  if (!nav?.clipboard?.writeText) {
    throw new Error("Clipboard is not available in this browser.");
  }

  await nav.clipboard.writeText(value);
}

function buildQrImageUrl(value: string) {
  const encoded = encodeURIComponent(value);
  return `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encoded}`;
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

function IntegrityBadge({ integrityStatus }: { integrityStatus?: string | null }) {
  const normalized = normalizeText(integrityStatus);
  const isValid = normalized === "valid";

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold ${
        isValid
          ? "border-green-200 bg-green-100 text-green-800"
          : "border-red-200 bg-red-100 text-red-800"
      }`}
    >
      {isValid ? "✓ HASH MATCH · VERIFIED" : "⚠ HASH MISMATCH · REVIEW REQUIRED"}
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
      visibility: {visibility || "—"}
    </span>
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
      await copyToClipboard(value);
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
    <div className="rounded-xl bg-slate-50 p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
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

function ScopeListCard({
  title,
  items,
  emptyText,
}: {
  title: string;
  items: Array<string | number>;
  emptyText: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <h2 className="text-2xl font-semibold">{title}</h2>
      {items.length === 0 ? (
        <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">{emptyText}</div>
      ) : (
        <div className="mt-4 flex flex-wrap gap-2">
          {items.map((item) => (
            <span
              key={String(item)}
              className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-medium text-slate-700"
            >
              {item}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function PublicTradeEvidenceTable({
  title,
  subtitle,
  rows,
  emptyText,
  showExclusionColumns = false,
}: {
  title: string;
  subtitle: string;
  rows: ClaimTradeScopeRow[];
  emptyText: string;
  showExclusionColumns?: boolean;
}) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">{title}</h2>
          <div className="mt-2 text-sm text-slate-500">{subtitle}</div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
          <div className="text-slate-500">Rows</div>
          <div className="mt-1 font-semibold">{rows.length}</div>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">{emptyText}</div>
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
                <th className="px-3 py-2">Entry</th>
                <th className="px-3 py-2">Exit</th>
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
              {rows.map((row) => (
                <tr
                  key={`${row.trade_id}-${row.index}-${row.scope_status}`}
                  className="border-b last:border-0 align-top"
                >
                  <td className="px-3 py-2">{row.index}</td>
                  <td className="px-3 py-2">{row.trade_id}</td>
                  <td className="px-3 py-2">{formatDateTime(row.opened_at)}</td>
                  <td className="px-3 py-2">{row.symbol}</td>
                  <td className="px-3 py-2">{row.side}</td>
                  <td className="px-3 py-2">{formatNumber(row.entry_price, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.exit_price, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.quantity, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.net_pnl, 4)}</td>
                  <td className="px-3 py-2">{formatNumber(row.cumulative_pnl, 4)}</td>
                  <td className="px-3 py-2">
                    <ScopeStatusBadge status={row.scope_status} />
                  </td>
                  {showExclusionColumns ? (
                    <td className="px-3 py-2">
                      <div className="min-w-[140px]">
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

export default function PublicVerifyClaimPage() {
  const params = useParams();

  const claimHash = useMemo(() => {
    const raw = Array.isArray(params?.claimHash) ? params.claimHash[0] : params?.claimHash;
    return String(raw || "").trim();
  }, [params]);

  const [result, setResult] = useState<PublicVerifyResult | null>(null);
  const [v7Payload, setV7Payload] = useState<VerifyPayloadV7 | null>(null);
  const [tradeEvidence, setTradeEvidence] = useState<ClaimTradeEvidence | null>(null);
  const [loading, setLoading] = useState(true);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evidenceError, setEvidenceError] = useState<string | null>(null);
  const [shareMessage, setShareMessage] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!claimHash) {
        setError("Invalid claim hash.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        setEvidenceError(null);

        // Phase 6 public endpoint
        const res = await api.getPublicClaimByHash(claimHash);
        setResult(res);

        // Phase 7 canonical endpoint
        try {
          const verify = await api.getVerifyClaimByHash(claimHash);
          
          // detect V7 payload (raw)
          if ((verify as any)?.payload_version) {
            setV7Payload(verify as unknown as VerifyPayloadV7);
          }
        } catch {
          // ignore — Phase 7 optional
        }

        if (res.claim_schema_id) {
          try {
            setEvidenceLoading(true);
            const evidence = await api.getClaimTrades(res.claim_schema_id);
            setTradeEvidence(evidence);
          } catch (err) {
            setTradeEvidence(emptyTradeEvidence(res.claim_schema_id));
            setEvidenceError(
              err instanceof Error ? err.message : "Failed to load verified trade evidence."
            );
          } finally {
            setEvidenceLoading(false);
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load public verification record.");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [claimHash]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            Loading public verification record...
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="mb-6">
            <Link
              href="/claims"
              className="inline-flex rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Back to Public Claims
            </Link>
          </div>

          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700 shadow-sm">
            {error}
          </div>
        </main>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Claim not found.</div>
        </main>
      </div>
    );
  }

  const verifiedResult = result;

  const scope = verifiedResult.scope ?? {
    period_start: "—",
    period_end: "—",
    included_members: [],
    included_symbols: [],
    methodology_notes: "",
    visibility: "—",
  };

  const lifecycle = verifiedResult.lifecycle ?? {
    status: verifiedResult.verification_status || "unknown",
    verified_at: null,
    published_at: null,
    locked_at: null,
  };

  const lineage = verifiedResult.lineage ?? {
    parent_claim_id: null,
    root_claim_id: null,
    version_number: null,
  };
  const lineageSummary = buildLineageSummary(lineage);
  const networkType = resolveClaimOriginType(lineage);
  const networkLabel = resolveNetworkLabel(lineage);
  const issuerName = resolveIssuerSafe(verifiedResult, v7Payload);

  const leaderboard = Array.isArray(verifiedResult.leaderboard) ? verifiedResult.leaderboard : [];
  const integrityOk = normalizeText(verifiedResult.integrity_status) === "valid";
  const lifecycleStatus = normalizeText(verifiedResult.verification_status);

  const trustLevel = (() => {
    if (!integrityOk) return "compromised";
    if (lifecycleStatus === "locked") return "finalized";
    if (lifecycleStatus === "published") return "public_verified";
    if (lifecycleStatus === "verified") return "internally_verified";
    return "unverified";
  })();
  const verificationUrl =
    typeof window !== "undefined" ? window.location.href : `/verify/${verifiedResult.claim_hash}`;
  const publicViewUrl = `/claim/${verifiedResult.claim_schema_id}/public`;
  const qrImageUrl = buildQrImageUrl(verificationUrl);

  const includedRows = Array.isArray(tradeEvidence?.included_trades)
    ? tradeEvidence.included_trades
    : [];
  const excludedRows = Array.isArray(tradeEvidence?.excluded_trades)
    ? tradeEvidence.excluded_trades
    : [];
  const evidenceSummary = tradeEvidence?.summary;

  const publicCurvePoints = Array.isArray(verifiedResult.equity_curve?.curve)
    ? verifiedResult.equity_curve.curve
    : [];
  const hasDisputes = Boolean((verifiedResult as any)?.has_active_disputes);  

 const exposureLevel = resolveVerificationExposureLevel(verifiedResult);   
 const canonicalCapability = true;
 const portableCapability = true;
 const apiAddressableCapability = true;
 const trustState = (() => {
  switch (trustLevel) {
    case "finalized":
      return "Finalized · Cryptographically Locked";
    case "public_verified":
      return "Published · Public Verification Record";
    case "internally_verified":
      return "Verified · Pre-Public State";
    case "compromised":
      return "Integrity Failure · Not Trustworthy";
    default:
      return "Unverified Record";
  }
})();

  async function handleShare() {
    try {
      setShareMessage(null);

      if (typeof navigator !== "undefined" && typeof navigator.share === "function") {
        await navigator.share({
          title: verifiedResult.name || "Verified Claim Record",
          text: "View this verified trading claim record.",
          url: verificationUrl,
        });
        return;
      }

      await copyToClipboard(verificationUrl);
      setShareMessage("Share not available here. Verification link copied instead.");
    } catch {
      // native share may be cancelled
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · External Verification Endpoint</div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Verified Claim Record</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Canonical verification route for a lifecycle-governed trading claim, including
              integrity state, fingerprints, scope, lifecycle history, leaderboard snapshot,
              verified trade evidence, and equity-curve inspection.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              href={publicViewUrl}
              className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
            >
              Open Public View
            </Link>

            <CopyButton value={verificationUrl} label="Copy Verification Link" />

            <button
              type="button"
              onClick={() => void handleShare()}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Share Verification
            </button>

            <Link
              href="/claims"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Back to Public Claims
            </Link>
          </div>
        </div>

        {shareMessage ? (
          <div className="mb-6 text-sm text-slate-500">{shareMessage}</div>
        ) : null}

        <div className="mb-8 rounded-2xl border border-indigo-200 bg-indigo-50 p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-700">
                Canonical Verification Endpoint
              </div>
              <div className="mt-1 text-xl font-semibold text-indigo-950">
                Machine-readable proof surface for external validation
              </div>
              <div className="mt-2 max-w-3xl text-sm leading-7 text-indigo-900">
                This route is the authoritative verification surface for the claim. It exposes
                canonical identity, trade-set fingerprint, lifecycle state, and integrity posture
                for human review, platform integrations, and audit-grade validation.
              </div>
            </div>

            <span className="rounded-full border border-indigo-200 bg-white px-3 py-1 text-xs font-semibold text-indigo-800">
              EXPOSURE: {String(exposureLevel || "unknown").toUpperCase()}
            </span>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl border bg-white p-3 text-sm">
              <div className="text-slate-500">Verification Endpoint</div>
              <div className="mt-1 font-mono text-xs break-all text-slate-800">
                {verificationUrl}
              </div>
            </div>

            <div className="rounded-xl border bg-white p-3 text-sm">
              <div className="text-slate-500">Public Record Endpoint</div>
              <div className="mt-1 font-mono text-xs break-all text-slate-800">
                {publicViewUrl}
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <ClaimVerificationSignature
            status={verifiedResult.verification_status}
            integrityStatus={verifiedResult.integrity_status}
            claimHash={verifiedResult.claim_hash}
            tradeSetHash={verifiedResult.trade_set_hash}
            verifiedAt={lifecycle.verified_at}
            lockedAt={lifecycle.locked_at}
          />
        </div>

        {v7Payload ? (
          <div className="mb-8 rounded-2xl border border-indigo-200 bg-indigo-50 p-5 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-700">
              Portable verification metadata
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-3 text-sm">
              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">Canonical</div>
                <div className="mt-1 font-semibold text-slate-900">
                  {String(canonicalCapability)}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">Portable</div>
                <div className="mt-1 font-semibold text-slate-900">
                  {String(portableCapability)}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">API Addressable</div>
                <div className="mt-1 font-semibold text-slate-900">
                  {String(apiAddressableCapability)}
                </div>
              </div>
            </div>

            <div className="mt-2 grid gap-3 md:grid-cols-2 xl:grid-cols-4 text-sm">
              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">Issuer</div>
                <div className="mt-1 font-semibold text-slate-900">{v7Payload.issuer?.name || "—"}</div>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">Network State</div>
                <div className="mt-1 font-semibold text-slate-900">{networkLabel}</div>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">Exposure Level</div>
                <div className="mt-1 font-semibold text-slate-900">
                  {v7Payload.network_identity?.exposure_level || "—"}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <div className="text-slate-500">Integrity Status</div>
                <div className="mt-1 font-semibold text-slate-900">
                  {v7Payload.integrity_record?.status || "—"}
                </div>
              </div>
            </div>
          </div>
        ) : null}

        <div
          className={`mb-8 rounded-2xl border px-5 py-4 ${
            integrityOk ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
          }`}
        >

        <div className="mt-4 rounded-xl bg-white/70 p-4 text-sm text-slate-700">
          <div className="font-medium text-slate-900">How to interpret this verification</div>

          <div className="mt-2 leading-6">
            This record is currently classified as <span className="font-medium">{trustState}</span>.
          </div>

          <div className="mt-3 grid gap-2 md:grid-cols-3">
            <div className="rounded-lg bg-white px-3 py-2">
              <span className="font-medium text-slate-900">Integrity</span>
              <div className="mt-1 text-slate-600">Trade-set hash matches canonical fingerprint.</div>
            </div>

            <div className="rounded-lg bg-white px-3 py-2">
              <span className="font-medium text-slate-900">Lifecycle</span>
              <div className="mt-1 text-slate-600">Claim status determines governance finality.</div>
            </div>

            <div className="rounded-lg bg-white px-3 py-2">
              <span className="font-medium text-slate-900">Exposure</span>
              <div className="mt-1 text-slate-600">Visibility defines how the claim is distributed.</div>
            </div>
          </div>
        </div>  
          <div className="text-sm text-slate-500">Verification Result · Cryptographic Integrity Check</div>

          <div className="mt-2 text-xl font-semibold">
            {integrityOk ? "Verified Record — Cryptographic Integrity Confirmed" : "Verification Failed — Cryptographic Mismatch Detected"}
          </div>

          <div className="mt-2 text-sm text-slate-600 max-w-2xl">
            {integrityOk
              ? "The recomputed trade-set hash matches the canonical fingerprint. This record is cryptographically consistent with its original state."
              : "The recomputed trade-set hash does NOT match the canonical fingerprint. This record is inconsistent with its original state and should not be trusted without further investigation."}
          </div>
        </div>

        {hasDisputes ? (
          <div className="mb-8 rounded-2xl border border-red-300 bg-red-50 p-5 shadow-sm">
            <div className="text-sm font-semibold text-red-900">
              Active Governance Dispute
            </div>

            <div className="mt-2 text-sm text-red-800">
              This claim currently has active disputes or challenges.
            </div>

            <div className="mt-2 text-xs text-red-700">
              External trust, capital allocation decisions, and leaderboard interpretation
              should be treated as provisional until disputes are resolved.
            </div>
          </div>
        ) : null}
        <div className="mb-8 rounded-3xl border border-green-200 bg-green-50 p-6 shadow-sm">
          <div className="mb-5 rounded-xl border border-green-200 bg-white p-4">
            <div className="text-xs uppercase tracking-wide text-slate-500">
              Machine-Readable Identity · External Verification Layer
            </div>

            <div className="mt-3 grid gap-3 md:grid-cols-2 text-xs font-mono text-slate-700">
              <div>
                <div className="text-slate-500">claim_hash</div>
                <div className="break-all">{verifiedResult.claim_hash}</div>
              </div>

              <div>
                <div className="text-slate-500">trade_set_hash</div>
                <div className="break-all">{verifiedResult.trade_set_hash}</div>
              </div>

              <div>
                <div className="text-slate-500">verification_status</div>
                <div>{verifiedResult.verification_status}</div>
              </div>

              <div>
                <div className="text-slate-500">integrity_status</div>
                <div>{verifiedResult.integrity_status}</div>
              </div>
            </div>
          </div>
          <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
            <div>
              <div className="text-sm font-medium text-green-700">
                Trust Summary · Canonical Verification Layer
              </div>
              <h2 className="mt-2 text-3xl font-semibold text-green-950">{verifiedResult.name}</h2>

              <div className="mt-4 flex flex-wrap gap-2">
                <StatusBadge status={verifiedResult.verification_status} />
                <IntegrityBadge integrityStatus={verifiedResult.integrity_status} />
                <VisibilityBadge visibility={scope.visibility || "—"} />
                <span className="inline-flex rounded-full border border-green-200 bg-white px-3 py-1 text-sm font-medium text-green-800">
                  trust state: {trustState} · Verification-grade record
                </span>
              </div>

              <div className="mt-5 rounded-2xl border border-green-200 bg-white/70 p-5">
                <div className="text-base font-semibold text-green-900">Verification Reading</div>
                <div className="mt-2 text-sm leading-7 text-green-800">
                  This route is the canonical proof surface for this claim. It exposes the identity
                  fingerprint, the in-scope trade-set fingerprint, lifecycle milestones, and the
                  integrity posture needed for external trust, disputes, and audit review.
                </div>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-green-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Verification path</div>
                  <div className="mt-2 rounded-xl bg-slate-50 p-3 font-mono text-xs break-all text-slate-700">
                    {verificationUrl}
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <CopyButton value={verificationUrl} label="Copy Verify Link" />
                    <button
                      type="button"
                      onClick={() => void handleShare()}
                      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                    >
                      Share Proof
                    </button>
                  </div>
                </div>



                <div className="rounded-2xl border border-green-200 bg-white p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">Public view path</div>
                  <div className="mt-2 rounded-xl bg-slate-50 p-3 font-mono text-xs break-all text-slate-700">
                    {publicViewUrl}
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <CopyButton value={publicViewUrl} label="Copy Public Path" />
                    <Link
                      href={publicViewUrl}
                      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                    >
                      Open Public View
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-green-200 bg-white p-5 shadow-sm">
              <div className="text-sm font-medium text-slate-500">Scan to verify</div>
              <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-3">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={qrImageUrl}
                  alt="QR code for verification link"
                  className="mx-auto h-auto w-full max-w-[220px]"
                />
              </div>
              <div className="mt-4 text-sm leading-6 text-slate-600">
                Scan this code to open the canonical verification route.
                This enables independent validation of identity, lifecycle state,
                and trade-set fingerprint integrity.
              </div>

              <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm">
                <div className="text-slate-500">Claim hash</div>
                <div className="mt-1 break-all font-mono text-xs text-slate-800">
                  {verifiedResult.claim_hash || "—"}
                </div>
                <div className="mt-2 text-slate-500">{shortHash(verifiedResult.claim_hash)}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm font-semibold text-slate-900">
            Intended Trust Consumers
          </div>

          <div className="mt-3 grid gap-2 text-sm text-slate-600">
            <div>• Trading communities and evaluation programs</div>
            <div>• Investors and capital allocators</div>
            <div>• Prop firms and verification platforms</div>
            <div>• Dispute resolution and audit workflows</div>
          </div>
        </div>

        <div className="mb-8 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-4xl">
              <div className="text-sm text-slate-500">Canonical Proof Identity</div>
              <h2 className="mt-2 text-3xl font-semibold">{verifiedResult.name}</h2>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Claim Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-[11px] leading-5 break-all text-slate-700">
                    {verifiedResult.claim_hash || "—"}
                  </div>
                  <div className="mt-2 text-sm text-slate-500">{shortHash(verifiedResult.claim_hash)}</div>
                  <div className="mt-3">
                    <CopyButton value={verifiedResult.claim_hash} label="Copy Claim Hash" />
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Trade Set Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-[11px] leading-5 break-all text-slate-700">
                    {verifiedResult.trade_set_hash || "—"}
                  </div>
                  <div className="mt-2 text-sm text-slate-500">{shortHash(verifiedResult.trade_set_hash)}</div>
                  <div className="mt-3">
                    <CopyButton value={verifiedResult.trade_set_hash} label="Copy Trade Set Hash" />
                  </div>
                </div>
              </div>
            </div>

            <div
              className={`rounded-2xl border px-5 py-4 ${
                integrityOk ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"
              }`}
            >
              <div className="text-sm text-slate-500">Integrity Posture</div>
              <div className="mt-2 text-lg font-semibold">
                {integrityOk ? "Integrity Confirmed" : "Integrity Alert"}
              </div>
              <div className="mt-2 max-w-xs text-sm text-slate-600">
                {integrityOk
                  ? "The public record matches the recomputed integrity fingerprint for the current trade set."
                  : "The public record does not currently match the recomputed integrity fingerprint."}
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Trade Count"
              value={String(verifiedResult.trade_count)}
              hint="In-scope trades used for this record"
            />
            <MetricCard
              label="Net PnL"
              value={formatNumber(verifiedResult.net_pnl)}
              hint="Aggregate net trading result"
            />
            <MetricCard
              label="Profit Factor"
              value={formatNumber(verifiedResult.profit_factor, 4)}
              hint="Gross profit ÷ gross loss"
            />
            <MetricCard
              label="Win Rate"
              value={formatPercent(verifiedResult.win_rate, 2)}
              hint="Winning trades as percentage"
            />
          </div>
        </div>

        <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="text-xs uppercase tracking-wide text-slate-500">
            Trust Network Context · Phase 8
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${networkTone(lineage)}`}>
              network: {networkType}
            </span>

            <span className="inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700">
              issuer: {issuerName}
            </span>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5 text-sm text-slate-700">
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
              <div className="font-medium text-slate-900">{lineageSummary.root}</div>
            </div>

            <div>
              <div className="text-slate-500">Parent</div>
              <div className="font-medium text-slate-900">{lineageSummary.parent}</div>
            </div>

            <div>
              <div className="text-slate-500">Version</div>
              <div className="font-medium text-slate-900">{lineageSummary.version}</div>
            </div>
          </div>
        </div>

        <div className="mb-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Verification Scope</h2>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <DetailRow label="Period Start" value={scope.period_start || "—"} />
              <DetailRow label="Period End" value={scope.period_end || "—"} />
              <DetailRow
                label="Included Members"
                value={
                  Array.isArray(scope.included_members) && scope.included_members.length > 0
                    ? scope.included_members.join(", ")
                    : "All in scope"
                }
              />
              <DetailRow
                label="Included Symbols"
                value={
                  Array.isArray(scope.included_symbols) && scope.included_symbols.length > 0
                    ? scope.included_symbols.join(", ")
                    : "All in scope"
                }
              />
            </div>

            <div className="mt-5">
              <div className="text-sm text-slate-500">Methodology Notes</div>
              <div className="mt-1 rounded-xl bg-slate-50 p-4 text-sm whitespace-pre-wrap text-slate-700">
                {scope.methodology_notes || "—"}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Lifecycle & Lineage</h2>

              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <DetailRow label="Status" value={lifecycle.status || "—"} />
                <DetailRow label="Integrity" value={verifiedResult.integrity_status || "—"} />
                <DetailRow label="Verified At" value={formatDateTime(lifecycle.verified_at)} />
                <DetailRow label="Published At" value={formatDateTime(lifecycle.published_at)} />
                <DetailRow label="Locked At" value={formatDateTime(lifecycle.locked_at)} />
                <DetailRow label="Version Number" value={lineageSummary.version} />
                <DetailRow label="Root Claim" value={lineageSummary.root} />
                <DetailRow label="Parent Claim" value={lineageSummary.parent} />
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Verification Reading</h2>
              <div className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Claim hash:</span> canonical identity
                  fingerprint for this claim definition.
                </div>
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Trade-set hash:</span> fingerprint of
                  the in-scope trade evidence used by the record.
                </div>
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Integrity valid:</span> recomputed
                  trade-set fingerprint matches the stored locked fingerprint.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8 grid gap-6 lg:grid-cols-2">
          <ScopeListCard
            title="Included Members"
            items={Array.isArray(scope.included_members) ? scope.included_members : []}
            emptyText="All members were considered in scope for this public claim."
          />

          <ScopeListCard
            title="Included Symbols"
            items={Array.isArray(scope.included_symbols) ? scope.included_symbols : []}
            emptyText="All symbols were considered in scope for this public claim."
          />
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Leaderboard Snapshot</h2>

          {leaderboard.length === 0 ? (
            <div className="mt-4 text-slate-500">No leaderboard rows available.</div>
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
                  {leaderboard.map((row) => (
                    <tr
                      key={`${row.rank}-${row.member}-${row.member_id ?? "na"}`}
                      className="border-b last:border-0"
                    >
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

        <div className="mb-8">
          {publicCurvePoints.length > 0 ? (
            <EquityCurveChart title="Public Equity Curve" points={publicCurvePoints} />
          ) : (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
              No equity curve data available for this verified record.
            </div>
          )}
        </div>

        <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Evidence Inspection Layer
              </div>
              <h2 className="mt-2 text-2xl font-semibold">Verified Trade Evidence</h2>
              <div className="mt-2 max-w-3xl text-sm leading-7 text-slate-600">
                Trade-level evidence supporting the verified claim scope. This section is intended for
                deeper inspection after identity, lifecycle, and integrity have been reviewed above.
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
                <div className="text-slate-500">Workspace Trades</div>
                <div className="mt-1 font-semibold">
                  {evidenceSummary?.workspace_trade_count ?? "—"}
                </div>
              </div>
              <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm">
                <div className="text-green-700">Included Trades</div>
                <div className="mt-1 font-semibold text-green-900">
                  {evidenceSummary?.included_trade_count ?? includedRows.length}
                </div>
              </div>
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm">
                <div className="text-red-700">Excluded Trades</div>
                <div className="mt-1 font-semibold text-red-900">
                  {evidenceSummary?.excluded_trade_count ?? excludedRows.length}
                </div>
              </div>
            </div>
          </div>

          {evidenceLoading ? (
            <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
              Loading verified trade evidence...
            </div>
          ) : evidenceError ? (
            <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              {evidenceError}
            </div>
          ) : null}

          <div className="mt-6 space-y-6">
            <PublicTradeEvidenceTable
              title="Included Trade Rows"
              subtitle="Trades included in the public claim scope and used to compute the published verification metrics."
              rows={includedRows}
              emptyText="No included trade rows are available for this public claim."
            />

            <PublicTradeEvidenceTable
              title="Excluded Trade Rows"
              subtitle="Trades outside the final public claim scope, shown with explicit exclusion reasons when available."
              rows={excludedRows}
              emptyText="No excluded trade rows are available for this public claim."
              showExclusionColumns
            />
          </div>
        </div>

        <div className="text-center text-xs text-slate-400 space-y-2">
          <div>
            Trading Truth Layer — Canonical verification infrastructure for trading claims
          </div>

          <div>
            This verification route is designed for investors, trading communities, prop firms,
            auditors, and external systems that require standardized proof of trading performance.
          </div>
        </div>
      </main>
    </div>
  );
}