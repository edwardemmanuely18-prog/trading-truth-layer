"use client";

import { useEffect, useState } from "react";
import {
    useParams,
    useRouter,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getTrustScores,
  TrustScore,
} from "../../../../lib/api";

export default function TrustScoresPage() {
  const params = useParams();

  const router = useRouter();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [scores, setScores] =
    useState<TrustScore[]>([]);

  const [summary, setSummary] =
    useState<any>(null);

  const [visibleRows, setVisibleRows] =
    useState(20);

  useEffect(() => {
    async function load() {
      try {
        const response =
          await getTrustScores(
            workspaceId
          );

        setSummary(
          response.summary
        );

        setScores(
          response.scores || []
        );

      } catch (err: any) {

          console.error(err);

          if (
              err?.payload?.code === "page_locked" ||
              err?.payload?.upgrade_required === true
          ) {

              router.replace(
                  `/workspace/${workspaceId}/billing?upgrade=true`
              );

              return;

          }

          throw err;

      } finally {
        setLoading(false);
      }
    }

    if (!Number.isNaN(workspaceId)) {
      load();
    }
  }, [workspaceId]);

  if (loading) {

    return (

      <div className="min-h-screen bg-slate-50">

        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10">

          Loading TVS verification profile...

        </div>

      </div>

    );

  }

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
            TRUST INTELLIGENCE
          </div>

          <h1 className="mt-2 text-5xl font-bold">
            Trust Scores
          </h1>

          <p className="mt-4 max-w-4xl text-slate-600">
            Institutional trust
            ranking generated from
            lifecycle integrity,
            verification status,
            publication status,
            lock status and
            independent review
            activity.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-12 mb-8">

          <div className="lg:col-span-2">

            <MetricCard
              title="Claims"
              value={
                summary?.claims ?? 0
              }
            />

          </div>

          <div className="lg:col-span-2">

            <MetricCard
              title="Average Trust"
              value={
                summary?.average_score ?? 0
              }
            />

          </div>

          <div className="lg:col-span-4">

            <MetricCard
              title="Institutional Grade"
              value={
                summary?.institutional_grade ??
                "-"
              }
            />

          </div>

          <div className="lg:col-span-2">

            <MetricCard
              title="Verified Claims"
              value={
                summary?.verified ?? 0
              }
            />

          </div>

          <div className="lg:col-span-2">

            <MetricCard
              title="Network Score"
              value={
                summary?.network_score ?? 0
              }
            />

          </div>

          <div className="lg:col-span-2">

            <MetricCard
              title="Registry"
              value="TVS"
            />

          </div>

        </div>

        <div className="rounded-2xl border bg-white p-8 mb-8">

          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
            TRUST ENGINE
          </div>

          <h2 className="mt-3 text-3xl font-semibold">
            Institutional Ranking Registry
          </h2>

          <p className="mt-4 text-slate-600">
            Trust scores aggregate
            lifecycle governance,
            verification maturity
            and external review
            participation into a
            standardized
            institutional signal.
          </p>

        </div>

        <div className="rounded-2xl border bg-white p-8 mb-8">

          <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
            TVS REGISTRY
          </div>

          <h2 className="mt-3 text-3xl font-semibold">
            Verification Registry
          </h2>

          <p className="mt-4 text-slate-600">
            Every verification decision shown below is
            produced by the Trading Verification System
            (TVS). The registry represents the canonical
            verification status of every claim in this
            workspace and will progressively expose
            evidence quality, governance, network trust,
            transparency and lifecycle verification
            metrics.
          </p>

        </div>

        <div className="rounded-2xl border bg-white overflow-hidden">

          <div className="max-h-[700px] overflow-y-auto">

            <table className="w-full">

              <thead className="sticky top-0 bg-slate-100 z-10">

                <tr>

                  <th className="p-4 text-left">
                    Rank
                  </th>

                  <th className="p-4 text-left">
                    Claim
                  </th>

                  <th className="p-4 text-center">
                    Trust Score
                  </th>

                  <th className="p-4 text-left">
                    Tier
                  </th>

                  <th className="p-4 text-left">
                    Status
                  </th>

                  <th className="p-4 text-center">
                    Reviews
                  </th>

                  <th className="p-4 text-center">
                    Rating
                  </th>

                </tr>

              </thead>

              <tbody>

                {scores
                  .slice(0, visibleRows)
                  .map((score,index)=>(

                  <tr
                    key={score.claim_id}
                    className="border-t"
                  >

                    <td className="p-4">
                      {index + 1}
                    </td>

                    <td className="p-4 font-medium">
                      {score.claim_name}
                    </td>

                    <td className="p-4 text-center font-bold">
                      {score.trust_score}
                    </td>

                    <td className="p-4">

                      <span
                        className={`rounded-full px-3 py-1 text-sm border ${
                          score.tier ===
                          "INSTITUTIONAL GRADE"
                            ? "border-emerald-300 bg-emerald-50 text-emerald-700"
                            : score.tier ===
                              "VERIFIED"
                            ? "border-blue-300 bg-blue-50 text-blue-700"
                            : "border-amber-300 bg-amber-50 text-amber-700"
                        }`}
                      >
                        {score.tier}
                      </span>

                    </td>

                    <td className="p-4">
                      {score.status}
                    </td>

                    <td className="p-4 text-center">
                      {score.review_count}
                    </td>

                    <td className="p-4 text-center">
                      {score.average_rating}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </div>

        {scores.length > visibleRows && (

          <div className="mt-8 flex justify-center">

            <button
              onClick={() =>
                setVisibleRows(
                  visibleRows + 20
                )
              }
              className="rounded-xl bg-slate-900 px-6 py-3 text-white"
            >
              Load More
            </button>

          </div>

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

  const isText =
    typeof value === "string" &&
    value.length > 4;

  return (

    <div className="rounded-2xl border bg-white p-6 h-full">

      <div className="text-sm text-slate-500">
        {title}
      </div>

      {

        isText ? (

          <div className="mt-5">

            <span className="inline-flex items-center rounded-full border border-amber-300 bg-amber-50 px-4 py-2 text-lg font-semibold text-amber-700">

              {value}

            </span>

          </div>

        ) : (

          <div className="mt-2 text-4xl font-bold whitespace-nowrap">

            {value}

          </div>

        )

      }

    </div>

  );

}