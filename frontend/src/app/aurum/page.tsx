"use client";

import { useEffect, useState } from "react";
import AurumNav from "../../components/AurumNav";

type Overview = {
  total_users: number;
  verified_users: number;

  total_workspaces: number;
  internal_workspaces: number;

  total_memberships: number;

  total_claims: number;
  draft_claims: number;
  verified_claims: number;
  published_claims: number;
  locked_claims: number;

  total_trades: number;
};

export default function AurumPage() {
  const [data, setData] =
    useState<Overview | null>(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    async function load() {
      try {
        const response =
          await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/aurum/overview`
          );

        const json =
          await response.json();

        setData(json);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 p-8">
        Loading Aurum Operations Center...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-7xl">

        <div className="mb-10">
          <div className="text-sm uppercase tracking-[0.2em] text-slate-500">
            AURUM
          </div>

          <h1 className="mt-2 text-5xl font-bold">
            Operations Center
          </h1>

          <p className="mt-4 text-slate-600">
            Founder visibility across users,
            workspaces, claims and platform activity.
          </p>

          <AurumNav />
        </div>

        <div className="grid gap-6 md:grid-cols-4">

          <Card
            title="Users"
            value={data?.total_users ?? 0}
            subtitle={`${data?.verified_users ?? 0} verified`}
          />

          <Card
            title="Workspaces"
            value={data?.total_workspaces ?? 0}
            subtitle={`${data?.internal_workspaces ?? 0} internal`}
          />

          <Card
            title="Claims"
            value={data?.total_claims ?? 0}
            subtitle={`${data?.locked_claims ?? 0} locked`}
          />

          <Card
            title="Trades"
            value={data?.total_trades ?? 0}
            subtitle="Total platform trades"
          />

        </div>

        <div className="mt-10 grid gap-6 md:grid-cols-4">

          <Card
            title="Draft Claims"
            value={data?.draft_claims ?? 0}
          />

          <Card
            title="Verified Claims"
            value={data?.verified_claims ?? 0}
          />

          <Card
            title="Published Claims"
            value={data?.published_claims ?? 0}
          />

          <Card
            title="Memberships"
            value={data?.total_memberships ?? 0}
          />

        </div>

      </div>
    </main>
  );
}

function Card({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: number;
  subtitle?: string;
}) {
  return (
    <div className="rounded-3xl border bg-white p-6 shadow-sm">
      <div className="text-sm text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-4xl font-bold">
        {value}
      </div>

      {subtitle && (
        <div className="mt-2 text-sm text-slate-500">
          {subtitle}
        </div>
      )}
    </div>
  );
}