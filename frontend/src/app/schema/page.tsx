"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { useMemo } from "react";
import { useAuth } from "../../components/AuthProvider";

const ClaimSchemaForm = dynamic(() => import("../../components/ClaimSchemaForm"), {
  ssr: false,
  loading: () => (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="text-sm font-medium text-slate-600">Loading schema builder...</div>
    </div>
  ),
});

function StatusCard({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-7 text-slate-600">{body}</p>
    </div>
  );
}

function StepCard({
  step,
  title,
  body,
}: {
  step: string;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
        {step}
      </div>
      <h3 className="mt-4 text-xl font-semibold tracking-tight text-slate-950">{title}</h3>
      <p className="mt-3 text-sm leading-7 text-slate-600">{body}</p>
    </div>
  );
}

function Pill({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
      {children}
    </span>
  );
}

export default function SchemaPage() {
  const { user, workspaces, loading, logout } = useAuth();

  const firstWorkspace = workspaces[0] ?? null;

  const workspaceHref = useMemo(() => {
    if (!firstWorkspace) return "/";
    return `/workspace/${firstWorkspace.workspace_id}/dashboard`;
  }, [firstWorkspace]);

  const sessionSummary = useMemo(() => {
    if (loading) return "Authenticating current user and workspace session.";
    if (user) return `Signed in as ${user.name}.`;
    return "You are not signed in yet.";
  }, [loading, user]);

  const workspaceSummary = useMemo(() => {
    if (!workspaces.length) {
      return "No connected workspace detected yet.";
    }

    if (workspaces.length === 1) {
      return "1 workspace available for claim operations.";
    }

    return `${workspaces.length} workspaces available for claim operations.`;
  }, [workspaces]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <div className="text-lg font-bold tracking-tight text-slate-950">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">Claims Schema Builder</div>
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
                  onClick={() => logout()}
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

      <main className="mx-auto max-w-7xl px-6 py-10">
        <section className="mb-8 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm md:p-8">
          <div className="grid gap-6 xl:grid-cols-[1.35fr_0.9fr]">
            <div>
              <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-slate-600">
                Guided Claim Creation
              </div>

              <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 md:text-4xl">
                Claims Schema Builder
              </h1>

              <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">
                Define the exact scope, evidence universe, methodology, and visibility posture for a
                lifecycle-governed performance claim. This page is the structured entry point for
                creating claims that can later be verified, published, locked, and publicly audited.
              </p>

              <div className="mt-5 flex flex-wrap items-center gap-2">
                <Pill>draft-first workflow</Pill>
                <Pill>scope-controlled evidence</Pill>
                <Pill>public verification compatible</Pill>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
              <StatusCard title="Session State" body={sessionSummary} />
              <StatusCard title="Workspace Readiness" body={workspaceSummary} />
            </div>
          </div>
        </section>

        <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StepCard
            step="Step 1"
            title="Define Claim Identity"
            body="Set the claim name and reporting period. This anchors the record and its time-bounded verification scope."
          />
          <StepCard
            step="Step 2"
            title="Build Scope"
            body="Choose included members, symbols, and explicit exclusions so the evidence set is deterministic and reviewable."
          />
          <StepCard
            step="Step 3"
            title="Set Exposure"
            body="Choose private, unlisted, or public exposure so later lifecycle actions align with intended verification visibility."
          />
          <StepCard
            step="Step 4"
            title="Progress Lifecycle"
            body="After creation, move the draft through verify, publish, and lock to create a public trust-grade verification record."
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.45fr_0.85fr]">
          <div>
            <ClaimSchemaForm />
          </div>

          <aside className="space-y-5">
            <StatusCard
              title="Builder Rules"
              body="Claims should be created as drafts first. Scope and methodology should be finalized before verification because downstream lifecycle transitions depend on this definition."
            />

            <StatusCard
              title="Visibility Guidance"
              body="Private keeps the claim internal. Unlisted allows direct verification links without public directory exposure. Public makes the claim discoverable in the public registry after lifecycle progression."
            />

            <StatusCard
              title="Recommended Sequence"
              body="Create draft → review scope → verify claim → publish claim → lock claim → review public verification surface."
            />
          </aside>
        </section>
      </main>
    </div>
  );
}