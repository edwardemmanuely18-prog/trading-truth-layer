"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  getVerificationAnalytics,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {

  const resolvedParams =
    use(params);

  const workspaceId =
    Number(
      resolvedParams.workspaceId
    );

  const [data, setData] =
    useState<any>(null);

  const [loading, setLoading] =
    useState(true);

  const [feedLimit, setFeedLimit] =
    useState(20);

  const [exporting, setExporting] =
    useState(false);

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

    load();

  }, [workspaceId]);

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Trust Intelligence
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Verification Analytics
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional visibility into
            workspace verification coverage,
            claim lifecycle progression,
            verification governance,
            publication readiness,
            and Trading Verification System (TVS)
            adoption across the workspace.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">

            <button
                onClick={async () => {

                    try {

                        setExporting(true);

                        const response = await fetch(
                            `/api/reports/workspace/${workspaceId}/verification`
                        );

                        const blob =
                            await response.blob();

                        const url =
                            window.URL.createObjectURL(
                                blob
                            );

                        const link =
                            document.createElement("a");

                        link.href = url;

                        link.download =
                            `verification-report-${workspaceId}.json`;

                        document.body.appendChild(link);

                        link.click();

                        link.remove();

                        window.URL.revokeObjectURL(
                            url
                        );

                    } finally {

                        setExporting(false);

                    }

                }}
                disabled={exporting}
                className="rounded-lg border bg-white px-4 py-2 disabled:opacity-60"
            >

                {
                    exporting
                        ? "Exporting..."
                        : "Export Verification JSON"
                }

            </button>

          </div>

        </div>

        {loading && (

          <div className="rounded-xl border bg-white p-6">
            Loading verification analytics...
          </div>

        )}

        {!loading && data && (

          <>

            {/* KPI CARDS */}

            <div className="mb-8 grid gap-4 md:grid-cols-3 xl:grid-cols-6">

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Total Claims
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.draft +
                   data.lifecycle.verified +
                   data.lifecycle.published +
                   data.lifecycle.locked}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Draft Claims
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.draft}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Verified Claims
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.verified}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Published Claims
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.published}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Locked Claims
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {data.lifecycle.locked}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="text-sm text-slate-500">
                  Verification Coverage
                </div>
                <div className="mt-2 text-3xl font-bold">
                  {data.coverage.verification}%
                </div>
              </div>

            </div>

            {/* DISTRIBUTIONS */}

            <div className="mb-8 grid gap-6 lg:grid-cols-2">

              <div className="rounded-xl border bg-white p-6">

                <h2 className="text-xl font-semibold">
                  Lifecycle Distribution
                </h2>

                <div className="mt-6 space-y-4">

                  <div className="flex justify-between">
                    <span>Draft</span>
                    <span className="font-semibold">
                      {data.lifecycle.draft}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span>Verified</span>
                    <span className="font-semibold">
                      {data.lifecycle.verified}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span>Published</span>
                    <span className="font-semibold">
                      {data.lifecycle.published}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span>Locked</span>
                    <span className="font-semibold">
                      {data.lifecycle.locked}
                    </span>
                  </div>

                </div>

              </div>

              <div className="rounded-xl border bg-white p-6">

                <h2 className="text-xl font-semibold">
                  Visibility Distribution
                </h2>

                <div className="mt-6 space-y-4">

                  <div className="flex justify-between">
                    <span>Public Claims</span>
                    <span className="font-semibold">
                      {data.visibility.public}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span>Private Claims</span>
                    <span className="font-semibold">
                      {data.visibility.private}
                    </span>
                  </div>

                </div>

              </div>

            </div>

            {/* ACTIVITY FEED */}

            <div className="rounded-xl border bg-white overflow-hidden">

              <div className="border-b px-6 py-4">

                <h2 className="text-xl font-semibold">
                  Verification Activity Feed
                </h2>

              </div>

              <div className="max-h-[420px] overflow-y-auto">

              <table className="w-full">

                <thead className="sticky top-0 bg-slate-100 z-10">

                  <tr>

                    <th className="p-4 text-left">
                      Claim
                    </th>

                    <th className="p-4 text-left">
                      Status
                    </th>

                    <th className="p-4 text-left">
                      Visibility
                    </th>

                    <th className="p-4 text-left">
                      Verified
                    </th>

                    <th className="p-4 text-left">
                      Published
                    </th>

                    <th className="p-4 text-left">
                      Locked
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {[...data.claims]
                      .sort(
                          (a, b) =>
                              new Date(
                                  b.locked_at ??
                                  b.published_at ??
                                  b.verified_at ??
                                  0
                              ).getTime()
                              -
                              new Date(
                                  a.locked_at ??
                                  a.published_at ??
                                  a.verified_at ??
                                  0
                              ).getTime()
                      )
                      .slice(0, feedLimit)
                      .map(
                    (event: any) => (

                      <tr
                        key={event.id}
                        className="border-t"
                      >

                        <td className="p-4">
                          {event.name}
                        </td>

                        <td className="p-4">
                          {event.status}
                        </td>

                        <td className="p-4">
                          {event.visibility}
                        </td>

                        <td className="p-4">
                          {event.verified_at
                            ? new Date(
                                event.verified_at
                              ).toLocaleDateString()
                            : "-"}
                        </td>

                        <td className="p-4">
                          {event.published_at
                            ? new Date(
                                event.published_at
                              ).toLocaleDateString()
                            : "-"}
                        </td>

                        <td className="p-4">
                          {event.locked_at
                            ? new Date(
                                event.locked_at
                              ).toLocaleDateString()
                            : "-"}
                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

              </div>

              {data.claims?.length >
                feedLimit && (

                <div className="border-t p-4">

                  <button
                    onClick={() =>
                      setFeedLimit(
                        prev => prev + 20
                      )
                    }
                    className="rounded-lg border px-4 py-2"
                  >
                    Load More
                  </button>

                </div>

              )}

            </div>

          </>

        )}

      </div>

    </div>
  );
}