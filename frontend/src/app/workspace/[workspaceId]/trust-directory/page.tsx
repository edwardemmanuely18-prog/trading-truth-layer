"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  VerificationAnalytics,
  getVerificationAnalytics,
} from "../../../../lib/api";

export default function Page() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [data, setData] =
    useState<VerificationAnalytics | null>(
      null
    );

  useEffect(() => {
    async function load() {
      try {
        const response =
          await getVerificationAnalytics(
            workspaceId
          );

        setData(response);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (!Number.isNaN(workspaceId)) {
      load();
    }
  }, [workspaceId]);

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Public Trust Layer
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Trust Directory
          </h1>

          <p className="mt-3 text-slate-600">
            Discover publicly exposed
            claim records, verification
            routes, and trust-ready
            entities across the workspace.
          </p>

        </div>

        {loading && (

          <div className="rounded-xl border bg-white p-6">
            Loading trust directory...
          </div>

        )}

        {!loading && data && (

          <>

            <div className="grid gap-4 md:grid-cols-4 mb-8">

              <MetricCard
                title="Claims"
                value={
                  data.lifecycle.draft +
                  data.lifecycle.verified +
                  data.lifecycle.published +
                  data.lifecycle.locked
                }
              />

              <MetricCard
                title="Verified"
                value={data.lifecycle.verified}
              />

              <MetricCard
                title="Published"
                value={data.lifecycle.published}
              />

              <MetricCard
                title="Locked"
                value={data.lifecycle.locked}
              />

            </div>

            <div className="mb-8 rounded-2xl border bg-white p-6">

              <div className="text-xs uppercase tracking-widest text-slate-500">
                Trust Registry
              </div>

              <h2 className="mt-2 text-2xl font-semibold">
                Public Trust Directory
              </h2>

              <p className="mt-3 text-slate-600">
                Registry of publicly
                exposed records,
                verification routes,
                governance-ready claims,
                and externally verifiable
                trading evidence.
              </p>

            </div>

            <div className="space-y-6">

              {data.claims.map(
                (claim) => (

                  <div
                    key={claim.id}
                    className="rounded-2xl border bg-white p-6"
                  >

                    <div className="flex items-start justify-between gap-6">

                      <div>

                        <h2 className="text-2xl font-semibold">
                          {claim.name}
                        </h2>

                        <div className="mt-3 flex flex-wrap gap-2">

                          <span
                            className={
                              claim.status
                                ?.toLowerCase() ===
                              "locked"
                                ? "rounded-full border border-green-300 bg-green-50 px-3 py-1 text-sm text-green-700"
                                : claim.status
                                    ?.toLowerCase() ===
                                  "published"
                                ? "rounded-full border border-blue-300 bg-blue-50 px-3 py-1 text-sm text-blue-700"
                                : "rounded-full border px-3 py-1 text-sm"
                            }
                          >
                            {claim.status}
                          </span>

                          <span
                            className={
                              claim.visibility
                                ?.toLowerCase() ===
                              "public"
                                ? "rounded-full border border-green-300 bg-green-50 px-3 py-1 text-sm text-green-700"
                                : claim.visibility
                                    ?.toLowerCase() ===
                                  "unlisted"
                                ? "rounded-full border border-blue-300 bg-blue-50 px-3 py-1 text-sm text-blue-700"
                                : "rounded-full border px-3 py-1 text-sm"
                            }
                          >
                            {claim.visibility}
                          </span>

                          {claim.claim_hash && (

                            <span className="rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-sm text-emerald-700">
                              Verification Ready
                            </span>

                          )}

                        </div>

                      </div>

                      <div className="flex gap-3 flex-wrap">

                        <a
                          href={`/claim/${claim.id}/public`}
                          className="rounded-xl border px-5 py-3"
                        >
                          Public Record
                        </a>

                        {claim.claim_hash && (

                          <a
                            href={`/verify/${claim.claim_hash}`}
                            className="rounded-xl bg-slate-900 px-5 py-3 text-white"
                          >
                            Verification Route
                          </a>

                        )}

                      </div>

                    </div>

                    <div className="mt-6 grid gap-4 md:grid-cols-4">

                      <div className="rounded-xl border p-4">

                        <div className="text-xs text-slate-500">
                          CLAIM ID
                        </div>

                        <div className="mt-2">
                          #{claim.id}
                        </div>

                      </div>

                      <div className="rounded-xl border p-4">

                        <div className="text-xs text-slate-500">
                          VERIFIED AT
                        </div>

                        <div className="mt-2">
                          {claim.verified_at || "—"}
                        </div>

                      </div>

                      <div className="rounded-xl border p-4">

                        <div className="text-xs text-slate-500">
                          PUBLISHED AT
                        </div>

                        <div className="mt-2">
                          {claim.published_at || "—"}
                        </div>

                      </div>

                      <div className="rounded-xl border p-4">

                        <div className="text-xs text-slate-500">
                          LOCKED AT
                        </div>

                        <div className="mt-2">
                          {claim.locked_at || "—"}
                        </div>

                      </div>

                    </div>

                    <div className="mt-4 grid gap-4 md:grid-cols-2">

                      <div className="rounded-xl border p-4">

                        <div className="text-xs text-slate-500">
                          PUBLIC RECORD ROUTE
                        </div>

                        <div className="mt-2 break-all font-mono text-sm">
                          {`/claim/${claim.id}/public`}
                        </div>

                      </div>

                      <div className="rounded-xl border p-4">

                        <div className="text-xs text-slate-500">
                          VERIFICATION ROUTE
                        </div>

                        <div className="mt-2 break-all font-mono text-sm">
                          {claim.claim_hash
                            ? `/verify/${claim.claim_hash}`
                            : "Unavailable"}
                        </div>

                      </div>

                    </div>

                  </div>

                )
              )}

            </div>

          </>

        )}

      </div>

    </div>
  );
}

function MetricCard({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl border bg-white p-5">

      <div className="text-sm text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-3xl font-bold">
        {value}
      </div>

    </div>
  );
}