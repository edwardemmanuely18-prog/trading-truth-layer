"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import Navbar from "../../components/Navbar";
import ClaimVerificationSignature from "../../components/ClaimVerificationSignature";
import { api } from "../../lib/api";

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

function extractTopLeaderboardEntry(row: any) {
  const leaderboard = toArray(row?.leaderboard);
  return leaderboard.length > 0 ? leaderboard[0] : null;
}

function buildVerifyHref(row: any) {
  const claimHash = String(row?.claim_hash ?? "").trim();
  return claimHash ? `/verify/${claimHash}` : "/claims";
}

function statusTone(status: string) {
  const value = normalize(status);
  if (value === "locked") return "border-green-200 bg-green-50 text-green-800";
  if (value === "published") return "border-blue-200 bg-blue-50 text-blue-800";
  if (value === "verified") return "border-indigo-200 bg-indigo-50 text-indigo-800";
  if (value === "draft") return "border-slate-200 bg-slate-50 text-slate-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function visibilityTone(value: string) {
  const normalized = normalize(value);
  if (normalized === "public") return "border-emerald-200 bg-emerald-50 text-emerald-800";
  if (normalized === "unlisted") return "border-amber-200 bg-amber-50 text-amber-800";
  if (normalized === "private") return "border-slate-200 bg-slate-50 text-slate-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function integrityTone(value: string) {
  const normalized = normalize(value);
  if (normalized === "valid") return "border-green-200 bg-green-50 text-green-800";
  if (normalized === "compromised") return "border-red-200 bg-red-50 text-red-800";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function routeTone(value: string) {
  const normalized = normalize(value);
  if (normalized === "active") return "border-green-200 bg-green-50 text-green-800";
  if (normalized === "pending lock") return "border-amber-200 bg-amber-50 text-amber-800";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function Pill({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {children}
    </div>
  );
}

function getVerificationRouteState(row: any) {
  const status = normalize(row?.verification_status ?? row?.status);
  const visibility = normalize(row?.visibility);

  if (status === "locked" && (visibility === "public" || visibility === "unlisted")) {
    return "active";
  }
  if (status === "published" && (visibility === "public" || visibility === "unlisted")) {
    return "pending lock";
  }
  if (status === "locked") {
    return "active";
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
    if (sortBy === "oldest") {
      return Number(a?.claim_schema_id ?? a?.id ?? 0) - Number(b?.claim_schema_id ?? b?.id ?? 0);
    }
    return Number(b?.claim_schema_id ?? b?.id ?? 0) - Number(a?.claim_schema_id ?? a?.id ?? 0);
  });

  return next;
}

export default function ClaimsPageClient() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  const [searchInput, setSearchInput] = useState("");
  const [statusInput, setStatusInput] = useState("all");
  const [visibilityInput, setVisibilityInput] = useState("all");
  const [sortInput, setSortInput] = useState("newest");

  const [searchApplied, setSearchApplied] = useState("");
  const [statusApplied, setStatusApplied] = useState("all");
  const [visibilityApplied, setVisibilityApplied] = useState("all");
  const [sortApplied, setSortApplied] = useState("newest");
  const [quickFilter, setQuickFilter] = useState("newest");

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

  const summary = useMemo(() => {
    const locked = rows.filter(
      (row) => normalize(row?.verification_status ?? row?.status) === "locked",
    ).length;

    const published = rows.filter(
      (row) => normalize(row?.verification_status ?? row?.status) === "published",
    ).length;

    const tradeCount = rows.reduce((sum, row) => {
      const value = Number(row?.trade_count);
      return sum + (Number.isFinite(value) ? value : 0);
    }, 0);

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
          row?.visibility,
          row?.verification_status,
          ...(toArray(row?.included_symbols) as any[]),
        ]
          .map((value) => String(value ?? ""))
          .join(" ")
          .toLowerCase();

        return haystack.includes(q);
      });
    }

    if (statusApplied !== "all") {
      next = next.filter(
        (row) => normalize(row?.verification_status ?? row?.status) === normalize(statusApplied),
      );
    }

    if (visibilityApplied !== "all") {
      next = next.filter((row) => normalize(row?.visibility) === normalize(visibilityApplied));
    }

    if (quickFilter === "locked only") {
      next = next.filter(
        (row) => normalize(row?.verification_status ?? row?.status) === "locked",
      );
    } else if (quickFilter === "public only") {
      next = next.filter((row) => normalize(row?.visibility) === "public");
    }

    const effectiveSort =
      quickFilter === "best net pnl"
        ? "best_net_pnl"
        : quickFilter === "best profit factor"
          ? "best_profit_factor"
          : quickFilter === "best win rate"
            ? "best_win_rate"
            : sortApplied;

    return sortRows(next, effectiveSort);
  }, [rows, searchApplied, statusApplied, visibilityApplied, sortApplied, quickFilter]);

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

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={1} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="text-sm text-slate-500">Trading Truth Layer · Public Claim Directory</div>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
            Verified Claims
          </h1>
          <p className="mt-4 max-w-5xl text-base leading-7 text-slate-600">
            Public registry of lifecycle-governed, hash-verifiable trading claims that are
            published or locked and eligible for external credibility, verification, and evidence
            review.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Public claims</div>
              <div className="mt-2 text-2xl font-semibold text-slate-950">{summary.total}</div>
              <div className="mt-2 text-sm text-slate-500">Claims shown in this public directory</div>
            </div>

            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Locked</div>
              <div className="mt-2 text-2xl font-semibold text-slate-950">{summary.locked}</div>
              <div className="mt-2 text-sm text-slate-500">
                Finalized claims with locked trade-set state
              </div>
            </div>

            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">Published</div>
              <div className="mt-2 text-2xl font-semibold text-slate-950">{summary.published}</div>
              <div className="mt-2 text-sm text-slate-500">
                Externally visible but not yet locked
              </div>
            </div>

            <div className="rounded-3xl bg-slate-50 p-5">
              <div className="text-sm text-slate-500">In-scope trades</div>
              <div className="mt-2 text-2xl font-semibold text-slate-950">
                {summary.tradeCount}
              </div>
              <div className="mt-2 text-sm text-slate-500">
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
              const leaderboard = toArray(row?.leaderboard);
              const topEntry = extractTopLeaderboardEntry(row);
              const routeState = getVerificationRouteState(row);
              const verifyHref = buildVerifyHref(row);

              return (
                <section
                  key={String(row?.claim_schema_id ?? row?.id ?? row?.claim_hash)}
                  className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="max-w-5xl">
                      <div className="text-sm text-slate-500">Public Verified Claim</div>
                      <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
                        {safeString(row?.name, "Unnamed Claim")}
                      </h2>

                      <div className="mt-4 flex flex-wrap gap-2">
                        <Pill className={statusTone(String(row?.verification_status ?? row?.status))}>
                          {safeString(row?.verification_status ?? row?.status, "unknown")}
                        </Pill>
                        <Pill className={visibilityTone(String(row?.visibility))}>
                          visibility: {safeString(row?.visibility, "unknown")}
                        </Pill>
                        <Pill className={routeTone(routeState)}>
                          verification route {routeState}
                        </Pill>
                        <Pill className="border-slate-200 bg-slate-100 text-slate-700">
                          claim #{safeString(row?.claim_schema_id ?? row?.id, "—")}
                        </Pill>
                      </div>

                      <p className="mt-4 max-w-5xl text-base leading-7 text-slate-600">
                        Public trust surface for lifecycle-governed trading performance with claim
                        fingerprinting, trade-set fingerprinting, methodology scope, and
                        verification-ready metric snapshots.
                      </p>
                    </div>

                    <Link
                      href={verifyHref}
                      className="rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
                    >
                      Open Verification Surface
                    </Link>
                  </div>

                  <div className="mt-6">
                    <ClaimVerificationSignature
                      compact
                      status={String(row?.verification_status ?? row?.status ?? "")}
                      integrityStatus={String(row?.integrity_status ?? "")}
                      claimHash={String(row?.claim_hash ?? "")}
                      tradeSetHash={String(row?.trade_set_hash ?? row?.locked_trade_set_hash ?? "")}
                      verifiedAt={String(row?.verified_at ?? "")}
                      lockedAt={String(row?.locked_at ?? "")}
                    />
                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Trade Count</div>
                      <div className="mt-2 text-2xl font-semibold text-slate-950">
                        {safeString(row?.trade_count, "0")}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">In-scope evidence rows</div>
                    </div>

                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Net PnL</div>
                      <div className="mt-2 text-2xl font-semibold text-slate-950">
                        {formatNumber(row?.net_pnl, 2)}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">Aggregate net performance</div>
                    </div>

                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Profit Factor</div>
                      <div className="mt-2 text-2xl font-semibold text-slate-950">
                        {formatNumber(row?.profit_factor, 4)}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">Gross profit ÷ gross loss</div>
                    </div>

                    <div className="rounded-3xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Win Rate</div>
                      <div className="mt-2 text-2xl font-semibold text-slate-950">
                        {formatPercent(row?.win_rate, 2)}
                      </div>
                      <div className="mt-2 text-sm text-slate-500">
                        Winning trades as percentage
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4 xl:grid-cols-[1.6fr_1fr]">
                    <div className="space-y-4">
                      <div>
                        <div className="text-sm text-slate-500">Verification Period</div>
                        <div className="mt-1 text-lg font-medium text-slate-950">
                          {safeString(row?.period_start)} → {safeString(row?.period_end)}
                        </div>
                      </div>

                      <div className="grid gap-4 md:grid-cols-2">
                        <div className="rounded-2xl bg-slate-50 p-4">
                          <div className="text-sm text-slate-500">Verified At</div>
                          <div className="mt-2 text-base text-slate-950">
                            {formatDateTime(row?.verified_at)}
                          </div>
                        </div>

                        <div className="rounded-2xl bg-slate-50 p-4">
                          <div className="text-sm text-slate-500">Locked At</div>
                          <div className="mt-2 text-base text-slate-950">
                            {formatDateTime(row?.locked_at)}
                          </div>
                        </div>
                      </div>

                      <div className="rounded-2xl bg-slate-50 p-4">
                        <div className="text-sm text-slate-500">Methodology</div>
                        <div className="mt-3 whitespace-pre-wrap text-base leading-7 text-slate-700">
                          {safeString(
                            row?.methodology_notes,
                            "No methodology notes were supplied for this public claim.",
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
                                2,
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
                            10,
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <div className="text-lg font-semibold text-slate-900">Top Leaderboard Entries</div>
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
                                <td className="px-4 py-4">{safeString(entry?.rank, String(index + 1))}</td>
                                <td className="px-4 py-4">{safeString(entry?.member, "Member")}</td>
                                <td className="px-4 py-4">{formatNumber(entry?.net_pnl, 2)}</td>
                                <td className="px-4 py-4">{formatPercent(entry?.win_rate, 2)}</td>
                                <td className="px-4 py-4">{formatNumber(entry?.profit_factor, 4)}</td>
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