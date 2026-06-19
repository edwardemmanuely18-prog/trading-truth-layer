"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  IntegrityRecord,
  getIntegrityRegistry,
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

  const [records, setRecords] =
    useState<IntegrityRecord[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    async function load() {

      try {

        const data =
          await getIntegrityRegistry(
            workspaceId
          );

        setRecords(data);

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }

    }

    load();

  }, [workspaceId]);

  const totalRecords =
    records.length;

  const hashProtected =
    records.filter(
      r => r.raw_trade_hash
    ).length;

  const fingerprinted =
    records.filter(
      r => r.trade_fingerprint
    ).length;

  const dualProtected =
    records.filter(
      r =>
        r.raw_trade_hash &&
        r.trade_fingerprint
    ).length;

  const hashOnly =
    records.filter(
      r =>
        r.raw_trade_hash &&
        !r.trade_fingerprint
    ).length;

  const fingerprintOnly =
    records.filter(
      r =>
        !r.raw_trade_hash &&
        r.trade_fingerprint
    ).length;

  const unprotected =
    records.filter(
      r =>
        !r.raw_trade_hash &&
        !r.trade_fingerprint
    ).length;

  const integrityCoverage =
    totalRecords === 0
      ? 0
      : Math.round(
          (
            records.filter(
              r =>
                r.raw_trade_hash ||
                r.trade_fingerprint
            ).length /
            totalRecords
          ) * 100
        );

  const integrityHealth =
    Math.round(
      (
        (hashProtected + fingerprinted)
        / totalRecords
      ) * 100
    );

  const verifiedCount =
    records.filter(
      r =>
        (
          r.verification_state ||
          ""
        )
          .toLowerCase()
          .includes("verified")
    ).length;

  const pendingCount =
    records.filter(
      r =>
        (
          r.verification_state ||
          ""
        )
          .toLowerCase()
          .includes("pending")
    ).length;

  const unverifiedCount =
    totalRecords -
    verifiedCount -
    pendingCount;

  const brokerVerified =
    records.filter(
      r =>
        r.verification_state ===
        "broker_verified"
    ).length;

  const manualEvidence =
    records.filter(
      r =>
        r.import_source ===
        "manual_edit"
    ).length;

  const exportEvidence =
    records.filter(
      r =>
        r.verification_state ===
        "verified"
    ).length;

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Trust Intelligence
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Integrity Analytics
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional integrity
            monitoring, evidence
            protection analytics,
            verification coverage,
            and provenance health.
          </p>

        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-5">

          <MetricCard
            title="Integrity Records"
            value={totalRecords}
          />

          <MetricCard
            title="Hash Protected"
            value={hashProtected}
          />

          <MetricCard
            title="Fingerprinted"
            value={fingerprinted}
          />

          <MetricCard
            title="Coverage"
            value={`${integrityCoverage}%`}
          />

          <MetricCard
            title="Integrity Health"
            value={`${integrityHealth}%`}
          />

        </div>

        <div className="grid gap-6 md:grid-cols-3">

          <AnalyticsCard
            title="Verification Distribution"
            items={[
              {
                label: "Verified",
                value: verifiedCount,
              },
              {
                label: "Pending",
                value: pendingCount,
              },
              {
                label: "Unverified",
                value: unverifiedCount,
              },
            ]}
          />

          <AnalyticsCard
            title="Evidence Trust Distribution"
            items={[
              {
                label: "Broker Verified",
                value: brokerVerified,
              },
              {
                label: "Broker Export",
                value: exportEvidence,
              },
              {
                label: "Manual Entry",
                value: manualEvidence,
              },
            ]}
          />

          <AnalyticsCard
            title="Protection Distribution"
            items={[
              {
                label: "Dual Protected",
                value: dualProtected,
              },
              {
                label: "Hash Only",
                value: hashOnly,
              },
              {
                label: "Fingerprint Only",
                value: fingerprintOnly,
              },
              {
                label: "Unprotected",
                value: unprotected,
              },
            ]}
          />

        </div>

        <div className="mt-8 rounded-xl border bg-white overflow-hidden">

          <div className="border-b px-6 py-4 font-semibold">
            Integrity Monitoring Feed
          </div>

          <table className="w-full">

            <thead className="bg-slate-100">

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

              {loading && (

                <tr>

                  <td
                    colSpan={5}
                    className="p-6"
                  >
                    Loading...
                  </td>

                </tr>

              )}

              {!loading &&
                records.map(record => (

                  <tr
                    key={record.trade_id}
                    className="border-t"
                  >

                    <td className="p-4">
                      {record.trade_id}
                    </td>

                    <td className="p-4">
                      {record.symbol}
                    </td>

                    <td className="p-4">
                      {
                        record.verification_state
                      }
                    </td>

                    <td className="p-4">
                      {
                        record.evidence_trust_tier
                      }
                    </td>

                    <td className="p-4">
                      {
                        record.integrity_type
                        || "-"
                      }
                    </td>

                  </tr>

                ))}

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

function AnalyticsCard({
  title,
  items,
}: {
  title: string;
  items: {
    label: string;
    value: number;
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