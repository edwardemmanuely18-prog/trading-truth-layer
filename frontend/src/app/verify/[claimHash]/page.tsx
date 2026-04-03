"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  api,
  type ClaimTradeEvidence,
  type ClaimTradeScopeRow,
} from "../../../lib/api";
import ClaimVerificationSignature from "../../../components/ClaimVerificationSignature";

type VerifyClaimResult = {
  claim_id: number;
  workspace_id: number;
  name: string;
  status: string;
  visibility: string;
  claim_hash: string;
  stored_trade_set_hash?: string | null;
  recomputed_trade_set_hash?: string | null;
  integrity: "valid" | "compromised" | "unlocked";
  version_number?: number | null;
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  published_at?: string | null;
  verified_at?: string | null;
  locked_at?: string | null;
  period_start?: string | null;
  period_end?: string | null;
  public_view_path: string;
  verify_path: string;
};

async function fetchVerifyClaimByHash(claimHash: string): Promise<VerifyClaimResult> {
  const response = await fetch(`/api/verify/${encodeURIComponent(claimHash)}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const raw = await response.text();
    try {
      const parsed = JSON.parse(raw);
      const detail =
        typeof parsed?.detail === "string"
          ? parsed.detail
          : typeof parsed?.message === "string"
            ? parsed.message
            : raw;
      throw new Error(detail || `Verify request failed with status ${response.status}`);
    } catch {
      throw new Error(raw || `Verify request failed with status ${response.status}`);
    }
  }

  return response.json() as Promise<VerifyClaimResult>;
}

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

function normalizeText(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function shortHash(value?: string | null, head = 16, tail = 10) {
  const text = String(value ?? "").trim();
  if (!text) return "—";
  if (text.length <= head + tail + 3) return text;
  return `${text.slice(0, head)}...${text.slice(-tail)}`;
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
        : normalized === "draft"
          ? "border-slate-200 bg-slate-100 text-slate-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function IntegrityBadge({ integrityStatus }: { integrityStatus?: string | null }) {
  const normalized = normalizeText(integrityStatus);

  const className =
    normalized === "valid"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "compromised"
        ? "border-red-200 bg-red-100 text-red-800"
        : "border-amber-200 bg-amber-100 text-amber-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      integrity: {integrityStatus || "unknown"}
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

  const [result, setResult] = useState<VerifyClaimResult | null>(null);
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

        const res = await fetchVerifyClaimByHash(claimHash);
        setResult(res);

        if (res.claim_id) {
          try {
            setEvidenceLoading(true);
            const evidence = await api.getClaimTrades(res.claim_id);
            setTradeEvidence(evidence);
          } catch (err) {
            setTradeEvidence(emptyTradeEvidence(res.claim_id));
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
  const integrityOk = normalizeText(verifiedResult.integrity) === "valid";
  const verificationUrl =
    typeof window !== "undefined" ? window.location.href : verifiedResult.verify_path;
  const publicViewUrl = verifiedResult.public_view_path;
  const qrImageUrl = buildQrImageUrl(verificationUrl);

  const includedRows = Array.isArray(tradeEvidence?.included_trades)
    ? tradeEvidence.included_trades
    : [];
  const excludedRows = Array.isArray(tradeEvidence?.excluded_trades)
    ? tradeEvidence.excluded_trades
    : [];
  const evidenceSummary = tradeEvidence?.summary;

  const trustState = integrityOk
    ? normalizeText(verifiedResult.status) === "locked"
      ? "High-trust finalized record"
      : "Trusted verification record"
    : normalizeText(verifiedResult.integrity) === "compromised"
      ? "Integrity review required"
      : "Pre-final verification state";

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
            <div className="text-sm text-slate-500">Trading Truth Layer · Public Verification Surface</div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Verified Claim Record</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Canonical verification route for a lifecycle-governed trading claim, including
              integrity state, fingerprints, lifecycle history, and optional evidence inspection.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              href={publicViewUrl}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Open Public View
            </Link>

            <CopyButton value={verificationUrl} label="Copy Verify Link" />

            <button
              type="button"
              onClick={() => void handleShare()}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Share
            </button>
          </div>
        </div>

        {shareMessage ? (
          <div className="mb-6 text-sm text-slate-500">{shareMessage}</div>
        ) : null}

        <div className="mb-8">
          <ClaimVerificationSignature
            status={verifiedResult.status}
            integrityStatus={verifiedResult.integrity}
            claimHash={verifiedResult.claim_hash}
            tradeSetHash={verifiedResult.stored_trade_set_hash || verifiedResult.recomputed_trade_set_hash || ""}
            verifiedAt={verifiedResult.verified_at}
            lockedAt={verifiedResult.locked_at}
          />
        </div>

        <div className="mb-8 rounded-3xl border border-green-200 bg-green-50 p-6 shadow-sm">
          <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
            <div>
              <div className="text-sm font-medium text-green-700">Trust Summary</div>
              <h2 className="mt-2 text-3xl font-semibold text-green-950">{verifiedResult.name}</h2>

              <div className="mt-4 flex flex-wrap gap-2">
                <StatusBadge status={verifiedResult.status} />
                <IntegrityBadge integrityStatus={verifiedResult.integrity} />
                <VisibilityBadge visibility={verifiedResult.visibility || "—"} />
                <span className="inline-flex rounded-full border border-green-200 bg-white px-3 py-1 text-sm font-medium text-green-800">
                  trust state: {trustState}
                </span>
              </div>

              <div className="mt-5 rounded-2xl border border-green-200 bg-white/70 p-5">
                <div className="text-base font-semibold text-green-900">Verification Reading</div>
                <div className="mt-2 text-sm leading-7 text-green-800">
                  {integrityOk
                    ? "This route confirms that the current record matches its canonical verification state and may be used as a trusted public reference."
                    : normalizeText(verifiedResult.integrity) === "compromised"
                      ? "This route indicates an integrity mismatch between the stored and recomputed trade-set fingerprints. Review is required before reliance."
                      : "This claim is not locked yet. Verification is available, but should not be interpreted as a final locked record."}
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
                Scan this code to open the canonical verification route for this claim.
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

        <div className="mb-8 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-4xl">
              <div className="text-sm text-slate-500">Canonical Proof Identity</div>
              <h2 className="mt-2 text-3xl font-semibold">{verifiedResult.name}</h2>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Claim Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-xs break-all text-slate-700">
                    {verifiedResult.claim_hash || "—"}
                  </div>
                  <div className="mt-2 text-sm text-slate-500">{shortHash(verifiedResult.claim_hash)}</div>
                  <div className="mt-3">
                    <CopyButton value={verifiedResult.claim_hash} label="Copy Claim Hash" />
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Stored Trade Set Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-xs break-all text-slate-700">
                    {verifiedResult.stored_trade_set_hash || "—"}
                  </div>
                  <div className="mt-2 text-sm text-slate-500">{shortHash(verifiedResult.stored_trade_set_hash)}</div>
                  <div className="mt-3">
                    <CopyButton value={verifiedResult.stored_trade_set_hash} label="Copy Stored Hash" />
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Recomputed Trade Set Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-xs break-all text-slate-700">
                    {verifiedResult.recomputed_trade_set_hash || "—"}
                  </div>
                  <div className="mt-2 text-sm text-slate-500">{shortHash(verifiedResult.recomputed_trade_set_hash)}</div>
                  <div className="mt-3">
                    <CopyButton value={verifiedResult.recomputed_trade_set_hash} label="Copy Recomputed Hash" />
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
                  <div className="mt-2 text-sm text-slate-600">
                    {integrityOk
                      ? "Stored and recomputed trade-set fingerprints are aligned."
                      : "Stored and recomputed trade-set fingerprints are not aligned."}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Claim ID"
              value={String(verifiedResult.claim_id)}
              hint="Canonical claim record id"
            />
            <MetricCard
              label="Workspace ID"
              value={String(verifiedResult.workspace_id)}
              hint="Owning workspace"
            />
            <MetricCard
              label="Version Number"
              value={String(verifiedResult.version_number ?? "—")}
              hint="Lineage version"
            />
            <MetricCard
              label="Visibility"
              value={verifiedResult.visibility || "—"}
              hint="Public access posture"
            />
          </div>
        </div>

        <div className="mb-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Verification Scope</h2>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <DetailRow label="Period Start" value={verifiedResult.period_start || "—"} />
              <DetailRow label="Period End" value={verifiedResult.period_end || "—"} />
              <DetailRow label="Status" value={verifiedResult.status || "—"} />
              <DetailRow label="Visibility" value={verifiedResult.visibility || "—"} />
            </div>

            <div className="mt-5 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
              Scope detail, methodology notes, and public performance interpretation continue on the public claim page.
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Lifecycle & Lineage</h2>

              <div className="mt-5 grid gap-4 sm:grid-cols-2">
                <DetailRow label="Status" value={verifiedResult.status || "—"} />
                <DetailRow label="Integrity" value={verifiedResult.integrity || "—"} />
                <DetailRow label="Verified At" value={formatDateTime(verifiedResult.verified_at)} />
                <DetailRow label="Published At" value={formatDateTime(verifiedResult.published_at)} />
                <DetailRow label="Locked At" value={formatDateTime(verifiedResult.locked_at)} />
                <DetailRow label="Version Number" value={verifiedResult.version_number ?? "—"} />
                <DetailRow label="Root Claim ID" value={verifiedResult.root_claim_id ?? "—"} />
                <DetailRow label="Parent Claim ID" value={verifiedResult.parent_claim_id ?? "—"} />
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
                  <span className="font-medium text-slate-900">Stored trade-set hash:</span> fingerprint
                  persisted on the claim record when finalized.
                </div>
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Recomputed trade-set hash:</span> freshly
                  generated fingerprint from the current in-scope trade set.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Verified Trade Evidence</h2>
          <div className="mt-2 text-sm text-slate-500">
            Trade-level evidence loaded from the canonical claim record when access is available.
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
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
              subtitle="Trades included in the canonical claim scope."
              rows={includedRows}
              emptyText="No included trade rows are available for this claim."
            />

            <PublicTradeEvidenceTable
              title="Excluded Trade Rows"
              subtitle="Trades outside the final canonical claim scope, shown with exclusion reasons where available."
              rows={excludedRows}
              emptyText="No excluded trade rows are available for this claim."
              showExclusionColumns
            />
          </div>
        </div>

        <div className="text-center text-xs text-slate-400">
          Verified by Trading Truth Layer — Trust Infrastructure for Trading Claims
        </div>
      </main>
    </div>
  );
}