import Link from "next/link";
import { api } from "../../../lib/api";

export const revalidate = 60;

export default async function PublicClaimsPage() {
  let claims: any[] = [];

  try {
    // temporary: fetch from workspace 1 (you can improve later)
    claims = await api.getWorkspacePublicClaims(1);
  } catch (e) {
    console.error("Failed to load public claims", e);
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-10">
      <h1 className="text-3xl font-bold mb-6">Public Claims Directory</h1>

      {claims.length === 0 ? (
        <p className="text-slate-600">No public claims available.</p>
      ) : (
        <div className="space-y-4">
          {claims.map((claim) => (
            <div
              key={claim.claim_schema_id}
              className="p-4 bg-white rounded-xl border"
            >
              <div className="font-semibold">{claim.name}</div>
              <div className="text-sm text-slate-500">
                Net PnL: {claim.net_pnl}
              </div>

              <Link
                href={`/claim/${claim.claim_schema_id}/public`}
                className="text-blue-600 text-sm underline mt-2 inline-block"
              >
                View Claim
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}