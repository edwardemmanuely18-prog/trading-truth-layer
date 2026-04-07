import Link from "next/link";
import type { ReactNode } from "react";
import Navbar from "../../components/Navbar";
import {
  api,
  computeTrustScore,
  type PublicClaimDirectoryItem,
} from "../../lib/api";

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

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function normalizeText(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function resolveExposureLevelFromClaim(claim: PublicClaimDirectoryItem): string {
  const visibility = normalizeText(claim?.scope?.visibility);
  const status = normalizeText(claim?.verification_status);

  if (visibility === "public") return "public";
  if (visibility === "unlisted") return "unlisted";
  if (status === "locked") return "external_distribution";

  return "internal";
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

function buildQrImageUrl(value: string) {
  const encoded = encodeURIComponent(value);
  return `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${encoded}`;
}

type ClaimOriginType = "independent" | "derived" | "versioned";

type ClaimNetworkContext = {
  claim_origin_type: ClaimOriginType;
  root_claim_hash: string | null;
  parent_claim_hash: string | null;
  version_depth: number;
  independence_weight: number;
  lineage_penalty: number;
  version_decay: number;
  network_score: number;
  network_context_label: string;
};

function inferClaimNetworkContext(
  claim: PublicClaimDirectoryItem,
  trustScore: number
): ClaimNetworkContext {
  const lineage = claim.lineage;
  const versionNumber = Number(lineage?.version_number ?? 1);
  const hasParent = typeof lineage?.parent_claim_id === "number" && lineage.parent_claim_id > 0;
  const hasRoot = typeof lineage?.root_claim_id === "number" && lineage.root_claim_id > 0;

  let claim_origin_type: ClaimOriginType = "independent";

  if (versionNumber > 1) {
    claim_origin_type = "versioned";
  } else if (hasParent || hasRoot) {
    claim_origin_type = "derived";
  }

  const root_claim_hash = hasRoot ? `claim#${lineage?.root_claim_id}` : null;
  const parent_claim_hash = hasParent ? `claim#${lineage?.parent_claim_id}` : null;

  const versionDepth =
    claim_origin_type === "versioned"
      ? Math.max(versionNumber - 1, 1)
      : claim_origin_type === "derived"
        ? 1
        : 0;

  const independence_weight =
    claim_origin_type === "independent"
      ? 1
      : claim_origin_type === "derived"
        ? 0.9
        : 0.94;

  const lineage_penalty =
    claim_origin_type === "independent"
      ? 1
      : claim_origin_type === "derived"
        ? 0.92
        : 0.96;

  const version_decay =
    claim_origin_type === "versioned"
      ? Math.max(0.82, 1 - versionDepth * 0.03)
      : 1;

  const networkScoreRaw =
    trustScore * independence_weight * lineage_penalty * version_decay;

  const network_score = Number(networkScoreRaw.toFixed(2));

  const network_context_label =
    claim_origin_type === "independent"
      ? "Independent"
      : claim_origin_type === "derived"
        ? "Derived"
        : "Versioned";

  return {
    claim_origin_type,
    root_claim_hash,
    parent_claim_hash,
    version_depth: versionDepth,
    independence_weight,
    lineage_penalty,
    version_decay,
    network_score,
    network_context_label,
  };
}

function NetworkOriginBadge({ type }: { type: ClaimOriginType }) {
  const className =
    type === "independent"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : type === "derived"
        ? "border-amber-200 bg-amber-50 text-amber-800"
        : "border-sky-200 bg-sky-50 text-sky-800";

  const label =
    type === "independent"
      ? "independent"
      : type === "derived"
        ? "derived"
        : "versioned";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${className}`}>
      {label}
    </span>
  );
}

function buildClaimRankRows(claims: PublicClaimDirectoryItem[]) {
  return claims.map((claim) => {
    const scope = safeScope(claim);
    const lifecycle = safeLifecycle(claim);

    // ===============================
    // Phase 10 — Dispute Awareness
    // ===============================

    // Future-ready: backend will send disputes_count
    const disputes_count = Number((claim as any)?.disputes_count ?? 0);
    const has_active_dispute = disputes_count > 0;

    // penalty model (can be tuned later)
    const dispute_penalty_factor = has_active_dispute ? 0.75 : 1;

    const base_trust_score = computeTrustScore({
      ...claim,
      verification_status: lifecycle.status,
      verified_at: lifecycle.verified_at,
      scope: {
        ...scope,
        visibility: scope.visibility,
      },
    });

    const trust_score = Number((base_trust_score * dispute_penalty_factor).toFixed(2));

    const network = inferClaimNetworkContext(claim, trust_score);

    const trust_weighted_pnl = (Number(claim.net_pnl ?? 0) * trust_score) / 100;
    const network_weighted_pnl = (Number(claim.net_pnl ?? 0) * network.network_score) / 100;

    return {
      claim_schema_id: claim.claim_schema_id,
      claim_hash: claim.claim_hash,
      has_active_dispute,
      dispute_penalty_factor,
      exposure_level: resolveExposureLevelFromClaim(claim),
      name: claim.name,
      verification_status: claim.verification_status,
      visibility: scope.visibility || "—",
      trade_count: claim.trade_count ?? 0,
      net_pnl: claim.net_pnl ?? 0,
      profit_factor: claim.profit_factor ?? 0,
      win_rate: claim.win_rate ?? 0,
      trust_score,
      trust_weighted_pnl,
      network_weighted_pnl,
      period_start: scope.period_start || "—",
      period_end: scope.period_end || "—",
      methodology_notes: scope.methodology_notes || "",
      locked_at: lifecycle.locked_at || null,
      published_at: lifecycle.published_at || null,
      verified_at: lifecycle.verified_at || null,
      short_hash: claim.claim_hash
        ? `${claim.claim_hash.slice(0, 16)}...${claim.claim_hash.slice(-10)}`
        : "—",
      ...network,
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
      return items.sort(
        (a, b) => b.win_rate - a.win_rate || b.claim_schema_id - a.claim_schema_id
      );
    case "trade_count_desc":
      return items.sort(
        (a, b) => b.trade_count - a.trade_count || b.claim_schema_id - a.claim_schema_id
      );
    case "best_trust_score":
      return items.sort(
        (a, b) => b.trust_score - a.trust_score || b.net_pnl - a.net_pnl
      );
    case "best_trust_weighted_pnl":
      return items.sort(
        (a, b) =>
          b.trust_weighted_pnl - a.trust_weighted_pnl || b.trust_score - a.trust_score
      );
    case "best_network_score":
      return items.sort(
        (a, b) => b.network_score - a.network_score || b.trust_score - a.trust_score
      );
    case "best_network_weighted_pnl":
      return items.sort(
        (a, b) =>
          b.network_weighted_pnl - a.network_weighted_pnl ||
          b.network_score - a.network_score
      );
    case "name_asc":
      return items.sort(
        (a, b) => a.name.localeCompare(b.name) || b.claim_schema_id - a.claim_schema_id
      );
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
      return items.sort(
        (a, b) => b.avg_win_rate - a.avg_win_rate || b.total_net_pnl - a.total_net_pnl
      );
    case "profit_factor_desc":
      return items.sort(
        (a, b) =>
          b.avg_profit_factor - a.avg_profit_factor || b.total_net_pnl - a.total_net_pnl
      );
    case "trade_count_desc":
      return items.sort(
        (a, b) => b.trade_count - a.trade_count || b.total_net_pnl - a.total_net_pnl
      );
    case "name_asc":
      return items.sort(
        (a, b) => a.member.localeCompare(b.member) || b.total_net_pnl - a.total_net_pnl
      );
    case "best_network_score":
    case "best_network_weighted_pnl":
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

function TrustBadge({
  status,
  verifiedAt,
  lockedAt,
}: {
  status?: string | null;
  verifiedAt?: string | null;
  lockedAt?: string | null;
}) {
  const normalized = normalizeText(status);
  const isLocked = normalized === "locked";
  const isVerified = normalized === "verified" || normalized === "published";

  if (isLocked) {
    return (
      <span className="inline-flex rounded-full border border-green-200 bg-green-100 px-3 py-1 text-xs font-semibold text-green-800">
        finalized trust
      </span>
    );
  }

  if (isVerified || verifiedAt || lockedAt) {
    return (
      <span className="inline-flex rounded-full border border-amber-200 bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
        reviewable
      </span>
    );
  }

  return (
    <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
      limited trust
    </span>
  );
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
      <div className="mt-2 text-[24px] font-bold leading-none tabular-nums text-slate-950">
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

  const rankingLabelMap: Record<string, string> = {
    net_pnl_desc: "net pnl",
    profit_factor_desc: "profit factor",
    win_rate_desc: "win rate",
    best_trust_score: "trust score",
    best_trust_weighted_pnl: "trust-weighted pnl",
    best_network_score: "network-aware trust score",
    best_network_weighted_pnl: "network-aware weighted pnl",
    trade_count_desc: "trade count",
    newest: "newest claims",
    name_asc: "name",
  };

  const rankingLabel = rankingLabelMap[sort] || sort.replace(/_/g, " ");

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
          <p className="mt-3 max-w-4xl text-slate-600">
            Public ranking surface for locked public claims, combining performance metrics,
            trust posture, and verification-ready record access for distribution across
            trading communities, investor review, and audit-oriented workflows.
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
                  <option value="best_trust_score">Best Trust Score</option>
                  <option value="best_trust_weighted_pnl">Trust-Weighted PnL</option>
                  <option value="best_network_score">Best Network Score</option>
                  <option value="best_network_weighted_pnl">Network-Weighted PnL</option>
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
                  <option value="all">Public ranking set</option>
                  <option value="public">Public</option>
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
              href={qs({ sort: "best_trust_score" })}
              label="Best Trust Score"
              active={sort === "best_trust_score"}
            />

            <FilterChip
              href={qs({ sort: "best_trust_weighted_pnl" })}
              label="Trust-Weighted PnL"
              active={sort === "best_trust_weighted_pnl"}
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
            <FilterChip
              href={qs({ sort: "best_network_score" })}
              label="Best Network Score"
              active={sort === "best_network_score"}
            />

            <FilterChip
              href={qs({ sort: "best_network_weighted_pnl" })}
              label="Network-Weighted PnL"
              active={sort === "best_network_weighted_pnl"}
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
            label="Top Ranked Signal"
            value={
              claimRows.length
                ? sort === "best_network_score"
                  ? formatNumber(claimRows[0].network_score)
                  : sort === "best_network_weighted_pnl"
                    ? formatNumber(claimRows[0].network_weighted_pnl)
                    : formatNumber(claimRows[0].net_pnl)
                : "—"
            }
            hint="Top current value for the active ranking mode"
          />
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <div className="text-sm text-slate-500">Trust Distribution Context</div>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Intended Trust Consumers</h2>

          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4 text-sm text-slate-600">
            <div className="rounded-2xl bg-slate-50 p-4">
              Trading communities and educator-led evaluation programs
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              Investors and capital allocators reviewing verifiable records
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              Prop firms and verification platforms requiring canonical proof
            </div>
            <div className="rounded-2xl bg-slate-50 p-4">
              Audit, dispute, and challenge-review workflows
            </div>
          </div>
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Claim Rankings</h2>
          <div className="mt-2 max-w-3xl text-sm text-slate-500">
            Ranked by {rankingLabel}. Only locked and public claims are included so that
            leaderboard positions remain tied to canonical public records with verification-grade distribution paths.
          </div>
          <div className="mt-2 text-xs text-slate-400">
            Claims with active disputes are automatically penalized in trust scoring and ranking.
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
                    <th className="px-3 py-3">Period</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3">Trades</th>
                    <th className="px-3 py-3">Net PnL</th>
                    <th className="px-3 py-3">Trust-Weighted PnL</th>
                    <th className="px-3 py-3">Network PnL</th>
                    <th className="px-3 py-3">Profit Factor</th>
                    <th className="px-3 py-3">Win Rate</th>
                    <th className="px-3 py-3">Trust</th>
                    <th className="px-3 py-3">Score</th>
                    <th className="px-3 py-3">Network</th>
                    <th className="px-3 py-3">Network Score</th>
                    <th className="px-3 py-3">Locked At</th>
                    <th className="px-3 py-3">Exposure</th>
                    <th className="px-3 py-3">Distribution</th>
                    <th className="px-3 py-3">Verification</th>
                  </tr>
                </thead>
                <tbody>
                  {claimRows.map((row, index) => {
                    const trustBand = row.has_active_dispute
                      ? {
                          label: "Contested",
                          className: "border-red-300 bg-red-100 text-red-800",
                        }
                      : resolveTrustBand(row.trust_score);
                    const verificationPath = `/verify/${row.claim_hash}`;
                    const publicViewPath = `/claim/${row.claim_schema_id}/public`;
                    const qrImageUrl = buildQrImageUrl(verificationPath);

                    return (
                      <tr
                        key={`${row.claim_schema_id}-${row.claim_hash}`}
                        className="border-b last:border-0 align-top"
                      >
                        <td className="px-3 py-3 font-semibold tabular-nums">{index + 1}</td>

                        <td className="px-3 py-3">
                          <div className="font-medium text-slate-950">{row.name}</div>
                          <div className="mt-1 text-xs text-slate-500">claim #{row.claim_schema_id}</div>
                          <div className="mt-1 font-mono text-xs text-slate-500">{row.short_hash}</div>
                        </td>

                        <td className="px-3 py-3">
                          <div className="text-sm text-slate-900">
                            {row.period_start} → {row.period_end}
                          </div>
                        </td>

                        <td className="px-3 py-3">
                          <div className="flex flex-wrap gap-2">
                            <StatusBadge status={row.verification_status} />
                            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                              {row.visibility}
                            </span>
                          </div>
                        </td>

                        <td className="px-3 py-3 tabular-nums">{row.trade_count}</td>

                        <td className="px-3 py-3 font-semibold tabular-nums">
                          {formatNumber(row.net_pnl)}
                        </td>

                        <td className="px-3 py-3 font-semibold tabular-nums">
                          {formatNumber(row.trust_weighted_pnl)}
                        </td>

                        <td className="px-3 py-3 font-semibold tabular-nums">
                          {formatNumber(row.network_weighted_pnl)}
                        </td>

                        <td className="px-3 py-3 tabular-nums">
                          {formatNumber(row.profit_factor, 4)}
                        </td>

                        <td className="px-3 py-3 tabular-nums">
                          {formatPercent(row.win_rate, 2)}
                        </td>

                        <td className="px-3 py-3">
                          <div className="flex flex-col gap-2">
                            <TrustBadge
                              status={row.verification_status}
                              verifiedAt={row.verified_at}
                              lockedAt={row.locked_at}
                            />

                            {row.has_active_dispute && (
                              <span className="inline-flex rounded-full border border-red-300 bg-red-100 px-3 py-1 text-xs font-semibold text-red-800">
                                contested
                              </span>
                            )}
                          </div>
                        </td>

                        <td className="px-3 py-3 font-semibold tabular-nums">
                          <div>{row.trust_score}</div>
                          <div className="mt-1">
                            <span
                              className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${trustBand.className}`}
                            >
                              {trustBand.label}
                            </span>
                          </div>
                        </td>

                        <td className="px-3 py-3">
                          <div className="flex flex-col gap-2">
                            <NetworkOriginBadge type={row.claim_origin_type} />
                            <div className="text-[11px] leading-5 text-slate-500">
                              <div>depth: {row.version_depth}</div>
                              <div>root: {row.root_claim_hash ?? "self"}</div>
                              <div>parent: {row.parent_claim_hash ?? "none"}</div>
                            </div>
                          </div>
                        </td>

                        <td className="px-3 py-3">
                          <div className="font-semibold tabular-nums text-slate-950">
                            {formatNumber(row.network_score)}
                          </div>
                          <div className="mt-1 text-[11px] leading-5 text-slate-500">
                            <div>indep: {formatNumber(row.independence_weight, 2)}</div>
                            <div>lineage: {formatNumber(row.lineage_penalty, 2)}</div>
                            <div>decay: {formatNumber(row.version_decay, 2)}</div>
                          </div>
                        </td>

                        <td className="px-3 py-3 text-sm text-slate-700">
                          {formatDateTime(row.locked_at)}
                        </td>

                        <td className="px-3 py-3">
                          <span
                            className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
                              row.exposure_level === "public"
                                ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                                : row.exposure_level === "external_distribution"
                                  ? "border-indigo-200 bg-indigo-50 text-indigo-800"
                                  : "border-slate-200 bg-slate-100 text-slate-600"
                            }`}
                          >
                            {row.exposure_level}
                          </span>
                        </td>

                        <td className="px-3 py-3">
                          <div className="flex flex-col gap-3">
                            <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50 p-2">
                              <img
                                src={qrImageUrl}
                                alt="QR code for verification link"
                                className="mx-auto h-auto w-full max-w-[90px]"
                              />
                            </div>

                            <div className="flex flex-wrap gap-2">
                              <Link
                                href={verificationPath}
                                className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                              >
                                Verify Route
                              </Link>

                              <Link
                                href={publicViewPath}
                                className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                              >
                                Public Record
                              </Link>
                            </div>
                          </div>
                        </td>

                        <td className="px-3 py-3">
                          <div className="flex flex-col gap-2">
                            <div className="flex flex-wrap gap-2">
                              <Link
                                href={verificationPath}
                                className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                              >
                                Canonical Verify
                              </Link>

                              <Link
                                href={publicViewPath}
                                className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                              >
                                Public Record
                              </Link>
                            </div>

                            <div className="text-[11px] text-slate-400">
                              portable · api-addressable · canonical
                            </div>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
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