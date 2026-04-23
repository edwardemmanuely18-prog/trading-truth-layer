"use client";

import { useState, useEffect } from "react";
import { api } from "../../../lib/api";

type Tier = "gold" | "silver" | "bronze" | "unranked";

type PublicClaim = {
  id: number;
  workspace_id: number;
  net_pnl: number;
  trade_count: number;
  trust_score: number;
  rank: number;
  tier: Tier;
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
  const [sortBy, setSortBy] = useState<"trust" | "pnl" | "trades">("trust");

  async function loadFiltered() {
    setLoading(true);
    try {
      const data = await api.getGlobalPublicClaims(
        minTrust,
        minTrades,
        sortBy
      );
      setClaims(data);
    } catch (e) {
      console.error("Filter fetch failed", e);
    } finally {
      setLoading(false);
    }
  }

  // ✅ FIXED: include sortBy
  useEffect(() => {
    loadFiltered();
  }, [minTrust, minTrades, sortBy]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-10">
      <h1 className="text-3xl font-bold mb-6">
        Global Public Claims Leaderboard
      </h1>

      {/* FILTER + SORT CONTROLS */}
      <div className="flex flex-wrap gap-3 mb-6">
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

        <select
          value={sortBy}
          onChange={(e) =>
            setSortBy(e.target.value as "trust" | "pnl" | "trades")
          }
          className="border px-3 py-2 rounded-lg"
        >
          <option value="trust">Sort by Trust</option>
          <option value="pnl">Sort by PnL</option>
          <option value="trades">Sort by Trades</option>
        </select>
      </div>

      {/* LOADING */}
      {loading && (
        <div className="text-sm text-slate-500 mb-4">
          Loading leaderboard...
        </div>
      )}

      {/* EMPTY */}
      {!loading && claims.length === 0 && (
        <p className="text-slate-600">
          No public claims match your filters.
        </p>
      )}

      {/* LIST */}
      <div className="space-y-4">
        {claims.map((claim) => {
          const tierColor =
            claim.tier === "gold"
              ? "text-yellow-500"
              : claim.tier === "silver"
              ? "text-gray-400"
              : claim.tier === "bronze"
              ? "text-orange-500"
              : "text-gray-300";

          return (
            <div
              key={claim.id}
              className="p-5 bg-white rounded-xl border shadow-sm"
            >
              <div className="flex justify-between items-center mb-2">
                <div className="text-lg font-bold">
                  #{claim.rank}
                </div>

                <div
                  className={`text-sm font-semibold ${tierColor}`}
                >
                  {claim.tier.toUpperCase()}
                </div>
              </div>

              <div className="text-sm text-slate-500 mb-2">
                Workspace {claim.workspace_id}
              </div>

              <div className="text-sm space-y-1">
                <div>Trust Score: {claim.trust_score}</div>
                <div>Trades: {claim.trade_count}</div>
                <div>Net PnL: {claim.net_pnl}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}