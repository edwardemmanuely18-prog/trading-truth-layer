"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api, type PublicVerifyResult } from "../../../lib/api";
import ClaimVerificationSignature from "../../../components/ClaimVerificationSignature";

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

  const className =
    normalized === "valid"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "compromised"
        ? "border-red-200 bg-red-100 text-red-800"
        : "border-slate-200 bg-slate-100 text-slate-800";

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

export default function PublicVerifyClaimPage() {
  const params = useParams();

  const claimHash = useMemo(() => {
    const raw = Array.isArray(params?.claimHash) ? params.claimHash[0] : params?.claimHash;
    return String(raw || "").trim();
  }, [params]);

  const [result, setResult] = useState<PublicVerifyResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        const res = await api.getPublicClaimByHash(claimHash);
        setResult(res);
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

  const scope = result.scope ?? {
    period_start: "—",
    period_end: "—",
    included_members: [],
    included_symbols: [],
    methodology_notes: "",
    visibility: "—",
  };

  const lifecycle = result.lifecycle ?? {
    status: result.verification_status || "unknown",
    verified_at: null,
    published_at: null,
    locked_at: null,
  };

  const lineage = result.lineage ?? {
    parent_claim_id: null,
    root_claim_id: null,
    version_number: null,
  };

  const leaderboard = Array.isArray(result.leaderboard) ? result.leaderboard : [];
  const integrityOk = normalizeText(result.integrity_status) === "valid";
  const verificationUrl =
    typeof window !== "undefined" ? window.location.href : `/verify/${result.claim_hash}`;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Public Verification Surface</div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Verified Claim Record</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Public verification view for a lifecycle-governed trading claim, including integrity
              state, canonical fingerprints, scope definition, lifecycle history, and leaderboard
              snapshot.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              href="/claims"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Public Claims
            </Link>

            <Link
              href="/"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Home
            </Link>

            <CopyButton value={verificationUrl} label="Copy Verify Link" />
          </div>
        </div>

        <div className="mb-8">
          <ClaimVerificationSignature
            status={result.verification_status}
            integrityStatus={result.integrity_status}
            claimHash={result.claim_hash}
            tradeSetHash={result.trade_set_hash}
            verifiedAt={lifecycle.verified_at}
            lockedAt={lifecycle.locked_at}
          />
        </div>

        <div className="mb-8 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="max-w-4xl">
              <div className="text-sm text-slate-500">Public Claim Identity</div>
              <h2 className="mt-2 text-3xl font-semibold">{result.name}</h2>

              <div className="mt-4 flex flex-wrap gap-2">
                <StatusBadge status={result.verification_status} />
                <IntegrityBadge integrityStatus={result.integrity_status} />
                <VisibilityBadge visibility={scope.visibility || "—"} />
                <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
                  claim #{result.claim_schema_id}
                </span>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Claim Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-xs break-all text-slate-700">
                    {result.claim_hash || "—"}
                  </div>
                  <div className="mt-3">
                    <CopyButton value={result.claim_hash} label="Copy Claim Hash" />
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="text-sm text-slate-500">Trade Set Hash</div>
                  <div className="mt-2 rounded-xl bg-white p-3 font-mono text-xs break-all text-slate-700">
                    {result.trade_set_hash || "—"}
                  </div>
                  <div className="mt-3">
                    <CopyButton value={result.trade_set_hash} label="Copy Trade Set Hash" />
                  </div>
                </div>
              </div>
            </div>

            <div
              className={`rounded-2xl border px-5 py-4 ${
                integrityOk
                  ? "border-green-200 bg-green-50"
                  : "border-red-200 bg-red-50"
              }`}
            >
              <div className="text-sm text-slate-500">Public Verification</div>
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
              value={String(result.trade_count)}
              hint="In-scope trades used for this record"
            />
            <MetricCard
              label="Net PnL"
              value={formatNumber(result.net_pnl)}
              hint="Aggregate net trading result"
            />
            <MetricCard
              label="Profit Factor"
              value={formatNumber(result.profit_factor, 4)}
              hint="Gross profit ÷ gross loss"
            />
            <MetricCard
              label="Win Rate"
              value={formatPercent(result.win_rate, 2)}
              hint="Winning trades as percentage"
            />
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
                <DetailRow label="Integrity" value={result.integrity_status || "—"} />
                <DetailRow label="Verified At" value={formatDateTime(lifecycle.verified_at)} />
                <DetailRow label="Published At" value={formatDateTime(lifecycle.published_at)} />
                <DetailRow label="Locked At" value={formatDateTime(lifecycle.locked_at)} />
                <DetailRow label="Version Number" value={lineage.version_number ?? "—"} />
                <DetailRow label="Root Claim ID" value={lineage.root_claim_id ?? "—"} />
                <DetailRow label="Parent Claim ID" value={lineage.parent_claim_id ?? "—"} />
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Verification Reading</h2>
              <div className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Claim hash:</span> canonical
                  identity fingerprint for this claim definition.
                </div>
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Trade-set hash:</span> fingerprint
                  of the in-scope trade evidence used by the record.
                </div>
                <div className="rounded-xl bg-slate-50 p-4">
                  <span className="font-medium text-slate-900">Integrity valid:</span> recomputed
                  trade-set fingerprint matches the stored locked fingerprint.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-6 shadow-sm">
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
      </main>
    </div>
  );
}