"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { useMemo } from "react";
import { useAuth } from "../../components/AuthProvider";

const ImportForm = dynamic(() => import("../../components/ImportForm"), {
  ssr: false,
  loading: () => (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading import form...</div>
  ),
});

function SourceCard({
  title,
  subtitle,
  status,
  tone,
  bullets,
}: {
  title: string;
  subtitle: string;
  status: string;
  tone: "active" | "ready" | "planned";
  bullets: string[];
}) {
  const toneClass =
    tone === "active"
      ? "border-emerald-200 bg-emerald-50 text-emerald-900"
      : tone === "ready"
        ? "border-blue-200 bg-blue-50 text-blue-900"
        : "border-amber-200 bg-amber-50 text-amber-900";

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          <div className="mt-1 text-sm text-slate-500">{subtitle}</div>
        </div>

        <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${toneClass}`}>
          {status}
        </span>
      </div>

      <div className="mt-4 space-y-2 text-sm text-slate-600">
        {bullets.map((bullet) => (
          <div key={bullet}>• {bullet}</div>
        ))}
      </div>
    </div>
  );
}

function PipelineCard({
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
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {step}
      </div>
      <h3 className="mt-2 text-lg font-semibold text-slate-900">{title}</h3>
      <div className="mt-2 text-sm leading-6 text-slate-600">{body}</div>
    </div>
  );
}

function ReadinessCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
      <div className="mt-2 text-xs text-slate-500">{hint}</div>
    </div>
  );
}

export default function ImportPage() {
  const { user, workspaces, loading, logout } = useAuth();

  const firstWorkspace = workspaces[0] ?? null;
  const workspaceHref = firstWorkspace
    ? `/workspace/${firstWorkspace.workspace_id}/dashboard`
    : "/";

  const workspaceCount = useMemo(() => workspaces.length, [workspaces]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <div className="text-lg font-bold tracking-tight">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">Broker Integration · Trade Import Hub</div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
            >
              Home
            </Link>

            <Link
              href="/claims"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
            >
              Public Claims
            </Link>

            {loading ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-500">
                Loading session...
              </div>
            ) : user ? (
              <>
                <Link
                  href={workspaceHref}
                  className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  Open Workspace
                </Link>

                <button
                  onClick={logout}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-4xl">
              <div className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                Broker Integration Layer
              </div>
              <h1 className="mt-2 text-3xl font-bold">Trade Import Hub</h1>
              <p className="mt-3 text-slate-600">
                This surface is the ingestion entry point for canonical trade evidence.
                Manual import is active now. CSV, MT5, and IBKR-ready pipelines should plug
                into the same normalization and verification workflow so downstream claims,
                trust scoring, and public proofs remain broker-neutral.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
              <div>
                <span className="font-medium text-slate-900">Session:</span>{" "}
                {loading ? "loading" : user ? "authenticated" : "guest"}
              </div>
              <div className="mt-2">
                <span className="font-medium text-slate-900">Workspaces:</span>{" "}
                {workspaceCount}
              </div>
              <div className="mt-2">
                <span className="font-medium text-slate-900">Current mode:</span>{" "}
                integration-ready import
              </div>
            </div>
          </div>
        </section>

        <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ReadinessCard
            label="Manual Import"
            value="Active"
            hint="Current operator-ready ingestion surface"
          />
          <ReadinessCard
            label="CSV Pipeline"
            value="Ready"
            hint="Next connector path for structured batch trade uploads"
          />
          <ReadinessCard
            label="MT5 Adapter"
            value="Planned"
            hint="Broker/platform ingestion through normalization layer"
          />
          <ReadinessCard
            label="IBKR Adapter"
            value="Planned"
            hint="Institutional ingestion bridge for verified trading workflows"
          />
        </section>

        <section className="mb-8">
          <div className="mb-4">
            <h2 className="text-2xl font-semibold">Import Sources</h2>
            <div className="mt-2 text-sm text-slate-500">
              Every source should resolve into the same canonical trade schema before claims,
              evidence review, trust scoring, and public verification are generated.
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
            <SourceCard
              title="Manual Entry"
              subtitle="Human-entered trades"
              status="active"
              tone="active"
              bullets={[
                "Fastest path for controlled testing",
                "Good for QA and workflow validation",
                "Already connected to current import form",
              ]}
            />

            <SourceCard
              title="CSV Upload"
              subtitle="Batch ingestion pipeline"
              status="ready"
              tone="ready"
              bullets={[
                "Best next operational import path",
                "Maps broker exports into canonical trades",
                "Supports preview, validation, and normalization",
              ]}
            />

            <SourceCard
              title="MT5 Connector"
              subtitle="MetaTrader-ready adapter"
              status="planned"
              tone="planned"
              bullets={[
                "Platform-specific export ingestion",
                "Timestamp and symbol normalization needed",
                "Should flow into same trust/evidence system",
              ]}
            />

            <SourceCard
              title="IBKR Connector"
              subtitle="Institutional broker adapter"
              status="planned"
              tone="planned"
              bullets={[
                "Broker-neutral evidence ingestion goal",
                "Requires account/source attribution mapping",
                "Should preserve auditability across imports",
              ]}
            />
          </div>
        </section>

        <section className="mb-8">
          <div className="mb-4">
            <h2 className="text-2xl font-semibold">Canonical Import Pipeline</h2>
            <div className="mt-2 text-sm text-slate-500">
              Import quality matters because bad ingestion contaminates claims, profiles, and trust outputs.
            </div>
          </div>

          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
            <PipelineCard
              step="Step 1"
              title="Ingest"
              body="Receive trades from manual entry, CSV, MT5, IBKR, or future providers."
            />
            <PipelineCard
              step="Step 2"
              title="Normalize"
              body="Map symbols, timestamps, quantities, sides, and account/member metadata into one canonical schema."
            />
            <PipelineCard
              step="Step 3"
              title="Validate"
              body="Reject malformed rows, detect missing required fields, and surface import-quality feedback."
            />
            <PipelineCard
              step="Step 4"
              title="Route"
              body="Store clean trades into the ledger so claims, evidence packs, and trust layers remain defensible."
            />
          </div>
        </section>

        <section className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-3xl">
              <h2 className="text-2xl font-semibold">Current Import Surface</h2>
              <p className="mt-2 text-slate-600">
                The active form below remains the current ingestion surface. It should continue
                to work as the canonical fallback even after CSV and broker connectors are introduced.
              </p>
            </div>

            {firstWorkspace ? (
              <Link
                href={`/workspace/${firstWorkspace.workspace_id}/ledger`}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
              >
                Open Ledger
              </Link>
            ) : null}
          </div>

          <div className="mt-6">
            <ImportForm />
          </div>
        </section>

        <section className="rounded-2xl border bg-white p-6 shadow-sm">
          <h2 className="text-2xl font-semibold">Integration Notes</h2>
          <div className="mt-3 grid gap-4 lg:grid-cols-3">
            <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
              <div className="font-semibold text-slate-900">Broker-neutral posture</div>
              <div className="mt-2">
                Claims and trust outputs should never depend on a single broker format.
                Every provider must collapse into the same evidence model.
              </div>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
              <div className="font-semibold text-slate-900">Auditability first</div>
              <div className="mt-2">
                Import pipelines must preserve row-level traceability so disputes and verification
                surfaces can always map back to canonical source evidence.
              </div>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
              <div className="font-semibold text-slate-900">Validation before trust</div>
              <div className="mt-2">
                Trust scoring starts after ingestion quality is defended. Dirty imports should be
                blocked or quarantined before they contaminate claims and profile reputation.
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}