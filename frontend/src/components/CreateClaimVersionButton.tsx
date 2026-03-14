"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "../lib/api";

type Props = {
  claimSchemaId: number;
  workspaceId?: number;
};

export default function CreateClaimVersionButton({ claimSchemaId, workspaceId }: Props) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleClone() {
    try {
      setLoading(true);
      const created = await api.cloneClaimSchema(claimSchemaId);

      if (workspaceId) {
        router.push(`/workspace/${workspaceId}/claim/${created.id}`);
      } else {
        router.push(`/claim/${created.id}`);
      }

      router.refresh();
    } catch (error) {
      console.error(error);
      alert(error instanceof Error ? error.message : "Failed to create claim version.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      type="button"
      disabled={loading}
      onClick={handleClone}
      className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 disabled:opacity-50"
    >
      {loading ? "Creating Version..." : "Create New Version"}
    </button>
  );
}