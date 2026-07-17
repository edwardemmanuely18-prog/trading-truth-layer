"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useAuth } from "../components/AuthProvider";
import { useRouter } from "next/navigation";

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

  const router = useRouter();

  const [isExploring, setIsExploring] = useState(false);

  const firstWorkspace = workspaces[0] ?? null;

  const primaryWorkspaceHref = useMemo(() => {
    if (!firstWorkspace) return null;
    return `/workspace/${firstWorkspace.workspace_id}/dashboard`;
  }, [firstWorkspace]);

  const featureCards = [
    {
      title: "Evidence Registry",
      description:
        "Canonical evidence storage for imported trading activity, normalized into a governed institutional record.",
    },
    {
      title: "Trading Verification System (TVS)",
      description:
        "The canonical verification engine that computes every claim, metric, report, and public verification surface from a single source of truth.",
    },
    {
      title: "Institutional Investigation System (IIS)",
      description:
        "Institutional reasoning engine that evaluates verified trading records across multiple investigation domains to produce allocator decisions, findings, recommendations and institutional readiness assessments.",
    },
    {
      title: "Verification Engine",
      description:
        "Produces institutional verification certificates, trust metrics, governance scores, and verification coverage.",
    },
    {
      title: "Evidence Graph",
      description:
        "Visualizes relationships between trades, evidence, claims, reports, and verification artifacts for complete traceability.",
    },
    {
      title: "Institutional Reporting",
      description:
        "Generate allocator reports, claim reports, governance reports, and due-diligence documentation directly from verified evidence.",
    },
    {
      title: "Governance & Audit Trail",
      description:
        "Every action is governed, auditable, cryptographically traceable, and protected against silent modification.",
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
                  onClick={() => logout()}
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
            Turn trading activity into institutional verification,
            governed evidence and independently verifiable trust.
          </h1>

          <p className="mt-6 text-lg text-slate-600">
            Trading Truth Layer transforms raw trading activity into governed evidence,
            institutional reports, public verification records and cryptographically
            verifiable proof suitable for investors, allocators, regulators and external reviewers.
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

            <button
                disabled={isExploring}
                onClick={() => {
                    setIsExploring(true);
                    router.push("/leaderboard");
                }}
                className="rounded-xl border px-6 py-3 transition hover:bg-slate-100 disabled:opacity-60"
            >
                {isExploring
                    ? "Exploring Public Proof..."
                    : "Explore Public Proof"}
            </button>
          </div>
        </div>
      </section>

      {/* 🔥 NEW: PROOF OUTPUTS */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <h2 className="text-2xl font-semibold">
          Institutional Outputs
        </h2>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <SurfaceCard
            title="Verification Certificate"
            description="Institutional verification certificate containing trust metrics, governance score and verification outcome."
          />
          <SurfaceCard
            title="Allocator Due-Diligence Report"
            description="Institutional allocator report generated directly from governed evidence and verification output."
          />
          <SurfaceCard
            title="Institutional Investigation Report"
            description="Institutional allocator investigation output containing findings, recommendations, confidence scores and final investment decisions generated from canonical investigation domains."
          />
          <SurfaceCard
            title="Institutional Claim Report"
            description="Presentation-grade report suitable for investors, institutions and compliance review."
          />
          <SurfaceCard
            title="Evidence Bundle"
            description="Governed archive containing canonical evidence, verification artifacts and supporting records."
          />
          <SurfaceCard
            title="Public Verification Record"
            description="Public verification surface exposing immutable verification results without exposing private trading data."
          />
          <SurfaceCard
            title="Canonical Evidence Graph"
            description="Relationship graph connecting evidence, claims, reports and verification history into a single trust network."
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

      <section className="mx-auto max-w-7xl px-6 pb-16">

        <h2 className="text-2xl font-semibold">
          Why institutions use Trading Truth Layer
        </h2>

        <div className="mt-6 grid gap-4 md:grid-cols-3">

          <SurfaceCard
            title="Evidence-first"
            description="Every performance metric originates from governed trading evidence."
          />

          <SurfaceCard
            title="Independent verification"
            description="Verification results can be validated independently without trusting the publisher."
          />

          <SurfaceCard
            title="Allocator ready"
            description="Generate professional due-diligence documentation directly from verified claims."
          />

          <SurfaceCard
            title="Governed lifecycle"
            description="Claims progress through Draft, Verify, Publish and Lock with full audit history."
          />

          <SurfaceCard
            title="Evidence Graph"
            description="Navigate relationships between evidence, reports and verification artifacts."
          />

          <SurfaceCard
            title="Permanent audit trail"
            description="Every verification event is permanently traceable through canonical governance records."
          />

          <SurfaceCard
              title="Institutional investigation"
              description="Institutional reasoning engines investigate verified claims across multiple domains before allocator decisions are produced."
          />

        </div>

      </section>

      {/* COMMERCIAL */}
      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="rounded-3xl border bg-white p-8">
          <h2 className="text-2xl font-semibold">
            Institutional Verification Lifecycle
          </h2>

          <div className="mt-4 text-sm text-slate-600">
            Import → Verify → Govern → Investigate → Report → Publish
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div className="border p-4 rounded-xl">
              Import trading activity into the canonical Evidence Registry.
            </div>
            <div className="border p-4 rounded-xl">
              Perform institutional investigations, generate allocator decisions, produce institutional reports and publish independently verifiable trust records.
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}