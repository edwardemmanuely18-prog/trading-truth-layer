"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import {
  api,
  type ClaimSchema,
  type ClaimSchemaPreview,
  type ClaimIntegrityResult,
} from "../../../../lib/api";

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(digits);
}

function StatusBadge({ status }: { status?: string | null }) {
  const s = (status || "").toLowerCase();

  const cls =
    s === "locked"
      ? "bg-green-100 text-green-800"
      : s === "published"
      ? "bg-blue-100 text-blue-800"
      : s === "verified"
      ? "bg-amber-100 text-amber-800"
      : "bg-slate-100 text-slate-800";

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${cls}`}>
      {status || "unknown"}
    </span>
  );
}

function IntegrityBadge({ integrity }: { integrity?: ClaimIntegrityResult | null }) {
  if (!integrity) {
    return <span className="text-slate-500 text-sm">Not verified</span>;
  }

  const ok = integrity.hash_match && integrity.integrity_status === "valid";

  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-medium ${
        ok ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
      }`}
    >
      {ok ? "Integrity Verified" : "Integrity Failed"}
    </span>
  );
}

export default function PublicClaimPage() {
  const params = useParams();
  const idParam = params?.id;
  const claimId = useMemo(() => Number(idParam), [idParam]);

  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [preview, setPreview] = useState<ClaimSchemaPreview | null>(null);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [c, p] = await Promise.all([
          api.getClaimSchema(claimId),
          api.getClaimPreview(claimId),
        ]);

        setClaim(c);
        setPreview(p);

        if (c.status === "locked") {
          try {
            const i = await api.getClaimIntegrity(claimId);
            setIntegrity(i);
          } catch {}
        }
      } finally {
        setLoading(false);
      }
    }

    if (claimId) load();
  }, [claimId]);

  if (loading) return <div className="p-10">Loading verification…</div>;

  if (!claim || !preview) {
    return <div className="p-10 text-red-600">Claim not found</div>;
  }

  return (
    <div className="max-w-5xl mx-auto p-8 space-y-8">
      {/* HEADER */}
      <div>
        <h1 className="text-3xl font-bold">{claim.name}</h1>

        <div className="mt-3 flex gap-3">
          <StatusBadge status={claim.status} />
          <IntegrityBadge integrity={integrity} />
        </div>
      </div>

      {/* METRICS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Metric label="Trades" value={preview.trade_count} />
        <Metric label="Net PnL" value={formatNumber(preview.net_pnl)} />
        <Metric label="Win Rate" value={formatNumber(preview.win_rate, 4)} />
        <Metric label="Profit Factor" value={formatNumber(preview.profit_factor, 4)} />
      </div>

      {/* VERIFICATION STATEMENT */}
      <div className="p-6 rounded-xl border bg-slate-50">
        <h2 className="font-semibold mb-2">Verification Statement</h2>
        <p className="text-sm text-slate-600">
          This trading claim has been processed through Trading Truth Layer.
          Data integrity is cryptographically verified upon locking.
        </p>
      </div>

      {/* LEADERBOARD */}
      {preview.leaderboard.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Leaderboard</h2>

          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th>Rank</th>
                <th>Trader</th>
                <th>PnL</th>
              </tr>
            </thead>
            <tbody>
              {preview.leaderboard.map((r) => (
                <tr key={r.member} className="border-b">
                  <td>{r.rank}</td>
                  <td>{r.member}</td>
                  <td>{formatNumber(r.net_pnl)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: any) {
  return (
    <div className="border rounded-xl p-4 bg-white">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="text-xl font-semibold mt-1">{value}</div>
    </div>
  );
}