"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import ImportForm from "../../../../components/ImportForm";
import { useAuth } from "../../../../components/AuthProvider";
import { api, type WorkspaceUsageSummary } from "../../../../lib/api";

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatNumber(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toLocaleString();
}

function getUsageTone(ratio?: number | null, limitReached?: boolean) {
  if (limitReached) {
    return {
      wrapper: "border-amber-200 bg-amber-50",
      badge: "border-amber-200 bg-white text-amber-700",
      label: "Import blocked",
    };
  }

  if (ratio !== null && ratio !== undefined && Number(ratio) >= 0.8) {
    return {
      wrapper: "border-amber-200 bg-amber-50",
      badge: "border-amber-200 bg-white text-amber-700",
      label: "Near trade ceiling",
    };
  }

  return {
    wrapper: "border-slate-200 bg-white",
    badge: "border-slate-200 bg-slate-50 text-slate-700",
    label: "Capacity available",
  };
}

function WorkflowStage({
  label,
  status,
}: {
  label: string;
  status: "complete" | "active" | "pending";
}) {
  const className =
    status === "complete"
      ? "border-green-200 bg-green-50 text-green-800"
      : status === "active"
        ? "border-blue-200 bg-blue-50 text-blue-800"
        : "border-slate-200 bg-white text-slate-600";

  return (
    <div className={`rounded-full border px-4 py-2 text-sm font-semibold ${className}`}>
      {label}
    </div>
  );
}

function SourceCard({
  title,
  description,
  status,
  tone = "neutral",
  selected = false,
  recommended = false,
}: {
  title: string;
  description: string;
  status: string;
  tone?: "neutral" | "blue" | "amber" | "dark";
  selected?: boolean;
  recommended?: boolean;
}) {
  const toneClass =
    tone === "dark"
      ? "border-slate-900 bg-slate-950 text-white"
      : tone === "blue"
        ? "border-blue-200 bg-blue-50 text-blue-900"
        : tone === "amber"
          ? "border-amber-200 bg-amber-50 text-amber-900"
          : "border-slate-200 bg-white text-slate-900";

  const badgeClass =
    tone === "dark"
      ? "border-slate-700 bg-slate-900 text-white"
      : tone === "blue"
        ? "border-blue-200 bg-white text-blue-700"
        : tone === "amber"
          ? "border-amber-200 bg-white text-amber-700"
          : "border-slate-200 bg-slate-50 text-slate-700";

  return (
    <div className={`rounded-2xl border p-5 shadow-sm ${toneClass}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xl font-semibold">{title}</div>
          <div className={`mt-2 text-sm leading-6 ${tone === "dark" ? "text-slate-200" : "text-current/80"}`}>
            {description}
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {recommended ? (
            <span className={`rounded-full border px-3 py-1 text-[11px] font-semibold ${badgeClass}`}>
              recommended
            </span>
          ) : null}
          <span className={`rounded-full border px-3 py-1 text-[11px] font-semibold ${badgeClass}`}>
            {status}
          </span>
          {selected ? (
            <span className={`rounded-full border px-3 py-1 text-[11px] font-semibold ${badgeClass}`}>
              selected
            </span>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function PostImportCard({
  title,
  description,
  href,
  label,
}: {
  title: string;
  description: string;
  href: string;
  label: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-base font-semibold text-slate-900">{title}</div>
      <div className="mt-2 text-sm leading-6 text-slate-600">{description}</div>
      <div className="mt-4">
        <Link
          href={href}
          className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50"
        >
          {label}
        </Link>
      </div>
    </div>
  );
}

export default function WorkspaceImportPage() {
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
  const canImportTradesByRole = workspaceRole === "owner" || workspaceRole === "operator";

  const tradeUsage = usage?.usage?.trades;
  const tradeLimitReached =
    (tradeUsage?.limit ?? 0) > 0 && (tradeUsage?.used ?? 0) >= (tradeUsage?.limit ?? 0);

  const canImportTrades = canImportTradesByRole && !tradeLimitReached;
  const usageTone = getUsageTone(tradeUsage?.ratio, tradeLimitReached);

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

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading import page...</div>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-5xl px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace import page.
          </div>
        </main>
      </div>
    );
  }

  const workflowTradeStatus: "complete" | "active" | "pending" =
    (tradeUsage?.used ?? 0) > 0 ? "complete" : canImportTrades ? "active" : "pending";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Ledger Intake</div>
            <h1 className="mt-2 text-4xl font-bold">Trade Import</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Bring broker data into the canonical trade ledger. Import is the first operational
              step in the governed verification workflow.
            </p>
          </div>

          <div className="rounded-xl border bg-white px-4 py-3 text-sm shadow-sm">
            <div className="text-slate-500">Workspace Role</div>
            <div className="mt-1 font-semibold">{workspaceRole}</div>
          </div>
        </div>

        <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Intake guidance
          </div>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">
            Choose the fastest path into the canonical ledger
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600">
            For first-time setup, CSV upload is the simplest route. MT5 and IBKR adapters support
            broker-export workflows, while auto-import and live ingestion are designed for
            recurring operational intake.
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <WorkflowStage label="Import" status={workflowTradeStatus} />
            <div className="text-slate-300">→</div>
            <WorkflowStage label="Ledger Review" status={(tradeUsage?.used ?? 0) > 0 ? "active" : "pending"} />
            <div className="text-slate-300">→</div>
            <WorkflowStage label="Create Claim" status="pending" />
            <div className="text-slate-300">→</div>
            <WorkflowStage label="Verify / Publish" status="pending" />
          </div>
        </div>

        {usageLoading ? (
          <div className="mb-6 rounded-2xl border bg-white p-6 shadow-sm">
            Loading workspace trade usage...
          </div>
        ) : tradeUsage ? (
          <div className={`mb-8 rounded-2xl border p-6 shadow-sm ${usageTone.wrapper}`}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-semibold">Trade Usage</h2>
                <p className="mt-2 text-sm leading-7 text-slate-600">
                  Import rights are governed by workspace role and current trade-capacity posture.
                </p>
              </div>

              <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${usageTone.badge}`}>
                {usageTone.label}
              </span>
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-3">
              <div>
                <div className="text-sm text-slate-500">Used</div>
                <div className="mt-1 text-2xl font-semibold">{formatNumber(tradeUsage.used)}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Limit</div>
                <div className="mt-1 text-2xl font-semibold">{formatNumber(tradeUsage.limit)}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Utilization</div>
                <div className="mt-1 text-2xl font-semibold">{formatPercent(tradeUsage.ratio)}</div>
              </div>
            </div>

            {tradeLimitReached ? (
              <div className="mt-4 rounded-xl border border-amber-200 bg-amber-100 px-4 py-3 text-sm text-amber-800">
                Trade limit reached. Upgrade the workspace plan before importing additional trades.
              </div>
            ) : null}
          </div>
        ) : null}

        <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Broker Integration Console</h2>
          <p className="mt-2 text-sm leading-7 text-slate-600">
            Select the right ingestion route for the operator and data source you are working with.
          </p>

          <div className="mt-5 grid gap-4 md:grid-cols-3">
            <SourceCard
              title="CSV Upload"
              description="Fastest manual onboarding path. Best for first-time setup, backfill, and batch import of broker exports."
              status="active"
              tone="dark"
              selected
              recommended
            />
            <SourceCard
              title="MT5 Adapter"
              description="Use when operating from MetaTrader export workflows and scheduled broker-file ingestion."
              status="active"
              tone="blue"
            />
            <SourceCard
              title="IBKR Adapter"
              description="Use for institutional broker-export ingestion and repeatable import orchestration."
              status="active"
              tone="amber"
            />
          </div>

          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-base font-semibold text-slate-900">Selected source</div>
              <div className="mt-2 text-sm text-slate-700">CSV Upload</div>
              <div className="mt-1 text-sm text-slate-500">Recommended for first-time import</div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-base font-semibold text-slate-900">Scheduled intake</div>
              <div className="mt-2 text-sm text-slate-700">Available</div>
              <div className="mt-1 text-sm text-slate-500">
                Recurring import cadence can be enabled for CSV, MT5, and IBKR workflows.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-base font-semibold text-slate-900">Live ingestion</div>
              <div className="mt-2 text-sm text-slate-700">Available</div>
              <div className="mt-1 text-sm text-slate-500">
                Stream-event and webhook ingestion routes are active in backend infrastructure.
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-slate-600">
            CSV, MT5, and IBKR all feed the same canonical broker-neutral ledger. The ingestion
            path changes transport and orchestration, not the underlying verification model.
          </div>
        </div>

        {!canImportTradesByRole ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Read-only access</h2>
            <p className="mt-2 text-slate-600">
              Your current workspace role is <span className="font-medium">{workspaceRole}</span>.
              You can review ledger and claims data, but you cannot import trades.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/ledger`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Ledger
              </Link>
              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Claim Library
              </Link>
            </div>
          </div>
        ) : tradeLimitReached ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-amber-900">Trade import blocked</h2>
            <p className="mt-2 text-amber-800">
              This workspace has reached its trade limit. Upgrade the plan before importing more
              trades.
            </p>

            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/settings`}
                className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium hover:bg-amber-100"
              >
                Review Plan & Billing
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
            <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                Primary ingestion action
              </div>
              <h2 className="mt-2 text-2xl font-semibold">Upload source file and control intake</h2>
              <p className="mt-2 text-sm leading-7 text-slate-600">
                Upload a broker export file, inspect ingestion results, and configure recurring or
                live intake from the same operational surface.
              </p>

              <div className="mt-5">
                <ImportForm workspaceId={workspaceId} />
              </div>
            </div>

            <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                After import
              </div>
              <h2 className="mt-2 text-2xl font-semibold">Move into governed verification workflow</h2>
              <p className="mt-2 text-sm leading-7 text-slate-600">
                Once trades are ingested, the next step is to review canonical ledger output and
                create a claim that defines what should be verified and published.
              </p>

              <div className="mt-5 grid gap-4 md:grid-cols-3">
                <PostImportCard
                  title="Review ledger"
                  description="Inspect normalized broker records, confirm timestamps, symbols, and ingestion quality."
                  href={`/workspace/${workspaceId}/ledger`}
                  label="Open Ledger"
                />
                <PostImportCard
                  title="Create claim"
                  description="Define scope, methodology, included members, and symbols for the record you want to verify."
                  href={`/workspace/${workspaceId}/schema`}
                  label="Open Claim Builder"
                />
                <PostImportCard
                  title="Inspect evidence"
                  description="Review claim-linked evidence and verification artifacts once records move into governed workflows."
                  href={`/workspace/${workspaceId}/evidence`}
                  label="Open Evidence Review"
                />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}