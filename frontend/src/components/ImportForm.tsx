"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type WorkspaceUsageSummary } from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  workspaceId?: number;
};

type ImportSourceType =
  | "csv"
  | "mt5"
  | "ibkr";

type ImportCadence = "hourly" | "daily";

type ImportStats = {
  received: number;
  imported: number;
  rejected: number;
  duplicates: number;
};

type NormalizedTradePreviewRow = {
  symbol?: string;
  side?: string;
  quantity?: number | string;
  entry_price?: number | string;
  exit_price?: number | string;
  net_pnl?: number | string;
  opened_at?: string;
  closed_at?: string;
  external_id?: string;
  fingerprint?: string;
  source_type?: string;
  source_system?: string;
  currency?: string;
};

type RejectedPreviewRow = {
  reason?: string;
  row?: Record<string, unknown>;
};

type DuplicatePreviewRow = {
  reason?: string;
  fingerprint?: string;
  row?: Record<string, unknown>;
};

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatSourceStatus(
  _source: ImportSourceType,
  selected: boolean
) {
  return selected ? "selected" : "active";
}

function sourceCardClass(
  source: ImportSourceType,
  selected: boolean
) {
  if (selected) {
    return "border-slate-900 bg-slate-900 text-white shadow-sm";
  }

  switch (source) {
    case "csv":
      return "border-emerald-200 bg-emerald-50 text-emerald-900 hover:bg-emerald-100";

    case "mt5":
      return "border-blue-200 bg-blue-50 text-blue-900 hover:bg-blue-100";

    case "ibkr":
      return "border-amber-200 bg-amber-50 text-amber-900 hover:bg-amber-100";

    default:
      return "border-slate-200 bg-white text-slate-900";
  }
}

function SourceCard({
  source,
  title,
  subtitle,
  selected,
  onSelect,
}: {
  source: ImportSourceType;
  title: string;
  subtitle: string;
  selected: boolean;
  onSelect: (source: ImportSourceType) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(source)}
      className={`w-full rounded-2xl border p-4 text-left transition ${sourceCardClass(
        source,
        selected
      )}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold">{title}</div>
          <div className={`mt-1 text-xs ${selected ? "text-slate-300" : "opacity-80"}`}>
            {subtitle}
          </div>
        </div>

        <span
          className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${
            selected
              ? "border-white/20 bg-white/10 text-white"
              : "border-current/20 bg-white/40"
          }`}
        >
          {formatSourceStatus(source, selected)}
        </span>
      </div>
    </button>
  );
}

function StatCard({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: number;
  tone?: "neutral" | "success" | "danger" | "warning";
}) {
  const className =
    tone === "success"
      ? "bg-emerald-50 text-emerald-900"
      : tone === "danger"
        ? "bg-red-50 text-red-900"
        : tone === "warning"
          ? "bg-amber-50 text-amber-900"
          : "bg-slate-50 text-slate-900";

  return (
    <div className={`rounded-xl p-4 text-sm ${className}`}>
      <div className="opacity-75">{label}</div>
      <div className="mt-1 text-lg font-semibold">{value}</div>
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
  const [duplicatePreview, setDuplicatePreview] = useState<DuplicatePreviewRow[]>([]);
  const [stats, setStats] = useState<ImportStats | null>(null);

  const [autoImportEnabled, setAutoImportEnabled] = useState(false);
  const [autoImportSaving, setAutoImportSaving] = useState(false);
  const [autoImportCadence, setAutoImportCadence] = useState<ImportCadence>("daily");

  const [
    previewSessionId,
    setPreviewSessionId,
  ] = useState<number | null>(null);

  const [
    previewMode,
    setPreviewMode,
  ] = useState(false);

  const workspaceRole = getWorkspaceRole(workspaceId);
  const canImportByRole = workspaceRole === "owner" || workspaceRole === "operator";

  const tradesUsed = Number(usage?.usage?.trades ?? 0);
  const tradesLimit = Number(usage?.limits?.trades ?? 0);

  const tradesRatio =
    tradesLimit > 0
      ? tradesUsed / tradesLimit
      : 0;

  const tradeLimitReached =
    tradesLimit > 0 &&
    tradesUsed >= tradesLimit;

  const canImport = canImportByRole && !tradeLimitReached;

  const selectedFileSummary = useMemo(() => {
    if (!file) return null;
    const sizeKb = Math.max(1, Math.round(file.size / 1024));
    return `${file.name} · ${sizeKb} KB`;
  }, [file]);

  const sourceTitle = useMemo(() => {
    switch (sourceType) {
      case "csv":
        return "CSV Upload";

      case "mt5":
        return "MT5 Adapter";

      case "ibkr":
        return "IBKR Adapter";

      default:
        return "CSV Upload";
    }
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

  function resetImportFeedback() {
    setStatus(null);
    setError(null);
    setPreview([]);
    setRejectedPreview([]);
    setDuplicatePreview([]);
    setStats(null);
  }

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
      setError(`Please select a ${sourceType.toUpperCase()} CSV file.`);
      setStatus(null);
      return;
    }

    setLoading(true);
    resetImportFeedback();

    try {
      const result =
        await api.previewImportFile(workspaceId, file, sourceType);

      setStats({
        received: Number(
          result.preview?.rows_received ?? 0
        ),

        imported: Number(
          result.preview?.rows_accepted ?? 0
        ),

        rejected: Number(
          result.preview?.rows_rejected ?? 0
        ),

        duplicates: Number(
          result.preview?.rows_duplicates ?? 0
        ),
      });

      setPreview(
        Array.isArray(
          result.preview?.normalized_preview
        )
          ? result.preview.normalized_preview
          : []
      );

      setRejectedPreview(
        Array.isArray(
          result.preview?.rejected_preview
        )
          ? result.preview.rejected_preview
          : []
      );

      setDuplicatePreview(
        Array.isArray(
          result.preview?.duplicate_preview
        )
          ? result.preview.duplicate_preview
          : []
      );

      setPreviewSessionId(
        result.preview_session_id
      );

      setPreviewMode(true);

      setStatus(
        `${sourceType.toUpperCase()} preview generated. Received: ${
          result.preview.rows_received ?? 0
        }, Accepted: ${
          result.preview.rows_accepted ?? 0
        }, Rejected: ${
          result.preview.rows_rejected ?? 0
        }, Duplicates: ${
          result.preview.rows_duplicates ?? 0
        }`
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

  async function handleConfirmImport() {

    if (!previewSessionId) {
      return;
    }

    setLoading(true);

    try {

      const result =
        await api.confirmImportPreview(
          workspaceId,
          previewSessionId
        );

      setStatus(
        `Import confirmed. Imported: ${result.rows_imported}, Rejected: ${result.rows_rejected}, Duplicates: ${result.rows_duplicates}`
      );

      setPreviewMode(false);

      setPreviewSessionId(null);

      const refreshedUsage =
        await api.getWorkspaceUsage(
          workspaceId
        );

      setUsage(refreshedUsage);

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Failed to confirm import"
      );

    } finally {

      setLoading(false);
    }
  }

  async function handleAutoImportToggle() {
    setAutoImportSaving(true);
    setError(null);

    try {
      const nextValue = !autoImportEnabled;

      await api.configureAutoImport(workspaceId, {
        source_type: sourceType,
        enabled: nextValue,
        cadence: autoImportCadence,
      });

      setAutoImportEnabled(nextValue);
      setStatus(
        `Auto-import ${nextValue ? "enabled" : "disabled"} for ${sourceType.toUpperCase()} (${autoImportCadence}).`
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update auto-import settings");
    } finally {
      setAutoImportSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Broker Integration Console</h2>
          <p className="mt-2 text-sm text-slate-600">
            Select an ingestion source and route trade evidence into the canonical import pipeline.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <SourceCard
            source="csv"
            selected={sourceType === "csv"}
            title="CSV Upload"
            subtitle="Canonical batch ingestion"
            onSelect={(source) => {
              setSourceType(source);
              resetImportFeedback();
            }}
          />
          <SourceCard
            source="mt5"
            selected={sourceType === "mt5"}
            title="MT5 Adapter"
            subtitle="MetaTrader export ingestion"
            onSelect={(source) => {
              setSourceType(source);
              resetImportFeedback();
            }}
          />
          <SourceCard
            source="ibkr"
            selected={sourceType === "ibkr"}
            title="IBKR Adapter"
            subtitle="Institutional broker export ingestion"
            onSelect={(source) => {
              setSourceType(source);
              resetImportFeedback();
            }}
          />
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">Selected Source</div>
            <div className="mt-2">{sourceTitle}</div>
            <div className="mt-1 text-xs text-slate-500">
              {sourceType === "csv"
                ? "Batch ingestion active"
                : sourceType === "mt5"
                  ? "MT5 adapter active"
                  : "IBKR adapter active"}
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">Auto-import Pipelines</div>
            <div className="mt-2">{autoImportEnabled ? "Enabled" : "Available"}</div>
            <div className="mt-1 text-xs text-slate-500">
              Configuration endpoint active for CSV, MT5, and IBKR.
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <div className="font-semibold text-slate-900">
              Import Status
            </div>

            <div className="mt-2">
              Active
            </div>

            <div className="mt-1 text-xs text-slate-500">
              CSV, MT5 and IBKR import pipelines available.
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          CSV, MT5, and IBKR are active ingestion paths on the shared broker-neutral pipeline.
          Auto-import configuration is available for recurring broker export ingestion workflows.
        </div>

        <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <h3 className="text-sm font-semibold text-slate-900">
            Institutional Export Requirements
          </h3>

          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <div className="text-sm font-semibold text-amber-900">
                IBKR Flex Export
              </div>

              <ul className="mt-3 space-y-1 text-xs text-amber-800">
                <li>Format: CSV</li>
                <li>Date Format: yyyy-MM-dd</li>
                <li>Time Format: HH:mm:ss</li>
                <li>Required: Symbol, Buy/Sell, Quantity</li>
                <li>Required: TradePrice, Date/Time</li>
              </ul>
            </div>

            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
              <div className="text-sm font-semibold text-blue-900">
                MT5 Export
              </div>

              <ul className="mt-3 space-y-1 text-xs text-blue-800">
                <li>Export Type: Closed Trades</li>
                <li>Format: CSV</li>
                <li>Required: Symbol, Type, Volume</li>
                <li>Required: Price, Time</li>
              </ul>
            </div>

            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
              <div className="text-sm font-semibold text-emerald-900">
                Canonical CSV
              </div>

              <ul className="mt-3 space-y-1 text-xs text-emerald-800">
                <li>Required: symbol</li>
                <li>Required: side</li>
                <li>Required: quantity</li>
                <li>Required: price</li>
                <li>Required: timestamp</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Import Permissions & Capacity</h2>
          <p className="mt-2 text-sm text-slate-600">
            Import rights are controlled by workspace role and current trade usage limits.
          </p>
        </div>

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
              <span className="font-semibold">{tradesUsed ?? 0}</span> of{" "}
              <span className="font-semibold">{tradesLimit ?? 0}</span> allowed trades.
            </div>
            <div className="mt-1">
              Utilization: <span className="font-medium">{formatPercent(tradesRatio)}</span>
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
                {tradesUsed ?? 0} / {tradesLimit ?? "—"}
              </span>
            </div>
            <div className="mt-1 text-slate-500">
              Utilization: {formatPercent(tradesRatio)}
            </div>
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">Source Upload & Pipeline Controls</h2>
          <p className="mt-2 text-sm text-slate-600">
            Upload a broker export file, inspect ingestion results, and configure import orchestration.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => {
              setFile(e.target.files?.[0] || null);
              resetImportFeedback();
            }}
            className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"
          />

          {selectedFileSummary ? (
            <div className="text-sm text-slate-500">Selected file: {selectedFileSummary}</div>
          ) : null}

          <div className="grid gap-4 lg:grid-cols-[1fr_220px_220px]">
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                disabled={loading || !canImport}
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? `Importing ${sourceType.toUpperCase()}...` : `Upload ${sourceType.toUpperCase()}`}
              </button>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">
                Auto-import cadence
              </label>
              <select
                value={autoImportCadence}
                onChange={(e) => setAutoImportCadence(e.target.value as ImportCadence)}
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
              >
                <option value="daily">daily</option>
                <option value="hourly">hourly</option>
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <button
                type="button"
                onClick={handleAutoImportToggle}
                disabled={autoImportSaving || !canImportByRole}
                className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {autoImportSaving
                  ? "Saving..."
                  : autoImportEnabled
                    ? "Disable Auto-import"
                    : "Enable Auto-import"}
              </button>
            </div>
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
            <div className="grid gap-4 md:grid-cols-4">
              <StatCard label="Received" value={stats.received} />
              <StatCard label="Imported" value={stats.imported} tone="success" />
              <StatCard label="Rejected" value={stats.rejected} tone="danger" />
              <StatCard label="Duplicates" value={stats.duplicates} tone="warning" />
            </div>
          ) : null}

          {
            previewMode &&
            previewSessionId && (
              <div className="mt-6 flex items-center gap-3">

                <button
                  type="button"
                  onClick={handleConfirmImport}
                  disabled={loading}
                  className="
                    rounded-xl
                    bg-slate-900
                    px-5
                    py-3
                    text-sm
                    font-semibold
                    text-white
                    hover:bg-slate-800
                    disabled:opacity-50
                  "
                >
                  Confirm Import Persistence
                </button>

                <div className="text-xs text-slate-500">
                  Trades will be permanently persisted into the institutional trade ledger.
                </div>

              </div>
            )
          }

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
                      <th className="px-3 py-2 text-left">Entry</th>
                      <th className="px-3 py-2 text-left">PnL</th>
                      <th className="px-3 py-2 text-left">Opened At</th>
                      <th className="px-3 py-2 text-left">Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((row, i) => (
                      <tr key={`${row.external_id ?? row.fingerprint ?? row.symbol ?? "row"}-${i}`} className="border-t">
                        <td className="px-3 py-2">{row.symbol ?? "—"}</td>
                        <td className="px-3 py-2">{row.side ?? "—"}</td>
                        <td className="px-3 py-2">{row.quantity ?? "—"}</td>
                        <td className="px-3 py-2">{row.entry_price ?? "—"}</td>
                        <td className="px-3 py-2">{row.net_pnl ?? "—"}</td>
                        <td className="px-3 py-2">{row.opened_at ?? "—"}</td>
                        <td className="px-3 py-2">{row.source_type ?? row.source_system ?? sourceType}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}

          {rejectedPreview.length > 0 ? (
            <div className="mt-2">
              <h3 className="mb-2 text-sm font-semibold text-red-700">Rejected Rows</h3>

              <div className="overflow-x-auto rounded-xl border bg-red-50">
                <table className="min-w-full text-xs">
                  <thead className="text-red-700">
                    <tr>
                      <th className="px-3 py-2 text-left">Reason</th>
                      <th className="px-3 py-2 text-left">Raw Row</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rejectedPreview.map((row, i) => (
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

          {duplicatePreview.length > 0 ? (
            <div className="mt-2">
              <h3 className="mb-2 text-sm font-semibold text-amber-700">Duplicate Rows</h3>

              <div className="overflow-x-auto rounded-xl border bg-amber-50">
                <table className="min-w-full text-xs">
                  <thead className="text-amber-700">
                    <tr>
                      <th className="px-3 py-2 text-left">Reason</th>
                      <th className="px-3 py-2 text-left">Fingerprint</th>
                    </tr>
                  </thead>
                  <tbody>
                    {duplicatePreview.map((row, i) => (
                      <tr key={`duplicate-${i}`} className="border-t">
                        <td className="px-3 py-2">{row.reason ?? "Duplicate"}</td>
                        <td className="px-3 py-2 font-mono text-[11px] text-slate-700">
                          {row.fingerprint ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </form>
      </div>
    </div>
  );
}