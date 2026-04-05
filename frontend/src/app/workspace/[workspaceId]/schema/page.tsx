"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";
import { api, type WorkspaceUsageSummary } from "../../../../lib/api";

function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-3xl font-semibold leading-none tracking-tight tabular-nums text-slate-950">
        {value}
      </div>
      <div className="mt-3 text-sm leading-6 text-slate-500">{hint}</div>
    </div>
  );
}

function InfoCard({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{body}</p>
    </div>
  );
}

function ActionCard({
  title,
  body,
  href,
  label,
}: {
  title: string;
  body: string;
  href: string;
  label: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{body}</p>
      <div className="mt-4">
        <Link
          href={href}
          className="inline-flex rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
        >
          {label}
        </Link>
      </div>
    </div>
  );
}

function GuidanceItem({
  step,
  title,
  body,
}: {
  step: string;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
        {step}
      </div>
      <h3 className="mt-3 text-base font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{body}</p>
    </div>
  );
}

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
  const paidAccessActive = Boolean(usage?.governance?.paid_access_active);
  const effectivePlanCode = usage?.effective_plan_code || usage?.plan_code || "starter";

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
        <div className="p-6">Loading schema registry...</div>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-6xl px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace schema registry.
          </div>
        </main>
      </div>
    );
  }

  const claimsUsed = claimUsage?.used ?? 0;
  const claimsLimit = claimUsage?.limit ?? 0;
  const usageRatio =
    claimUsage?.ratio !== null && claimUsage?.ratio !== undefined
      ? `${Math.round(claimUsage.ratio * 100)}%`
      : "—";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-6xl px-6 py-10">
        <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.9fr]">
            <div>
              <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
                Workspace Governance Surface
              </div>

              <h1 className="mt-4 text-3xl font-bold tracking-tight">Schema Registry</h1>

              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-600">
                Review workspace claim-authoring posture, creation permissions, plan-governed capacity,
                and the operational pathways that connect schema drafting, claims registry review,
                ledger evidence, and billing-based governance.
              </p>

              <div className="mt-5 flex flex-wrap items-center gap-2">
                <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  workspace-specific governance
                </span>
                <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  claim creation readiness
                </span>
                <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  plan-aware capacity
                </span>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
              <InfoCard
                title="Workspace Role"
                body={workspaceRole ? `Current role: ${workspaceRole}.` : "Workspace role not available."}
              />
              <InfoCard
                title="Registry Purpose"
                body="This page governs claim-authoring readiness and workspace schema posture. It is not the primary draft builder."
              />
            </div>
          </div>
        </section>

        {usageLoading ? (
          <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
            Loading workspace governance and usage...
          </div>
        ) : (
          <>
            <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <MetricCard
                label="Claims Used"
                value={claimsUsed}
                hint="Current workspace claim count"
              />
              <MetricCard
                label="Claim Limit"
                value={claimsLimit || "—"}
                hint="Plan-governed claim capacity"
              />
              <MetricCard
                label="Usage Ratio"
                value={usageRatio}
                hint="Claims usage against plan limit"
              />
              <MetricCard
                label="Effective Plan"
                value={effectivePlanCode}
                hint={paidAccessActive ? "Paid access active" : "Fallback or inactive paid posture"}
              />
            </section>

            {!canCreateClaimRole ? (
              <section className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
                <h2 className="text-xl font-semibold">Read-only registry access</h2>

                <p className="mt-2 text-slate-600">
                  Your workspace role is <span className="font-medium">{workspaceRole}</span>.
                  Only owners and operators can author or modify claim drafts. You can still review
                  claims, ledger evidence, and governance posture from this workspace registry surface.
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

                  <Link
                    href={`/workspace/${workspaceId}/settings`}
                    className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                  >
                    Review Settings & Billing
                  </Link>
                </div>
              </section>
            ) : (
              <>
                {claimLimitReached ? (
                  <section className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 shadow-sm">
                    <h2 className="text-xl font-semibold text-amber-800">Claim capacity reached</h2>

                    <p className="mt-2 text-amber-700">
                      This workspace is currently using <span className="font-semibold">{claimsUsed}</span> claims
                      out of <span className="font-semibold">{claimsLimit}</span>.
                    </p>

                    <p className="mt-2 text-amber-700">
                      New claim drafting should be governed by billing posture and plan capacity.
                      Use the actions below to review existing claims or update workspace billing.
                    </p>

                    <div className="mt-5 flex flex-wrap gap-3">
                      <Link
                        href={`/workspace/${workspaceId}/claims`}
                        className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium hover:bg-amber-100"
                      >
                        View Existing Claims
                      </Link>

                      <Link
                        href={`/workspace/${workspaceId}/settings`}
                        className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium hover:bg-amber-100"
                      >
                        Review Billing
                      </Link>
                    </div>
                  </section>
                ) : null}

                <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  <ActionCard
                    title="Create New Claim"
                    body="Open the guided creation surface to define a new draft claim with controlled scope, methodology, and exposure."
                    href="/schema"
                    label="Open Create Claim"
                  />
                  <ActionCard
                    title="Open Claims Registry"
                    body="Review created claims, lifecycle state, and downstream governance actions inside the workspace claim registry."
                    href={`/workspace/${workspaceId}/claims`}
                    label="Open Claims"
                  />
                  <ActionCard
                    title="Review Billing & Governance"
                    body="Inspect plan posture, billing activation, and workspace governance signals that affect claim creation capacity."
                    href={`/workspace/${workspaceId}/settings`}
                    label="Open Settings & Billing"
                  />
                </section>
              </>
            )}

            <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <GuidanceItem
                step="Registry 1"
                title="Creation Lives in One Place"
                body="Use Create Claim as the primary authoring surface. This registry page should govern readiness, not duplicate the full drafting form."
              />
              <GuidanceItem
                step="Registry 2"
                title="Claims Are Workspace-Governed"
                body="Claim capacity, role permissions, and billing posture should be reviewed here before operators create additional draft claims."
              />
              <GuidanceItem
                step="Registry 3"
                title="Evidence Flows from Ledger"
                body="Schema posture should remain connected to ledger evidence and claims registry review, not act as a second isolated builder."
              />
              <GuidanceItem
                step="Registry 4"
                title="Lifecycle Progression Happens After Drafting"
                body="After draft creation, claims proceed through verification, publication, and locking from the claims workflow, not from this registry page."
              />
            </section>
          </>
        )}
      </main>
    </div>
  );
}
