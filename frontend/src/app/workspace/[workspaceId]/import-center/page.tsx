"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getBrokerAdapters,
  getImportJobs,
  uploadImportJob,
  BrokerAdapter,
  ImportJob,
} from "../../../../lib/api";


export default function ImportCenterPage() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const [adapters, setAdapters] =
    useState<BrokerAdapter[]>([]);

  const [jobs, setJobs] =
    useState<ImportJob[]>([]);

  const [selectedAdapter,
    setSelectedAdapter] =
      useState("");

  const [error, setError] =
    useState("");

  async function load() {
    try {
      setLoading(true);

      const [
        adapterData,
        jobData,
      ] = await Promise.all([
        getBrokerAdapters(
          workspaceId
        ),
        getImportJobs(
          workspaceId
        ),
      ]);

      setAdapters(adapterData);
      setJobs(jobData);

      if (
        adapterData.length &&
        !selectedAdapter
      ) {
        setSelectedAdapter(
          adapterData[0].provider
        );
      }
    } catch (err: any) {
      setError(
        err?.message ??
        "Failed loading import center"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (workspaceId) {
      load();
    }
  }, [workspaceId]);

  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file =
      event.target.files?.[0];

    if (!file) return;

    try {
      setUploading(true);

      await uploadImportJob(
        workspaceId,
        selectedAdapter,
        file
      );

      await load();

      event.target.value = "";
    } catch (err: any) {
      alert(
        err?.message ??
        "Upload failed"
      );
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10 space-y-8">

        <div className="rounded-2xl border bg-white p-8">
          <h1 className="text-4xl font-bold">
            Import Center
          </h1>

          <p className="mt-4 text-slate-600">
            Institutional-grade evidence
            ingestion pipeline for
            broker exports, CSV files,
            historical account data,
            and third-party trading
            records.
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        )}

        <div className="rounded-2xl border bg-white p-8">
          <h2 className="text-2xl font-semibold">
            Create Import Job
          </h2>

          <div className="mt-6 grid gap-6 md:grid-cols-2">

            <div>
              <label className="block text-sm font-medium">
                Adapter
              </label>

              <select
                className="mt-2 w-full rounded-lg border p-3"
                value={selectedAdapter}
                onChange={(e) =>
                  setSelectedAdapter(
                    e.target.value
                  )
                }
              >
                {adapters.map(
                  (adapter) => (
                    <option
                      key={
                        adapter.id
                      }
                      value={
                        adapter.provider
                      }
                    >
                      {
                        adapter.display_name
                      }
                    </option>
                  )
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium">
                Evidence File
              </label>

              <input
                type="file"
                onChange={
                  handleUpload
                }
                disabled={
                  uploading
                }
                className="mt-2 block w-full"
              />
            </div>

          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border bg-white">

          <div className="border-b bg-slate-50 px-6 py-4">
            <h2 className="font-semibold">
              Import Job Ledger
            </h2>
          </div>

          {loading ? (
            <div className="p-8">
              Loading jobs...
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="p-4 text-left">
                    Adapter
                  </th>

                  <th className="p-4 text-left">
                    File
                  </th>

                  <th className="p-4 text-left">
                    Status
                  </th>

                  <th className="p-4 text-left">
                    Records
                  </th>

                  <th className="p-4 text-left">
                    Imported
                  </th>

                  <th className="p-4 text-left">
                    Created
                  </th>
                </tr>
              </thead>

              <tbody>

                {jobs.map(
                  (job) => (
                    <tr
                      key={job.id}
                      className="border-b"
                    >
                      <td className="p-4">
                        {
                          job.adapter_provider
                        }
                      </td>

                      <td className="p-4">
                        {
                          job.filename
                        }
                      </td>

                      <td className="p-4">
                        {
                          job.status
                        }
                      </td>

                      <td className="p-4">
                        {
                          job.records_detected
                        }
                      </td>

                      <td className="p-4">
                        {
                          job.imported_records
                        }
                      </td>

                      <td className="p-4">
                        {new Date(
                          job.created_at
                        ).toLocaleString()}
                      </td>
                    </tr>
                  )
                )}

                {!jobs.length && (
                  <tr>
                    <td
                      colSpan={6}
                      className="p-10 text-center text-slate-500"
                    >
                      No import jobs yet.
                    </td>
                  </tr>
                )}

              </tbody>
            </table>
          )}
        </div>

      </div>
    </div>
  );
}