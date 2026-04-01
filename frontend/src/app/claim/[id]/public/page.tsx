"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import {
  api,
  type ClaimSchema,
  type ClaimSchemaPreview,
  type ClaimIntegrityResult,
} from "../../../../lib/api";

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function shortHash(value?: string | null, head = 16, tail = 10) {
  const text = String(value || "").trim();
  if (!text) return "—";
  if (text.length <= head + tail + 3) return text;
  return `${text.slice(0, head)}...${text.slice(-tail)}`;
}

function canShowPublicSurface(status?: string | null) {
  const normalized = normalizeText(status);
  return normalized === "published" || normalized === "locked";
}

async function copyText(value: string) {
  if (typeof navigator === "undefined" || !navigator.clipboard) {
    throw new Error("Clipboard is not available in this browser.");
  }
  await navigator.clipboard.writeText(value);
}

function formatRatioPercent(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(digits)}%`;
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
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function IntegrityBadge({ integrity }: { integrity?: ClaimIntegrityResult | null }) {
  const isValid = Boolean(
    integrity &&
      integrity.hash_match &&
      normalizeText(integrity.integrity_status) === "valid"
  );

  if (!integrity) {
    return (
      <span className="inline-flex rounded-full border border-amber-200 bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-800">
        Integrity pending
      </span>
    );
  }

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-sm font-semibold ${
        isValid
          ? "border-green-200 bg-green-100 text-green-800"
          : "border-red-200 bg-red-100 text-red-800"
      }`}
    >
      {isValid ? "Integrity Verified" : "Integrity Check Failed"}
    </span>
  );
}

function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint: string;
}) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">{value}</div>
      <div className="mt-3 text-sm leading-6 text-slate-500">{hint}</div>
    </div>
  );
}

export default function PublicClaimPage() {
  const params = useParams();
  const rawId = Array.isArray(params?.id) ? params.id[0] : params?.id;
  const claimId = useMemo(() => Number(rawId), [rawId]);

  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [preview, setPreview] = useState<ClaimSchemaPreview | null>(null);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [linkMessage, setLinkMessage] = useState<string | null>(null);
  const [copying, setCopying] = useState(false);

  useEffect(() => {
    let active = true;

    async function load() {
      if (!Number.isFinite(claimId) || claimId <= 0) {
        setError("Invalid claim id.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const [claimResult, previewResult] = await Promise.all([
          api.getClaimSchema(claimId),
          api.getClaimPreview(claimId),
        ]);

        if (!active) return;

        if (!canShowPublicSurface(claimResult.status)) {
          setError("This claim is not eligible for public viewing.");
          setLoading(false);
          return;
        }

        setClaim(claimResult);
        setPreview(previewResult);

        if (normalizeText(claimResult.status) === "locked") {
          try {
            const integrityResult = await api.getClaimIntegrity(claimId);
            if (!active) return;
            setIntegrity(integrityResult);
          } catch {
            if (!active) return;
            setIntegrity(null);
          }
        } else {
          setIntegrity(null);
        }
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load public claim.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [claimId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <main className="mx-auto max-w-[1200px] px-6 py-10">
          <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
            <div className="text-xl text-slate-500">Loading public verification…</div>
          </section>
        </main>
      </div>
    );
  }

  if (error || !claim || !preview) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <main className="mx-auto max-w-[1200px] px-6 py-10">
          <section className="rounded-[32px] border border-red-200 bg-red-50 p-8 shadow-sm">
            <div className="text-base font-medium text-red-700">
              {error || "Public claim not available."}
            </div>
          </section>
        </main>
      </div>
    );
  }

  const isLocked = normalizeText(claim.status) === "locked";
  const claimHash = claim.claim_hash || preview.claim_hash || "";
  const publicPath = `/claim/${claimId}/public`;
  const verifyPath = claimHash ? `/verify/${claimHash}` : null;
  const topEntry =
    Array.isArray(preview.leaderboard) && preview.leaderboard.length > 0
      ? preview.leaderboard[0]
      : null;

  async function handleCopyLink() {
    try {
      setCopying(true);
      setLinkMessage(null);

      const origin =
        typeof window !== "undefined" && window.location?.origin
          ? window.location.origin
          : "";

      const fullUrl = origin ? `${origin}${publicPath}` : publicPath;
      await copyText(fullUrl);
      setLinkMessage("Public link copied.");
    } catch (err) {
      setLinkMessage(err instanceof Error ? err.message : "Failed to copy public link.");
    } finally {
      setCopying(false);
    }
  }

  async function handleCopyVerifyLink() {
    if (!verifyPath) return;

    try {
      setLinkMessage(null);

      const origin =
        typeof window !== "undefined" && window.location?.origin
          ? window.location.origin
          : "";

      const fullUrl = origin ? `${origin}${verifyPath}` : verifyPath;
      await copyText(fullUrl);
      setLinkMessage("Verify link copied.");
    } catch (err) {
      setLinkMessage(err instanceof Error ? err.message : "Failed to copy verify link.");
    }
  }

  async function handleCopyClaimHash() {
    if (!claimHash) return;

    try {
      setLinkMessage(null);
      await copyText(claimHash);
      setLinkMessage("Claim hash copied.");
    } catch (err) {
      setLinkMessage(err instanceof Error ? err.message : "Failed to copy claim hash.");
    }
  }

  async function handleNativeShare() {
    try {
      setLinkMessage(null);

      const origin =
        typeof window !== "undefined" && window.location?.origin
          ? window.location.origin
          : "";
      const fullUrl = origin ? `${origin}${publicPath}` : publicPath;

      if (typeof navigator !== "undefined" && "share" in navigator) {
        await navigator.share({
          title: claim?.name || "Verified Trading Claim",
          text: "View this public verified trading claim.",
          url: fullUrl,
        });
        return;
      }

      await copyText(fullUrl);
      setLinkMessage("Share not available here. Public link copied instead.");
    } catch {
      // user may cancel native share; ignore
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-[1200px] px-6 py-10">
        <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
          <div className="text-sm text-slate-500">Trading Truth Layer · Public Claim Verification</div>

          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">
            {claim.name}
          </h1>

          <div className="mt-5 flex flex-wrap gap-3">
            <StatusBadge status={claim.status} />
            <IntegrityBadge integrity={integrity} />
          </div>

          <div className="mt-5 rounded-3xl border border-green-200 bg-green-50 p-6">
            <div className="text-base font-semibold text-green-900">Trust Summary</div>

            <div className="mt-3 text-sm leading-7 text-green-800">
              This claim is publicly exposed through Trading Truth Layer. The public page presents
              performance, scope, and leaderboard context, while the verification route provides
              canonical proof, integrity validation, and claim fingerprints.
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div className="rounded-xl border border-green-200 bg-white p-3 text-sm">
                <div className="text-slate-500">Public surface</div>
                <div className="mt-1 text-slate-900">Presentation and performance view</div>
              </div>

              <div className="rounded-xl border border-green-200 bg-white p-3 text-sm">
                <div className="text-slate-500">Verification route</div>
                <div className="mt-1 text-slate-900">Canonical proof and integrity validation</div>
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void handleCopyLink()}
              disabled={copying}
              className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {copying ? "Copying..." : "Copy Public Link"}
            </button>

            {verifyPath ? (
              <>
                <button
                  type="button"
                  onClick={() => void handleCopyVerifyLink()}
                  className="rounded-2xl border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
                >
                  Copy Verify Link
                </button>

                <button
                  type="button"
                  onClick={() => {
                    if (typeof window !== "undefined") {
                      window.open(verifyPath, "_blank");
                    }
                  }}
                  className="rounded-2xl border border-slate-900 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50"
                >
                  Open Verify Route
                </button>
              </>
            ) : null}

            <button
              type="button"
              onClick={() => void handleNativeShare()}
              className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50"
            >
              Share
            </button>

            <button
              type="button"
              onClick={() => void handleCopyClaimHash()}
              disabled={!claimHash}
              className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Copy Claim Hash
            </button>
          </div>

          {linkMessage ? <div className="mt-3 text-sm text-slate-500">{linkMessage}</div> : null}

          <div className="mt-5 grid gap-3 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-xs uppercase tracking-wide text-slate-500">Public path</div>
              <div className="mt-2 break-all font-mono text-sm text-slate-800">{publicPath}</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-xs uppercase tracking-wide text-slate-500">Verify path</div>
              <div className="mt-2 break-all font-mono text-sm text-slate-800">
                {verifyPath || "—"}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 md:col-span-2">
              <div className="text-xs uppercase tracking-wide text-slate-500">Claim hash</div>
              <div className="mt-2 break-all font-mono text-sm text-slate-800">
                {claimHash || "—"}
              </div>
              <div className="mt-2 text-sm text-slate-500">{shortHash(claimHash)}</div>
            </div>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Trades"
              value={preview.trade_count ?? 0}
              hint="In-scope evidence rows"
            />
            <MetricCard
              label="Net PnL"
              value={formatNumber(preview.net_pnl, 2)}
              hint="Aggregate net performance"
            />
            <MetricCard
              label="Win Rate"
              value={formatRatioPercent(preview.win_rate, 2)}
              hint="Winning trades as percentage"
            />
            <MetricCard
              label="Profit Factor"
              value={formatNumber(preview.profit_factor, 4)}
              hint="Gross profit ÷ gross loss"
            />
          </div>

          <div className="mt-8 grid gap-4 xl:grid-cols-[1.5fr_1fr]">
            <div className="space-y-4">
              <div className="rounded-3xl border border-slate-200 bg-white p-6">
                <div className="text-xl font-semibold text-slate-950">Verification Statement</div>
                <div className="mt-3 text-base leading-8 text-slate-700">
                  This trading claim has been processed through Trading Truth Layer.
                  {isLocked
                    ? " Data integrity is cryptographically verified upon locking."
                    : " Public exposure is active and the record remains available for independent review."}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6">
                <div className="text-xl font-semibold text-slate-950">Verification Scope</div>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <div>
                    <div className="text-sm text-slate-500">Period</div>
                    <div className="mt-2 text-base font-medium text-slate-950">
                      {preview.scope?.period_start || "—"} → {preview.scope?.period_end || "—"}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-slate-500">Visibility</div>
                    <div className="mt-2 text-base font-medium capitalize text-slate-950">
                      {claim.visibility || preview.scope?.visibility || "—"}
                    </div>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="text-sm text-slate-500">Methodology</div>
                  <div className="mt-2 whitespace-pre-wrap text-base leading-7 text-slate-700">
                    {preview.scope?.methodology_notes?.trim()
                      ? preview.scope.methodology_notes
                      : "No methodology notes were supplied for this public claim."}
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-3xl border border-slate-200 bg-white p-6">
                <div className="text-sm text-slate-500">Lifecycle State</div>
                <div className="mt-2 text-2xl font-semibold capitalize text-slate-950">
                  {claim.status}
                </div>

                <div className="mt-4 space-y-3 text-sm text-slate-700">
                  <div>Verified at: {formatDateTime(claim.verified_at)}</div>
                  <div>Published at: {formatDateTime(claim.published_at)}</div>
                  <div>Locked at: {formatDateTime(claim.locked_at)}</div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6">
                <div className="text-sm text-slate-500">Top leaderboard entry</div>
                <div className="mt-2 text-base font-medium text-slate-950">
                  {topEntry
                    ? `${topEntry.member} · ${formatNumber(topEntry.net_pnl, 2)}`
                    : "No leaderboard data"}
                </div>
              </div>

              {integrity ? (
                <div className="rounded-3xl border border-slate-200 bg-white p-6">
                  <div className="text-sm text-slate-500">Integrity Posture</div>
                  <div className="mt-2 text-2xl font-semibold text-slate-950">
                    {normalizeText(integrity.integrity_status) === "valid" && integrity.hash_match
                      ? "Confirmed"
                      : "Check required"}
                  </div>

                  <div className="mt-4 space-y-3 text-sm text-slate-700">
                    <div>Hash match: {integrity.hash_match ? "true" : "false"}</div>
                    <div>Stored hash: {shortHash(integrity.stored_hash)}</div>
                    <div>Recomputed hash: {shortHash(integrity.recomputed_hash)}</div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>

          <div className="mt-8">
            <div className="text-2xl font-semibold text-slate-950">Leaderboard</div>

            {Array.isArray(preview.leaderboard) && preview.leaderboard.length > 0 ? (
              <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
                <table className="min-w-full">
                  <thead className="bg-slate-50 text-left text-sm text-slate-500">
                    <tr>
                      <th className="px-4 py-3 font-medium">Rank</th>
                      <th className="px-4 py-3 font-medium">Trader</th>
                      <th className="px-4 py-3 font-medium">PnL</th>
                      <th className="px-4 py-3 font-medium">Win Rate</th>
                      <th className="px-4 py-3 font-medium">Profit Factor</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white text-sm text-slate-900">
                    {preview.leaderboard.map((row, index) => (
                      <tr key={`${row.member}-${index}`}>
                        <td className="px-4 py-4">{row.rank}</td>
                        <td className="px-4 py-4">{row.member}</td>
                        <td className="px-4 py-4">{formatNumber(row.net_pnl, 2)}</td>
                        <td className="px-4 py-4">{formatRatioPercent(row.win_rate, 2)}</td>
                        <td className="px-4 py-4">{formatNumber(row.profit_factor, 4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                No leaderboard snapshot is available for this claim.
              </div>
            )}
          </div>

          <div className="mt-10 text-center text-xs text-slate-400">
            Verified by Trading Truth Layer — Trust Infrastructure for Trading Claims
          </div>
        </section>
      </main>
    </div>
  );
}