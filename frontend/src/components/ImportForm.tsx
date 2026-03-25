"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type WorkspaceUsageSummary } from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  workspaceId?: number;
};

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

export default function ImportForm({ workspaceId = 1 }: Props) {
  const { getWorkspaceRole } = useAuth();

  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(true);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);

  const workspaceRole = getWorkspaceRole(workspaceId);
  const canImportByRole = workspaceRole === "owner" || workspaceRole === "operator";

  const tradeUsage = usage?.usage?.trades;
  const tradeLimitReached =
    (tradeUsage?.limit ?? 0) > 0 && (tradeUsage?.used ?? 0) >= (tradeUsage?.limit ?? 0);

  const canImport = canImportByRole && !tradeLimitReached;

  const selectedFileSummary = useMemo(() => {
    if (!file) return null;
    const sizeKb = Math.max(1, Math.round(file.size / 1024));
    return `${file.name} · ${sizeKb} KB`;
  }, [file]);

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(workspaceId);
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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!canImportByRole) {
      setError("Only workspace owners and operators can import trades.");
      setStatus(null);
      return;
    }

    if (tradeLimitReached) {
      setError("Trade limit reached. Upgrade workspace plan before importing more trades.");
      setStatus(null);
      return;
    }

    if (!file) {
      setError("Please select a CSV file.");
      setStatus(null);
      return;
    }

    setLoading(true);
    setStatus(null);
    setError(null);

    try {
      const result = await api.importTradesCsv(workspaceId, file);

      const summary = `Import complete. Received: ${result.rows_received}, Imported: ${result.rows_imported}, Rejected: ${result.rows_rejected}, Duplicates: ${result.rows_skipped_duplicates}`;

      if (Array.isArray(result.errors) && result.errors.length > 0) {
        setError(`${summary} Errors: ${result.errors.join(" | ")}`);
        setStatus(null);
      } else {
        setStatus(summary);
        setError(null);
      }

      setFile(null);

      try {
        const refreshedUsage = await api.getWorkspaceUsage(workspaceId);
        setUsage(refreshedUsage);
      } catch {
        // preserve current usage state if refresh fails
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-semibold">Upload Trade CSV</h2>
        <p className="mt-2 text-sm text-slate-600">
          Import trades into workspace {workspaceId} from a supported CSV file.
        </p>
      </div>

      {usageLoading ? (
        <div className="mb-4 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
          Loading import permissions and trade usage...
        </div>
      ) : null}

      {!canImportByRole ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
          Only workspace owners and operators can import trades. Your current role is{" "}
          <span className="font-medium">{workspaceRole || "unknown"}</span>.
        </div>
      ) : tradeLimitReached ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          <div className="font-medium">Trade limit reached</div>
          <div className="mt-1">
            This workspace is currently using{" "}
            <span className="font-semibold">{tradeUsage?.used ?? 0}</span> of{" "}
            <span className="font-semibold">{tradeUsage?.limit ?? 0}</span> allowed trades.
          </div>
          <div className="mt-1">
            Utilization: <span className="font-medium">{formatPercent(tradeUsage?.ratio)}</span>
          </div>
          <div className="mt-2">
            Upgrade the workspace plan before importing additional trades.
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {tradeUsage ? (
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
              <div>
                Current trade usage:{" "}
                <span className="font-semibold">
                  {tradeUsage.used} / {tradeUsage.limit}
                </span>
              </div>
              <div className="mt-1 text-slate-500">
                Utilization: {formatPercent(tradeUsage.ratio)}
              </div>
            </div>
          ) : null}

          <input
            type="file"
            accept=".csv"
            onChange={(e) => {
              setFile(e.target.files?.[0] || null);
              setError(null);
              setStatus(null);
            }}
            className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"
          />

          {selectedFileSummary ? (
            <div className="text-sm text-slate-500">Selected file: {selectedFileSummary}</div>
          ) : null}

          <button
            type="submit"
            disabled={loading || !canImport}
            className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Importing..." : "Upload CSV"}
          </button>

          {error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          {status ? (
            <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
              {status}
            </div>
          ) : null}
        </form>
      )}
    </div>
  );
}