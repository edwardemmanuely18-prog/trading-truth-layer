"use client";

import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50">
      {/* 🔴 DEBUG BANNER (TEMPORARY) */}
      <section className="mx-auto max-w-7xl px-6 pt-6">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700 shadow-sm">
          PADDLE HANDOFF BUILD ACTIVE
        </div>
      </section>

      {/* HERO */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="max-w-3xl">
          <div className="mb-4 inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 shadow-sm">
            Trading Truth Layer
          </div>

          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Verified Trading Claims OS
          </h1>

          <p className="mt-6 text-lg text-slate-600">
            Broker-neutral verification infrastructure for trading communities, operators, and
            performance claims. Convert raw trading activity into canonical ledgers,
            standardized claims, verified leaderboards, and dispute-ready evidence packs.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/workspace"
              className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow hover:bg-slate-800"
            >
              Open Workspace Dashboard
            </Link>

            <Link
              href="/import"
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow hover:bg-slate-50"
            >
              Go to Trade Import
            </Link>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="mx-auto max-w-7xl px-6 pb-16">
        <div className="grid gap-6 md:grid-cols-3">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">
              Canonical Trade Ledger
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Normalize imported trading activity into a durable, queryable source of truth.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">
              Claims Schema Engine
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Define exactly what is included in a performance claim, with clear methodology and
              exclusions.
            </p>
          </div>

          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">
              Evidence Pack Generator
            </h3>
            <p className="mt-2 text-sm text-slate-600">
              Export signed, dispute-ready claim artifacts with trade-set hashes and reproducible
              metrics.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}