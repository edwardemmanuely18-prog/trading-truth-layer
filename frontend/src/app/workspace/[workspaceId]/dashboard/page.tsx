import Link from "next/link";
import Navbar from "../../../../components/Navbar";
import { api } from "../../../../lib/api";

type PageProps = {
  params: Promise<{
    workspaceId: string;
  }>;
};

function formatNumber(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString();
}

export default async function WorkspaceDashboardPage({ params }: PageProps) {
  const resolvedParams = await params;
  const workspaceId = Number(resolvedParams.workspaceId);

  if (Number.isNaN(workspaceId)) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  const dashboard = await api.getDashboard(workspaceId);
  const claims = await api.getWorkspaceClaims(workspaceId);

  const lockedClaims = claims.filter((c) => c.verification_status === "locked").length;
  const publicClaims = claims.filter(
    (c) => c.scope?.visibility === "public" && ["published", "locked"].includes(c.verification_status)
  ).length;

  const recentClaims = [...claims].sort((a, b) => b.claim_schema_id - a.claim_schema_id).slice(0, 5);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Operations</div>
          <h1 className="mt-2 text-4xl font-bold">Workspace Dashboard</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Control center for workspace {workspaceId}, including claim activity, ledger volume,
            and quick access to creation, evidence, and verification workflows.
          </p>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-sm text-slate-500">Workspace Members</div>
            <div className="mt-2 text-3xl font-bold">{formatNumber(dashboard.member_count)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-sm text-slate-500">Total Trades</div>
            <div className="mt-2 text-3xl font-bold">{formatNumber(dashboard.trade_count)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-sm text-slate-500">Total Claims</div>
            <div className="mt-2 text-3xl font-bold">{formatNumber(dashboard.claim_count)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="text-sm text-slate-500">Locked / Public</div>
            <div className="mt-2 text-3xl font-bold">
              {lockedClaims} / {publicClaims}
            </div>
          </div>
        </div>

        <div className="mb-8 grid gap-6 lg:grid-cols-[1.3fr_1fr]">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Recent Claims</h2>

            {recentClaims.length === 0 ? (
              <div className="mt-4 text-slate-500">No claims available yet.</div>
            ) : (
              <div className="mt-4 space-y-3">
                {recentClaims.map((claim) => (
                  <div
                    key={claim.claim_schema_id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 p-4"
                  >
                    <div>
                      <div className="font-medium">{claim.name}</div>
                      <div className="mt-1 text-sm text-slate-500">
                        claim #{claim.claim_schema_id} · {claim.verification_status} ·{" "}
                        {claim.scope?.visibility || "private"}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Link
                        href={`/workspace/${workspaceId}/claim/${claim.claim_schema_id}`}
                        className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                      >
                        Open
                      </Link>

                      <Link
                        href={`/workspace/${workspaceId}/evidence?claimId=${claim.claim_schema_id}`}
                        className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                      >
                        Evidence
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-2xl font-semibold">Quick Actions</h2>

            <div className="mt-4 space-y-3">
              <Link
                href={`/workspace/${workspaceId}/schema`}
                className="block rounded-xl bg-slate-900 px-5 py-3 text-center text-sm font-semibold text-white hover:bg-slate-800"
              >
                Create Draft Claim
              </Link>

              <Link
                href={`/workspace/${workspaceId}/import`}
                className="block rounded-xl border border-slate-300 px-5 py-3 text-center text-sm font-semibold hover:bg-slate-50"
              >
                Import Trades
              </Link>

              <Link
                href={`/workspace/${workspaceId}/ledger`}
                className="block rounded-xl border border-slate-300 px-5 py-3 text-center text-sm font-semibold hover:bg-slate-50"
              >
                Open Ledger
              </Link>

              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="block rounded-xl border border-slate-300 px-5 py-3 text-center text-sm font-semibold hover:bg-slate-50"
              >
                Open Claims Registry
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
