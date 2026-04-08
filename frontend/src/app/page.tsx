"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useAuth } from "../components/AuthProvider";

function SurfaceCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold tracking-tight text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
    </div>
  );
}

function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
      <div className="mt-2 text-sm text-slate-600">{hint}</div>
    </div>
  );
}

export default function HomePage() {
  const { user, workspaces, loading, logout } = useAuth();

  const firstWorkspace = workspaces[0] ?? null;

  const primaryWorkspaceHref = useMemo(() => {
    if (!firstWorkspace) return null;
    return `/workspace/${firstWorkspace.workspace_id}/dashboard`;
  }, [firstWorkspace]);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <div className="text-lg font-bold tracking-tight">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">Verified Trading Claims OS</div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {loading ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-500">
                Loading session...
              </div>
            ) : user ? (
              <>
                {primaryWorkspaceHref ? (
                  <Link
                    href={primaryWorkspaceHref}
                    className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                  >
                    Open Workspace
                  </Link>
                ) : null}

                <button
                  onClick={logout}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="max-w-4xl">
          <div className="inline-flex rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-600 shadow-sm">
            Broker-neutral verification infrastructure
          </div>

          <h1 className="mt-6 text-5xl font-bold tracking-tight text-slate-900 sm:text-6xl">
            Turn trading activity into verifiable claims, canonical ledgers, and dispute-ready proof.
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-600">
            Trading Truth Layer gives trading operators, communities, and serious performance
            businesses a governance-grade system for ingestion, verification, claim publication,
            and evidence preservation.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            {user && primaryWorkspaceHref ? (
              <Link
                href={primaryWorkspaceHref}
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Enter Workspace
              </Link>
            ) : (
              <>
                <Link
                  href="/register"
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  Create Workspace
                </Link>
                <Link
                  href="/login"
                  className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
                >
                  Sign In
                </Link>
              </>
            )}

            <Link
              href="/public/claims"
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
            >
              Explore Public Claims
            </Link>
          </div>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-3">
          <MetricCard
            label="Verification Posture"
            value="Governance-first"
            hint="Claims are structured, hashed, attributable, and evidence-backed."
          />
          <MetricCard
            label="Ingestion Surface"
            value="CSV · MT5 · IBKR · Webhook"
            hint="Multiple ingestion paths route into the same canonical trade pipeline."
          />
          <MetricCard
            label="Operational Output"
            value="Public proof"
            hint="Verified claims can become auditable, externally checkable trust surfaces."
          />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="grid gap-4 md:grid-cols-3">
          <SurfaceCard
            title="Canonical Trade Ledger"
            description="Normalize imported trading activity into a durable, queryable source of truth that supports verification, governance, and downstream evidence generation."
          />
          <SurfaceCard
            title="Claims Schema Engine"
            description="Define exactly what is included in a claim, including time window, participants, symbols, exclusions, and methodology, with full lineage across versions."
          />
          <SurfaceCard
            title="Evidence Pack Generator"
            description="Produce dispute-ready artifacts with reproducible metrics, trade-set hashes, lifecycle traceability, and externally reviewable verification surfaces."
          />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="max-w-3xl">
            <h2 className="text-2xl font-semibold text-slate-900">Commercial posture</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              The product is designed around a controlled commercial ladder:
              Sandbox for limited evaluation, then Starter, Pro, Growth, and Business for real
              operational deployment.
            </p>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm font-semibold text-slate-900">Sandbox</div>
              <div className="mt-2 text-sm text-slate-600">
                Limited evaluation environment for product proof, onboarding, and safe experimentation.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm font-semibold text-slate-900">Paid operational tiers</div>
              <div className="mt-2 text-sm text-slate-600">
                Starter and above unlock real governed capacity for claims, trades, members,
                verification workflows, and commercial trust surfaces.
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}