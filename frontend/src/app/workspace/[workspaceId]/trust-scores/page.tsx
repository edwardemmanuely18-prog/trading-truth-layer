"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getTrustScores,
  TrustScore,
} from "../../../../lib/api";

export default function TrustScoresPage() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [scores, setScores] =
    useState<TrustScore[]>([]);

  const [visibleRows, setVisibleRows] =
    useState(10);

  useEffect(() => {
    async function load() {
      try {
        const response =
          await getTrustScores(
            workspaceId
          );

        setScores(
          response.scores || []
        );

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

  const institutional =
    scores.filter(
      x =>
        x.tier ===
        "INSTITUTIONAL GRADE"
    ).length;

  const verified =
    scores.filter(
      x => x.tier === "VERIFIED"
    ).length;

  const averageScore =
    scores.length > 0
      ? (
          scores.reduce(
            (sum, x) =>
              sum + x.trust_score,
            0
          ) / scores.length
        ).toFixed(1)
      : "0";

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

        <div className="grid gap-4 md:grid-cols-4 mb-8">

          <MetricCard
            title="Claims"
            value={scores.length}
          />

          <MetricCard
            title="Average Score"
            value={averageScore}
          />

          <MetricCard
            title="Institutional Grade"
            value={institutional}
          />

          <MetricCard
            title="Verified"
            value={verified}
          />

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

        <div className="space-y-6">

          {scores
            .slice(0, visibleRows)
            .map(score => (

            <div
              key={score.claim_id}
              className="rounded-2xl border bg-white p-8"
            >

              <div className="flex items-start justify-between">

                <div>

                  <h2 className="text-3xl font-semibold">
                    {score.claim_name}
                  </h2>

                  <div className="mt-3 flex gap-2 flex-wrap">

                    <span className="rounded-full border border-slate-300 px-3 py-1 text-sm">
                      {score.status}
                    </span>

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

                  </div>

                </div>

                <div className="text-right">

                  <div className="text-xs text-slate-500">
                    TRUST SCORE
                  </div>

                  <div className="text-5xl font-bold">
                    {score.trust_score}
                  </div>

                </div>

              </div>

              <div className="mt-8 grid gap-4 md:grid-cols-3">

                <InfoCard
                  label="Reviews"
                  value={
                    score.review_count
                  }
                />

                <InfoCard
                  label="Average Rating"
                  value={
                    score.average_rating
                  }
                />

                <InfoCard
                  label="Claim ID"
                  value={
                    score.claim_id
                  }
                />

              </div>

            </div>

          ))}

        </div>

        {scores.length > visibleRows && (

          <div className="mt-8 flex justify-center">

            <button
              onClick={() =>
                setVisibleRows(
                  visibleRows + 10
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
  return (
    <div className="rounded-2xl border bg-white p-6">
      <div className="text-sm text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-4xl font-bold">
        {value}
      </div>
    </div>
  );
}

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl border p-5">
      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className="mt-2 text-xl font-semibold">
        {value}
      </div>
    </div>
  );
}