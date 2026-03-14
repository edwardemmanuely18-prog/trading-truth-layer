import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-6 py-16">
        <div className="max-w-4xl">
          <div className="mb-4 inline-flex rounded-full border border-slate-200 bg-white px-4 py-1 text-sm font-medium text-slate-600">
            Trading Truth Layer
          </div>

          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            Verified Trading Claims OS
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            Broker-neutral verification infrastructure for trading communities,
            operators, and performance claims. Convert raw trading activity into
            canonical ledgers, standardized claims, verified leaderboards, and
            dispute-ready evidence packs.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
            >
              Open Workspace Dashboard
            </Link>

            <Link
              href="/import"
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-100"
            >
              Go to Trade Import
            </Link>
          </div>
        </div>

        <div className="mt-16 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">Canonical Trade Ledger</h2>
            <p className="mt-2 text-sm text-slate-600">
              Normalize imported trading activity into a durable, queryable
              source of truth.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">Claims Schema Engine</h2>
            <p className="mt-2 text-sm text-slate-600">
              Define exactly what is included in a performance claim, with clear
              methodology and exclusions.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold">Evidence Pack Generator</h2>
            <p className="mt-2 text-sm text-slate-600">
              Export signed, dispute-ready claim artifacts with trade-set hashes
              and reproducible metrics.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}