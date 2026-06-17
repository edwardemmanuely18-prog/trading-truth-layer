"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getSyncJobs,
  createSyncJob,
  executeSyncJob,
  getBrokerConnections,
  type BrokerConnection,
} from "../../../../lib/api";

type SyncJob = {
  id: number;
  provider: string;
  sync_type: string;
  status: string;
  records_processed: number;
  records_imported: number;
  error_message?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
};

export default function SyncJobsPage() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [creating, setCreating] =
    useState(false);

  const [jobs, setJobs] = useState<
    SyncJob[]
  >([]);

  const [executingJobId, setExecutingJobId] =
    useState<number | null>(null);

  const [connections, setConnections] =
    useState<BrokerConnection[]>([]);

  const [selectedConnectionId,
    setSelectedConnectionId] =
      useState<number | null>(null);

  const [syncType, setSyncType] =
    useState("historical");

  const [error, setError] =
    useState("");

  async function load() {
    try {
      setLoading(true);

      const [
        syncJobs,
        brokerConnections,
      ] = await Promise.all([
        getSyncJobs(workspaceId),
        getBrokerConnections(
          workspaceId
        ),
      ]);

      setJobs(syncJobs);

      const verifiedConnections =
        brokerConnections.filter(
          (connection) =>
            connection.connection_status ===
            "connected"
        );

      setConnections(
        verifiedConnections
      );

      if (
        verifiedConnections.length > 0 &&
        !selectedConnectionId
      ) {
        setSelectedConnectionId(
          verifiedConnections[0].id
        );
      }
    } catch (err: any) {
      setError(
        err?.message ??
          "Failed loading sync center"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (workspaceId) {
      void load();
    }
  }, [workspaceId]);

  async function handleCreateJob() {
    try {
      if (!selectedConnectionId) {
        alert(
          "Select a verified broker connection"
        );
        return;
      }

      setCreating(true);

      await createSyncJob(
        workspaceId,
        {
          connection_id:
            selectedConnectionId,
          sync_type: syncType,
        }
      );

      await load();
    } catch (err: any) {
      alert(
        err?.message ??
          "Failed creating sync job"
      );
    } finally {
      setCreating(false);
    }
  }

  async function handleExecute(
    jobId: number
  ) {
    try {

      setExecutingJobId(jobId);

      await executeSyncJob(
        workspaceId,
        jobId
      );

      await load();

    } catch (err: any) {

      alert(
        err?.message ??
        "Sync execution failed"
      );

    } finally {

      setExecutingJobId(null);

    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">
          <h1 className="text-4xl font-bold">
            Sync Center
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional broker
            synchronization engine
            responsible for
            importing verified
            broker evidence into
            the TTL canonical
            trade ledger.
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        <div className="mb-8 rounded-2xl border bg-white p-6">

          <h2 className="mb-4 text-xl font-semibold">
            Create Sync Job
          </h2>

          <div className="grid gap-4 md:grid-cols-3">

            <select
              value={
                selectedConnectionId ??
                ""
              }
              onChange={(e) =>
                setSelectedConnectionId(
                  Number(
                    e.target.value
                  )
                )
              }
              className="rounded-lg border p-3"
            >
              {connections.map(
                (connection) => (
                  <option
                    key={
                      connection.id
                    }
                    value={
                      connection.id
                    }
                  >
                    {
                      connection.connection_name
                    }
                    {" • "}
                    {
                      connection.provider
                    }
                    {" • "}
                    {
                      connection.account_environment
                    }
                  </option>
                )
              )}
            </select>

            <select
              value={syncType}
              onChange={(e) =>
                setSyncType(
                  e.target.value
                )
              }
              className="rounded-lg border p-3"
            >
              <option value="historical">
                Historical Trades
              </option>

              <option value="incremental">
                Incremental Trades
              </option>

              <option value="positions">
                Open Positions
              </option>

              <option value="account_state">
                Account State Snapshot
              </option>
            </select>

            <button
              onClick={
                handleCreateJob
              }
              disabled={
                creating
              }
              className="rounded-lg bg-slate-900 px-4 py-3 text-white"
            >
              {creating
                ? "Creating..."
                : "Create Sync Job"}
            </button>

          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">

          <div className="border-b bg-slate-50 px-6 py-4">
            <h2 className="font-semibold">
              Synchronization Ledger
            </h2>
          </div>

          {loading ? (
            <div className="p-8">
              Loading sync jobs...
            </div>
          ) : (
            <table className="w-full">

              <thead className="border-b bg-slate-50">
                <tr>

                  <th className="px-6 py-4 text-left">
                    Provider
                  </th>

                  <th className="px-6 py-4 text-left">
                    Type
                  </th>

                  <th className="px-6 py-4 text-left">
                    Status
                  </th>

                  <th className="px-6 py-4 text-left">
                    Processed
                  </th>

                  <th className="px-6 py-4 text-left">
                    Imported
                  </th>

                  <th className="px-6 py-4 text-left">
                    Created
                  </th>

                  <th className="px-6 py-4 text-left">
                    Action
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
                      <td className="px-6 py-4">
                        {job.provider}
                      </td>

                      <td className="px-6 py-4">
                        {job.sync_type}
                      </td>

                      <td className="px-6 py-4">
                        {job.status}
                      </td>

                      <td className="px-6 py-4">
                        {
                          job.records_processed
                        }
                      </td>

                      <td className="px-6 py-4">
                        {
                          job.records_imported
                        }
                      </td>

                      <td className="px-6 py-4">
                        {new Date(
                          job.created_at
                        ).toLocaleString()}
                      </td>

                      <td className="px-6 py-4">
                        <button
                          onClick={() =>
                            handleExecute(job.id)
                          }
                          disabled={
                            executingJobId === job.id
                          }
                          className={
                            executingJobId === job.id
                              ? "rounded-lg bg-black px-3 py-2 text-white opacity-75"
                              : "rounded-lg border px-3 py-2"
                          }
                        >
                          {executingJobId === job.id
                            ? "Synchronizing..."
                            : "Sync Now"}
                        </button>
                      </td>
                    </tr>
                  )
                )}

                {!loading &&
                  jobs.length === 0 && (
                    <tr>
                      <td
                        colSpan={7}
                        className="p-10 text-center text-slate-500"
                      >
                        No sync jobs found.
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