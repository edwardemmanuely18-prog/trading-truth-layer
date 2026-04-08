"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type WorkspaceUsageSummary } from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  workspaceId?: number;
};

type ImportSourceType = "csv" | "mt5" | "ibkr";

type ImportStats = {
  received: number;
  imported: number;
  rejected: number;
};

type NormalizedTradePreviewRow = {
  symbol?: string;
  side?: string;
  quantity?: number | string;
  price?: number | string;
  pnl?: number | string;
  timestamp?: string;
  external_id?: string;
};

type RejectedPreviewRow = {
  reason?: string;
  row?: Record<string, unknown>;
};

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatAdapterStatus(source: ImportSourceType, enabled: boolean) {
  if (source === "csv") return enabled ? "active" : "disabled";
  return enabled ? "ready" : "planned";
}

function sourceBadgeClass(source: ImportSourceType, enabled: boolean) {
  if (source === "csv") {
    return enabled
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : "border-slate-200 bg-slate-100 text-slate-600";
  }

  return enabled
    ? "border-blue-200 bg-blue-50 text-blue-800"
    : "border-amber-200 bg-amber-50 text-amber-800";
}

function SourceSelectorCard({
  source,
  selected,
  enabled,
  title,
  subtitle,
  onSelect,
}: {
  source: ImportSourceType;
  selected: boolean;
  enabled: boolean;
  title: string;
  subtitle: string;
  onSelect: (source: ImportSourceType) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(source)}
      className={`w-full rounded-2xl border p-4 text-left transition ${
        selected
          ? "border-slate-900 bg-slate-900 text-white shadow-sm"
          : "border-slate-200 bg-white hover:bg-slate-50"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold">{title}</div>
          <div className={`mt-1 text-xs ${selected ? "text-slate-300" : "text-slate-500"}`}>
            {subtitle}
          </div>
        </div>

        <span
          className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${
            selected
              ? "border-white/20 bg-white/10 text-white"
              : sourceBadgeClass(source, enabled)
          }`}
        >
          {formatAdapterStatus(source, enabled)}
        </span>
      </div>
    </button>
  );
}

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        {subtitle ? <div className="mt-1 text-sm text-slate-500">{subtitle}</div> : null}
      </div>
      {children}
    </div>
  );
}

export default function ImportForm({ workspaceId = 1 }: Props) {
  const { getWorkspaceRole } = useAuth();

  const [sourceType, setSourceType] = useState<ImportSourceType>("csv");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(true);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);

  const [preview, setPreview] = useState<NormalizedTradePreviewRow[]>([]);
  const [rejectedPreview, setRejectedPreview] = useState<RejectedPreviewRow[]>([]);
  const [stats, setStats] = useState<ImportStats | null>(null);

  const [autoImportEnabled, setAutoImportEnabled] = useState(false);
  const [realTimeEnabled, setRealTimeEnabled] = useState(false);

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

  const sourceTitle = useMemo(() => {
    if (sourceType === "csv") return "CSV Upload";
    if (sourceType === "mt5") return "MT5 Adapter";
    return "IBKR Adapter";
  }, [sourceType]);

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

    if (sourceType !== "csv") {
      setError(
        `${sourceTitle} is not wired to a live backend adapter yet. Build the backend connector before enabling this source.`
      );
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
    setPreview([]);
    setRejectedPreview([]);
    setStats(null);

    try {
      const result = await api.importTradesCsv(workspaceId, file);

      setStats({
        received: result.rows_received,
        imported: result.rows_imported,
        rejected: result.rows_rejected,
      });

      setPreview(
        Array.isArray((result as any).normalized_preview)
          ? ((result as any).normalized_preview as NormalizedTradePreviewRow[])
          : []
      );

      setRejectedPreview(
        Array.isArray((result as any).rejected_preview)
          ? ((result as any).rejected_preview as RejectedPreviewRow[])
          : []
      );

      setStatus(
        `Import complete. Received: ${result.rows_received}, Imported: ${result.rows_imported}, Rejected: ${result.rows_rejected}`
      );
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
    <div className="space-y-6">
      <SectionCard
        title="Broker Integration Console"
        subtitle="Select an ingestion source and route trade evidence into the canonical import pipeline."
      >
        <div className="grid gap-4 md:grid-cols-3">
          <SourceSelectorCard
            source="csv"
            selected={sourceType === "csv"}
            enabled={true}
            title="CSV Upload"
            subtitle="Canonical batch ingestion"
            onSelect={setSourceType}
          />

          <SourceSelectorCard
            source="mt5"
            selected={sourceType === "mt5"}
            enabled={false}
            title="MT5 Adapter"
            subtitle="MetaTrader connector surface"
            onSelect={setSourceType}
          />

          <SourceSelectorCard
            source="ibkr"
            selected={sourceType === "ibkr"}
            enabled={false}
            title="IBKR Adapter"
            subtitle="Institutional broker connector"
            onSelect={setSourceType}
          />
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">Selected Source</div>
            <div className="mt-2">{sourceTitle}</div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">Auto-import Pipelines</div>
            <div className="mt-2">
              {autoImportEnabled ? "Enabled" : "Not connected yet"}
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">Real-time Ingestion</div>
            <div className="mt-2">
              {realTimeEnabled ? "Streaming active" : "Not connected yet"}
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          CSV is live now. MT5, IBKR, auto-import pipelines, and real-time ingestion require backend
          adapters, scheduled jobs, or streaming infrastructure. This form exposes the control
          surface and readiness state, while the actual connectors should be implemented in backend
          services and import orchestration.
        </div>
      </SectionCard>

      <SectionCard
        title="Import Permissions & Capacity"
        subtitle="Import rights are gated by workspace role and plan usage."
      >
        {usageLoading ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
            Loading import permissions and trade usage...
          </div>
        ) : !canImportByRole ? (
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
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <div>
              Current trade usage:{" "}
              <span className="font-semibold">
                {tradeUsage?.used ?? 0} / {tradeUsage?.limit ?? "—"}
              </span>
            </div>
            <div className="mt-1 text-slate-500">
              Utilization: {formatPercent(tradeUsage?.ratio)}
            </div>
          </div>
        )}
      </SectionCard>

      <SectionCard
        title="CSV Import"
        subtitle="Canonical fallback ingestion surface. Use this while adapters are still being connected."
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => {
              setFile(e.target.files?.[0] || null);
              setError(null);
              setStatus(null);
              setPreview([]);
              setRejectedPreview([]);
              setStats(null);
            }}
            className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"
          />

          {selectedFileSummary ? (
            <div className="text-sm text-slate-500">Selected file: {selectedFileSummary}</div>
          ) : null}

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={loading || !canImport}
              className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Importing..." : "Upload CSV"}
            </button>

            <button
              type="button"
              onClick={() => setAutoImportEnabled((value) => !value)}
              className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              {autoImportEnabled ? "Auto-import: On" : "Auto-import: Off"}
            </button>

            <button
              type="button"
              onClick={() => setRealTimeEnabled((value) => !value)}
              className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              {realTimeEnabled ? "Real-time: On" : "Real-time: Off"}
            </button>
          </div>

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

          {stats ? (
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-xl bg-slate-50 p-4 text-sm">
                <div className="text-slate-500">Received</div>
                <div className="text-lg font-semibold">{stats.received}</div>
              </div>

              <div className="rounded-xl bg-emerald-50 p-4 text-sm">
                <div className="text-emerald-700">Imported</div>
                <div className="text-lg font-semibold text-emerald-800">{stats.imported}</div>
              </div>

              <div className="rounded-xl bg-red-50 p-4 text-sm">
                <div className="text-red-700">Rejected</div>
                <div className="text-lg font-semibold text-red-800">{stats.rejected}</div>
              </div>
            </div>
          ) : null}

          {preview.length > 0 ? (
            <div className="mt-2">
              <h3 className="mb-2 text-sm font-semibold text-slate-900">
                Accepted Trades Preview
              </h3>

              <div className="overflow-x-auto rounded-xl border">
                <table className="min-w-full text-xs">
                  <thead className="bg-slate-100 text-slate-600">
                    <tr>
                      <th className="px-3 py-2 text-left">Symbol</th>
                      <th className="px-3 py-2 text-left">Side</th>
                      <th className="px-3 py-2 text-left">Qty</th>
                      <th className="px-3 py-2 text-left">Price</th>
                      <th className="px-3 py-2 text-left">PnL</th>
                      <th className="px-3 py-2 text-left">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((row: NormalizedTradePreviewRow, i: number) => (
                      <tr key={`${row.external_id ?? row.symbol ?? "row"}-${i}`} className="border-t">
                        <td className="px-3 py-2">{row.symbol ?? "—"}</td>
                        <td className="px-3 py-2">{row.side ?? "—"}</td>
                        <td className="px-3 py-2">{row.quantity ?? "—"}</td>
                        <td className="px-3 py-2">{row.price ?? "—"}</td>
                        <td className="px-3 py-2">{row.pnl ?? "—"}</td>
                        <td className="px-3 py-2">{row.timestamp ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}

          {rejectedPreview.length > 0 ? (
            <div className="mt-2">
              <h3 className="mb-2 text-sm font-semibold text-red-700">
                Rejected Rows
              </h3>

              <div className="overflow-x-auto rounded-xl border bg-red-50">
                <table className="min-w-full text-xs">
                  <thead className="text-red-700">
                    <tr>
                      <th className="px-3 py-2 text-left">Reason</th>
                      <th className="px-3 py-2 text-left">Raw Row</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rejectedPreview.map((row: RejectedPreviewRow, i: number) => (
                      <tr key={`rejected-${i}`} className="border-t">
                        <td className="px-3 py-2">{row.reason ?? "Unknown rejection"}</td>
                        <td className="px-3 py-2 font-mono text-[11px] text-slate-700">
                          {row.row ? JSON.stringify(row.row) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </form>
      </SectionCard>
    </div>
  );
}