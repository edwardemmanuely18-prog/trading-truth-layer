import Link from "next/link";
import Navbar from "../../../../components/Navbar";
import { api, type PublicClaimDirectoryItem } from "../../../../lib/api";

type PageProps = {
  params: Promise<{
    workspaceId: string;
  }>;
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

function normalizeText(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
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
          : normalized === "draft"
            ? "bg-slate-100 text-slate-800 border-slate-200"
            : "bg-slate-100 text-slate-800 border-slate-200";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {status || "unknown"}
    </span>
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
      normalizeText(scope.period_end).includes(query);

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

function ClaimCard({
  claim,
  workspaceId,
}: {
  claim: PublicClaimDirectoryItem;
  workspaceId: number;
}) {
  const scope = safeScope(claim);
  const lifecycle = safeLifecycle(claim);
  const leaderboard = safeLeaderboard(claim);
  const isPublic = Boolean(claim.is_publicly_accessible);

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-2 text-sm text-slate-500">Workspace Claim Record</div>
          <h2 className="text-2xl font-semibold">{claim.name}</h2>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={claim.verification_status} />
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
              visibility: {scope.visibility || "—"}
            </span>
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
              claim #{claim.claim_schema_id}
            </span>
            <span
              className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${
                isPublic
                  ? "border-green-200 bg-green-50 text-green-700"
                  : "border-slate-200 bg-slate-50 text-slate-700"
              }`}
            >
              {isPublic ? "publicly accessible" : "internal only"}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {isPublic ? (
            <Link
              href={`/verify/${claim.claim_hash}`}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Public Verify
            </Link>
          ) : (
            <span className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-400">
              Public Verify Unavailable
            </span>
          )}

          <Link
            href={`/workspace/${workspaceId}/claim/${claim.claim_schema_id}`}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Internal View
          </Link>

          <Link
            href={`/workspace/${workspaceId}/evidence?claimId=${claim.claim_schema_id}`}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Evidence
          </Link>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Trade Count</div>
          <div className="mt-1 text-2xl font-semibold">{claim.trade_count ?? 0}</div>
        </div>

        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Net PnL</div>
          <div className="mt-1 text-2xl font-semibold">{formatNumber(claim.net_pnl)}</div>
        </div>

        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Profit Factor</div>
          <div className="mt-1 text-2xl font-semibold">{formatNumber(claim.profit_factor, 4)}</div>
        </div>

        <div className="rounded-xl bg-slate-50 p-4">
          <div className="text-sm text-slate-500">Win Rate</div>
          <div className="mt-1 text-2xl font-semibold">{formatNumber(claim.win_rate, 4)}</div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div>
          <div className="text-sm text-slate-500">Period</div>
          <div className="mt-1 font-medium">
            {scope.period_start || "—"} → {scope.period_end || "—"}
          </div>

          <div className="mt-4 text-sm text-slate-500">Methodology</div>
          <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
            {scope.methodology_notes || "—"}
          </div>
        </div>

        <div>
          <div className="text-sm text-slate-500">Lifecycle</div>
          <div className="mt-1 space-y-1 text-sm">
            <div>verified: {formatDateTime(lifecycle.verified_at)}</div>
            <div>published: {formatDateTime(lifecycle.published_at)}</div>
            <div>locked: {formatDateTime(lifecycle.locked_at)}</div>
          </div>

          <div className="mt-4 text-sm text-slate-500">Claim Hash</div>
          <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
            {claim.claim_hash || "—"}
          </div>

          <div className="mt-4 text-sm text-slate-500">Trade Set Hash</div>
          <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
            {claim.trade_set_hash || "—"}
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
                    <td className="px-3 py-2">{formatNumber(row.win_rate, 4)}</td>
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

export default async function WorkspaceClaimsPage({ params, searchParams }: PageProps) {
  const resolvedParams = await params;
  const workspaceId = Number(resolvedParams.workspaceId);

  if (Number.isNaN(workspaceId)) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  const resolvedSearch = (await searchParams) || {};
  const q = resolvedSearch.q || "";
  const sort = resolvedSearch.sort || "newest";
  const status = resolvedSearch.status || "all";
  const visibility = resolvedSearch.visibility || "all";

  const claims = await api.getWorkspaceClaims(workspaceId);
  const filtered = sortClaims(filterClaims(claims, q, status, visibility), sort);

  const qs = (next: { q?: string; sort?: string; status?: string; visibility?: string }) => {
    const params = new URLSearchParams({
      q: next.q ?? q,
      sort: next.sort ?? sort,
      status: next.status ?? status,
      visibility: next.visibility ?? visibility,
    });
    return `/workspace/${workspaceId}/claims?${params.toString()}`;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Registry</div>
          <h1 className="mt-2 text-4xl font-bold">Workspace Claims</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Internal registry for verification-ready claims in workspace {workspaceId}, with
            lifecycle visibility, evidence access, and public verification routing.
          </p>
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <form action={`/workspace/${workspaceId}/claims`} method="get" className="space-y-4">
            <div className="grid gap-4 lg:grid-cols-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Search</label>
                <input
                  type="text"
                  name="q"
                  defaultValue={q}
                  placeholder="Search by name, claim id, hash, notes..."
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
                  <option value="draft">Draft</option>
                  <option value="verified">Verified</option>
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
                  <option value="private">Private</option>
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
                href={`/workspace/${workspaceId}/claims?q=&sort=newest&status=all&visibility=all`}
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
              >
                Reset
              </Link>

              <div className="text-sm text-slate-500">
                Showing {filtered.length} of {claims.length} workspace claim
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
            <div className="text-slate-600">No claims match the selected filters.</div>
          </div>
        ) : (
          <div className="space-y-6">
            {filtered.map((claim) => (
              <ClaimCard key={`${claim.claim_schema_id}-${claim.claim_hash}`} claim={claim} workspaceId={workspaceId} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
