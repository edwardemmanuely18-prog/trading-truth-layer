"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  BrokerAdapter,
  getBrokerAdapters,
} from "../../../../lib/api";

export default function AdapterRegistryPage() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] = useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [adapters, setAdapters] = useState<
    BrokerAdapter[]
  >([]);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);

        const data =
          await getBrokerAdapters(
            workspaceId
          );

        const operationalNames = [
          "CSV Import",
          "Interactive Brokers",
          "MetaTrader 5",
        ];

        const sorted = [...data].sort(
          (a, b) => {
            const aOperational =
              operationalNames.includes(
                a.display_name
              );

            const bOperational =
              operationalNames.includes(
                b.display_name
              );

            if (
              aOperational &&
              !bOperational
            )
              return -1;

            if (
              !aOperational &&
              bOperational
            )
              return 1;

            return a.display_name.localeCompare(
              b.display_name
            );
          }
        );

        setAdapters(sorted);
      } catch (err: any) {
        setError(
          err?.message ??
            "Failed to load adapters"
        );
      } finally {
        setLoading(false);
      }
    }

    if (workspaceId) {
      load();
    }
  }, [workspaceId]);

  return (
  <div className="min-h-screen bg-slate-50">
    <Navbar />

    <div className="mx-auto max-w-7xl px-6 py-10 space-y-6">
      <div className="rounded-2xl border bg-white p-8">
        <h1 className="text-4xl font-bold text-slate-900">
          Adapter Registry
        </h1>

        <p className="mt-4 text-slate-600">
          Institutional adapter catalog used
          by Trading Truth Layer for broker
          connectivity, evidence ingestion,
          synchronization, and trust
          verification.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border bg-white">
        <div className="border-b bg-slate-50 px-6 py-4">
          <h2 className="font-semibold">
            Registered Adapters
          </h2>

          <div className="mt-2 text-sm text-slate-500">
            3 Operational • 7 Planned
          </div>

        </div>

        {loading ? (
          <div className="p-8">
            Loading adapters...
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b text-left">
                <th className="p-4">
                  Provider
                </th>

                <th className="p-4">
                  Adapter Type
                </th>

                <th className="p-4">
                  Trust Tier
                </th>

                <th className="p-4">
                  Live Sync
                </th>

                <th className="p-4">
                  Historical Import
                </th>

                <th className="p-4">
                  Status
                </th>
              </tr>
            </thead>

            <tbody>
              {adapters.map((adapter) => (
                <tr
                  key={adapter.id}
                  className="border-b"
                >
                  <td className="p-4 font-medium">
                    {adapter.display_name}
                  </td>

                  <td className="p-4">
                    {adapter.adapter_type}
                  </td>

                  <td className="p-4">
                    {adapter.trust_tier}
                  </td>

                  <td className="p-4">

                    {[
                      "Interactive Brokers",
                      "MetaTrader 5",
                    ].includes(
                      adapter.display_name
                    )
                      ? "Yes"
                      : adapter.display_name ===
                        "CSV Import"
                      ? "No"
                      : "Planned"}

                  </td>

                  <td className="p-4">

                    {[
                      "csv_import",
                      "interactive_brokers",
                      "ibkr",
                      "metatrader_5",
                      "mt5",
                    ].includes(adapter.provider)
                      ? "Yes"
                      : "Planned"}

                  </td>

                  <td className="p-4">

                    {[
                      "csv_import",
                      "interactive_brokers",
                      "ibkr",
                      "metatrader_5",
                      "mt5",
                    ].includes(adapter.provider) ? (

                      <span className="
                        rounded-full
                        bg-green-100
                        px-3
                        py-1
                        text-xs
                        font-medium
                        text-green-700
                      ">
                        Operational
                      </span>

                    ) : (

                      <span className="
                        rounded-full
                        bg-amber-100
                        px-3
                        py-1
                        text-xs
                        font-medium
                        text-amber-700
                      ">
                        Coming Soon
                      </span>

                    )}

                  </td>
                </tr>
              ))}

              {!loading &&
                adapters.length === 0 && (
                  <tr>
                    <td
                      colSpan={6}
                      className="p-8 text-center text-slate-500"
                    >
                      No adapters found.
                    </td>
                  </tr>
                )}
            </tbody>
          </table>
        )}
      </div>

      <div className="rounded-2xl border bg-white p-8">
        <h2 className="text-2xl font-semibold">
          TTL Trust Hierarchy
        </h2>

        <div className="mt-6 space-y-3">
          <div>
            Tier 1 — Direct Broker
            Ingestion
          </div>

          <div>
            Tier 2 — Broker Export
            Upload
          </div>

          <div>
            Tier 3 — Manual Trade Entry
          </div>
        </div>
      </div>
      </div>
    </div>
  );
}