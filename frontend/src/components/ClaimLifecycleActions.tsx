"use client";

import { useState } from "react";
import { api } from "../lib/api";

type Props = {
  claimSchemaId: number;
  status: string;
};

export default function ClaimLifecycleActions({ claimSchemaId, status }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const verifyClaim = async () => {
    try {
      setLoading(true);
      setError(null);
      await api.verifyClaimSchema(claimSchemaId);
      window.location.reload();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to verify claim.");
    } finally {
      setLoading(false);
    }
  };

  const publishClaim = async () => {
    try {
      setLoading(true);
      setError(null);
      await api.publishClaimSchema(claimSchemaId);
      window.location.reload();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to publish claim.");
    } finally {
      setLoading(false);
    }
  };

  const lockClaim = async () => {
    try {
      setLoading(true);
      setError(null);
      await api.lockClaimSchema(claimSchemaId);
      window.location.reload();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to lock claim.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={loading || status !== "draft"}
          onClick={verifyClaim}
          className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-900 hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading && status === "draft" ? "Working..." : "Verify"}
        </button>

        <button
          type="button"
          disabled={loading || status !== "verified"}
          onClick={publishClaim}
          className="rounded-xl border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-900 hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading && status === "verified" ? "Working..." : "Publish"}
        </button>

        <button
          type="button"
          disabled={loading || status !== "published"}
          onClick={lockClaim}
          className="rounded-xl border border-green-300 bg-green-50 px-4 py-2 text-sm font-semibold text-green-900 hover:bg-green-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading && status === "published" ? "Working..." : "Lock"}
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}
    </div>
  );
}
