"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import ImportForm from "../../../../components/ImportForm";
import { useAuth } from "../../../../components/AuthProvider";
import { api, type WorkspaceUsageSummary } from "../../../../lib/api";

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

export default function WorkspaceImportPage() {
  const params = useParams();
  const { user, workspaces, loading } = useAuth();

  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [usageLoading, setUsageLoading] = useState(true);

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const workspaceRole = workspaceMembership?.workspace_role ?? null;
  const canImportTradesByRole = workspaceRole === "owner" || workspaceRole === "operator";

  const tradeUsage = usage?.usage?.trades;
  const tradeLimitReached =
    (tradeUsage?.limit ?? 0) > 0 && (tradeUsage?.used ?? 0) >= (tradeUsage?.limit ?? 0);

  const canImportTrades = canImportTradesByRole && !tradeLimitReached;

  useEffect(() => {
    if (!workspaceId) {
      setUsageLoading(false);
      return;
    }

    const resolvedWorkspaceId = workspaceId;
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(resolvedWorkspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setUsageLoading(false);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId]);

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading import page...</div>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-4xl px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace import page.
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Ledger Intake</div>
            <h1 className="mt-2 text-3xl font-bold">Trade Import</h1>
            <p className="mt-2 text-slate-600">
              Add manual trades or CSV records for workspace {workspaceId}.
            </p>
          </div>

          <div className="rounded-xl border bg-white px-4 py-3 text-sm shadow-sm">
            <div className="text-slate-500">Workspace Role</div>
            <div className="mt-1 font-semibold">{workspaceRole}</div>
          </div>
        </div>

        {usageLoading ? (
          <div className="mb-6 rounded-2xl border bg-white p-6 shadow-sm">
            Loading workspace trade usage...
          </div>
        ) : tradeUsage ? (
          <div
            className={`mb-6 rounded-2xl border p-6 shadow-sm ${
              tradeLimitReached
                ? "border-amber-200 bg-amber-50"
                : "border-slate-200 bg-white"
            }`}
          >
            <h2 className="text-xl font-semibold">Trade Usage</h2>
            <div className="mt-3 grid gap-4 sm:grid-cols-3">
              <div>
                <div className="text-sm text-slate-500">Used</div>
                <div className="mt-1 text-2xl font-semibold">{tradeUsage.used}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Limit</div>
                <div className="mt-1 text-2xl font-semibold">{tradeUsage.limit}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Utilization</div>
                <div className="mt-1 text-2xl font-semibold">{formatPercent(tradeUsage.ratio)}</div>
              </div>
            </div>

            {tradeLimitReached ? (
              <div className="mt-4 rounded-xl border border-amber-200 bg-amber-100 px-4 py-3 text-sm text-amber-800">
                Trade limit reached. Upgrade the workspace plan before importing additional trades.
              </div>
            ) : null}
          </div>
        ) : null}

        {!canImportTradesByRole ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Read-only access</h2>
            <p className="mt-2 text-slate-600">
              Your current workspace role is <span className="font-medium">{workspaceRole}</span>.
              You can review ledger and claims data, but you cannot import trades.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/ledger`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Ledger
              </Link>
              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Claims Registry
              </Link>
            </div>
          </div>
        ) : tradeLimitReached ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-amber-900">Trade import blocked</h2>
            <p className="mt-2 text-amber-800">
              This workspace has reached its trade limit. Upgrade the plan before importing more
              trades.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/settings`}
                className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium hover:bg-amber-100"
              >
                Review Plan & Billing
              </Link>
              <Link
                href={`/workspace/${workspaceId}/ledger`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Ledger
              </Link>
            </div>
          </div>
        ) : (
          <ImportForm workspaceId={workspaceId} />
        )}
      </main>
    </div>
  );
}