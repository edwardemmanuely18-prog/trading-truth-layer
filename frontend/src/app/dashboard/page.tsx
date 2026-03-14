"use client";

import { useEffect, useState } from "react";
import { api, type DashboardResponse } from "../../lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getDashboard(1);
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  if (loading) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="p-6 text-red-600">{error}</div>;
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-3xl font-bold">Workspace Dashboard</h1>

        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Workspace ID</div>
            <div className="mt-2 text-2xl font-semibold">{stats?.workspace_id ?? "—"}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Workspace Name</div>
            <div className="mt-2 text-2xl font-semibold">{stats?.workspace_name ?? "—"}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Members</div>
            <div className="mt-2 text-2xl font-semibold">{stats?.member_count ?? 0}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trades</div>
            <div className="mt-2 text-2xl font-semibold">{stats?.trade_count ?? 0}</div>
          </div>
        </div>

        <div className="mt-4 rounded-2xl border bg-white p-5 shadow-sm">
          <div className="text-sm text-slate-500">Claim Count</div>
          <div className="mt-2 text-2xl font-semibold">{stats?.claim_count ?? 0}</div>
        </div>
      </div>
    </main>
  );
}
