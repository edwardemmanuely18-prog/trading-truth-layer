"use client";

export default function VerificationPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">

      <section className="border-b bg-white">
        <div className="mx-auto max-w-6xl px-6 py-20">

          <div className="inline-flex rounded-full border px-4 py-2 text-sm font-medium">
            TRADING TRUTH LAYER TRUST FRAMEWORK
          </div>

          <h1 className="mt-6 text-5xl font-bold">
            Verification Methodology
          </h1>

          <p className="mt-6 max-w-4xl text-lg text-slate-600">
            Trading Truth Layer establishes trust through
            canonical trade ledgers, governed claim workflows,
            evidence preservation, verification events,
            public publication, and immutable audit trails.
            Every verification record can be independently
            reviewed against the underlying evidence set.
          </p>

        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="text-3xl font-bold">
          Verification Architecture
        </h2>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              Canonical Ledger
            </h3>

            <p className="mt-3 text-slate-600">
              All imported trading activity is normalized into a
              single authoritative ledger used across every claim,
              evidence package, report, and verification record.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              Deterministic Claims
            </h3>

            <p className="mt-3 text-slate-600">
              Claims define exact inclusion criteria,
              methodologies, symbols, dates, and evidence scope
              so results can be reproduced consistently.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              Evidence Packages
            </h3>

            <p className="mt-3 text-slate-600">
              Every verification record can be supported by
              structured evidence artifacts, reports,
              fingerprints, and audit metadata.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              Public Trust Surfaces
            </h3>

            <p className="mt-3 text-slate-600">
              Published records can be distributed through
              public verification pages designed for allocators,
              investors, auditors, and due-diligence reviewers.
            </p>
          </div>

        </div>

      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="text-3xl font-bold">
          Verification Lifecycle
        </h2>

        <p className="mt-4 text-slate-600">
          Every verification record follows a governed lifecycle
          designed to preserve auditability and prevent silent
          modification of published claims.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-6">

          <div className="rounded-xl border bg-white p-4 text-center">
            Import
          </div>

          <div className="rounded-xl border bg-white p-4 text-center">
            Ledger
          </div>

          <div className="rounded-xl border bg-white p-4 text-center">
            Claim Builder
          </div>

          <div className="rounded-xl border bg-white p-4 text-center">
            Verify
          </div>

          <div className="rounded-xl border bg-white p-4 text-center">
            Publish
          </div>

          <div className="rounded-xl border bg-white p-4 text-center">
            Lock
          </div>

        </div>

      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="text-3xl font-bold">
          Verification Signals
        </h2>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <div className="rounded-2xl border bg-white p-6">
            ✓ Canonical Ledger Record
          </div>

          <div className="rounded-2xl border bg-white p-6">
            ✓ Evidence Package Available
          </div>

          <div className="rounded-2xl border bg-white p-6">
            ✓ Audit Trail Preserved
          </div>

          <div className="rounded-2xl border bg-white p-6">
            ✓ Tamper-Evident Fingerprint
          </div>

        </div>

      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <div className="rounded-3xl border bg-white p-10">

          <h2 className="text-3xl font-bold">
            Why Verification Matters
          </h2>

          <p className="mt-6 max-w-4xl text-slate-600">
            Screenshots, isolated reports, and manually prepared
            performance summaries are difficult to audit and easy
            to dispute. Trading Truth Layer provides a structured
            verification framework that connects trade evidence,
            claim methodology, governance actions, publication,
            and audit history into a single trust layer.
          </p>

        </div>

      </section>

    </main>
  );
}