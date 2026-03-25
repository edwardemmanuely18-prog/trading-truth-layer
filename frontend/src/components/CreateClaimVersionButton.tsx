"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { api, type WorkspaceUsageSummary } from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  claimSchemaId: number;
  workspaceId?: number;
};

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

export default function CreateClaimVersionButton({
  claimSchemaId,
  workspaceId,
}: Props) {
  const router = useRouter();
  const { getWorkspaceRole } = useAuth();

  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(Boolean(workspaceId));
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const workspaceRole = workspaceId ? getWorkspaceRole(workspaceId) : null;

  const canCloneByRole = useMemo(() => {
    return workspaceRole === "owner" || workspaceRole === "operator";
  }, [workspaceRole]);

  const claimUsage = usage?.usage?.claims;
  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 && (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  useEffect(() => {
    if (!workspaceId) {
      setUsageLoading(false);
      return;
    }

    const resolvedWorkspaceId = workspaceId;
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(resolvedWorkspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setUsageLoading(false);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId]);

  async function handleClone() {
    if (!canCloneByRole) {
      setError("Only workspace owners and operators can create a new claim version.");
      return;
    }

    if (claimLimitReached) {
      setError("Claim limit reached. Upgrade workspace plan before creating another version.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const created = await api.cloneClaimSchema(claimSchemaId);

      if (workspaceId) {
        router.push(`/workspace/${workspaceId}/claim/${created.id}`);
      } else {
        router.push(`/claim/${created.id}`);
      }

      router.refresh();
    } catch (cloneError) {
      setError(
        cloneError instanceof Error ? cloneError.message : "Failed to create claim version."
      );
    } finally {
      setLoading(false);
    }
  }

  const disabled = loading || usageLoading || !canCloneByRole || claimLimitReached;

  const currentPlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.plan_code)
    )?.name || usage?.plan_code || "—";

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">Versioning Action</div>
          <div className="mt-1 text-xs leading-5 text-slate-600">
            Create a new governed claim version instead of overwriting the current record.
            This preserves lineage and historical traceability.
          </div>
        </div>

        <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-semibold text-slate-700">
          {loading
            ? "creating..."
            : usageLoading
              ? "loading usage..."
              : disabled
                ? "restricted"
                : "available"}
        </span>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Workspace role</div>
          <div className="mt-1 font-semibold text-slate-900">{workspaceRole || "unknown"}</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Current plan</div>
          <div className="mt-1 font-semibold text-slate-900">{currentPlanName}</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Claim usage</div>
          <div className="mt-1 font-semibold text-slate-900">
            {workspaceId && !usageLoading && claimUsage
              ? `${claimUsage.used} / ${claimUsage.limit}`
              : "—"}
          </div>
          {workspaceId && !usageLoading && claimUsage ? (
            <div className="mt-1 text-xs text-slate-500">
              {formatPercent(claimUsage.ratio)}
            </div>
          ) : null}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <button
          type="button"
          disabled={disabled}
          onClick={() => void handleClone()}
          className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {loading ? "Creating Version..." : "Create New Version"}
        </button>
      </div>

      {!canCloneByRole && workspaceId ? (
        <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          Only workspace owners and operators can create new claim versions.
        </div>
      ) : null}

      {claimLimitReached ? (
        <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          Claim limit reached. Upgrade the workspace plan before creating another version.
        </div>
      ) : null}

      {error ? (
        <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
          {error}
        </div>
      ) : null}
    </div>
  );
}