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
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-7 text-slate-600">{description}</p>
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
      title: "Deterministic claim definition",
      description:
        "Define exactly what a claim includes so results can be recomputed, audited, and independently reviewed.",
    },
    {
      title: "Canonical trade ledger",
      description:
        "All ingestion routes normalize into a single source of truth used across claims, evidence, and verification.",
    },
    {
      title: "Evidence-first computation",
      description:
        "Metrics and performance outputs are derived directly from underlying trade evidence, not detached summaries.",
    },
    {
      title: "Verification surfaces",
      description:
        "Each claim produces both a public presentation layer and a canonical verification route.",
    },
    {
      title: "Governed lifecycle",
      description:
        "Draft, verify, publish, and lock states enforce discipline and prevent silent mutation of claims.",
    },
    {
      title: "Audit and traceability",
      description:
        "Every claim maintains a full lifecycle history suitable for internal review and external validation.",
    },
  ];

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      
      {/* HEADER */}
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <div className="text-lg font-bold">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">
              Verified Trading Claims OS
            </div>
          </div>

          <div className="flex items-center gap-3">
            {loading ? (
              <div className="text-sm text-slate-500">Loading...</div>
            ) : user ? (
              <>
                {primaryWorkspaceHref && (
                  <Link
                    href={primaryWorkspaceHref}
                    className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  >
                    Open Workspace
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="rounded-xl border px-4 py-2 text-sm"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="rounded-xl border px-4 py-2 text-sm">
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="rounded-xl bg-slate-900 px-4 py-2 text-sm text-white"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* HERO */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="max-w-4xl">
          <div className="inline-flex rounded-full border px-4 py-2 text-xs uppercase text-slate-600">
            Trust infrastructure for trading
          </div>

          <h1 className="mt-6 text-5xl font-bold leading-tight">
            Turn trading activity into verifiable performance records,
            canonical ledgers, and dispute-ready proof.
          </h1>

          <p className="mt-6 text-lg text-slate-600">
            Replace screenshots and unverifiable claims with structured,
            cryptographically verifiable records that are auditable and externally provable.
          </p>

          {/* CTA */}
          <div className="mt-8 flex gap-3">
            {user && primaryWorkspaceHref ? (
              <Link
                href={primaryWorkspaceHref}
                className="rounded-xl bg-slate-900 px-6 py-3 text-white"
              >
                Enter Workspace
              </Link>
            ) : (
              <Link
                href="/register"
                className="rounded-xl bg-slate-900 px-6 py-3 text-white"
              >
                Create Workspace
              </Link>
            )}

            <Link
              href="/public/claims"
              className="rounded-xl border px-6 py-3"
            >
              Explore Public Proof
            </Link>
          </div>
        </div>
      </section>

      {/* 🔥 NEW: PROOF OUTPUTS */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <h2 className="text-2xl font-semibold">
          What the system produces
        </h2>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <SurfaceCard
            title="Evidence JSON"
            description="Machine-readable structured evidence payload for systems, audits, and automation."
          />
          <SurfaceCard
            title="Evidence ZIP bundle"
            description="Packaged archive for dispute handling, sharing, and long-term storage."
          />
          <SurfaceCard
            title="Claim report PDF"
            description="Presentation-grade report for investors, institutions, and formal review."
          />
          <SurfaceCard
            title="Public record"
            description="Clean presentation surface for distributing claim results."
          />
          <SurfaceCard
            title="Verification route"
            description="Canonical proof layer for independent verification."
          />
          <SurfaceCard
            title="Integrity hashes"
            description="Claim hash and trade fingerprint ensure tamper-evident trust."
          />
        </div>
      </section>

      {/* PROBLEM */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <h2 className="text-2xl font-semibold">
          The problem: trading has no trust infrastructure
        </h2>

        <div className="mt-4 space-y-2 text-slate-600">
          <div>• Performance claims are easy to fake</div>
          <div>• Screenshots are not verifiable</div>
          <div>• Results are inconsistent</div>
          <div>• Disputes are expensive</div>
        </div>

        <div className="mt-6 font-semibold text-slate-900">
          Trading Truth Layer turns trading activity into verifiable proof.
        </div>
      </section>

      {/* FEATURES */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {featureCards.map((card) => (
            <SurfaceCard key={card.title} {...card} />
          ))}
        </div>
      </section>

      {/* COMMERCIAL */}
      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="rounded-3xl border bg-white p-8">
          <h2 className="text-2xl font-semibold">
            Controlled commercial rollout
          </h2>

          <div className="mt-4 text-sm text-slate-600">
            Sandbox → Starter → Growth → Business
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="border p-4 rounded-xl">
              Sandbox: safe evaluation and onboarding
            </div>
            <div className="border p-4 rounded-xl">
              Paid tiers unlock governance and scale
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}