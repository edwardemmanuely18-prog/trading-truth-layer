import Link from "next/link";
import type { ReactNode } from "react";
import Navbar from "../../components/Navbar";
import { api, type PublicClaimDirectoryItem } from "../../lib/api";

type PageProps = {
  searchParams?: Promise<{
    q?: string;
    sort?: string;
    visibility?: string;
    minTrades?: string;
  }>;
};

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

function safeLeaderboardRows(claim: PublicClaimDirectoryItem) {
  return Array.isArray(claim?.leaderboard) ? claim.leaderboard : [];
}

function parsePositiveInt(value?: string) {
  const num = Number(value);
  if (!Number.isFinite(num) || num < 0) return 0;
  return Math.floor(num);
}

function buildClaimRankRows(claims: PublicClaimDirectoryItem[]) {
  return claims.map((claim) => {
    const scope = safeScope(claim);
    const lifecycle = safeLifecycle(claim);

    return {
      claim_schema_id: claim.claim_schema_id,
      claim_hash: claim.claim_hash,
      name: claim.name,
      verification_status: claim.verification_status,
      visibility: scope.visibility || "—",
      trade_count: claim.trade_count ?? 0,
      net_pnl: claim.net_pnl ?? 0,
      profit_factor: claim.profit_factor ?? 0,
      win_rate: claim.win_rate ?? 0,
      period_start: scope.period_start || "—",
      period_end: scope.period_end || "—",
      methodology_notes: scope.methodology_notes || "",
      locked_at: lifecycle.locked_at || null,
      published_at: lifecycle.published_at || null,
      verified_at: lifecycle.verified_at || null,
    };
  });
}

function sortClaimRows(rows: ReturnType<typeof buildClaimRankRows>, sort: string) {
  const items = [...rows];

  switch (sort) {
    case "net_pnl_desc":
      return items.sort((a, b) => b.net_pnl - a.net_pnl || b.claim_schema_id - a.claim_schema_id);
    case "profit_factor_desc":
      return items.sort(
        (a, b) => b.profit_factor - a.profit_factor || b.claim_schema_id - a.claim_schema_id
      );
    case "win_rate_desc":
      return items.sort((a, b) => b.win_rate - a.win_rate || b.claim_schema_id - a.claim_schema_id);
    case "trade_count_desc":
      return items.sort(
        (a, b) => b.trade_count - a.trade_count || b.claim_schema_id - a.claim_schema_id
      );
    case "name_asc":
      return items.sort((a, b) => a.name.localeCompare(b.name) || b.claim_schema_id - a.claim_schema_id);
    case "newest":
    default:
      return items.sort((a, b) => b.claim_schema_id - a.claim_schema_id);
  }
}

function filterClaimRows(
  rows: ReturnType<typeof buildClaimRankRows>,
  q: string,
  visibility: string,
  minTrades: number
) {
  const query = normalizeText(q);

  return rows.filter((row) => {
    const matchesQuery =
      !query ||
      normalizeText(row.name).includes(query) ||
      normalizeText(row.claim_hash).includes(query) ||
      normalizeText(row.claim_schema_id).includes(query) ||
      normalizeText(row.methodology_notes).includes(query) ||
      normalizeText(row.period_start).includes(query) ||
      normalizeText(row.period_end).includes(query);

    const matchesVisibility =
      visibility === "all" || normalizeText(row.visibility) === normalizeText(visibility);

    const matchesMinTrades = row.trade_count >= minTrades;

    return matchesQuery && matchesVisibility && matchesMinTrades;
  });
}

function buildMemberRows(claims: PublicClaimDirectoryItem[]) {
  const bucket = new Map<
    string,
    {
      member: string;
      claim_count: number;
      total_net_pnl: number;
      avg_win_rate: number;
      avg_profit_factor: number;
      trade_count: number;
      appearance_count: number;
      source_claims: { id: number; name: string; claim_hash: string }[];
    }
  >();

  for (const claim of claims) {
    const rows = safeLeaderboardRows(claim);

    for (const row of rows) {
      const key = String(row.member);
      const existing = bucket.get(key) ?? {
        member: row.member,
        claim_count: 0,
        total_net_pnl: 0,
        avg_win_rate: 0,
        avg_profit_factor: 0,
        trade_count: 0,
        appearance_count: 0,
        source_claims: [],
      };

      existing.total_net_pnl += Number(row.net_pnl ?? 0);
      existing.avg_win_rate += Number(row.win_rate ?? 0);
      existing.avg_profit_factor += Number(row.profit_factor ?? 0);
      existing.appearance_count += 1;
      existing.claim_count += 1;
      existing.trade_count += Number(claim.trade_count ?? 0);

      existing.source_claims.push({
        id: claim.claim_schema_id,
        name: claim.name,
        claim_hash: claim.claim_hash,
      });

      bucket.set(key, existing);
    }
  }

  return Array.from(bucket.values()).map((row) => ({
    ...row,
    avg_win_rate: row.appearance_count ? row.avg_win_rate / row.appearance_count : 0,
    avg_profit_factor: row.appearance_count ? row.avg_profit_factor / row.appearance_count : 0,
  }));
}

function sortMemberRows(rows: ReturnType<typeof buildMemberRows>, sort: string) {
  const items = [...rows];

  switch (sort) {
    case "win_rate_desc":
      return items.sort((a, b) => b.avg_win_rate - a.avg_win_rate || b.total_net_pnl - a.total_net_pnl);
    case "profit_factor_desc":
      return items.sort(
        (a, b) => b.avg_profit_factor - a.avg_profit_factor || b.total_net_pnl - a.total_net_pnl
      );
    case "trade_count_desc":
      return items.sort((a, b) => b.trade_count - a.trade_count || b.total_net_pnl - a.total_net_pnl);
    case "name_asc":
      return items.sort((a, b) => a.member.localeCompare(b.member) || b.total_net_pnl - a.total_net_pnl);
    case "newest":
    case "net_pnl_desc":
    default:
      return items.sort((a, b) => b.total_net_pnl - a.total_net_pnl);
  }
}

function FilterChip({
  href,
  label,
  active,
}: {
  href: string;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`inline-flex rounded-full border px-4 py-2 text-sm transition ${
        active
          ? "border-slate-900 bg-slate-900 text-white"
          : "border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100"
      }`}
    >
      {label}
    </Link>
  );
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
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function TrustBadge({ status }: { status?: string | null }) {
  const trusted = normalizeText(status) === "locked";

  return trusted ? (
    <span className="inline-flex rounded-full border border-green-200 bg-green-100 px-3 py-1 text-xs font-semibold text-green-800">
      verified
    </span>
  ) : (
    <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
      unverified
    </span>
  );
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-4xl font-semibold leading-none tracking-tight tabular-nums text-slate-950">
        {value}
      </div>
      <div className="mt-3 text-sm leading-6 text-slate-500">{hint}</div>
    </div>
  );
}

export default async function LeaderboardPage({ searchParams }: PageProps) {
  const resolvedSearch = (await searchParams) || {};
  const q = resolvedSearch.q || "";
  const sort = resolvedSearch.sort || "net_pnl_desc";
  const visibility = resolvedSearch.visibility || "all";
  const minTrades = parsePositiveInt(resolvedSearch.minTrades);

  let allClaims: PublicClaimDirectoryItem[] = [];
  let loadError: string | null = null;

  try {
    allClaims = await api.getPublicClaims();
  } catch (error) {
    loadError =
      error instanceof Error
        ? error.message
        : "Failed to load public claims for leaderboard.";
  }

  const claims = allClaims.filter((c) => {
    const lifecycle = safeLifecycle(c);
    const scope = safeScope(c);

    return (
      normalizeText(lifecycle.status) === "locked" &&
      normalizeText(scope.visibility) === "public"
    );
  });

  const claimRows = sortClaimRows(
    filterClaimRows(buildClaimRankRows(claims), q, visibility, minTrades),
    sort
  );

  const memberRows = sortMemberRows(buildMemberRows(claims), sort);

  const rankingLabel = sort
    .replace("_desc", "")
    .replace("_asc", "")
    .replace(/_/g, " ");

  const qs = (next: {
    q?: string;
    sort?: string;
    visibility?: string;
    minTrades?: string;
  }) => {
    const params = new URLSearchParams({
      q: next.q ?? q,
      sort: next.sort ?? sort,
      visibility: next.visibility ?? visibility,
      minTrades: next.minTrades ?? String(minTrades),
    });
    return `/leaderboard?${params.toString()}`;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <div className="text-sm text-slate-500">Trading Truth Layer · Public Leaderboard</div>
          <h1 className="mt-2 text-4xl font-bold">Leaderboard</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Public ranking surface for locked public claims, with sortable metrics and claim-level
            performance comparison across the trust registry.
          </p>
        </div>

        {loadError ? (
          <div className="mb-8 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {loadError}
          </div>
        ) : null}

        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <form action="/leaderboard" method="get" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Search</label>
                <input
                  type="text"
                  name="q"
                  defaultValue={q}
                  placeholder="Search by claim name, hash, notes..."
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
                  <option value="net_pnl_desc">Best Net PnL</option>
                  <option value="profit_factor_desc">Best Profit Factor</option>
                  <option value="win_rate_desc">Best Win Rate</option>
                  <option value="trade_count_desc">Most Trades</option>
                  <option value="newest">Newest Claims</option>
                  <option value="name_asc">Name A → Z</option>
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
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Minimum Trades</label>
                <input
                  type="number"
                  min="0"
                  name="minTrades"
                  defaultValue={String(minTrades)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Apply Filters
              </button>

              <Link
                href="/leaderboard?q=&sort=net_pnl_desc&visibility=all&minTrades=0"
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
              >
                Reset
              </Link>

              <div className="text-sm text-slate-500">
                Showing {claimRows.length} ranked claim{claimRows.length === 1 ? "" : "s"}.
              </div>
            </div>
          </form>

          <div className="mt-4 flex flex-wrap gap-2">
            <FilterChip
              href={qs({ sort: "net_pnl_desc" })}
              label="Best Net PnL"
              active={sort === "net_pnl_desc"}
            />
            <FilterChip
              href={qs({ sort: "profit_factor_desc" })}
              label="Best Profit Factor"
              active={sort === "profit_factor_desc"}
            />
            <FilterChip
              href={qs({ sort: "win_rate_desc" })}
              label="Best Win Rate"
              active={sort === "win_rate_desc"}
            />
            <FilterChip
              href={qs({ sort: "trade_count_desc" })}
              label="Most Trades"
              active={sort === "trade_count_desc"}
            />
            <FilterChip
              href={qs({ visibility: "public" })}
              label="Public Only"
              active={visibility === "public"}
            />
          </div>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SummaryCard
            label="Public Claims"
            value={claims.length}
            hint="Locked public claims eligible for trust ranking"
          />
          <SummaryCard
            label="Ranked Claims"
            value={claimRows.length}
            hint="Claims that match the current filter set"
          />
          <SummaryCard
            label="Distinct Members"
            value={memberRows.length}
            hint="Unique leaderboard members across public claims"
          />
          <SummaryCard
            label="Top Net PnL"
            value={claimRows.length ? formatNumber(claimRows[0].net_pnl) : "—"}
            hint="Highest claim-level net performance in the current ranking view"
          />
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Claim Rankings</h2>
          <div className="mt-2 text-sm text-slate-500">
            Ranked by {rankingLabel}. Only locked and public claims are included.
          </div>

          {claimRows.length === 0 ? (
            <div className="mt-4 text-slate-600">No claims match the selected leaderboard filters.</div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="px-3 py-3">Rank</th>
                    <th className="px-3 py-3">Claim</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3">Visibility</th>
                    <th className="px-3 py-3">Trades</th>
                    <th className="px-3 py-3">Net PnL</th>
                    <th className="px-3 py-3">Profit Factor</th>
                    <th className="px-3 py-3">Win Rate</th>
                    <th className="px-3 py-3">Trust</th>
                    <th className="px-3 py-3">Verification</th>
                  </tr>
                </thead>
                <tbody>
                  {claimRows.map((row, index) => (
                    <tr key={`${row.claim_schema_id}-${row.claim_hash}`} className="border-b last:border-0">
                      <td className="px-3 py-3 font-semibold tabular-nums">{index + 1}</td>
                      <td className="px-3 py-3">
                        <div className="font-medium">{row.name}</div>
                        <div className="mt-1 text-xs text-slate-500">claim #{row.claim_schema_id}</div>
                      </td>
                      <td className="px-3 py-3">
                        <StatusBadge status={row.verification_status} />
                      </td>
                      <td className="px-3 py-3">{row.visibility}</td>
                      <td className="px-3 py-3 tabular-nums">{row.trade_count}</td>
                      <td className="px-3 py-3 font-semibold tabular-nums">
                        {formatNumber(row.net_pnl)}
                      </td>
                      <td className="px-3 py-3 tabular-nums">
                        {formatNumber(row.profit_factor, 4)}
                      </td>
                      <td className="px-3 py-3 tabular-nums">
                        {formatPercent(row.win_rate, 2)}
                      </td>
                      <td className="px-3 py-3">
                        <TrustBadge status={row.verification_status} />
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex flex-wrap gap-2">
                          <Link
                            href={`/verify/${row.claim_hash}`}
                            className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                          >
                            Verify
                          </Link>

                          <Link
                            href={`/claim/${row.claim_schema_id}/public`}
                            className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                          >
                            View
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Member Appearances</h2>
          <div className="mt-2 text-sm text-slate-500">
            Aggregated from leaderboard rows present inside locked public claims.
          </div>

          {memberRows.length === 0 ? (
            <div className="mt-4 text-slate-600">No public member rows available.</div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="px-3 py-3">Rank</th>
                    <th className="px-3 py-3">Member</th>
                    <th className="px-3 py-3">Claim Appearances</th>
                    <th className="px-3 py-3">Total Net PnL</th>
                    <th className="px-3 py-3">Avg Win Rate</th>
                    <th className="px-3 py-3">Avg Profit Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {memberRows.map((row, index) => (
                    <tr key={`${row.member}-${index}`} className="border-b last:border-0">
                      <td className="px-3 py-3 font-semibold tabular-nums">{index + 1}</td>
                      <td className="px-3 py-3 font-medium">{row.member}</td>
                      <td className="px-3 py-3 tabular-nums">{row.claim_count}</td>
                      <td className="px-3 py-3 tabular-nums">{formatNumber(row.total_net_pnl)}</td>
                      <td className="px-3 py-3 tabular-nums">{formatPercent(row.avg_win_rate, 2)}</td>
                      <td className="px-3 py-3 tabular-nums">
                        {formatNumber(row.avg_profit_factor, 4)}
                      </td>
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