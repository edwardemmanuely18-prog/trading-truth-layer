"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";
import {
  api,
  type V2EvidenceRegistryRecord,
} from "../../../../lib/api";

type TradingTab =
  | "TRADE"
  | "ORDER"
  | "POSITION"
  | "EXECUTION"
  | "DEAL";

const TABS: Array<{
  key: TradingTab;
  label: string;
}> = [
  { key: "TRADE", label: "Trades" },
  { key: "ORDER", label: "Orders" },
  { key: "POSITION", label: "Positions" },
  { key: "EXECUTION", label: "Executions" },
  { key: "DEAL", label: "Deals" },
];

function formatDate(
  value: string | null,
) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-GB",
    {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZoneName: "short",
      hour12: false,
    },
  ).format(date);
}

function displayValue(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  return String(value);
}

export default function TradingRecordsPage() {
  const params = useParams<{
    workspaceId: string;
  }>();

  const workspaceId = Number(params.workspaceId);

  const [records, setRecords] =
    useState<V2EvidenceRegistryRecord[]>([]);

  const [activeTab, setActiveTab] =
    useState<TradingTab>("TRADE");

  const [page, setPage] =
    useState(1);

  const pageSize = 50;

  const [pagination, setPagination] =
    useState<{
      page: number;
      page_size: number;
      total_records: number;
      total_pages: number;
      has_previous: boolean;
      has_next: boolean;
    } | null>(null);

  const [tabCounts, setTabCounts] =
    useState<Record<TradingTab, number>>({
      TRADE: 0,
      ORDER: 0,
      POSITION: 0,
      EXECUTION: 0,
      DEAL: 0,
    });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadTradingRecords(
    requestedPage: number = page,
    requestedTab: TradingTab = activeTab,
  ) {
    try {
      setLoading(true);
      setError(null);

      const [
        pageResponse,
        summaryResponse,
      ] = await Promise.all([
        api.getV2EvidenceRegistryPage(
          workspaceId,
          requestedPage,
          pageSize,
          requestedTab,
        ),

        api.getV2EvidenceRegistrySummary(
          workspaceId,
        ),
      ]);

      setRecords(
        pageResponse.records
      );

      setPagination(
        pageResponse.pagination
      );

      const counts =
        summaryResponse.evidence_type_counts;

      setTabCounts({
        TRADE: counts.TRADE ?? 0,
        ORDER: counts.ORDER ?? 0,
        POSITION: counts.POSITION ?? 0,
        EXECUTION: counts.EXECUTION ?? 0,
        DEAL: counts.DEAL ?? 0,
      });

    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load V2 trading records."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!Number.isFinite(workspaceId)) {
      setError("Invalid workspace ID.");
      setLoading(false);
      return;
    }

    void loadTradingRecords();
  }, [workspaceId]);

  const filteredRecords = records;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-8">
          <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
            Evidence Registry
          </div>

          <div className="mt-2 flex items-center justify-between gap-6">
            <div>
              <h1 className="text-4xl font-bold text-slate-950">
                Trading Records
              </h1>

              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                Canonical trading evidence workspace containing
                trades, orders, positions, executions, and deals
                registered through the V2 evidence pipeline.
              </p>
            </div>

            <button
              type="button"
              onClick={() =>
                void loadTradingRecords(
                  page,
                  activeTab,
                )
              }
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

        {error && (
          <section className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
            <div className="text-sm font-semibold text-red-800">
              Trading Records unavailable
            </div>

            <div className="mt-1 text-sm text-red-700">
              {error}
            </div>
          </section>
        )}

        <section className="overflow-hidden rounded-2xl border border-slate-300 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 pt-5">
            <div className="flex flex-wrap gap-2">
              {TABS.map((tab) => {
                const active = activeTab === tab.key;

                return (
                  <button
                    key={tab.key}
                    type="button"
                    onClick={() => {
                      setActiveTab(tab.key);
                      setPage(1);
                      void loadTradingRecords(
                        1,
                        tab.key,
                      );
                    }}
                    className={[
                      "rounded-lg px-4 py-2 text-sm font-semibold transition",
                      active
                        ? "bg-slate-950 text-white"
                        : "border border-slate-200 text-slate-600 hover:bg-slate-50",
                    ].join(" ")}
                  >
                    {tab.label}
                    <span
                      className={[
                        "ml-2 rounded-full px-2 py-0.5 text-[10px]",
                        active
                          ? "bg-white/15 text-white"
                          : "bg-slate-100 text-slate-500",
                      ].join(" ")}
                    >
                      {tabCounts[tab.key]}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="px-6 py-5">
            <div className="mb-5">
              <div className="text-sm font-semibold text-slate-950">
                {TABS.find((tab) => tab.key === activeTab)?.label}
              </div>

              <div className="mt-1 text-xs text-slate-500">
                {pagination
                  ? pagination.total_records.toLocaleString()
                  : 0}{" "}
                record
                {pagination?.total_records === 1
                  ? ""
                  : "s"}
              </div>
            </div>

            {loading ? (
              <div className="py-16 text-center text-sm text-slate-500">
                Loading trading evidence...
              </div>
            ) : filteredRecords.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center">
                <div className="text-sm font-semibold text-slate-800">
                  No {TABS.find(
                    (tab) => tab.key === activeTab
                  )?.label.toLowerCase()} found
                </div>

                <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">
                  This workspace displays trading evidence that has
                  actually entered the V2 Evidence Registry. A provider
                  connection alone does not create a trading record.
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
                        Provider
                      </th>

                      <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Account
                      </th>

                      <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Provider Reference
                      </th>

                      <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Lifecycle
                      </th>

                      <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Registered
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-200">
                    {filteredRecords.map((record) => (
                      <tr
                        key={record.canonical_evidence_id}
                        className="transition hover:bg-slate-50"
                      >
                        <td className="px-5 py-4">
                          <a
                            href={`/workspace/${workspaceId}/evidence-explorer/${encodeURIComponent(
                              record.canonical_evidence_id
                            )}`}
                            className="font-mono text-xs font-semibold text-slate-900 hover:text-blue-700 hover:underline"
                          >
                            {record.canonical_evidence_id}
                          </a>

                          <div className="mt-1 text-[10px] text-slate-400">
                            {record.evidence_hash}
                          </div>
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

                          {record.provider.account_state && (
                            <div className="mt-1 text-xs text-slate-500">
                              {record.provider.account_state}
                            </div>
                          )}
                        </td>

                        <td className="px-5 py-4">
                          <div className="font-mono text-xs text-slate-700">
                            {displayValue(
                            record.provider.original_ticket_id ??
                                record.provider.original_order_id ??
                                record.provider.original_position_id ??
                                record.provider.original_execution_id ??
                                record.provider.original_deal_id
                            )}
                          </div>
                        </td>

                        <td className="px-5 py-4">
                          <span className="inline-flex rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700">
                            {record.lifecycle.replace(
                              /_/g,
                              " "
                            )}
                          </span>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-xs text-slate-500">
                          {formatDate(record.registered_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>

        {pagination && pagination.total_pages > 0 && (
          <div className="mt-5 flex items-center justify-between border-t border-slate-200 pt-4">
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
              {pagination.total_records.toLocaleString()} records
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

                  void loadTradingRecords(
                    previousPage,
                    activeTab,
                  );
                }}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-40"
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

                  void loadTradingRecords(
                    nextPage,
                    activeTab,
                  );
                }}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-40"
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