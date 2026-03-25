import Link from "next/link";
import Navbar from "../../components/Navbar";
import ClaimVerificationSignature from "../../components/ClaimVerificationSignature";
import { api, type PublicClaimDirectoryItem } from "../../lib/api";

type PageProps = {
  searchParams?: Promise<{
    q?: string;
    sort?: string;
    status?: string;
    visibility?: string;
  }>;
};

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

function truncateMiddle(value?: string | null, start = 12, end = 10) {
  if (!value) return "—";
  if (value.length <= start + end + 3) return value;
  return `${value.slice(0, start)}...${value.slice(-end)}`;
}

function safeLeaderboard(claim: PublicClaimDirectoryItem) {
  return Array.isArray(claim?.leaderboard) ? claim.leaderboard : [];
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
      visibility: {visibility || "—"}
    </span>
  );
}

function ExposureBadge({ claim }: { claim: PublicClaimDirectoryItem }) {
  const isPubliclyAccessible = Boolean(claim.is_publicly_accessible);

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${
        isPubliclyAccessible
          ? "border-green-200 bg-green-50 text-green-700"
          : "border-slate-200 bg-slate-50 text-slate-700"
      }`}
    >
      {isPubliclyAccessible ? "verification route active" : "route inactive"}
    </span>
  );
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
      <div className="mt-2 text-xs text-slate-500">{hint}</div>
    </div>
  );
}

function sortClaims(claims: PublicClaimDirectoryItem[], sort: string) {
  const items = [...claims];

  switch (sort) {
    case "net_pnl_desc":
      return items.sort((a, b) => (b.net_pnl ?? 0) - (a.net_pnl ?? 0));
    case "net_pnl_asc":
      return items.sort((a, b) => (a.net_pnl ?? 0) - (b.net_pnl ?? 0));
    case "profit_factor_desc":
      return items.sort((a, b) => (b.profit_factor ?? 0) - (a.profit_factor ?? 0));
    case "win_rate_desc":
      return items.sort((a, b) => (b.win_rate ?? 0) - (a.win_rate ?? 0));
    case "name_asc":
      return items.sort((a, b) => a.name.localeCompare(b.name));
    case "oldest":
      return items.sort((a, b) => a.claim_schema_id - b.claim_schema_id);
    case "newest":
    default:
      return items.sort((a, b) => b.claim_schema_id - a.claim_schema_id);
  }
}

function filterClaims(
  claims: PublicClaimDirectoryItem[],
  q: string,
  status: string,
  visibility: string
) {
  const query = normalizeText(q);

  return claims.filter((claim) => {
    const scope = safeScope(claim);

    const matchesQuery =
      !query ||
      normalizeText(claim.name).includes(query) ||
      normalizeText(claim.claim_hash).includes(query) ||
      normalizeText(claim.claim_schema_id).includes(query) ||
      normalizeText(scope.methodology_notes).includes(query) ||
      normalizeText(scope.period_start).includes(query) ||
      normalizeText(scope.period_end).includes(query) ||
      normalizeText(scope.included_symbols.join(",")).includes(query);

    const matchesStatus =
      status === "all" || normalizeText(claim.verification_status) === normalizeText(status);

    const matchesVisibility =
      visibility === "all" || normalizeText(scope.visibility) === normalizeText(visibility);

    return matchesQuery && matchesStatus && matchesVisibility;
  });
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

function ClaimCard({ claim }: { claim: PublicClaimDirectoryItem }) {
  const scope = safeScope(claim);
  const lifecycle = safeLifecycle(claim);
  const leaderboard = safeLeaderboard(claim);

  const topMember = leaderboard[0] ?? null;
  const isLocked = normalizeText(claim.verification_status) === "locked";

  return (
    <div className="rounded-3xl border bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-4xl">
          <div className="mb-2 text-sm text-slate-500">Public Verified Claim</div>
          <h2 className="text-2xl font-semibold tracking-tight">{claim.name}</h2>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={claim.verification_status} />
            <VisibilityBadge visibility={scope.visibility || "—"} />
            <ExposureBadge claim={claim} />
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
              claim #{claim.claim_schema_id}
            </span>
          </div>

          <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600">
            Public trust surface for lifecycle-governed trading performance with claim
            fingerprinting, trade-set fingerprinting, methodology scope, and verification-ready
            metric snapshots.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link
            href={`/verify/${claim.claim_hash}`}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Open Verification Surface
          </Link>
        </div>
      </div>

      <div className="mt-6">
        <ClaimVerificationSignature
          compact
          status={claim.verification_status}
          integrityStatus={isLocked ? "valid" : "not checked"}
          claimHash={claim.claim_hash}
          tradeSetHash={claim.trade_set_hash}
          verifiedAt={lifecycle.verified_at}
          lockedAt={lifecycle.locked_at}
        />
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          label="Trade Count"
          value={String(claim.trade_count ?? 0)}
          hint="In-scope evidence rows"
        />
        <SummaryCard
          label="Net PnL"
          value={formatNumber(claim.net_pnl)}
          hint="Aggregate net performance"
        />
        <SummaryCard
          label="Profit Factor"
          value={formatNumber(claim.profit_factor, 4)}
          hint="Gross profit ÷ gross loss"
        />
        <SummaryCard
          label="Win Rate"
          value={formatPercent(claim.win_rate, 2)}
          hint="Winning trades as percentage"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <div>
          <div className="text-sm text-slate-500">Verification Period</div>
          <div className="mt-1 font-medium">
            {scope.period_start || "—"} → {scope.period_end || "—"}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-slate-50 p-3">
              <div className="text-sm text-slate-500">Verified At</div>
              <div className="mt-1 font-medium">{formatDateTime(lifecycle.verified_at)}</div>
            </div>

            <div className="rounded-xl bg-slate-50 p-3">
              <div className="text-sm text-slate-500">Locked At</div>
              <div className="mt-1 font-medium">{formatDateTime(lifecycle.locked_at)}</div>
            </div>
          </div>

          <div className="mt-4 text-sm text-slate-500">Methodology</div>
          <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm whitespace-pre-wrap text-slate-700">
            {scope.methodology_notes || "—"}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl bg-slate-50 p-3">
            <div className="text-sm text-slate-500">Top leaderboard entry</div>
            <div className="mt-1 font-medium">
              {topMember ? `${topMember.member} · ${formatNumber(topMember.net_pnl)}` : "—"}
            </div>
          </div>

          <div>
            <div className="text-sm text-slate-500">Claim Hash</div>
            <div className="mt-1 rounded-xl bg-slate-50 p-3 font-mono text-xs break-all text-slate-700">
              {claim.claim_hash || "—"}
            </div>
            <div className="mt-1 text-xs text-slate-500">{truncateMiddle(claim.claim_hash)}</div>
          </div>

          <div>
            <div className="text-sm text-slate-500">Trade Set Hash</div>
            <div className="mt-1 rounded-xl bg-slate-50 p-3 font-mono text-xs break-all text-slate-700">
              {claim.trade_set_hash || "—"}
            </div>
            <div className="mt-1 text-xs text-slate-500">
              {truncateMiddle(claim.trade_set_hash)}
            </div>
          </div>
        </div>
      </div>

      {leaderboard.length > 0 && (
        <div className="mt-6">
          <div className="mb-2 text-sm font-medium text-slate-700">Top Leaderboard Entries</div>
          <div className="overflow-x-auto">
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
                {leaderboard.slice(0, 5).map((row) => (
                  <tr
                    key={`${claim.claim_schema_id}-${row.rank}-${row.member}`}
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
        </div>
      )}
    </div>
  );
}

export default async function PublicClaimsPage({ searchParams }: PageProps) {
  const resolvedSearch = (await searchParams) || {};
  const q = resolvedSearch.q || "";
  const sort = resolvedSearch.sort || "newest";
  const status = resolvedSearch.status || "all";
  const visibility = resolvedSearch.visibility || "all";

  const claims = await api.getPublicClaims();
  const filtered = sortClaims(filterClaims(claims, q, status, visibility), sort);

  const lockedCount = claims.filter(
    (claim) => normalizeText(claim.verification_status) === "locked"
  ).length;
  const publishedCount = claims.filter(
    (claim) => normalizeText(claim.verification_status) === "published"
  ).length;
  const totalTrades = claims.reduce((sum, claim) => sum + (claim.trade_count ?? 0), 0);

  const qs = (next: { q?: string; sort?: string; status?: string; visibility?: string }) => {
    const params = new URLSearchParams({
      q: next.q ?? q,
      sort: next.sort ?? sort,
      status: next.status ?? status,
      visibility: next.visibility ?? visibility,
    });
    return `/claims?${params.toString()}`;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 rounded-3xl border bg-white p-6 shadow-sm">
          <div className="text-sm text-slate-500">Trading Truth Layer · Public Claim Directory</div>
          <h1 className="mt-2 text-4xl font-bold tracking-tight">Verified Claims</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Public registry of lifecycle-governed, hash-verifiable trading claims that are
            published or locked and eligible for external credibility, verification, and evidence
            review.
          </p>

          <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <SummaryCard
              label="Public claims"
              value={String(claims.length)}
              hint="Claims shown in this public directory"
            />
            <SummaryCard
              label="Locked"
              value={String(lockedCount)}
              hint="Finalized claims with locked trade-set state"
            />
            <SummaryCard
              label="Published"
              value={String(publishedCount)}
              hint="Externally visible but not yet locked"
            />
            <SummaryCard
              label="In-scope trades"
              value={String(totalTrades)}
              hint="Aggregate public trade evidence count"
            />
          </div>
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <form action="/claims" method="get" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Search</label>
                <input
                  type="text"
                  name="q"
                  defaultValue={q}
                  placeholder="Search by name, hash, notes, symbols..."
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
                  <option value="newest">Newest</option>
                  <option value="oldest">Oldest</option>
                  <option value="net_pnl_desc">Net PnL High → Low</option>
                  <option value="net_pnl_asc">Net PnL Low → High</option>
                  <option value="profit_factor_desc">Best Profit Factor</option>
                  <option value="win_rate_desc">Best Win Rate</option>
                  <option value="name_asc">Name A → Z</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Status</label>
                <select
                  name="status"
                  defaultValue={status}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                >
                  <option value="all">All statuses</option>
                  <option value="published">Published</option>
                  <option value="locked">Locked</option>
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
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Apply Filters
              </button>

              <Link
                href="/claims?q=&sort=newest&status=all&visibility=all"
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
              >
                Reset
              </Link>

              <div className="text-sm text-slate-500">
                Showing {filtered.length} of {claims.length} public claim
                {claims.length === 1 ? "" : "s"}.
              </div>
            </div>
          </form>

          <div className="mt-4 flex flex-wrap gap-2">
            <FilterChip href={qs({ sort: "newest" })} label="Newest" active={sort === "newest"} />
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
              href={qs({ status: "locked" })}
              label="Locked Only"
              active={status === "locked"}
            />
            <FilterChip
              href={qs({ visibility: "public" })}
              label="Public Only"
              active={visibility === "public"}
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-slate-900 font-medium">No public claims match the selected filters.</div>
            <div className="mt-2 text-slate-600">
              Try resetting filters or broadening the search terms.
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {filtered.map((claim) => (
              <ClaimCard key={`${claim.claim_schema_id}-${claim.claim_hash}`} claim={claim} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}