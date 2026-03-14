"use client";

import { useState } from "react";
import { api } from "../lib/api";

type Props = {
  workspaceId?: number;
};

export default function ImportForm({ workspaceId = 1 }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!file) {
      setStatus("Please select a CSV file.");
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const result = await api.importTradesCsv(workspaceId, file);
      setStatus(
        `Import complete. Received: ${result.rows_received}, Imported: ${result.rows_imported}, Rejected: ${result.rows_rejected}, Duplicates: ${result.rows_skipped_duplicates}`
      );
      setFile(null);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">Upload Trade CSV</h2>

      <form onSubmit={handleSubmit} className="mt-4 space-y-4">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
        >
          {loading ? "Importing..." : "Upload CSV"}
        </button>

        {status ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            {status}
          </div>
        ) : null}
      </form>
    </div>
  );
}