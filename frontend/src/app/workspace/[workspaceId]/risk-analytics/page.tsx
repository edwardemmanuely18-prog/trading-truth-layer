"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  getRiskAnalytics,
  RiskAnalytics,
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
    useState<RiskAnalytics | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function load() {
      try {
        const response =
          await getRiskAnalytics(
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

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10">
          Loading...
        </div>
      </div>
    );
  }

  const overview =
    data?.overview;

  const claims =
    data?.recent_claims ?? [];

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Trust Intelligence
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Risk Analytics
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional risk monitoring,
            drawdown analysis,
            portfolio performance health,
            and risk-adjusted trade oversight.
          </p>

        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-6">

          <MetricCard
            title="Trades"
            value={
              overview?.trades ?? 0
            }
          />

          <MetricCard
            title="Net PnL"
            value={
              overview?.net_pnl ?? 0
            }
          />

          <MetricCard
            title="Wins"
            value={
              overview?.wins ?? 0
            }
          />

          <MetricCard
            title="Losses"
            value={
              overview?.losses ?? 0
            }
          />

          <MetricCard
            title="Win Rate"
            value={`${overview?.win_rate ?? 0}%`}
          />

          <MetricCard
            title="Profit Factor"
            value={
              overview?.profit_factor ??
              0
            }
          />

        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-3">

          <MetricCard
            title="Max Drawdown"
            value={
              overview?.max_drawdown ??
              0
            }
          />

          <MetricCard
            title="Risk Health"
            value={
              (
                overview?.profit_factor ??
                0
              ) > 1
                ? "Healthy"
                : "Weak"
            }
          />

          <MetricCard
            title="Portfolio Status"
            value={
              (
                overview?.net_pnl ??
                0
              ) >= 0
                ? "Positive"
                : "Negative"
            }
          />

        </div>

        <div className="rounded-xl border bg-white overflow-hidden">

          <div className="border-b px-6 py-4 font-semibold">
            Claim Risk Feed
          </div>

          <table className="w-full">

            <thead className="bg-slate-100">

              <tr>

                <th className="p-4 text-left">
                  Claim
                </th>

                <th className="p-4 text-left">
                  Status
                </th>

                <th className="p-4 text-left">
                  Trades
                </th>

                <th className="p-4 text-left">
                  Net PnL
                </th>

                <th className="p-4 text-left">
                  Profit Factor
                </th>

                <th className="p-4 text-left">
                  Max Drawdown
                </th>

              </tr>

            </thead>

            <tbody>

              {claims.map(
                (claim) => (
                  <tr
                    key={
                      claim.claim_schema_id
                    }
                    className="border-t"
                  >

                    <td className="p-4">
                      {claim.name}
                    </td>

                    <td className="p-4">
                      {claim.status}
                    </td>

                    <td className="p-4">
                      {claim.trade_count}
                    </td>

                    <td className="p-4">
                      {claim.net_pnl}
                    </td>

                    <td className="p-4">
                      {
                        claim.profit_factor
                      }
                    </td>

                    <td className="p-4">
                      {
                        claim.max_drawdown
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