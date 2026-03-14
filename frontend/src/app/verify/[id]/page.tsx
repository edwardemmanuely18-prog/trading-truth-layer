import Link from "next/link";
import Navbar from "../../../components/Navbar";
import DownloadEvidenceButton from "../../../components/DownloadEvidenceButton";
import PublicClaimTrustCard from "../../../components/PublicClaimTrustCard";
import EquityCurveChart from "../../../components/EquityCurveChart";
import { api, type PublicVerifyResult } from "../../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";

  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;

    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    const hours = String(date.getUTCHours()).padStart(2, "0");
    const minutes = String(date.getUTCMinutes()).padStart(2, "0");
    const seconds = String(date.getUTCSeconds()).padStart(2, "0");

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} UTC`;
  } catch {
    return value;
  }
}

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(digits);
}

function StatusBadge({ status }: { status?: string | null }) {
  const normalized = (status || "").toLowerCase();

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

function IntegrityBadge({ status }: { status: "valid" | "compromised" }) {
  const className =
    status === "valid"
      ? "bg-green-100 text-green-800 border-green-200"
      : "bg-red-100 text-red-800 border-red-200";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      integrity {status}
    </span>
  );
}

function LeaderboardTable({ claim }: { claim: PublicVerifyResult }) {
  if (claim.leaderboard.length === 0) {
    return (
      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">Leaderboard</h2>
        <div className="mt-3 text-slate-600">No leaderboard rows available.</div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <h2 className="text-xl font-semibold">Leaderboard</h2>
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
            {claim.leaderboard.map((row) => (
              <tr
                key={`${claim.claim_hash}-${row.rank}-${row.member}`}
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
  );
}

function EmbedCodePanel({
  claimHash,
  embedUrl,
}: {
  claimHash: string;
  embedUrl: string;
}) {
  const iframeCode = `<iframe
  src="${embedUrl}"
  width="560"
  height="320"
  frameborder="0"
  style="border:0; overflow:hidden;"
  title="Trading Truth Layer Verification Widget - ${claimHash}"
></iframe>`;

  const badgeUrl = `/embed/${claimHash}`;

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <h2 className="text-2xl font-semibold">Embed This Verified Claim</h2>
      <div className="mt-2 text-sm text-slate-600">
        Use this widget on websites, dashboards, profile pages, or community trust surfaces.
      </div>

      <div className="mt-5">
        <div className="text-sm text-slate-500">Embed URL</div>
        <div className="mt-2 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
          {embedUrl}
        </div>
      </div>

      <div className="mt-5">
        <div className="text-sm text-slate-500">Iframe Code</div>
        <pre className="mt-2 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
{iframeCode}
        </pre>
      </div>

      <div className="mt-5">
        <div className="text-sm text-slate-500">Direct Widget Route</div>
        <div className="mt-2 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
          <Link href={badgeUrl} className="font-medium text-slate-900 underline">
            {badgeUrl}
          </Link>
        </div>
      </div>
    </div>
  );
}

export default async function VerifyPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const claim = await api.getPublicClaimByHash(id);
  const equityCurve = await api.getClaimEquityCurve(claim.claim_schema_id);
  const embedUrl = `http://localhost:3000/embed/${claim.claim_hash}`;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-4 text-sm text-slate-500">
          Trading Truth Layer · Public Verification Surface
        </div>

        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold">{claim.name}</h1>
            <div className="mt-3 flex flex-wrap gap-2">
              <StatusBadge status={claim.verification_status} />
              <IntegrityBadge status={claim.integrity_status} />
              <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
                claim #{claim.claim_schema_id}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <DownloadEvidenceButton
              claimSchemaId={claim.claim_schema_id}
              claimHash={claim.claim_hash}
            />
          </div>
        </div>

        <div className="mb-6">
          <PublicClaimTrustCard
            name={claim.name}
            claimSchemaId={claim.claim_schema_id}
            verificationStatus={claim.verification_status}
            integrityStatus={claim.integrity_status}
            tradeCount={claim.trade_count}
            netPnl={claim.net_pnl}
            profitFactor={claim.profit_factor}
            winRate={claim.win_rate}
            periodStart={claim.scope.period_start}
            periodEnd={claim.scope.period_end}
            claimHash={claim.claim_hash}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trade Count</div>
            <div className="mt-2 text-2xl font-semibold">{claim.trade_count}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Net PnL</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(claim.net_pnl)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Profit Factor</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(claim.profit_factor, 4)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Win Rate</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(claim.win_rate, 4)}</div>
          </div>
        </div>

        <div className="mt-6">
          <EquityCurveChart title="Public Equity Curve" points={equityCurve.curve} />
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="space-y-6">
            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-2xl font-semibold">Verification Summary</h2>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Verification Status</div>
                  <div className="mt-1 text-3xl font-semibold">{claim.verification_status}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Integrity Status</div>
                  <div className="mt-1 text-3xl font-semibold">{claim.integrity_status}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Verified At</div>
                  <div className="mt-1 font-medium">{formatDateTime(claim.lifecycle.verified_at)}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Published At</div>
                  <div className="mt-1 font-medium">{formatDateTime(claim.lifecycle.published_at)}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Locked At</div>
                  <div className="mt-1 font-medium">{formatDateTime(claim.lifecycle.locked_at)}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Visibility</div>
                  <div className="mt-1 font-medium">{claim.scope.visibility || "—"}</div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-2xl font-semibold">Claim Scope</h2>

              <div className="mt-5 grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Period Start</div>
                  <div className="mt-1 font-medium">{claim.scope.period_start}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Period End</div>
                  <div className="mt-1 font-medium">{claim.scope.period_end}</div>
                </div>
              </div>

              <div className="mt-4">
                <div className="text-sm text-slate-500">Methodology Notes</div>
                <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                  {claim.scope.methodology_notes || "—"}
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Included Members</div>
                  <div className="mt-1 font-medium">
                    {claim.scope.included_members.length > 0
                      ? claim.scope.included_members.join(", ")
                      : "All in scope"}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Included Symbols</div>
                  <div className="mt-1 font-medium">
                    {claim.scope.included_symbols.length > 0
                      ? claim.scope.included_symbols.join(", ")
                      : "All in scope"}
                  </div>
                </div>
              </div>
            </div>

            <LeaderboardTable claim={claim} />

            <EmbedCodePanel claimHash={claim.claim_hash} embedUrl={embedUrl} />

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-2xl font-semibold">Evidence & Verification Links</h2>

              <div className="mt-4 flex flex-wrap gap-2">
                <Link
                  href={`/workspace/1/evidence?claimId=${claim.claim_schema_id}`}
                  className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                >
                  Open Internal Evidence View
                </Link>

                <Link
                  href={`/workspace/1/claim/${claim.claim_schema_id}`}
                  className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                >
                  Open Internal Claim View
                </Link>

                <Link
                  href={`/embed/${claim.claim_hash}`}
                  className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                >
                  Open Embed Widget
                </Link>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-2xl font-semibold">Integrity</h2>

              <div className="mt-5 space-y-4">
                <div>
                  <div className="text-sm text-slate-500">Integrity Status</div>
                  <div className="mt-1 text-2xl font-semibold">{claim.integrity_status}</div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Trade Set Hash</div>
                  <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                    {claim.trade_set_hash}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Claim Hash</div>
                  <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                    {claim.claim_hash}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-2xl font-semibold">Lineage</h2>

              <div className="mt-5 space-y-4 text-sm">
                <div>
                  <div className="text-slate-500">Root Claim ID</div>
                  <div className="mt-1 font-medium">{claim.lineage?.root_claim_id ?? "—"}</div>
                </div>

                <div>
                  <div className="text-slate-500">Parent Claim ID</div>
                  <div className="mt-1 font-medium">{claim.lineage?.parent_claim_id ?? "—"}</div>
                </div>

                <div>
                  <div className="text-slate-500">Version Number</div>
                  <div className="mt-1 font-medium">{claim.lineage?.version_number ?? "—"}</div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-2xl font-semibold">Trust Signal</h2>
              <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                This claim is publicly visible, lifecycle-governed, hash-verifiable, and
                evidence-exportable through the Trading Truth Layer verification engine.
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
