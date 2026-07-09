"use client";

import { use } from "react";
import {
  useEffect,
  useState,
} from "react";

import Navbar from "../../../../components/Navbar";

import {
  getEvidenceAnalytics,
  EvidenceAnalyticsResponse,
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
    useState<EvidenceAnalyticsResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [
    exceptionLimit,
    setExceptionLimit
  ] = useState(20);

  const formatPercent = (
    value: number
  ) =>
    `${Number(value).toFixed(2)}%`;

  const formatTier = (tier: string) => {

    switch ((tier || "").toLowerCase()) {

      case "tier_1":
        return "Tier I";

      case "tier_2":
        return "Tier II";

      case "tier_3":
        return "Tier III";

      default:
        return tier;
    }

  };

  useEffect(() => {

    async function load() {

      try {

        const data =
          await getEvidenceAnalytics(
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
        No analytics available.
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
            Evidence Analytics
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional evidence quality,
            verification coverage,
            protection analytics,
            and provenance intelligence.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-6">

          <MetricCard
            title="Records"
            value={
              report.overview.records
            }
          />

          <MetricCard
            title="Coverage %"
            value={
              formatPercent(
                report.overview.coverage
              )
            }
          />

          <MetricCard
            title="Reliability %"
            value={
              formatPercent(
                report.overview.reliability
              )
            }
          />

          <MetricCard
            title="Protection %"
            value={
              formatPercent(
                report.overview.protection
              )
            }
          />

          <MetricCard
            title="Quality Score"
            value={
              report.overview
                .quality_score
            }
          />

          <MetricCard
            title="Quality Band"
            value={
              report.overview.quality_band
                .toLowerCase()
                .replace(
                  /^./,
                  c => c.toUpperCase()
                )
            }
          />

        </div>

        <div className="mt-8">

          <div className="mb-4">

            <h2 className="text-2xl font-semibold">
              Evidence Quality Engine
            </h2>

            <p className="text-slate-500 mt-1">
              Institutional assessment of evidence quality,
              completeness, protection coverage,
              and source reliability.
            </p>

          </div>

          <div className="grid gap-4 md:grid-cols-4">

            <MetricCard
              title="Verification Quality"
              value={
                formatPercent(
                  report.quality
                    .verification_quality
                )
              }
            />

            <MetricCard
              title="Protection Quality"
              value={
                formatPercent(
                  report.quality
                    .protection_quality
                )
              }
            />

            <MetricCard
              title="Completeness Quality"
              value={
                formatPercent(
                  report.quality
                    .completeness_quality
                )
              }
            />

            <MetricCard
              title="Import Quality"
              value={
                formatPercent(
                  report.quality
                    .import_quality
                )
              }
            />

          </div>

        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-4">

          <AnalyticsCard
            title="Verification Coverage"
            items={[
              {
                label:
                  "Broker Verified",
                value:
                  report.verification
                    .broker_verified,
              },
              {
                label:
                  "Verified",
                value:
                  report.verification
                    .verified,
              },
              {
                label:
                  "Self Reported",
                value:
                  report.verification
                    .self_reported,
              },
            ]}
          />

          <AnalyticsCard
            title="Trust Tier Distribution"
            items={[
              {
                label:
                  "Tier 1",
                value:
                  report.tiers
                    .tier_1,
              },
              {
                label:
                  "Tier 2",
                value:
                  report.tiers
                    .tier_2,
              },
              {
                label:
                  "Tier 3",
                value:
                  report.tiers
                    .tier_3,
              },
            ]}
          />

          <AnalyticsCard
            title="Protection Analytics"
            items={[
              {
                label:
                  "Fingerprinted",
                value:
                  report.protection
                    .fingerprinted,
              },
              {
                label:
                  "Hash Protected",
                value:
                  report.protection
                    .hash_protected,
              },
              {
                label:
                  "Unprotected",
                value:
                  report.protection
                    .unprotected,
              },
            ]}
          />

          <AnalyticsCard
            title="Import Reliability"
            items={[
              {
                label:
                  "Broker Sources",
                value:
                  report.verification
                    .broker_verified,
              },
              {
                label:
                  "Export Sources",
                value:
                  report.verification
                    .verified,
              },
              {
                label:
                  "Manual Sources",
                value:
                  report.verification
                    .self_reported,
              },
            ]}
          />

        </div>

        <div className="mt-8 overflow-hidden rounded-xl border bg-white">

          <div className="flex items-center justify-between border-b p-5">

            <h2 className="text-xl font-semibold">
              Evidence Exceptions Registry
            </h2>

            <div className="text-sm text-slate-500">
              {report.exceptions.length} findings
            </div>

          </div>

          <div className="max-h-[500px] overflow-auto">

            <table className="w-full">

              <thead className="sticky top-0 z-10 bg-slate-100">

                <tr>

                  <th className="p-4 text-left">
                    Trade
                  </th>

                  <th className="p-4 text-left">
                    Symbol
                  </th>

                  <th className="p-4 text-left">
                    Issues
                  </th>

                </tr>

              </thead>

              <tbody>

                {report.exceptions.length === 0 ? (

                  <tr>

                    <td
                      colSpan={3}
                      className="p-6 text-center text-slate-500"
                    >
                      No evidence exceptions detected.
                    </td>

                  </tr>

                ) : (

                  report.exceptions
                    .slice(0, exceptionLimit)
                    .map(
                    row => (

                      <tr
                        key={row.trade_id}
                        className="border-t"
                      >

                        <td className="p-4">
                          {row.trade_id}
                        </td>

                        <td className="p-4">
                          {row.symbol}
                        </td>

                        <td className="p-4">
                          {row.issues
                             .map(issue =>
                               issue
                                 .replaceAll("_", " ")
                                 .replace(/\b\w/g, c => c.toUpperCase())
                             )
                             .join(", ")}
                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

          {report.exceptions.length >
            exceptionLimit && (

            <div className="border-t p-4">

              <button
                onClick={() =>
                  setExceptionLimit(
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

        <div className="mt-8 overflow-hidden rounded-xl border bg-white">

          <div className="flex items-center justify-between border-b p-5">

            <h2 className="text-xl font-semibold">
              Evidence Monitoring Feed
            </h2>

          </div>

          <div className="max-h-[600px] overflow-auto">

            <table className="w-full">

              <thead className="sticky top-0 z-10 bg-slate-100">

                <tr>

                  <th className="p-4 text-left">
                    Trade
                  </th>

                  <th className="p-4 text-left">
                    Symbol
                  </th>

                  <th className="p-4 text-left">
                    Verification
                  </th>

                  <th className="p-4 text-left">
                    Trust Tier
                  </th>

                  <th className="p-4 text-left">
                    Integrity Type
                  </th>

                </tr>

              </thead>

              <tbody>

                {report.feed.map(
                    row => (
                      <tr
                        key={
                          row.trade_id
                        }
                        className="border-t"
                      >
                        <td className="p-4">
                          {
                            row.trade_id
                          }
                        </td>

                        <td className="p-4">
                          {
                            row.symbol
                          }
                        </td>

                        <td className="p-4">
                          {
                            row.verification_state
                          }
                        </td>

                        <td className="p-4">
                          {formatTier(row.trust_tier)}
                        </td>

                        <td className="p-4">
                          {
                            row.integrity_type
                          }
                        </td>

                      </tr>
                    )
                  )}

              </tbody>

            </table>

          </div>

        </div>

      </div>

    </div>
  );
}

function MetricCard({
  title,
  value,
}: any) {
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
}: any) {
  return (
    <div className="rounded-xl border bg-white p-6">

      <h2 className="mb-4 text-lg font-semibold">
        {title}
      </h2>

      <div className="space-y-3">

        {items.map(
          (item: any) => (
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