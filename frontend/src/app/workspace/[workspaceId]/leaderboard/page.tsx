"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  getLeaderboardAnalytics,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

type ClaimRanking = {
  claim_schema_id: number;
  name: string;
  status: string;
  trade_count: number;
  net_pnl: number;
  profit_factor: number;
  win_rate: number;
};

type MemberRanking = {
  member: string;
  net_pnl: number;
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

  const [loading, setLoading] =
    useState(true);

  const [data, setData] =
    useState<any>(null);

  const [claimLimit, setClaimLimit] =
    useState(20);

  const [memberLimit, setMemberLimit] =
    useState(20);

  useEffect(() => {

    async function load() {

      try {

        const response =
          await getLeaderboardAnalytics(
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

  const claims =
    data?.claim_rankings ?? [];

  const members =
    data?.member_rankings ?? [];

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Trust Intelligence
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Leaderboard
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional ranking
            analytics across claims
            and workspace members.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-4 mb-8">

          <MetricCard
            title="Claims"
            value={
              data?.summary?.claims ?? 0
            }
          />

          <MetricCard
            title="Members"
            value={
              data?.summary?.members ?? 0
            }
          />

          <MetricCard
            title="Top Claim PnL"
            value={
              claims.length > 0
                ? claims[0].net_pnl.toFixed(2)
                : "0"
            }
          />

          <MetricCard
            title="Top Member PnL"
            value={
              members.length > 0
                ? members[0].net_pnl.toFixed(2)
                : "0"
            }
          />

        </div>

        <div className="grid gap-6 lg:grid-cols-2">

          <div className="rounded-xl border bg-white overflow-hidden">

            <div className="border-b px-6 py-4 font-semibold">
              Claim Rankings
            </div>

            <div className="max-h-[600px] overflow-y-auto">

            <table className="w-full">

              <thead className="bg-slate-100">

                <tr>

                  <th className="p-4 text-left">
                    Rank
                  </th>

                  <th className="p-4 text-left">
                    Claim
                  </th>

                  <th className="p-4 text-left">
                    Trades
                  </th>

                  <th className="p-4 text-left">
                    Net PnL
                  </th>

                  <th className="p-4 text-left">
                    PF
                  </th>

                  <th className="p-4 text-left">
                    Win Rate
                  </th>

                </tr>

              </thead>

              <tbody>

                {loading && (

                  <tr>

                    <td
                      colSpan={6}
                      className="p-6"
                    >
                      Loading...
                    </td>

                  </tr>

                )}

                {!loading &&
                  claims
                    .slice(0, claimLimit)
                    .map(
                    (
                      row: ClaimRanking,
                      index: number
                    ) => (

                      <tr
                        key={
                          row.claim_schema_id
                        }
                        className="border-t"
                      >

                        <td className="p-4">
                          {index + 1}
                        </td>

                        <td className="p-4">
                          {row.name}
                        </td>

                        <td className="p-4">
                          {row.trade_count}
                        </td>

                        <td className="p-4">
                          {row.net_pnl.toFixed(2)}
                        </td>

                        <td className="p-4">
                          {row.profit_factor.toFixed(2)}
                        </td>

                        <td className="p-4">
                          {(row.win_rate * 100)
                            .toFixed(2)}%
                        </td>

                      </tr>

                    )
                  )}

              </tbody>

            </table>

            </div>

          {claims.length > claimLimit && (

            <div className="border-t p-4">

              <button
                onClick={() =>
                  setClaimLimit(
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

          <div className="rounded-xl border bg-white overflow-hidden">

            <div className="border-b px-6 py-4 font-semibold">
              Member Rankings
            </div>

            <div className="max-h-[600px] overflow-y-auto">

            <table className="w-full">

              <thead className="bg-slate-100">

                <tr>

                  <th className="p-4 text-left">
                    Rank
                  </th>

                  <th className="p-4 text-left">
                    Member
                  </th>

                  <th className="p-4 text-left">
                    Net PnL
                  </th>

                </tr>

              </thead>

              <tbody>

                {loading && (

                  <tr>

                    <td
                      colSpan={3}
                      className="p-6"
                    >
                      Loading...
                    </td>

                  </tr>

                )}

                {!loading &&
                  members
                    .slice(0, memberLimit)
                    .map(
                    (
                      row: MemberRanking,
                      index: number
                    ) => (

                      <tr
                        key={row.member}
                        className="border-t"
                      >

                        <td className="p-4">
                          {index + 1}
                        </td>

                        <td className="p-4">
                          {row.member}
                        </td>

                        <td className="p-4">
                          {row.net_pnl.toFixed(2)}
                        </td>

                      </tr>

                    )
                  )}

              </tbody>

            </table>

            </div>

          {members.length > memberLimit && (

            <div className="border-t p-4">

              <button
                onClick={() =>
                  setMemberLimit(
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