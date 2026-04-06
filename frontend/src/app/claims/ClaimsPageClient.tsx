"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Navbar from "../../components/Navbar";
import ClaimVerificationSignature from "../../components/ClaimVerificationSignature";
import { api, computeTrustScore } from "../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value: unknown, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "—";
  return num.toFixed(digits);
}

function formatPercent(value: unknown, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "—";
  return `${(num * 100).toFixed(digits)}%`;
}

function shortHash(value?: string | null, head = 12, tail = 8) {
  const text = String(value ?? "").trim();
  if (!text) return "—";
  if (text.length <= head + tail + 3) return text;
  return `${text.slice(0, head)}...${text.slice(-tail)}`;
}

function normalize(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function toArray<T = any>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function safeString(value: unknown, fallback = "—") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function safeCount(value: unknown, fallback = 0) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function extractTopLeaderboardEntry(row: any) {
  const leaderboard = toArray(row?.leaderboard);
  return leaderboard.length > 0 ? leaderboard[0] : null;
}

function resolveVisibility(row: any) {
  const primary = normalize(
    row?.visibility ??
      row?.scope?.visibility ??
      row?.claim_visibility ??
      row?.public_visibility ??
      row?.exposure_visibility
  );

  if (primary === "public" || primary === "unlisted" || primary === "private") {
    return primary;
  }

  const status = normalize(
    row?.verification_status ?? row?.status ?? row?.lifecycle?.status
  );
  const hasClaimHash = Boolean(String(row?.claim_hash ?? "").trim());

  if ((status === "locked" || status === "published") && hasClaimHash) {
    return "unlisted";
  }

  return "unknown";
}

function resolveStatus(row: any) {
  return normalize(
    row?.verification_status ?? row?.status ?? row?.lifecycle?.status
  ) || "unknown";
}

function resolvePeriodStart(row: any) {
  return row?.period_start ?? row?.scope?.period_start ?? "—";
}

function resolvePeriodEnd(row: any) {
  return row?.period_end ?? row?.scope?.period_end ?? "—";
}

function resolveVerifiedAt(row: any) {
  return row?.verified_at ?? row?.lifecycle?.verified_at ?? null;
}

function resolveLockedAt(row: any) {
  return row?.locked_at ?? row?.lifecycle?.locked_at ?? null;
}

function resolveMethodologyNotes(row: any) {
  return (
    row?.methodology_notes ??
    row?.scope?.methodology_notes ??
    "No methodology notes were supplied for this public claim."
  );
}

function buildVerifyHref(row: any) {
  const verifyPath = String(row?.verify_path ?? "").trim();
  if (verifyPath) return verifyPath;

  const claimHash = String(row?.claim_hash ?? "").trim();
  return claimHash ? `/verify/${claimHash}` : "/claims";
}

function buildPublicViewHref(row: any) {
  const publicViewPath = String(row?.public_view_path ?? "").trim();
  if (publicViewPath) return publicViewPath;

  const claimId = row?.claim_schema_id ?? row?.id;
  return claimId ? `/claim/${claimId}/public` : "/claims";
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
  return `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encoded}`;
}

function statusTone(status: string) {
  const value = normalize(status);
  if (value === "locked") return "border-green-200 bg-green-50 text-green-800";
  if (value === "published") return "border-blue-200 bg-blue-50 text-blue-800";
  if (value === "verified") return "border-amber-200 bg-amber-50 text-amber-800";
  if (value === "draft") return "border-slate-200 bg-slate-50 text-slate-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function visibilityTone(value: string) {
  const normalized = normalize(value);
  if (normalized === "public") return "border-emerald-200 bg-emerald-50 text-emerald-800";
  if (normalized === "unlisted") return "border-violet-200 bg-violet-50 text-violet-800";
  if (normalized === "private") return "border-slate-200 bg-slate-50 text-slate-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function integrityTone(value: string) {
  const normalized = normalize(value);
  if (normalized === "valid") return "border-green-200 bg-green-50 text-green-800";
  if (normalized === "compromised") return "border-red-200 bg-red-50 text-red-800";
  if (normalized === "not_checked" || normalized === "not checked" || normalized === "unknown") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function routeTone(value: string) {
  const normalized = normalize(value);
  if (normalized === "active") return "border-green-200 bg-green-50 text-green-800";
  if (normalized === "pending lock") return "border-amber-200 bg-amber-50 text-amber-800";
  if (normalized === "internal only") return "border-slate-200 bg-slate-50 text-slate-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function Pill({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {children}
    </div>
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

function getVerificationRouteState(row: any) {
  const status = resolveStatus(row);
  const visibility = resolveVisibility(row);

  if (
    (status === "locked" || status === "published") &&
    (visibility === "public" || visibility === "unlisted")
  ) {
    return status === "locked" ? "active" : "pending lock";
  }

  return "internal only";
}

function sortRows(rows: any[], sortBy: string) {
  const next = [...rows];

  next.sort((a, b) => {
    if (sortBy === "best_net_pnl") {
      return Number(b?.net_pnl ?? 0) - Number(a?.net_pnl ?? 0);
    }

    if (sortBy === "best_profit_factor") {
      return Number(b?.profit_factor ?? 0) - Number(a?.profit_factor ?? 0);
    }

    if (sortBy === "best_win_rate") {
      return Number(b?.win_rate ?? 0) - Number(a?.win_rate ?? 0);
    }

    if (sortBy === "best_trust_score") {
      const trustA = computeTrustScore({
        ...a,
        verification_status: resolveStatus(a),
        verified_at: resolveVerifiedAt(a),
        scope: {
          ...(a?.scope || {}),
          visibility: resolveVisibility(a),
        },
      });

      const trustB = computeTrustScore({
        ...b,
        verification_status: resolveStatus(b),
        verified_at: resolveVerifiedAt(b),
        scope: {
          ...(b?.scope || {}),
          visibility: resolveVisibility(b),
        },
      });

      return trustB - trustA || Number(b?.net_pnl ?? 0) - Number(a?.net_pnl ?? 0);
    }

    if (sortBy === "best_trust_weighted_pnl") {
      const trustA = computeTrustScore({
        ...a,
        verification_status: resolveStatus(a),
        verified_at: resolveVerifiedAt(a),
        scope: {
          ...(a?.scope || {}),
          visibility: resolveVisibility(a),
        },
      });

      const trustB = computeTrustScore({
        ...b,
        verification_status: resolveStatus(b),
        verified_at: resolveVerifiedAt(b),
        scope: {
          ...(b?.scope || {}),
          visibility: resolveVisibility(b),
        },
      });

      const weightedA = (Number(a?.net_pnl ?? 0) * trustA) / 100;
      const weightedB = (Number(b?.net_pnl ?? 0) * trustB) / 100;

      return weightedB - weightedA || trustB - trustA;
    }

    if (sortBy === "oldest") {
      return Number(a?.claim_schema_id ?? a?.id ?? 0) - Number(b?.claim_schema_id ?? b?.id ?? 0);
    }

    return Number(b?.claim_schema_id ?? b?.id ?? 0) - Number(a?.claim_schema_id ?? a?.id ?? 0);
  });

  return next;
}

function compareMetricTone(left: number, right: number, isLeft: boolean) {
  if (!Number.isFinite(left) || !Number.isFinite(right) || left === right) {
    return "text-slate-900";
  }
  const wins = isLeft ? left > right : right > left;
  return wins ? "text-green-700" : "text-slate-900";
}

function resolveTrustState(row: any) {
  const status = resolveStatus(row);
  const integrity = normalize(row?.integrity_status);

  if (integrity === "valid" && status === "locked") {
    return "Finalized · Cryptographically Locked";
  }

  if (integrity === "valid") {
    return "Verified · Hash Match";
  }

  if (integrity === "compromised") {
    return "Integrity Mismatch";
  }

  if (status === "locked") {
    return "Locked · Integrity assumed from canonical lifecycle";
  }

  if (status === "published") {
    return "Published · Reviewable";
  }

  return "Limited Trust";
}

function resolveTrustBand(score: number) {
  if (score >= 85) {
    return {
      label: "High Trust",
      className: "border-green-200 bg-green-100 text-green-800",
    };
  }

  if (score >= 60) {
    return {
      label: "Moderate Trust",
      className: "border-amber-200 bg-amber-100 text-amber-800",
    };
  }

  return {
    label: "Low Trust",
    className: "border-red-200 bg-red-100 text-red-800",
  };
}

function resolveLineage(row: any) {
  return {
    rootClaimId: row?.root_claim_id ?? null,
    parentClaimId: row?.parent_claim_id ?? null,
    versionNumber: row?.version_number ?? null,
  };
}

function resolveNetworkContext(row: any) {
  const hasParent = Boolean(row?.parent_claim_id);
  const hasRoot = Boolean(row?.root_claim_id);
  const version = Number(row?.version_number ?? 1);

  if (hasRoot && hasParent) {
    return "Derived · Versioned Claim";
  }

  if (hasRoot && !hasParent && version > 1) {
    return "Root · Multi-Version Claim";
  }

  if (version === 1 && !hasParent) {
    return "Independent Claim";
  }

  return "Unknown Lineage";
}

function resolveIssuer(row: any) {
  return (
    row?.issuer_name ||
    row?.workspace_name ||
    "Unknown Issuer"
  );
}

export default function ClaimsPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchInput, setSearchInput] = useState("");
  const [statusInput, setStatusInput] = useState("all");
  const [visibilityInput, setVisibilityInput] = useState("all");
  const [sortInput, setSortInput] = useState("newest");

  const [searchApplied, setSearchApplied] = useState("");
  const [statusApplied, setStatusApplied] = useState("all");
  const [visibilityApplied, setVisibilityApplied] = useState("all");
  const [sortApplied, setSortApplied] = useState("newest");
  const [quickFilter, setQuickFilter] = useState("newest");

  const [selectedCompareHashes, setSelectedCompareHashes] = useState<string[]>([]);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        setLoading(true);
        setError("");
        const result = await api.getPublicClaims();
        if (!active) return;
        setRows(Array.isArray(result) ? result : []);
      } catch (err: any) {
        if (!active) return;
        setRows([]);
        setError(err?.message || "Failed to load public claims.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const compareParam = searchParams.get("compare");
    if (!compareParam) {
      setSelectedCompareHashes([]);
      return;
    }

    const hashes = compareParam
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean)
      .slice(0, 2);

    setSelectedCompareHashes(hashes);
  }, [searchParams]);

  const summary = useMemo(() => {
    const locked = rows.filter((row) => resolveStatus(row) === "locked").length;
    const published = rows.filter((row) => resolveStatus(row) === "published").length;
    const tradeCount = rows.reduce((sum, row) => sum + safeCount(row?.trade_count, 0), 0);

    return {
      total: rows.length,
      locked,
      published,
      tradeCount,
    };
  }, [rows]);

  const filteredRows = useMemo(() => {
    let next = [...rows];
    const q = normalize(searchApplied);

    if (q) {
      next = next.filter((row) => {
        const haystack = [
          row?.name,
          row?.claim_hash,
          row?.trade_set_hash,
          row?.locked_trade_set_hash,
          row?.methodology_notes,
          row?.scope?.methodology_notes,
          row?.visibility,
          row?.scope?.visibility,
          row?.claim_visibility,
          row?.verification_status,
          row?.status,
          row?.scope?.period_start,
          row?.scope?.period_end,
          ...(toArray(row?.included_symbols) as any[]),
          ...(toArray(row?.scope?.included_symbols) as any[]),
        ]
          .map((value) => String(value ?? ""))
          .join(" ")
          .toLowerCase();

        return haystack.includes(q);
      });
    }

    if (statusApplied !== "all") {
      next = next.filter((row) => resolveStatus(row) === normalize(statusApplied));
    }

    if (visibilityApplied !== "all") {
      next = next.filter((row) => resolveVisibility(row) === normalize(visibilityApplied));
    }

    if (quickFilter === "locked only") {
      next = next.filter((row) => resolveStatus(row) === "locked");
    } else if (quickFilter === "public only") {
      next = next.filter((row) => resolveVisibility(row) === "public");
    }

    const effectiveSort =
      quickFilter === "best net pnl"
        ? "best_net_pnl"
        : quickFilter === "best profit factor"
          ? "best_profit_factor"
          : quickFilter === "best win rate"
            ? "best_win_rate"
            : quickFilter === "best trust score"
              ? "best_trust_score"
              : quickFilter === "trust weighted pnl"
                ? "best_trust_weighted_pnl"
                : sortApplied;

    return sortRows(next, effectiveSort);
  }, [rows, searchApplied, statusApplied, visibilityApplied, sortApplied, quickFilter]);

  const compareCandidates = useMemo(() => {
    if (selectedCompareHashes.length === 0) return [];
    return rows.filter((row) =>
      selectedCompareHashes.includes(String(row?.claim_hash ?? "").trim())
    );
  }, [rows, selectedCompareHashes]);

  const compareReady = compareCandidates.length === 2;

  const compareLeft = compareReady ? compareCandidates[0] : null;
  const compareRight = compareReady ? compareCandidates[1] : null;

  const compareLeftTrustScore = compareLeft
    ? computeTrustScore({
        ...compareLeft,
        verification_status: resolveStatus(compareLeft),
        verified_at: resolveVerifiedAt(compareLeft),
        scope: {
          ...(compareLeft?.scope || {}),
          visibility: resolveVisibility(compareLeft),
        },
      })
    : 0;

  const compareRightTrustScore = compareRight
    ? computeTrustScore({
        ...compareRight,
        verification_status: resolveStatus(compareRight),
        verified_at: resolveVerifiedAt(compareRight),
        scope: {
          ...(compareRight?.scope || {}),
          visibility: resolveVisibility(compareRight),
        },
      })
    : 0;

const compareLeftTrustBand = resolveTrustBand(compareLeftTrustScore);
const compareRightTrustBand = resolveTrustBand(compareRightTrustScore);

  function applyFilters() {
    setSearchApplied(searchInput);
    setStatusApplied(statusInput);
    setVisibilityApplied(visibilityInput);
    setSortApplied(sortInput);
  }

  function resetFilters() {
    setSearchInput("");
    setStatusInput("all");
    setVisibilityInput("all");
    setSortInput("newest");

    setSearchApplied("");
    setStatusApplied("all");
    setVisibilityApplied("all");
    setSortApplied("newest");
    setQuickFilter("newest");
  }

  function setQuickMode(value: string) {
    setQuickFilter(value);
  }

  function updateCompareInUrl(nextHashes: string[]) {
    const params = new URLSearchParams(searchParams.toString());

    if (nextHashes.length === 0) {
      params.delete("compare");
    } else {
      params.set("compare", nextHashes.join(","));
    }

    const query = params.toString();
    router.push(query ? `/claims?${query}` : "/claims");
  }

  function toggleCompare(hash: string) {
    const normalizedHash = String(hash || "").trim();
    if (!normalizedHash) return;

    if (selectedCompareHashes.includes(normalizedHash)) {
      updateCompareInUrl(selectedCompareHashes.filter((item) => item !== normalizedHash));
      return;
    }

    if (selectedCompareHashes.length >= 2) {
      updateCompareInUrl([selectedCompareHashes[1], normalizedHash]);
      return;
    }

    updateCompareInUrl([...selectedCompareHashes, normalizedHash]);
  }

  function clearCompare() {
    updateCompareInUrl([]);
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={1} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="text-sm text-slate-500">Trading Truth Layer · Public Claim Directory</div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-950 md:text-3xl">
            Verified Claims
          </h1>
          <p className="mt-4 max-w-5xl text-base leading-8 text-slate-700">
            Public registry of lifecycle-governed, hash-verifiable trading claims that are
            published or locked and ready for external verification, trust review, evidence
            inspection, and distribution across trading communities and institutional workflows.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Public claims</div>
              <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                {summary.total}
              </div>
              <div className="mt-3 text-sm leading-6 text-slate-500">
                Claims shown in this public directory
              </div>
            </div>

            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Locked</div>
              <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                {summary.locked}
              </div>
              <div className="mt-3 text-sm leading-6 text-slate-500">
                Finalized claims with locked trade-set state
              </div>
            </div>

            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Published</div>
              <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                {summary.published}
              </div>
              <div className="mt-3 text-sm leading-6 text-slate-500">
                Externally visible but not yet locked
              </div>
            </div>

            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">In-scope trades</div>
              <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                {summary.tradeCount}
              </div>
              <div className="mt-3 text-sm leading-6 text-slate-500">
                Aggregate public trade evidence count
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-[32px] border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 xl:grid-cols-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Search</label>
              <input
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Search by name, hash, notes, symbol"
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base outline-none ring-0 placeholder:text-slate-400"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">Sort By</label>
              <select
                value={sortInput}
                onChange={(e) => setSortInput(e.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base outline-none"
              >
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
                <option value="best_net_pnl">Best Net PnL</option>
                <option value="best_profit_factor">Best Profit Factor</option>
                <option value="best_win_rate">Best Win Rate</option>
                <option value="best_trust_score">Best Trust Score</option>
                <option value="best_trust_weighted_pnl">Trust-Weighted PnL</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">Status</label>
              <select
                value={statusInput}
                onChange={(e) => setStatusInput(e.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base outline-none"
              >
                <option value="all">All statuses</option>
                <option value="locked">Locked</option>
                <option value="published">Published</option>
                <option value="verified">Verified</option>
                <option value="draft">Draft</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-slate-700">Visibility</label>
              <select
                value={visibilityInput}
                onChange={(e) => setVisibilityInput(e.target.value)}
                className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base outline-none"
              >
                <option value="all">All visibility</option>
                <option value="public">Public</option>
                <option value="unlisted">Unlisted</option>
                <option value="private">Private</option>
              </select>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={applyFilters}
              className="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
            >
              Apply Filters
            </button>

            <button
              type="button"
              onClick={resetFilters}
              className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Reset
            </button>

            <div className="text-sm text-slate-500">
              Showing {filteredRows.length} of {rows.length} public claims.
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            {[
              { key: "newest", label: "Newest" },
              { key: "best net pnl", label: "Best Net PnL" },
              { key: "best profit factor", label: "Best Profit Factor" },
              { key: "best win rate", label: "Best Win Rate" },
              { key: "best trust score", label: "Best Trust Score" },
              { key: "trust weighted pnl", label: "Trust-Weighted PnL" },
              { key: "locked only", label: "Locked Only" },
              { key: "public only", label: "Public Only" },
            ].map((item) => {
              const active = quickFilter === item.key;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setQuickMode(item.key)}
                  className={
                    active
                      ? "rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white"
                      : "rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
                  }
                >
                  {item.label}
                </button>
              );
            })}
          </div>
        </section>

        <section className="mt-8 rounded-[32px] border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="text-sm text-slate-500">Claim Comparison</div>
              <div className="mt-1 text-lg font-semibold text-slate-950">
                Select two public claims for side-by-side comparison
              </div>
              <div className="mt-2 text-sm text-slate-600">
                Comparison uses canonical public claim records already exposed in the trust layer,
                allowing side-by-side review of verification posture, methodology, fingerprints,
                and performance credibility.
              </div>
            </div>

            <div className="mt-2 text-xs text-slate-500">
              Higher trust score indicates stronger verification confidence and integrity.
            </div>

            <div className="flex flex-wrap gap-2">
              <div className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700">
                Selected: {selectedCompareHashes.length}/2
              </div>
              <button
                type="button"
                onClick={clearCompare}
                disabled={selectedCompareHashes.length === 0}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Clear Compare
              </button>
            </div>
          </div>

          {selectedCompareHashes.length === 0 ? (
            <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
              Use the Compare button on any claim card below to begin building a side-by-side trust comparison.
            </div>
          ) : null}

          {selectedCompareHashes.length === 1 ? (
            <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              One claim selected. Choose one more to activate the comparison surface.
            </div>
          ) : null}
          </section>

          {compareReady && compareLeft && compareRight ? (
            <div className="mt-6 space-y-5">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm font-medium text-slate-500">Comparison Mode</div>
                <div className="mt-2 text-base font-semibold text-slate-950">
                  Side-by-side trust view
                </div>
                <div className="mt-2 text-sm text-slate-600">
                  Compare claim identity, lifecycle, proof fingerprints, performance metrics, and methodology in a single structured surface.
                </div>
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                {[compareLeft, compareRight].filter(Boolean).map((row) => {
                  const compareStatus = resolveStatus(row);
                  const compareIntegrity =
                    normalize(row?.integrity_status) ||
                    (compareStatus === "locked" ? "valid" : "unknown");

                  return (
                    <div
                      key={`selected-${String(row?.claim_hash ?? "")}`}
                      className="rounded-2xl border border-slate-200 bg-white p-5"
                    >
                      <div className="text-sm text-slate-500">Selected Claim</div>
                      <div className="mt-2 text-2xl font-semibold text-slate-950">
                        {safeString(row?.name, "Unnamed Claim")}
                      </div>
                      <div className="mt-2 font-mono text-xs break-all text-slate-500">
                        {safeString(row?.claim_hash, "—")}
                      </div>

                      <div className="mt-2 text-xs text-slate-500">
                        {resolveNetworkContext(row)} · Issuer: {resolveIssuer(row)}
                      </div>

                      <div className="mt-4 flex flex-wrap gap-2">
                        <Pill className={statusTone(compareStatus)}>{compareStatus}</Pill>
                        <Pill className={visibilityTone(resolveVisibility(row))}>
                          visibility: {resolveVisibility(row)}
                        </Pill>
                        <Pill className={integrityTone(compareIntegrity)}>
                          integrity: {compareIntegrity}
                        </Pill>
                      </div>

                      <div className="mt-5 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-xl bg-slate-50 p-3">
                          <div className="text-xs uppercase tracking-wide text-slate-500">
                            Verification Period
                          </div>
                          <div className="mt-1 text-sm font-medium text-slate-900">
                            {safeString(resolvePeriodStart(row))} → {safeString(resolvePeriodEnd(row))}
                          </div>
                        </div>

                        <div className="rounded-xl bg-slate-50 p-3">
                          <div className="text-xs uppercase tracking-wide text-slate-500">
                            Trade Count
                          </div>
                          <div className="mt-1 text-sm font-medium text-slate-900">
                            {safeString(row?.trade_count, "0")}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                {[compareLeft, compareRight].filter(Boolean).map((row) => {
                  const compareStatus = resolveStatus(row);
                  const compareIntegrity =
                    normalize(row?.integrity_status) ||
                    (compareStatus === "locked" ? "valid" : "unknown");

                  return (
                    <div
                      key={`signature-${String(row?.claim_hash ?? "")}`}
                      className="rounded-2xl border border-slate-200 bg-white p-4"
                    >
                      <ClaimVerificationSignature
                        compact
                        status={compareStatus}
                        integrityStatus={compareIntegrity}
                        claimHash={String(row?.claim_hash ?? "")}
                        tradeSetHash={String(row?.trade_set_hash ?? row?.locked_trade_set_hash ?? "")}
                        verifiedAt={String(resolveVerifiedAt(row) ?? "")}
                        lockedAt={String(resolveLockedAt(row) ?? "")}
                      />
                    </div>
                  );
                })}
              </div>

              <div className="overflow-x-auto rounded-2xl border border-slate-200">
                <table className="min-w-full bg-white text-sm text-slate-900">
                  <thead className="bg-slate-50 text-left text-slate-500">
                    <tr>
                      <th className="px-4 py-3 font-medium">Metric</th>
                      <th className="px-4 py-3 font-medium">{safeString(compareLeft?.name)}</th>
                      <th className="px-4 py-3 font-medium">{safeString(compareRight?.name)}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    <tr>
                      <td className="px-4 py-4 font-medium">Net PnL</td>
                      <td
                        className={`px-4 py-4 font-semibold ${compareMetricTone(
                          Number(compareLeft?.net_pnl),
                          Number(compareRight?.net_pnl),
                          true
                        )}`}
                      >
                        {formatNumber(compareLeft?.net_pnl, 2)}
                      </td>
                      <td
                        className={`px-4 py-4 font-semibold ${compareMetricTone(
                          Number(compareLeft?.net_pnl),
                          Number(compareRight?.net_pnl),
                          false
                        )}`}
                      >
                        {formatNumber(compareRight?.net_pnl, 2)}
                      </td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Win Rate</td>
                      <td
                        className={`px-4 py-4 font-semibold ${compareMetricTone(
                          Number(compareLeft?.win_rate),
                          Number(compareRight?.win_rate),
                          true
                        )}`}
                      >
                        {formatPercent(compareLeft?.win_rate, 2)}
                      </td>
                      <td
                        className={`px-4 py-4 font-semibold ${compareMetricTone(
                          Number(compareLeft?.win_rate),
                          Number(compareRight?.win_rate),
                          false
                        )}`}
                      >
                        {formatPercent(compareRight?.win_rate, 2)}
                      </td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Profit Factor</td>
                      <td
                        className={`px-4 py-4 font-semibold ${compareMetricTone(
                          Number(compareLeft?.profit_factor),
                          Number(compareRight?.profit_factor),
                          true
                        )}`}
                      >
                        {formatNumber(compareLeft?.profit_factor, 4)}
                      </td>
                      <td
                        className={`px-4 py-4 font-semibold ${compareMetricTone(
                          Number(compareLeft?.profit_factor),
                          Number(compareRight?.profit_factor),
                          false
                        )}`}
                      >
                        {formatNumber(compareRight?.profit_factor, 4)}
                      </td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Trade Count</td>
                      <td className="px-4 py-4 font-semibold">{safeString(compareLeft?.trade_count, "0")}</td>
                      <td className="px-4 py-4 font-semibold">{safeString(compareRight?.trade_count, "0")}</td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Trust State</td>
                      <td className="px-4 py-4">{resolveTrustState(compareLeft)}</td>
                      <td className="px-4 py-4">{resolveTrustState(compareRight)}</td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Trust Score</td>
                      <td className="px-4 py-4 font-semibold">
                        <div>{compareLeftTrustScore}</div>
                        <div className="mt-2">
                          <span
                            className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${compareLeftTrustBand.className}`}
                          >
                            {compareLeftTrustBand.label}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 font-semibold">
                        <div>{compareRightTrustScore}</div>
                        <div className="mt-2">
                          <span
                            className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${compareRightTrustBand.className}`}
                          >
                            {compareRightTrustBand.label}
                          </span>
                        </div>
                      </td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Status</td>
                      <td className="px-4 py-4">{resolveStatus(compareLeft)}</td>
                      <td className="px-4 py-4">{resolveStatus(compareRight)}</td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Visibility</td>
                      <td className="px-4 py-4">{resolveVisibility(compareLeft)}</td>
                      <td className="px-4 py-4">{resolveVisibility(compareRight)}</td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Verification Period</td>
                      <td className="px-4 py-4">
                        {safeString(resolvePeriodStart(compareLeft))} → {safeString(resolvePeriodEnd(compareLeft))}
                      </td>
                      <td className="px-4 py-4">
                        {safeString(resolvePeriodStart(compareRight))} → {safeString(resolvePeriodEnd(compareRight))}
                      </td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Verified At</td>
                      <td className="px-4 py-4">{formatDateTime(resolveVerifiedAt(compareLeft))}</td>
                      <td className="px-4 py-4">{formatDateTime(resolveVerifiedAt(compareRight))}</td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Locked At</td>
                      <td className="px-4 py-4">{formatDateTime(resolveLockedAt(compareLeft))}</td>
                      <td className="px-4 py-4">{formatDateTime(resolveLockedAt(compareRight))}</td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Claim Hash</td>
                      <td className="px-4 py-4 font-mono text-xs break-all">
                        {safeString(compareLeft?.claim_hash)}
                      </td>
                      <td className="px-4 py-4 font-mono text-xs break-all">
                        {safeString(compareRight?.claim_hash)}
                      </td>
                    </tr>

                    <tr>
                      <td className="px-4 py-4 font-medium">Trade Set Hash</td>
                      <td className="px-4 py-4 font-mono text-xs break-all">
                        {safeString(compareLeft?.trade_set_hash ?? compareLeft?.locked_trade_set_hash)}
                      </td>
                      <td className="px-4 py-4 font-mono text-xs break-all">
                        {safeString(compareRight?.trade_set_hash ?? compareRight?.locked_trade_set_hash)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="grid gap-4 xl:grid-cols-2">
                {[compareLeft, compareRight].filter(Boolean).map((row) => (
                  <div
                    key={`methodology-${String(row?.claim_hash ?? "")}`}
                    className="rounded-2xl border border-slate-200 bg-white p-4"
                  >
                    <div className="text-sm text-slate-500">Methodology Review</div>
                    <div className="mt-2 text-base font-semibold text-slate-950">
                      {safeString(row?.name, "Unnamed Claim")}
                    </div>
                    <div className="mt-3 whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                      {safeString(
                        resolveMethodologyNotes(row),
                        "No methodology notes were supplied for this public claim."
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          <section className="mt-8 rounded-[32px] border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trust Distribution Context</div>
            <div className="mt-2 text-xl font-semibold text-slate-950">
              Intended Trust Consumers
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4 text-sm text-slate-600">
              <div className="rounded-2xl bg-slate-50 p-4">Trading communities and educator networks</div>
              <div className="rounded-2xl bg-slate-50 p-4">Investors and capital allocators</div>
              <div className="rounded-2xl bg-slate-50 p-4">Prop firms and verification platforms</div>
              <div className="rounded-2xl bg-slate-50 p-4">Audit, challenge, and dispute workflows</div>
            </div>
          </section>

        {loading ? (
          <section className="mt-8 rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
            <div className="text-base text-slate-500">Loading public claims…</div>
          </section>
        ) : error ? (
          <section className="mt-8 rounded-[32px] border border-red-200 bg-red-50 p-8 shadow-sm">
            <div className="text-base font-medium text-red-700">{error}</div>
          </section>
        ) : filteredRows.length === 0 ? (
          <section className="mt-8 rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
            <div className="text-lg font-medium text-slate-900">
              No public claims match the selected filters.
            </div>
          </section>
        ) : (
          <div className="mt-8 space-y-6">
            {filteredRows.map((row) => {
              const trustScore = computeTrustScore({
                ...row,
                verification_status: resolveStatus(row),
                verified_at: resolveVerifiedAt(row),
                scope: {
                  ...(row?.scope || {}),
                  visibility: resolveVisibility(row),
                },
              });
              const trustBand = resolveTrustBand(trustScore);
              const leaderboard = toArray(row?.leaderboard);
              const topEntry = extractTopLeaderboardEntry(row);
              const routeState = getVerificationRouteState(row);
              const verifyHref = buildVerifyHref(row);
              const publicViewHref = buildPublicViewHref(row);
              const verificationUrl =
                typeof window !== "undefined"
                  ? `${window.location.origin}${verifyHref}`
                  : verifyHref;

              const publicViewUrl =
                typeof window !== "undefined"
                  ? `${window.location.origin}${publicViewHref}`
                  : publicViewHref;

              const qrImageUrl = buildQrImageUrl(verificationUrl);
              const resolvedVisibility = resolveVisibility(row);
              const resolvedStatus = resolveStatus(row);
              const resolvedIntegrity = (() => {
                const raw = normalize(row?.integrity_status);

                if (raw && raw !== "unknown") return raw;

                const status = resolveStatus(row);

                // If locked → assume valid (since locked claims should have passed integrity)
                if (status === "locked") return "valid";

                // If published but not locked → not yet confirmed
                if (status === "published") return "not_checked";

                return "unknown";
              })();
              const resolvedPeriodStart = resolvePeriodStart(row);
              const resolvedPeriodEnd = resolvePeriodEnd(row);
              const resolvedVerifiedAt = resolveVerifiedAt(row);
              const resolvedLockedAt = resolveLockedAt(row);
              const resolvedMethodologyNotes = resolveMethodologyNotes(row);
              const compareHash = String(row?.claim_hash ?? "").trim();
              const compareSelected = selectedCompareHashes.includes(compareHash);

              return (
                <section
                  key={String(row?.claim_schema_id ?? row?.id ?? row?.claim_hash)}
                  className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="max-w-5xl">
                      <div className="text-sm text-slate-500">Public Verified Claim</div>
                      <h2 className="mt-3 text-3xl font-bold leading-tight tracking-tight text-slate-950">
                        {safeString(row?.name, "Unnamed Claim")}
                      </h2>

                      <div className="mt-5 flex flex-wrap gap-2">
                        <Pill className={statusTone(resolvedStatus)}>{resolvedStatus}</Pill>
                        <Pill className={visibilityTone(resolvedVisibility)}>
                          visibility: {resolvedVisibility}
                        </Pill>
                        <Pill className={routeTone(routeState)}>
                          verification route {routeState}
                        </Pill>
                        <Pill className={integrityTone(resolvedIntegrity)}>
                          integrity: {resolvedIntegrity}
                        </Pill>
                        <Pill className="border-slate-200 bg-slate-100 text-slate-700">
                          claim #{safeString(row?.claim_schema_id ?? row?.id, "—")}
                        </Pill>
                      </div>

                      <p className="mt-5 max-w-5xl text-base leading-8 text-slate-700">
                        Public trust surface for lifecycle-governed trading performance with claim
                        fingerprinting, trade-set fingerprinting, methodology scope, and
                        verification-ready metric snapshots.
                      </p>
                    </div>

                    {/* Phase 8 — Trust Network Context */}
                    <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-xs uppercase tracking-wide text-slate-500">
                        Trust Network Context
                      </div>

                      <div className="mt-3 grid gap-3 md:grid-cols-3 text-sm text-slate-700">
                        <div>
                          <div className="text-slate-500">Issuer</div>
                          <div className="font-medium text-slate-900">
                            {resolveIssuer(row)}
                          </div>
                        </div>

                        <div>
                          <div className="text-slate-500">Network State</div>
                          <div className="font-medium text-slate-900">
                            {resolveNetworkContext(row)}
                          </div>
                        </div>

                        <div>
                          <div className="text-slate-500">Version</div>
                          <div className="font-medium text-slate-900">
                            {safeString(row?.version_number, "1")}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => toggleCompare(compareHash)}
                        disabled={!compareHash}
                        className={`rounded-2xl px-4 py-2 text-sm font-medium ${
                          compareSelected
                            ? "border border-blue-300 bg-blue-50 text-blue-800"
                            : "border border-slate-300 bg-white text-slate-900 hover:bg-slate-50"
                        } disabled:cursor-not-allowed disabled:opacity-50`}
                      >
                        {compareSelected ? "Selected for Compare" : "Compare"}
                      </button>

                      <Link
                        href={publicViewHref}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
                      >
                        Open Public Record
                      </Link>

                      <Link
                        href={verifyHref}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
                      >
                        Open Canonical Verification
                      </Link>

                      <CopyButton value={verificationUrl} label="Copy Verify Link" />
                      <CopyButton value={publicViewUrl} label="Copy Public Link" />
                    </div>
                  </div>

                  <div className="mt-6">
                    <ClaimVerificationSignature
                      compact
                      status={resolvedStatus}
                      integrityStatus={resolvedIntegrity}
                      claimHash={String(row?.claim_hash ?? "")}
                      tradeSetHash={String(row?.trade_set_hash ?? row?.locked_trade_set_hash ?? "")}
                      verifiedAt={String(resolveVerifiedAt(row) ?? "")}
                      lockedAt={String(resolveLockedAt(row) ?? "")}
                    />
                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Trade Count</div>
                      <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                        {safeString(row?.trade_count, "0")}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">In-scope evidence rows</div>
                    </div>

                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Net PnL</div>
                      <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                        {formatNumber(row?.net_pnl, 2)}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">Aggregate net performance</div>
                    </div>

                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Profit Factor</div>
                      <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                        {formatNumber(row?.profit_factor, 4)}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">Gross profit ÷ gross loss</div>
                    </div>

                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Win Rate</div>
                      <div className="mt-2 text-[24px] font-bold leading-none text-slate-950">
                        {formatPercent(row?.win_rate, 2)}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">
                        Winning trades as percentage
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">Trust Score</div>
                    <div className="mt-2 flex flex-wrap items-center gap-3">
                      <div className="text-[24px] font-bold leading-none text-slate-950">
                        {trustScore}
                      </div>
                      <span
                        className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${trustBand.className}`}
                      >
                        {trustBand.label}
                      </span>
                    </div>
                    <div className="mt-2 text-sm text-slate-500">
                      Composite trust score derived from lifecycle state, integrity, visibility,
                      and verification posture within the trust network.
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                      <div className="text-sm font-semibold text-slate-900">
                        Verification Distribution Surface
                      </div>

                      <div className="mt-3 text-sm leading-7 text-slate-600">
                        Use the canonical verification route for independent validation and the public record
                        route for presentation, sharing, and distribution across communities, investor review,
                        and audit-oriented workflows.
                      </div>

                      <div className="mt-4 grid gap-4 md:grid-cols-2">
                        <div className="rounded-xl border border-slate-200 bg-white p-4">
                          <div className="text-xs uppercase tracking-wide text-slate-500">Verification route</div>
                          <div className="mt-2 break-all font-mono text-xs text-slate-700">{verificationUrl}</div>
                          <div className="mt-3 flex flex-wrap gap-2">
                            <CopyButton value={verificationUrl} label="Copy Verify Link" />
                          </div>
                        </div>

                        <div className="rounded-xl border border-slate-200 bg-white p-4">
                          <div className="text-xs uppercase tracking-wide text-slate-500">Public record route</div>
                          <div className="mt-2 break-all font-mono text-xs text-slate-700">{publicViewUrl}</div>
                          <div className="mt-3 flex flex-wrap gap-2">
                            <CopyButton value={publicViewUrl} label="Copy Public Link" />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-5">
                      <div className="text-sm font-semibold text-slate-900">Scan to verify</div>
                      <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-3">
                        <img
                          src={qrImageUrl}
                          alt="QR code for verification link"
                          className="mx-auto h-auto w-full max-w-[180px]"
                        />
                      </div>
                      <div className="mt-4 text-sm leading-6 text-slate-600">
                        Scan this code to open the canonical verification route for this claim.
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4 xl:grid-cols-[1.6fr_1fr]">
                    <div className="space-y-4">
                      <div>
                        <div className="text-sm text-slate-500">Verification Period</div>
                        <div className="mt-1 text-lg font-medium text-slate-950">
                          {safeString(resolvedPeriodStart)} → {safeString(resolvedPeriodEnd)}
                        </div>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="rounded-2xl bg-slate-50 p-4">
                          <div className="text-sm text-slate-500">Verified At</div>
                          <div className="mt-2 text-base text-slate-950">
                            {formatDateTime(resolvedVerifiedAt)}
                          </div>
                        </div>

                        <div className="rounded-2xl bg-slate-50 p-4">
                          <div className="text-sm text-slate-500">Locked At</div>
                          <div className="mt-2 text-base text-slate-950">
                            {formatDateTime(resolvedLockedAt)}
                          </div>
                        </div>
                      </div>

                      <div className="rounded-2xl bg-slate-50 p-4">
                        <div className="text-sm text-slate-500">Methodology</div>
                        <div className="mt-3 whitespace-pre-wrap text-base leading-7 text-slate-700">
                          {safeString(
                            resolvedMethodologyNotes,
                            "No methodology notes were supplied for this public claim."
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="rounded-2xl bg-slate-50 p-4">
                        <div className="text-sm text-slate-500">Top leaderboard entry</div>
                        <div className="mt-2 text-base font-medium text-slate-950">
                          {topEntry
                            ? `${safeString(topEntry?.member, "Member")} · ${formatNumber(
                                topEntry?.net_pnl,
                                2
                              )}`
                            : "No leaderboard data"}
                        </div>
                      </div>

                      <div className="rounded-2xl bg-slate-50 p-4">
                        <div className="text-sm text-slate-500">Claim Hash</div>
                        <div className="mt-2 break-all font-mono text-sm text-slate-800">
                          {safeString(row?.claim_hash)}
                        </div>
                        <div className="mt-2 text-sm text-slate-500">
                          {shortHash(String(row?.claim_hash ?? ""), 16, 10)}
                        </div>
                      </div>

                      <div className="rounded-2xl bg-slate-50 p-4">
                        <div className="text-sm text-slate-500">Trade Set Hash</div>
                        <div className="mt-2 break-all font-mono text-sm text-slate-800">
                          {safeString(row?.trade_set_hash ?? row?.locked_trade_set_hash)}
                        </div>
                        <div className="mt-2 text-sm text-slate-500">
                          {shortHash(
                            String(row?.trade_set_hash ?? row?.locked_trade_set_hash ?? ""),
                            16,
                            10
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-2xl bg-slate-50 p-4">
                    <div className="text-sm text-slate-500">Lineage</div>

                    <div className="mt-2 text-sm text-slate-800">
                      Root: {safeString(row?.root_claim_id, "—")}
                    </div>

                    <div className="mt-1 text-sm text-slate-800">
                      Parent: {safeString(row?.parent_claim_id, "—")}
                    </div>

                    <div className="mt-1 text-sm text-slate-800">
                      Version: {safeString(row?.version_number, "1")}
                    </div>
                  </div>

                  <div className="mt-6">
                    <div className="text-lg font-semibold text-slate-900">
                      Top Leaderboard Entries
                    </div>
                    {leaderboard.length === 0 ? (
                      <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">
                        No leaderboard snapshot available for this claim.
                      </div>
                    ) : (
                      <div className="mt-4 overflow-x-auto rounded-2xl border border-slate-200">
                        <table className="min-w-full">
                          <thead className="bg-slate-50 text-left text-sm text-slate-500">
                            <tr>
                              <th className="px-4 py-3 font-medium">Rank</th>
                              <th className="px-4 py-3 font-medium">Member</th>
                              <th className="px-4 py-3 font-medium">Net PnL</th>
                              <th className="px-4 py-3 font-medium">Win Rate</th>
                              <th className="px-4 py-3 font-medium">Profit Factor</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-200 bg-white text-sm text-slate-900">
                            {leaderboard.map((entry: any, index: number) => (
                              <tr key={`${row?.claim_hash}-leaderboard-${index}`}>
                                <td className="px-4 py-4">
                                  {safeString(entry?.rank, String(index + 1))}
                                </td>
                                <td className="px-4 py-4">{safeString(entry?.member, "Member")}</td>
                                <td className="px-4 py-4">{formatNumber(entry?.net_pnl, 2)}</td>
                                <td className="px-4 py-4">{formatPercent(entry?.win_rate, 2)}</td>
                                <td className="px-4 py-4">
                                  {formatNumber(entry?.profit_factor, 4)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}