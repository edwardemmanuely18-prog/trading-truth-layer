"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  VerificationAnalytics,
  getVerificationAnalytics,
} from "../../../../lib/api";

export default function VerificationRoutesPage() {
  const params = useParams();

  const workspaceId = Number(params.workspaceId);

  const [data, setData] =
    useState<VerificationAnalytics | null>(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function load() {
      try {
        const response =
          await getVerificationAnalytics(
            workspaceId
          );

        console.log(
          "VERIFICATION ANALYTICS",
          response
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
          <h1 className="text-4xl font-bold">
            Verification Routes
          </h1>

          <p className="mt-3 text-slate-600">
            Canonical verification endpoints
            for externally verifiable claims.
          </p>
        </div>

        {loading && (
          <div className="rounded-xl border bg-white p-6">
            Loading verification routes...
          </div>
        )}

        {!loading && data && (
          <>
            <div className="grid gap-4 md:grid-cols-5 mb-8">

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Total Claims
                </div>

                <div className="mt-2 text-3xl font-bold">
                  {
                    data.lifecycle.draft +
                    data.lifecycle.verified +
                    data.lifecycle.published +
                    data.lifecycle.locked
                  }
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Verified
                </div>

                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.verified}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Published
                </div>

                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.published}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Locked
                </div>

                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.locked}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">

                <div className="text-sm text-slate-500">
                  Coverage
                </div>

                <div className="mt-2 text-3xl font-bold">
                  {data.coverage.verification.toFixed(1)}%
                </div>

              </div>

            </div>

            <div className="mb-8 rounded-2xl border bg-white p-6">

              <div className="text-xs uppercase tracking-widest text-slate-500">
                Verification Network
              </div>

              <h2 className="mt-2 text-2xl font-semibold">
                Canonical Verification Registry
              </h2>

              <p className="mt-2 text-slate-600">
                Registry of publicly addressable verification
                routes, lifecycle-governed claims, and
                externally verifiable trust records.
              </p>

              <div className="mt-6 grid gap-4 md:grid-cols-4">

                <div>
                  <div className="text-sm text-slate-500">
                    Total Claims
                  </div>

                  <div className="mt-1 text-xl font-semibold">
                    {
                      data.lifecycle.draft +
                      data.lifecycle.verified +
                      data.lifecycle.published +
                      data.lifecycle.locked
                    }
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">
                    Locked Routes
                  </div>

                  <div className="mt-1 text-xl font-semibold">
                    {data.lifecycle.locked}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">
                    Published Routes
                  </div>

                  <div className="mt-1 text-xl font-semibold">
                    {data.lifecycle.published}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">
                    Verification Coverage
                  </div>

                  <div className="mt-1 text-xl font-semibold">
                    {data.coverage.verification.toFixed(1)}%
                  </div>
                </div>

              </div>

            </div>

            <div className="space-y-6">

              {data.claims.map((claim) => (

                <div
                  key={claim.id}
                  className="rounded-2xl border bg-white p-6"
                >

                  <div className="flex items-start justify-between gap-6">

                    <div>

                      <h2 className="text-2xl font-semibold">
                        {claim.name}
                      </h2>

                      <div className="mt-2 flex gap-2 flex-wrap">

                        <span
                          className={`rounded-full px-3 py-1 text-sm border
                            ${
                              claim.status?.toLowerCase() === "locked"
                                ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                                : claim.status?.toLowerCase() === "published"
                                ? "border-blue-300 bg-blue-50 text-blue-700"
                                : claim.status?.toLowerCase() === "verified"
                                ? "border-indigo-300 bg-indigo-50 text-indigo-700"
                                : "border-slate-300 bg-slate-50 text-slate-700"
                            }
                          `}
                        >
                          {claim.status}
                        </span>

                        <span
                          className={`rounded-full px-3 py-1 text-sm border
                            ${
                              claim.visibility?.toLowerCase() === "public"
                                ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                                : claim.visibility?.toLowerCase() === "unlisted"
                                ? "border-blue-300 bg-blue-50 text-blue-700"
                                : "border-slate-300 bg-slate-50 text-slate-700"
                            }
                          `}
                        >
                          {claim.visibility}
                        </span>

                        {claim.claim_hash && (
                          <span className="rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-sm text-emerald-700">
                            public route ready
                          </span>
                        )}

                      </div>

                    </div>

                    <div className="flex gap-3">

                      <a
                        href={`/claim/${claim.id}/public`}
                        className="rounded-xl border px-5 py-3"
                      >
                        Public View
                      </a>

                      {claim.claim_hash && (
                        <a
                          href={`/verify/${claim.claim_hash}`}
                          className="rounded-xl bg-slate-900 px-5 py-3 text-white"
                        >
                          Verify Route
                        </a>
                      )}

                    </div>

                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-3">

                    <div className="rounded-xl border p-4">
                      <div className="text-sm text-slate-500">
                        Claim Hash
                      </div>

                      <div className="mt-2 break-all font-mono text-sm">
                        {claim.claim_hash || "Unavailable"}
                      </div>
                    </div>

                    <div className="rounded-xl border p-4">
                      <div className="text-sm text-slate-500">
                        Verification Route
                      </div>

                      <div className="mt-2 break-all font-mono text-sm">
                        {claim.claim_hash
                          ? `/verify/${claim.claim_hash}`
                          : "Unavailable"}
                      </div>
                    </div>

                    <div className="rounded-xl border p-4">

                      <div className="text-sm text-slate-500">
                        Public View Route
                      </div>

                      <div className="mt-2 break-all font-mono text-sm">
                        {`/claim/${claim.id}/public`}
                      </div>

                    </div>

                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-3">

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

                </div>

              ))}

            </div>
          </>
        )}

      </div>
    </div>
  );
}