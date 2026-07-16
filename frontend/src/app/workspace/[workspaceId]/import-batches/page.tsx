"use client";

import { useEffect, useState } from "react";

import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  ImportBatch,
  getImportBatches,
} from "../../../../lib/api";

export default function Page() {

  const params = useParams();

  const workspaceId =
    Number(params.workspaceId);

  const [batches, setBatches] =
    useState<ImportBatch[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    async function load() {

      try {

        const data =
          await getImportBatches(
            workspaceId
          );

        setBatches(data);

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }
    }

    load();

  }, [workspaceId]);

  const totalReceived =
    batches.reduce(
      (sum, batch) =>
        sum + batch.rows_received,
      0
    );

  const totalImported =
    batches.reduce(
      (sum, batch) =>
        sum + batch.rows_imported,
      0
    );

  const totalRejected =
    batches.reduce(
      (sum, batch) =>
        sum + batch.rows_rejected,
      0
    );

  const totalDuplicates =
    batches.reduce(
      (sum, batch) =>
        sum +
        batch.rows_skipped_duplicates,
      0
    );

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Evidence Registry
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Import Batches
          </h1>

          <p className="mt-3 text-slate-600">
            Canonical ingestion audit
            ledger for all imported
            evidence entering the
            workspace.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-4 mb-8">

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Import Batches
            </div>

            <div className="mt-2 text-3xl font-bold">
              {batches.length}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Rows Received
            </div>

            <div className="mt-2 text-3xl font-bold">
              {totalReceived}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Imported
            </div>

            <div className="mt-2 text-3xl font-bold">
              {totalImported}
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5">
            <div className="text-sm text-slate-500">
              Rejected + Duplicates
            </div>

            <div className="mt-2 text-3xl font-bold">
              {
                totalRejected +
                totalDuplicates
              }
            </div>
          </div>

        </div>

        <div className="overflow-hidden rounded-xl border bg-white">

          <div className="max-h-[700px] overflow-auto">

          <table className="w-full">

            <thead className="sticky top-0 z-10 bg-slate-100">

              <tr className="bg-slate-100">

                <th className="p-4 text-left">
                  Batch ID
                </th>

                <th className="p-4 text-left">
                  Source
                </th>

                <th className="p-4 text-left">
                  File
                </th>

                <th className="p-4 text-left">
                  Received
                </th>

                <th className="p-4 text-left">
                  Imported
                </th>

                <th className="p-4 text-left">
                  Rejected
                </th>

                <th className="p-4 text-left">
                  Duplicates
                </th>

                <th className="p-4 text-left">
                  Created
                </th>

              </tr>

            </thead>

            <tbody>

              {loading && (
                <tr>
                  <td
                    colSpan={8}
                    className="p-6"
                  >
                    Loading...
                  </td>
                </tr>
              )}

              {!loading &&
                batches.map(batch => (

                  <tr
                    key={batch.id}
                    className="border-t"
                  >

                    <td className="p-4">
                      {batch.id}
                    </td>

                    <td className="p-4">
                      {batch.source_type}
                    </td>

                    <td className="p-4">
                      {batch.filename}
                    </td>

                    <td className="p-4">
                      {batch.rows_received}
                    </td>

                    <td className="p-4">
                      {batch.rows_imported}
                    </td>

                    <td className="p-4">
                      {batch.rows_rejected}
                    </td>

                    <td className="p-4">
                      {
                        batch.rows_skipped_duplicates
                      }
                    </td>

                    <td className="p-4">
                      {
                        batch.created_at
                          ?.substring(0, 19)
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