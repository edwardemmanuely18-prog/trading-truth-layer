import Link from "next/link";
import Navbar from "../../../../components/Navbar";
import EquityCurveChart from "../../../../components/EquityCurveChart";
import DownloadEvidenceButton from "../../../../components/DownloadEvidenceButton";
import { api } from "../../../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";

  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
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

function IntegrityBadge({
  integrityStatus,
  hashMatch,
}: {
  integrityStatus?: string | null;
  hashMatch?: boolean;
}) {
  const ok = integrityStatus === "valid" || hashMatch === true;

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${
        ok
          ? "border-green-200 bg-green-100 text-green-800"
          : "border-red-200 bg-red-100 text-red-800"
      }`}
    >
      integrity {ok ? "valid" : "compromised"}
    </span>
  );
}

export default async function ClaimInvestorReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const claimId = Number(id);

  if (Number.isNaN(claimId)) {
    return <div className="p-6 text-red-600">Invalid claim id.</div>;
  }

  const [claim, preview, equityCurve, evidencePack] = await Promise.all([
    api.getClaimSchema(claimId),
    api.getClaimPreview(claimId),
    api.getClaimEquityCurve(claimId),
    api.getEvidencePack(claimId),
  ]);

  let integrity = null;
  try {
    integrity = await api.getClaimIntegrity(claimId);
  } catch {
    integrity = null;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] space-y-6 px-6 py-10">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Institutional Claim Report</div>
            <h1 className="mt-2 text-4xl font-bold">{claim.name}</h1>

            <div className="mt-3 flex flex-wrap gap-2">
              <StatusBadge status={claim.status} />
              <IntegrityBadge
                integrityStatus={integrity?.integrity_status}
                hashMatch={integrity?.hash_match}
              />
              <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
                claim #{claim.id}
              </span>
              <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
                visibility: {claim.visibility}
              </span>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <DownloadEvidenceButton claimSchemaId={claim.id} claimHash={claim.claim_hash} />
            <Link
              href={`/workspace/${claim.workspace_id}/claim/${claim.id}`}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold hover:bg-slate-50"
            >
              Open Internal Claim
            </Link>
            <Link
              href={`/workspace/${claim.workspace_id}/evidence?claimId=${claim.id}`}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold hover:bg-slate-50"
            >
              Open Evidence Center
            </Link>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trade Count</div>
            <div className="mt-2 text-3xl font-semibold">{preview.trade_count}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Net PnL</div>
            <div className="mt-2 text-3xl font-semibold">{formatNumber(preview.net_pnl)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Profit Factor</div>
            <div className="mt-2 text-3xl font-semibold">{formatNumber(preview.profit_factor, 4)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Win Rate</div>
            <div className="mt-2 text-3xl font-semibold">{formatNumber(preview.win_rate, 4)}</div>
          </div>
        </div>

        <div className="rounded-3xl border bg-white p-6 shadow-sm">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-2xl font-semibold">Executive Summary</h2>
              <div className="mt-1 text-sm text-slate-500">
                Verification-grade performance summary with evidence-linked integrity controls.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-right">
              <div className="text-xs uppercase tracking-wide text-slate-500">Verification Window</div>
              <div className="mt-1 text-sm font-semibold">
                {claim.period_start} → {claim.period_end}
              </div>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <div className="space-y-4">
              <div>
                <div className="text-sm text-slate-500">Methodology</div>
                <div className="mt-2 rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                  {claim.methodology_notes || "—"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Claim Hash</div>
                <div className="mt-2 break-all rounded-2xl bg-slate-50 p-4 font-mono text-xs text-slate-700">
                  {claim.claim_hash || "—"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Trade Set Hash</div>
                <div className="mt-2 break-all rounded-2xl bg-slate-50 p-4 font-mono text-xs text-slate-700">
                  {evidencePack.trade_set_hash || claim.locked_trade_set_hash || "—"}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Status</div>
                <div className="mt-1 text-2xl font-semibold">{claim.status}</div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Verified At</div>
                <div className="mt-1 font-medium">{formatDateTime(claim.verified_at)}</div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Published At</div>
                <div className="mt-1 font-medium">{formatDateTime(claim.published_at)}</div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Locked At</div>
                <div className="mt-1 font-medium">{formatDateTime(claim.locked_at)}</div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Integrity</div>
                <div className="mt-1 font-medium">
                  {integrity ? integrity.integrity_status : "not available"}
                </div>
              </div>
            </div>
          </div>
        </div>

        <EquityCurveChart title="Institutional Equity Curve" points={equityCurve.curve} />

        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Claim Scope</h2>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div>
                <div className="text-sm text-slate-500">Period Start</div>
                <div className="mt-1 font-medium">{claim.period_start}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Period End</div>
                <div className="mt-1 font-medium">{claim.period_end}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Included Members</div>
                <div className="mt-1 font-medium">
                  {claim.included_member_ids_json.length > 0
                    ? claim.included_member_ids_json.join(", ")
                    : "All in scope"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Included Symbols</div>
                <div className="mt-1 font-medium">
                  {claim.included_symbols_json.length > 0
                    ? claim.included_symbols_json.join(", ")
                    : "All in scope"}
                </div>
              </div>

              <div className="md:col-span-2">
                <div className="text-sm text-slate-500">Excluded Trade IDs</div>
                <div className="mt-1 font-medium">
                  {claim.excluded_trade_ids_json.length > 0
                    ? claim.excluded_trade_ids_json.join(", ")
                    : "None"}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Lineage</h2>

            <div className="mt-5 space-y-4 text-sm">
              <div>
                <div className="text-slate-500">Root Claim ID</div>
                <div className="mt-1 font-medium">{claim.root_claim_id ?? "—"}</div>
              </div>

              <div>
                <div className="text-slate-500">Parent Claim ID</div>
                <div className="mt-1 font-medium">{claim.parent_claim_id ?? "—"}</div>
              </div>

              <div>
                <div className="text-slate-500">Version Number</div>
                <div className="mt-1 font-medium">{claim.version_number ?? "—"}</div>
              </div>

              <div>
                <div className="text-slate-500">Workspace ID</div>
                <div className="mt-1 font-medium">{claim.workspace_id}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Leaderboard</h2>

          {preview.leaderboard.length === 0 ? (
            <div className="mt-4 text-sm text-slate-500">No leaderboard rows available.</div>
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
                  {preview.leaderboard.map((row) => (
                    <tr key={`${row.member}-${row.rank}`} className="border-b last:border-0">
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
          )}
        </div>

        <div className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Evidence & Distribution</h2>

          <div className="mt-4 flex flex-wrap gap-2">
            <DownloadEvidenceButton claimSchemaId={claim.id} claimHash={claim.claim_hash} />

            <Link
              href={`/verify/${claim.claim_hash}`}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold hover:bg-slate-50"
            >
              Open Public Verification
            </Link>

            <Link
              href={`/embed/${claim.claim_hash}`}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold hover:bg-slate-50"
            >
              Open Embed Widget
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}