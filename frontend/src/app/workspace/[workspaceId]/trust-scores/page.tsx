"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";
import {
  getTrustScores,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {
  const resolvedParams = use(params);

  const workspaceId = Number(
    resolvedParams.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [profile, setProfile] =
    useState<any>(null);

  useEffect(() => {
    async function load() {
      try {
        const response =
          await getTrustScores(
            workspaceId
          )

        setProfile(
          response
        );
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
          Loading trust intelligence...
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10">
          Unable to load trust profile.
        </div>
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
            Trust Scores
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional trust scoring,
            network credibility,
            verification quality,
            and governance health.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-6">

          <MetricCard
            title="Trust Score"
            value={
              profile.average_trust_score
            }
          />

          <MetricCard
            title="Network Score"
            value={
              profile.average_network_score
            }
          />

          <MetricCard
            title="Claims"
            value={
              profile.claims_count
            }
          />

          <MetricCard
            title="Locked"
            value={
              profile.locked_claims_count
            }
          />

          <MetricCard
            title="Contested"
            value={
              profile.contested_claims_count
            }
          />

          <MetricCard
            title="Trust Band"
            value={
              profile.trust_profile_band
            }
          />

        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <AnalyticsCard
            title="Trust Profile"
            items={[
              {
                label: "Profile",
                value:
                  profile.profile_id,
              },
              {
                label: "Workspace",
                value:
                  profile.workspace_id,
              },
              {
                label: "Type",
                value:
                  profile.type,
              },
              {
                label: "Network",
                value:
                  profile.network,
              },
            ]}
          />

          <AnalyticsCard
            title="Performance Context"
            items={[
              {
                label:
                  "Total Net PnL",
                value:
                  profile.total_net_pnl,
              },
              {
                label:
                  "Average Trust",
                value:
                  profile.average_trust_score,
              },
              {
                label:
                  "Average Network",
                value:
                  profile.average_network_score,
              },
              {
                label:
                  "Trust Band",
                value:
                  profile.trust_profile_band,
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

        {items.map(item => (

          <div
            key={item.label}
            className="flex justify-between"
          >

            <span>
              {item.label}
            </span>

            <span className="font-semibold">
              {item.value}
            </span>

          </div>

        ))}

      </div>

    </div>
  );
}