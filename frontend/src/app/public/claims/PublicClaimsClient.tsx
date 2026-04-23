"use client";

import { useState, useEffect } from "react";
import { api } from "../../../lib/api";

type PublicClaim = {
  id: number;
  workspace_id: number;
  net_pnl: number;
  trade_count: number;
  trust_score: number;
  rank: number;
};

export default function PublicClaimsClient({
  initialClaims,
}: {
  initialClaims: PublicClaim[];
}) {
  const [claims, setClaims] = useState<PublicClaim[]>(initialClaims);
  const [minTrust, setMinTrust] = useState<number>(0);
  const [minTrades, setMinTrades] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);

  async function loadFiltered() {
    setLoading(true);
    try {
      const data = await api.getGlobalPublicClaims(minTrust, minTrades);
      setClaims(data);
    } catch (e) {
      console.error("Filter fetch failed", e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFiltered();
  }, [minTrust, minTrades]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-10">
      <h1 className="text-3xl font-bold mb-6">
        Global Public Claims Directory
      </h1>

      {/* FILTER CONTROLS */}
      <div className="flex gap-3 mb-6">
        <input
          type="number"
          placeholder="Min Trust"
          value={minTrust}
          onChange={(e) => setMinTrust(Number(e.target.value) || 0)}
          className="border px-3 py-2 rounded-lg"
        />

        <input
          type="number"
          placeholder="Min Trades"
          value={minTrades}
          onChange={(e) => setMinTrades(Number(e.target.value) || 0)}
          className="border px-3 py-2 rounded-lg"
        />
      </div>

      {/* LOADING STATE */}
      {loading && (
        <div className="text-sm text-slate-500 mb-4">
          Loading filtered results...
        </div>
      )}

      {/* EMPTY STATE */}
      {!loading && claims.length === 0 && (
        <p className="text-slate-600">No public claims match your filters.</p>
      )}

      {/* CLAIMS LIST */}
      <div className="space-y-4">
        {claims.map((claim) => (
          <div
            key={claim.id}
            className="p-5 bg-white rounded-xl border shadow-sm"
          >
            <div className="flex justify-between items-center mb-2">
              <div className="text-lg font-bold">#{claim.rank}</div>
              <div className="text-sm text-slate-500">
                Workspace {claim.workspace_id}
              </div>
            </div>

            <div className="text-sm">
              <div>Trust Score: {claim.trust_score}</div>
              <div>Trades: {claim.trade_count}</div>
              <div>Net PnL: {claim.net_pnl}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}