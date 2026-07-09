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

  function formatEvidenceBand(
      band: string,
  ) {
      switch (band) {

          case "tier_1":
              return "Tier I";

          case "tier_2":
              return "Tier II";

          case "tier_3":
              return "Tier III";

          case "tier_4":
              return "Tier IV";

          default:
              return band;
      }
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

          <div className="mt-6 rounded-xl border bg-white p-6">

            <h2 className="text-lg font-semibold">
              Executive Summary
            </h2>

            <p className="mt-3 text-slate-600">

              This report evaluates claim
              verification quality,
              evidence reliability,
              scanner health,
              governance compliance,
              and institutional trust
              readiness for workspace
              operations.

            </p>

          </div>

          <p className="mt-3 text-slate-600">
            Institutional assessment,
            verification quality,
            scanner health,
            trust evaluation,
            and risk review.
          </p>

        </div>

        <h2 className="mb-4 text-xl font-semibold">
            Executive Assessment
        </h2>

        <div className="grid gap-4 md:grid-cols-14">

          <MetricCard
            className="md:col-span-2"
            title="Claims"
            value={report.overview.claims}
          />

          <MetricCard
            className="md:col-span-2"
            title="Published"
            value={
              report.overview
                .published_claims
            }
          />

          <MetricCard
            className="md:col-span-2"
            title="Locked"
            value={
              report.overview
                .locked_claims
            }
          />

          <MetricCard
            className="md:col-span-2"
            title="Trust"
            value={`${Number(
                       report.trust.trust_score
                   ).toFixed(2)}%`}
          />

          <MetricCard
            className="md:col-span-2"
            title="Network"
            value={`${Number(
                       report.trust.network_score
                   ).toFixed(2)}%`}
          />

          <MetricCard
            className="md:col-span-4"
            title="Grade"
            value={
              report.assessment
                .grade
            }
          />

        </div>

        <h2 className="mb-4 mt-8 text-xl font-semibold">
            Institutional Scores
        </h2>

        <div className="mt-4 grid gap-4 md:grid-cols-5">

          <MetricCard
            title="Verification"
            value={`${Number(
                       report.verification.coverage
                   ).toFixed(2)}%`}
          />

          <MetricCard
            title="Scanner Health"
            value={`${Number(
                       report.scanner_health.health_score
                   ).toFixed(2)}%`}
          />

          <MetricCard
            title="Evidence"
            value={`${Number(
                       report.evidence.quality_score
                   ).toFixed(2)}%`}
          />

          <MetricCard
            title="Risk"
            value={`${Number(
                       report.risk.risk_score
                   ).toFixed(2)}%`}
          />

          <MetricCard
            title="Confidence"
            value={`${Number(
                       report.assessment.confidence
                   ).toFixed(2)}%`}
          />

        </div>

        <h2 className="mb-4 mt-10 text-xl font-semibold">
            Detailed Reviews
        </h2>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <AnalyticsCard
            title="Verification Review"
            items={[
              {
                label: "Coverage",
                value:
                  `${report.verification.coverage}%`,
              },
              {
                label: "Verified Claims",
                value:
                  report.verification.verified_claims,
              },
              {
                label: "Verification Status",
                value:
                  report.verification.status,
              },
            ]}
          />

          <AnalyticsCard
            title="Scanner Health"
            items={[
              {
                label: "Scanner Health Score",
                value:
                  `${report.scanner_health.health_score}%`,
              },
              {
                label: "Compromised Claims",
                value:
                  report.scanner_health.compromised_claims,
              },
              {
                label: "Open Findings",
                value:
                  report.scanner_health.open_findings,
              },
              {
                label: "Resolved Findings",
                value:
                  report.scanner_health.resolved_findings,
              },
            ]}
          />

          <AnalyticsCard
            title="Risk Review"
            items={[
              {
                label: "Profit Factor",
                value:
                  report.risk.profit_factor,
              },
              {
                label: "Win Rate",
                value:
                  `${report.risk.win_rate}%`,
              },
              {
                label:
                  "Peak→Trough DD (Units)",
                value:
                  `${report.risk.max_drawdown} units`,
              },
            ]}
          />

          <AnalyticsCard
            title="Evidence Review"
            items={[
              {
                label: "Quality Score",
                value:
                  `${report.evidence.quality_score}%`,
              },
              {
                label: "Quality Band",
                value:
                    formatEvidenceBand(
                        report.evidence.quality_band
                    ),
              },
              {
                label: "Coverage",
                value:
                  `${report.evidence.coverage}%`,
              },
            ]}
          />

          <AnalyticsCard
            title="Governance Review"
            items={[
              {
                label: "Published Claims",
                value:
                  report.overview.published_claims,
              },
              {
                label: "Locked Claims",
                value:
                  report.overview.locked_claims,
              },
              {
                label: "Audit Compliance",
                value:
                  `${report.governance.compliance}%`,
              },
            ]}
          />

          <AnalyticsCard
            title="Institutional Verdict"
            items={[
              {
                label: "Grade",
                value:
                  report.assessment.grade,
              },
              {
                label: "Status",
                value:
                  report.assessment.status,
              },
              {
                label: "Recommendation",
                value:
                  report.assessment.recommendation,
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
  className = "",
}: {
  title: string;
  value: string | number;
  className?: string;
}) {
  return (
    <div
        className={
            `rounded-xl border bg-white p-5 ${className}`
        }
    >
      <div className="text-sm text-slate-500">
        {title}
      </div>
      <div
          className="
              mt-2
              rounded-lg
              bg-slate-100
              px-3
              py-3
              text-center
              text-2xl
              font-bold
          "
      >
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