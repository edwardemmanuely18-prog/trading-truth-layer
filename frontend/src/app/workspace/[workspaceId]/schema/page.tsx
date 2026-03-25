"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import ClaimSchemaForm from "../../../../components/ClaimSchemaForm";
import { useAuth } from "../../../../components/AuthProvider";
import { api, type WorkspaceUsageSummary } from "../../../../lib/api";

export default function WorkspaceSchemaPage() {
  const params = useParams();
  const { user, workspaces, loading } = useAuth();

  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [usageLoading, setUsageLoading] = useState(true);

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const workspaceRole = workspaceMembership?.workspace_role ?? null;
  const canCreateClaimRole = workspaceRole === "owner" || workspaceRole === "operator";
  const claimUsage = usage?.usage?.claims;

  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 &&
    (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  useEffect(() => {
    if (!workspaceId) return;

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

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading schema builder...</div>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-5xl px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace schema builder.
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Claim Authoring</div>
            <h1 className="mt-2 text-3xl font-bold">Claims Schema Builder</h1>
            <p className="mt-2 text-slate-600">
              Define a verified performance claim for workspace {workspaceId}.
            </p>
          </div>

          <div className="rounded-xl border bg-white px-4 py-3 text-sm shadow-sm">
            <div className="text-slate-500">Workspace Role</div>
            <div className="mt-1 font-semibold">{workspaceRole}</div>
          </div>
        </div>

        {usageLoading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            Loading workspace usage...
          </div>
        ) : !canCreateClaimRole ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Read-only access</h2>

            <p className="mt-2 text-slate-600">
              Your workspace role is <span className="font-medium">{workspaceRole}</span>.
              Only owners and operators can create or modify claim schemas.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Claims Registry
              </Link>

              <Link
                href={`/workspace/${workspaceId}/ledger`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Ledger
              </Link>
            </div>
          </div>
        ) : (
          <>
            {claimLimitReached ? (
              <div className="mb-6 rounded-2xl border border-amber-200 bg-amber-50 p-6 shadow-sm">
                <h2 className="text-xl font-semibold text-amber-800">Local QA override active</h2>

                <p className="mt-2 text-amber-700">
                  This workspace is currently over the normal claim plan limit with{" "}
                  <span className="font-semibold">{claimUsage?.used}</span> claims out of{" "}
                  <span className="font-semibold">{claimUsage?.limit}</span>.
                </p>

                <p className="mt-2 text-amber-700">
                  Draft creation remains enabled in this local QA environment so the end-to-end
                  lifecycle can still be tested.
                </p>

                <p className="mt-2 text-amber-700">
                  In production, additional claim creation would be blocked until the workspace plan
                  is upgraded.
                </p>

                <div className="mt-5 flex gap-3">
                  <Link
                    href={`/workspace/${workspaceId}/claims`}
                    className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium hover:bg-amber-100"
                  >
                    View Existing Claims
                  </Link>
                </div>
              </div>
            ) : null}

            <ClaimSchemaForm workspaceId={workspaceId} />
          </>
        )}
      </main>
    </div>
  );
}