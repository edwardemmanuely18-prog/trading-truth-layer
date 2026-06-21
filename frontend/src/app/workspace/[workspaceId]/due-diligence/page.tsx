"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  DueDiligenceResponse,
  getDueDiligence,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {
  const resolved =
    use(params);

  const workspaceId =
    Number(
      resolved.workspaceId
    );

  const [report, setReport] =
    useState<DueDiligenceResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data =
          await getDueDiligence(
            workspaceId
          );

        setReport(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [workspaceId]);

  if (loading) {
    return (
      <div className="p-8">
        Loading...
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-8">
        No report available.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Trust Intelligence
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Due Diligence Report
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional assessment,
            verification quality,
            integrity monitoring,
            trust evaluation,
            and risk review.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-6">

          <MetricCard
            title="Claims"
            value={report.overview.claims}
          />

          <MetricCard
            title="Published"
            value={
              report.overview
                .published_claims
            }
          />

          <MetricCard
            title="Locked"
            value={
              report.overview
                .locked_claims
            }
          />

          <MetricCard
            title="Trust"
            value={
              report.trust
                .trust_score
            }
          />

          <MetricCard
            title="Network"
            value={
              report.trust
                .network_score
            }
          />

          <MetricCard
            title="Grade"
            value={
              report.assessment
                .grade
            }
          />

        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <AnalyticsCard
            title="Verification"
            items={[
              {
                label:
                  "Coverage",
                value:
                  report
                    .verification
                    .coverage,
              },
              {
                label:
                  "Verified Claims",
                value:
                  report
                    .verification
                    .verified_claims,
              },
            ]}
          />

          <AnalyticsCard
            title="Integrity"
            items={[
              {
                label:
                  "Integrity Score",
                value:
                  report
                    .integrity
                    .integrity_score,
              },
              {
                label:
                  "Compromised Claims",
                value:
                  report
                    .integrity
                    .compromised_claims,
              },
            ]}
          />

          <AnalyticsCard
            title="Risk"
            items={[
              {
                label:
                  "Profit Factor",
                value:
                  report.risk
                    .profit_factor,
              },
              {
                label:
                  "Win Rate",
                value:
                  report.risk
                    .win_rate,
              },
              {
                label:
                  "Max Drawdown",
                value:
                  report.risk
                    .max_drawdown,
              },
            ]}
          />

          <AnalyticsCard
            title="Institutional Assessment"
            items={[
              {
                label:
                  "Grade",
                value:
                  report
                    .assessment
                    .grade,
              },
              {
                label:
                  "Status",
                value:
                  report
                    .assessment
                    .status,
              },
              {
                label:
                  "Trust Band",
                value:
                  report
                    .trust
                    .trust_band,
              },
            ]}
          />

        </div>

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

function AnalyticsCard({
  title,
  items,
}: {
  title: string;
  items: {
    label: string;
    value: string | number;
  }[];
}) {
  return (
    <div className="rounded-xl border bg-white p-6">

      <h2 className="mb-4 text-lg font-semibold">
        {title}
      </h2>

      <div className="space-y-3">

        {items.map(
          item => (
            <div
              key={
                item.label
              }
              className="flex justify-between"
            >
              <span>
                {
                  item.label
                }
              </span>

              <span className="font-semibold">
                {
                  item.value
                }
              </span>
            </div>
          )
        )}

      </div>

    </div>
  );
}