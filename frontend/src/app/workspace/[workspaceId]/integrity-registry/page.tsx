"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  IntegrityRecord,
  getIntegrityRegistry,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {

  const resolvedParams =
    use(params);

  const workspaceId =
    Number(
      resolvedParams.workspaceId
    );

  const [records, setRecords] =
    useState<IntegrityRecord[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    async function load() {

      try {

        const data =
          await getIntegrityRegistry(
            workspaceId
          );

        setRecords(data);

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }

    }

    load();

  }, [workspaceId]);

  const hashed =
    records.filter(
      r => r.raw_trade_hash
    ).length;

  const fingerprinted =
    records.filter(
      r => r.trade_fingerprint
    ).length;

  const integrityCoverage =
    records.length === 0
      ? 0
      : Math.round(
          (
            records.filter(
              r =>
                r.raw_trade_hash ||
                r.trade_fingerprint
            ).length /
            records.length
          ) * 100
        );

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Integrity Layer
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Integrity Registry
          </h1>

          <p className="mt-3 text-slate-600">
            Canonical provenance,
            fingerprinting, and
            cryptographic integrity
            registry for all trade
            evidence.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-4 mb-8">

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Integrity Records
            </div>

            <div className="mt-2 text-3xl font-bold">
              {records.length}
            </div>

          </div>

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Hash Protected
            </div>

            <div className="mt-2 text-3xl font-bold">
              {hashed}
            </div>

          </div>

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Fingerprinted
            </div>

            <div className="mt-2 text-3xl font-bold">
              {fingerprinted}
            </div>

          </div>

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Integrity Coverage
            </div>

            <div className="mt-2 text-3xl font-bold">
              {integrityCoverage}%
            </div>

          </div>

        </div>

        <div className="rounded-xl border bg-white overflow-hidden">

          <div className="max-h-[700px] overflow-auto">

          <table className="w-full">

            <thead className="sticky top-0 z-10 bg-slate-100">

              <tr className="bg-slate-100">

                <th className="p-4 text-left">
                  Trade
                </th>

                <th className="p-4 text-left">
                  Symbol
                </th>

                <th className="p-4 text-left">
                  Verification
                </th>

                <th className="p-4 text-left">
                  Trust Tier
                </th>

                <th className="p-4 text-left">
                  Integrity Type
                </th>

                <th className="p-4 text-left">
                  Source
                </th>

                <th className="p-4 text-left">
                  Broker Trade
                </th>

                <th className="p-4 text-left">
                  Raw Hash
                </th>

                <th className="p-4 text-left">
                  Fingerprint
                </th>

              </tr>

            </thead>

            <tbody>

              {loading && (

                <tr>

                  <td
                    colSpan={9}
                    className="p-6"
                  >
                    Loading...
                  </td>

                </tr>

              )}

              {!loading &&
                records.map(record => (

                  <tr
                    key={record.trade_id}
                    className="border-t"
                  >

                    <td className="p-4">
                      {record.trade_id}
                    </td>

                    <td className="p-4">
                      {record.symbol}
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

                    <td className="p-4">
                      {
                        record.integrity_type
                          || "-"
                      }
                    </td>

                    <td className="p-4">
                      {
                        record.import_source
                      }
                    </td>

                    <td className="p-4">
                      {
                        record.broker_trade_id
                        || "-"
                      }
                    </td>

                    <td className="p-4 font-mono text-xs">
                      {
                        record.raw_trade_hash
                          ? `${record.raw_trade_hash.slice(0,12)}...`
                          : "-"
                      }
                    </td>

                    <td className="p-4 font-mono text-xs">
                      {
                        record.trade_fingerprint
                          ? `${record.trade_fingerprint.slice(0,12)}...`
                          : "-"
                      }
                    </td>

                  </tr>

                ))}

            </tbody>

          </table>

          </div>

        </div>

      </div>

    </div>
  );
}