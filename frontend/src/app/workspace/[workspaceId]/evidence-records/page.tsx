"use client";

import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  getEvidenceRecords,
  EvidenceRecord,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {
  const [workspaceId, setWorkspaceId] =
    useState<number | null>(null);

  const [records, setRecords] =
    useState<EvidenceRecord[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    async function initialize() {
      try {
        const resolved =
          await params;

        setWorkspaceId(
          Number(
            resolved.workspaceId
          )
        );
      } catch {
        setError(
          "Failed to resolve workspace."
        );
      }
    }

    initialize();
  }, [params]);

  useEffect(() => {
    if (workspaceId === null) {
      return;
    }

    async function loadRecords() {
      try {
        setLoading(true);

        const data =
          await getEvidenceRecords(
            workspaceId as number
          );

        setRecords(data);
      } catch (err: any) {
        console.error(err);

        setError(
          err?.message ||
          "Failed to load evidence records."
        );
      } finally {
        setLoading(false);
      }
    }

    loadRecords();
  }, [workspaceId]);

  const tier1Count =
    records.filter(
      r =>
        r.evidence_trust_tier ===
        "tier_1"
    ).length;

  const tier2Count =
    records.filter(
      r =>
        r.evidence_trust_tier ===
        "tier_2"
    ).length;

  const tier3Count =
    records.filter(
      r =>
        r.evidence_trust_tier ===
        "tier_3"
    ).length;

  const verifiedCount =
    records.filter(
      r =>
        r.verification_state ===
        "broker_verified" ||
        r.verification_state ===
        "verified"
    ).length;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">
          <div className="text-xs uppercase tracking-widest text-slate-500">
            Evidence Registry
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Evidence Records
          </h1>

          <p className="mt-3 text-slate-600">
            Canonical provenance registry
            for broker verified,
            imported, and manually
            created trade evidence.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-5 mb-8">

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Evidence Records
            </div>

            <div className="mt-2 text-3xl font-bold">
              {records.length}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Verified Evidence
            </div>

            <div className="mt-2 text-3xl font-bold">
              {verifiedCount}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Tier 1
            </div>

            <div className="mt-2 text-3xl font-bold">
              {tier1Count}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Tier 2
            </div>

            <div className="mt-2 text-3xl font-bold">
              {tier2Count}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Tier 3
            </div>

            <div className="mt-2 text-3xl font-bold">
              {tier3Count}
            </div>
          </div>

        </div>

        <div className="overflow-hidden rounded-xl border bg-white">

          <table className="w-full">

            <thead className="bg-slate-100">

              <tr>
                <th className="p-4 text-left">
                  Trade
                </th>

                <th className="p-4 text-left">
                  Source
                </th>

                <th className="p-4 text-left">
                  Import Batch
                </th>

                <th className="p-4 text-left">
                  Verification
                </th>

                <th className="p-4 text-left">
                  Trust Tier
                </th>

                <th className="p-4 text-left">
                  Hash
                </th>
              </tr>

            </thead>

            <tbody>

              {loading ? (
                <tr>
                  <td
                    colSpan={6}
                    className="p-6 text-center text-slate-500"
                  >
                    Loading evidence records...
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="p-6 text-center text-slate-500"
                  >
                    No evidence records found.
                  </td>
                </tr>
              ) : (
                records.map(
                  record => (
                    <tr
                      key={record.trade_id}
                      className="border-t"
                    >
                      <td className="p-4">
                        {record.symbol}
                      </td>

                      <td className="p-4">
                        {
                          record.source_system ||
                          record.import_source ||
                          "manual"
                        }
                      </td>

                      <td className="p-4">
                        {
                          record.import_job_id ||
                          "-"
                        }
                      </td>

                      <td className="p-4">
                        {
                          record.verification_state
                        }
                      </td>

                      <td className="p-4">
                        {
                          record.evidence_trust_tier
                        }
                      </td>

                      <td className="p-4 font-mono text-xs">
                        {
                          record.raw_trade_hash
                            ?.slice(
                              0,
                              16
                            ) || "-"
                        }
                      </td>
                    </tr>
                  )
                )
              )}

            </tbody>

          </table>

        </div>

      </div>
    </div>
  );
}