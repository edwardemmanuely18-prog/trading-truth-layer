export default function VerificationPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">

      <section className="border-b bg-white">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h1 className="text-5xl font-bold">
            Verification Center
          </h1>

          <p className="mt-6 max-w-3xl text-lg text-slate-600">
            Trading Truth Layer provides auditable
            trade records, governed claim workflows,
            evidence generation, verification events
            and public proof surfaces.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="text-3xl font-bold">
          Trade Verification Workflow
        </h2>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              1. Trade Imported
            </h3>

            <p className="mt-2 text-slate-600">
              Trades are imported from supported
              broker exports and normalized into
              the canonical ledger.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              2. Evidence Attached
            </h3>

            <p className="mt-2 text-slate-600">
              Supporting files, screenshots and
              broker statements may be attached.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              3. Fingerprint Generated
            </h3>

            <p className="mt-2 text-slate-600">
              Cryptographic fingerprints provide
              tamper-evident verification.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6">
            <h3 className="font-semibold">
              4. Audit Event Created
            </h3>

            <p className="mt-2 text-slate-600">
              Verification activity is recorded
              in the audit trail.
            </p>
          </div>

        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="text-3xl font-bold">
          Claim Lifecycle
        </h2>

        <div className="mt-8 grid gap-4 md:grid-cols-6">

          <div className="rounded-xl border bg-white p-4">
            Draft
          </div>

          <div className="rounded-xl border bg-white p-4">
            Review
          </div>

          <div className="rounded-xl border bg-white p-4">
            Approved
          </div>

          <div className="rounded-xl border bg-white p-4">
            Published
          </div>

          <div className="rounded-xl border bg-white p-4">
            Disputed
          </div>

          <div className="rounded-xl border bg-white p-4">
            Superseded
          </div>

        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="text-3xl font-bold">
          Verification Signals
        </h2>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <div className="rounded-2xl border bg-white p-6">
            ✓ Evidence Available
          </div>

          <div className="rounded-2xl border bg-white p-6">
            ✓ Audit Trail Available
          </div>

          <div className="rounded-2xl border bg-white p-6">
            ✓ Fingerprint Generated
          </div>

          <div className="rounded-2xl border bg-white p-6">
            ✓ Verification Event Recorded
          </div>

        </div>
      </section>

    </main>
  );
}