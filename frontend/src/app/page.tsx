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
      <p className="mt-2 text-sm leading-7 text-slate-600">{description}</p>
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
      <div className="mt-2 text-sm leading-7 text-slate-600">{hint}</div>
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

  const featureCards = [
    {
      title: "From screenshots to proof",
      description:
        "Replace unverifiable trading claims with structured, cryptographically verifiable records that can be independently reviewed.",
    },
    {
      title: "Canonical trade ledger",
      description:
        "Normalize raw trading activity into a durable, queryable, and audit-ready source of truth for claims and governance.",
    },
    {
      title: "Claim definition engine",
      description:
        "Define exactly what a claim includes — time window, members, symbols, exclusions, and methodology — with full lineage across versions.",
    },
    {
      title: "Verification layer",
      description:
        "Every claim produces a verification surface with identity, integrity, lifecycle state, and externally reviewable trust posture.",
    },
    {
      title: "Evidence-grade outputs",
      description:
        "Generate dispute-ready artifacts with trade-level evidence, reproducible metrics, lifecycle traceability, and public proof surfaces.",
    },
    {
      title: "Multi-source ingestion",
      description:
        "CSV, MT5, IBKR, and webhooks all route into a unified verification pipeline that feeds the same canonical ledger.",
    },
  ];

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
          <div className="inline-flex rounded-full border border-slate-200 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600 shadow-sm">
            Trust infrastructure for trading
          </div>

          <h1 className="mt-6 text-5xl font-bold leading-[1.05] tracking-tight text-slate-900 sm:text-6xl">
            Turn trading activity into
            <br />
            verifiable performance records,
            <br />
            canonical ledgers, and
            <br />
            dispute-ready proof.
          </h1>

          <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-600">
            Trading Truth Layer replaces screenshots and unverifiable claims with
            cryptographically verifiable records. Every claim becomes auditable,
            attributable, and externally provable.
          </p>

          <div className="mt-6 text-sm text-slate-500">
            Built for trading communities, prop firms, educators, and serious operators.
          </div>

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
              Explore Public Proof
            </Link>
          </div>
        </div>

        <div className="mt-16 max-w-3xl">
          <h2 className="text-2xl font-semibold text-slate-900">
            The problem: trading has no trust infrastructure
          </h2>

          <div className="mt-4 space-y-2 text-slate-600">
            <div>• Performance claims are easy to fake</div>
            <div>• Screenshots are not verifiable</div>
            <div>• Results are hard to standardize</div>
            <div>• Disputes are expensive and subjective</div>
          </div>

          <div className="mt-6 font-medium text-slate-700">
            Trading Truth Layer fixes this by turning activity into verifiable proof.
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
            hint="Verified claims become auditable, externally checkable trust surfaces."
          />
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {featureCards.map((card) => (
            <SurfaceCard
              key={card.title}
              title={card.title}
              description={card.description}
            />
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="max-w-3xl">
            <h2 className="text-2xl font-semibold text-slate-900">Commercial rollout</h2>
            <p className="mt-3 text-sm leading-7 text-slate-600">
              Trading Truth Layer is deployed through a controlled progression.
              Teams can evaluate safely, then move into production-grade operational tiers as
              verification workflows mature.
            </p>
          </div>

          <div className="mt-6 space-y-3 text-sm text-slate-600">
            <div>
              <span className="font-semibold text-slate-900">Sandbox:</span> evaluation,
              onboarding, and safe experimentation
            </div>

            <div>
              <span className="font-semibold text-slate-900">Starter → Growth:</span>
              production-grade claim workflows, verification surfaces, and governed capacity
            </div>

            <div>
              <span className="font-semibold text-slate-900">Business:</span>
              full-scale governance, audit, and external trust infrastructure
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm font-semibold text-slate-900">Sandbox</div>
              <div className="mt-2 text-sm leading-6 text-slate-600">
                Limited evaluation environment for product proof, onboarding, and safe
                experimentation before commercial deployment.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-sm font-semibold text-slate-900">Operational tiers</div>
              <div className="mt-2 text-sm leading-6 text-slate-600">
                Paid tiers unlock governed capacity for claims, trades, members, verification
                workflows, and externally reviewable trust surfaces.
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}