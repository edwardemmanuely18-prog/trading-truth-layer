"use client";

import { useEffect, useMemo, useState } from "react";
import { Search, RefreshCw, ChevronRight } from "lucide-react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";
import { api } from "../../../../lib/api";

type RegistryRecord = {
  canonical_evidence_id: string;
  evidence_type: string;
  workspace_id: number | null;
  provider_id: string | null;
  evidence_hash: string;
  evidence_version: number;
  lifecycle: string;
  synchronization_batch: string | null;
  synchronization_session: string | null;
  registered_at: string | null;
  registered_at_utc: string | null;
  registered_at_timezone: string;

  provider: {
    provider_name: string;
    provider_platform: string;
    broker_server: string | null;
    broker_account_id: string | null;
    broker_account_name: string | null;
    account_state: string | null;
    account_currency: string | null;
    original_ticket_id: string | null;
    original_deal_id: string | null;
    original_order_id: string | null;
    original_position_id: string | null;
    original_execution_id: string | null;
  };

  metadata: Record<string, unknown>;
};

type RegistrySummary = {
  total_records: number;
  lifecycle_counts: Record<string, number>;
  provider_counts: Record<string, number>;
  evidence_type_counts: Record<string, number>;
};

type RegistryPagination = {
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
  has_previous: boolean;
  has_next: boolean;
};

function formatUtcDate(value: string | null) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    timeZone: "UTC",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZoneName: "short",
  }).format(date);
}

function formatLocalDate(value: string | null) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-GB", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZoneName: "short",
  }).format(date);
}

function localTimezoneLabel() {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

function displayValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  return String(value);
}

function lifecycleLabel(value: string) {
  return value.replace(/_/g, " ");
}

function evidenceType(record: RegistryRecord) {
  if (!record.evidence_type) {
    return "—";
  }

  return record.evidence_type;
}

export default function EvidenceExplorerPage() {
  const params = useParams<{
    workspaceId: string;
  }>();

  const workspaceId = Number(params.workspaceId);

  const [records, setRecords] = useState<RegistryRecord[]>([]);
  const [summary, setSummary] = useState<RegistrySummary | null>(null);
  const [pagination, setPagination] =
  useState<RegistryPagination | null>(null);
  const [page, setPage] = useState(1);

  const pageSize = 50;

  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");

  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedProvider, setSelectedProvider] = useState("ALL");
  const [selectedLifecycle, setSelectedLifecycle] = useState("ALL");
  const [selectedEvidenceType, setSelectedEvidenceType] = useState("ALL");

  async function loadRegistry(
    requestedPage: number = page,
  ) {
    try {
      setLoading(true);
      setError(null);

      const [registryResponse, summaryResponse] =
        await Promise.all([
          api.getV2EvidenceRegistryPage(
            workspaceId,
            requestedPage,
            pageSize,
          ),
          api.getV2EvidenceRegistrySummary(
            workspaceId,
          ),
        ]);

      setRecords(
        registryResponse.records
      );

      setPagination(
        registryResponse.pagination
      );

      setSummary(summaryResponse);
      setSubmittedQuery("");
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load the V2 Evidence Registry."
      );
    } finally {
      setLoading(false);
    }
  }

  async function executeSearch() {
    const trimmed = query.trim();

    if (!trimmed) {
      setPage(1);
      await loadRegistry(1);
      return;
    }

    try {
      setSearching(true);
      setError(null);

      const response = await api.searchV2EvidenceRegistry(
        workspaceId,
        trimmed
      );

      setPage(1);
      setPagination(null);

      setRecords(response.results);
      setSubmittedQuery(trimmed);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Evidence search failed."
      );
    } finally {
      setSearching(false);
    }
  }

  useEffect(() => {
    if (!Number.isFinite(workspaceId)) {
      setError("Invalid workspace ID.");
      setLoading(false);
      return;
    }

    void loadRegistry(page);
  }, [workspaceId, page]);

  const providers = useMemo(() => {
    return Object.keys(summary?.provider_counts ?? {}).sort();
  }, [summary]);

  const lifecycles = useMemo(() => {
    return Object.keys(summary?.lifecycle_counts ?? {}).sort();
  }, [summary]);

  const evidenceTypes = useMemo(() => {
    return Object.keys(summary?.evidence_type_counts ?? {}).sort();
  }, [summary]);

  const filteredRecords = useMemo(() => {
    return records.filter((record) => {
      if (
        selectedProvider !== "ALL" &&
        record.provider.provider_name !== selectedProvider
      ) {
        return false;
      }

      if (
        selectedLifecycle !== "ALL" &&
        record.lifecycle !== selectedLifecycle
      ) {
        return false;
      }

      if (
        selectedEvidenceType !== "ALL" &&
        evidenceType(record) !== selectedEvidenceType
      ) {
        return false;
      }

      return true;
    });
  }, [
    records,
    selectedProvider,
    selectedLifecycle,
    selectedEvidenceType,
  ]);

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-7xl px-6 py-10">
        {/* Header */}
        <div className="mb-8">
          <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
            Evidence Registry
          </div>

          <div className="mt-2 flex items-center justify-between gap-6">
            <div>
              <h1 className="text-4xl font-bold text-slate-950">
                Evidence Explorer
              </h1>

              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                Universal evidence discovery workspace for searching,
                filtering, and inspecting canonical evidence across the
                Trading Truth Layer.
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setPage(1);
                void loadRegistry(1);
              }}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={`h-4 w-4 ${
                  loading ? "animate-spin" : ""
                }`}
              />
              Refresh
            </button>
          </div>
        </div>

        {/* Search */}
        <section className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 lg:flex-row">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />

              <input
                type="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    void executeSearch();
                  }
                }}
                placeholder="Search evidence, provider, account, order, position, hash..."
                className="w-full rounded-xl border border-slate-300 bg-slate-50 py-3 pl-11 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-slate-500 focus:bg-white"
              />
            </div>

            <button
              type="button"
              onClick={() => void executeSearch()}
              disabled={searching}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {searching ? "Searching..." : "Search Evidence"}
            </button>
          </div>

          {submittedQuery && (
            <div className="mt-3 text-xs text-slate-500">
              Search results for{" "}
              <span className="font-semibold text-slate-700">
                “{submittedQuery}”
              </span>
            </div>
          )}
        </section>

        {/* Error */}
        {error && (
          <section className="mt-5 rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
            <div className="text-sm font-semibold text-red-800">
              Evidence Registry unavailable
            </div>

            <div className="mt-1 text-sm text-red-700">
              {error}
            </div>
          </section>
        )}

        {/* Summary */}
        <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Total Evidence
            </div>

            <div className="mt-2 text-3xl font-bold text-slate-950">
              {summary?.total_records ?? 0}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Providers
            </div>

            <div className="mt-2 text-3xl font-bold text-slate-950">
              {providers.length}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Evidence Types
            </div>

            <div className="mt-2 text-3xl font-bold text-slate-950">
              {evidenceTypes.length}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Verified
            </div>

            <div className="mt-2 text-3xl font-bold text-slate-950">
              {summary?.lifecycle_counts?.VERIFIED ?? 0}
            </div>
          </div>
        </section>

        {/* Filters */}
        <section className="mt-6 rounded-2xl border border-slate-300 bg-white p-5 shadow-sm">
          <div className="mb-4 text-sm font-semibold text-slate-950">
            Filters
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Provider
              </span>

              <select
                value={selectedProvider}
                onChange={(event) => {
                  setPage(1);
                  setSelectedProvider(event.target.value);
                }}
                className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-slate-500"
              >
                <option value="ALL">All Providers</option>

                {providers.map((provider) => (
                  <option key={provider} value={provider}>
                    {provider}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Lifecycle
              </span>

              <select
                value={selectedLifecycle}
                onChange={(event) => {
                  setPage(1);
                  setSelectedLifecycle(event.target.value);
                }}
                className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-slate-500"
              >
                <option value="ALL">All Lifecycle States</option>

                {lifecycles.map((lifecycle) => (
                  <option key={lifecycle} value={lifecycle}>
                    {lifecycleLabel(lifecycle)}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Evidence Type
              </span>

              <select
                value={selectedEvidenceType}
                onChange={(event) => {
                  setPage(1);
                  setSelectedEvidenceType(event.target.value);
                }}
                className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-slate-500"
              >
                <option value="ALL">All Evidence Types</option>

                {evidenceTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </section>

        {/* Results */}
        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-300 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div>
              <div className="text-sm font-semibold text-slate-950">
                Registered Evidence
              </div>

              <div className="mt-1 text-xs text-slate-500">
                {pagination
                  ? `${pagination.total_records.toLocaleString()} total records`
                  : `${filteredRecords.length.toLocaleString()} search result${
                      filteredRecords.length === 1 ? "" : "s"
                    }`}
              </div>
            </div>
          </div>

          {loading ? (
            <div className="px-5 py-16 text-center text-sm text-slate-500">
              Loading canonical evidence...
            </div>
          ) : filteredRecords.length === 0 ? (
            <div className="px-5 py-16 text-center">
              <div className="text-sm font-semibold text-slate-800">
                No registered evidence found
              </div>

              <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-500">
                Connected providers do not automatically create registry
                records. Evidence appears here after it has passed through
                the V2 synchronization and registry pipeline.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Evidence
                    </th>

                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Type
                    </th>

                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Provider
                    </th>

                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Account
                    </th>

                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Environment
                    </th>

                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Lifecycle
                    </th>

                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Registered At
                    </th>

                    <th className="w-10 px-3" />
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-200">
                  {filteredRecords.map((record) => (
                    <tr
                      key={record.canonical_evidence_id}
                      className="transition hover:bg-slate-50"
                    >
                      <td className="px-5 py-4">
                        <div className="font-mono text-xs font-semibold text-slate-900">
                          {record.canonical_evidence_id}
                        </div>

                        <div className="mt-1 max-w-[220px] truncate font-mono text-[10px] text-slate-400">
                          {record.evidence_hash}
                        </div>
                      </td>

                      <td className="px-5 py-4">
                        <span className="inline-flex rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                          {evidenceType(record)}
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        <div className="text-sm font-semibold text-slate-900">
                          {record.provider.provider_name}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                          {record.provider.provider_platform}
                        </div>
                      </td>

                      <td className="px-5 py-4">
                        <div className="font-mono text-xs text-slate-800">
                          {displayValue(
                            record.provider.broker_account_id
                          )}
                        </div>

                        {record.provider.broker_account_name && (
                          <div className="mt-1 text-xs text-slate-500">
                            {record.provider.broker_account_name}
                          </div>
                        )}
                      </td>

                      <td className="px-5 py-4">
                        <span className="text-xs font-semibold text-slate-700">
                          {displayValue(
                            record.provider.account_state
                          )}
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        <span className="inline-flex rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700">
                          {lifecycleLabel(record.lifecycle)}
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        <div className="whitespace-nowrap text-xs font-semibold text-slate-700">
                          {formatLocalDate(record.registered_at_utc)}
                        </div>

                        <div className="mt-1 whitespace-nowrap text-[11px] text-slate-400">
                          Local · {localTimezoneLabel()}
                        </div>

                        <div className="mt-1 whitespace-nowrap text-[11px] text-slate-400">
                          UTC · {formatUtcDate(record.registered_at_utc)}
                        </div>
                      </td>

                      <td className="px-3 py-4 text-right">
                        <a
                          href={`/workspace/${workspaceId}/evidence-explorer/${encodeURIComponent(
                            record.canonical_evidence_id
                          )}`}
                          className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                          aria-label={`Open ${record.canonical_evidence_id}`}
                        >
                          <ChevronRight className="h-4 w-4" />
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {pagination && pagination.total_pages > 0 && (
          <div className="flex items-center justify-between border-t border-slate-200 px-5 py-4">
            <div className="text-xs text-slate-500">
              Page{" "}
              <span className="font-semibold text-slate-700">
                {pagination.page.toLocaleString()}
              </span>{" "}
              of{" "}
              <span className="font-semibold text-slate-700">
                {pagination.total_pages.toLocaleString()}
              </span>
              {" · "}
              {pagination.total_records.toLocaleString()} total records
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                disabled={
                  loading ||
                  !pagination.has_previous
                }
                onClick={() => {
                  const previousPage =
                    pagination.page - 1;

                  setPage(previousPage);

                  window.scrollTo({
                    top: 0,
                    behavior: "smooth",
                  });
                }}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>

              <button
                type="button"
                disabled={
                  loading ||
                  !pagination.has_next
                }
                onClick={() => {
                  const nextPage =
                    pagination.page + 1;

                  setPage(nextPage);

                  window.scrollTo({
                    top: 0,
                    behavior: "smooth",
                  });
                }}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}