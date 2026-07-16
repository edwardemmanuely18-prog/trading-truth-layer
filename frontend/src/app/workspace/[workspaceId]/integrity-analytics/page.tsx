"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import {
    useRouter,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  IntegrityRecord,
  IntegrityDashboardResponse,
  IntegrityAlertFeedItem,
  getIntegrityRegistry,
  getIntegrityDashboard,
  getIntegrityAlertFeed,
  acknowledgeAlert,
  investigateAlert,
  resolveAlert,
  runIntegrityScan,
  IntegrityScanHistoryItem,
  getIntegrityScanHistory,
  api,
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

  const router = useRouter();

  const [records, setRecords] =
    useState<IntegrityRecord[]>([]);

  const [
    dashboard,
    setDashboard,
  ] =
    useState<
      IntegrityDashboardResponse | null
    >(null);

  const [
    alerts,
    setAlerts,
  ] = useState<
    IntegrityAlertFeedItem[]
  >([]);

  const [
    alertFilter,
    setAlertFilter,
  ] = useState("all");

  const [
    searchTerm,
    setSearchTerm,
  ] = useState("");

  const [
    severityFilter,
    setSeverityFilter,
  ] = useState("all");

  const [
    alertLimit,
    setAlertLimit,
  ] = useState(20);

  const [
    feedLimit,
    setFeedLimit,
  ] = useState(20);

  const [
    scanLimit,
    setScanLimit,
  ] = useState(20);

  const [
    scanHistory,
    setScanHistory,
  ] = useState<
    IntegrityScanHistoryItem[]
  >([]);

  const [actionMessage, setActionMessage] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const load = async () => {

    try {

      const [
        registry,
        dashboardData,
        alertFeed,
        history,
      ] = await Promise.all([
        getIntegrityRegistry(
          workspaceId
        ),
        getIntegrityDashboard(
          workspaceId
        ),
        getIntegrityAlertFeed(
          workspaceId
        ),
        getIntegrityScanHistory(
          workspaceId
        ),
      ]);

      setRecords(registry);

      setDashboard(
        dashboardData
      );

      setAlerts(
        alertFeed
      );

      setScanHistory(
        history
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

  };

  useEffect(() => {

      if (!Number.isNaN(workspaceId)) {

          load();

      }

  }, [workspaceId]);

  useEffect(() => {

    const interval =
        setInterval(() => {

            if (!Number.isNaN(workspaceId)) {

                load();

            }

        }, 30000);

    return () =>
      clearInterval(interval);

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

  const filteredAlerts =
    alerts.filter(alert => {

      const statusMatch =
        alertFilter === "all" ||
        alert.status === alertFilter;

      const severityMatch =
        severityFilter === "all" ||
        alert.severity === severityFilter;

      const searchMatch =
        alert.alert_type
          .toLowerCase()
          .includes(
            searchTerm.toLowerCase()
          ) ||
        alert.message
          .toLowerCase()
          .includes(
            searchTerm.toLowerCase()
          );

      return (
        statusMatch &&
        severityMatch &&
        searchMatch
      );

    });

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

          {
            actionMessage && (
              <div
                className="
                  mt-4
                  rounded-lg
                  border
                  bg-blue-50
                  border-blue-200
                  px-4
                  py-3
                  text-sm
                  text-blue-700
                "
              >
                {actionMessage}
              </div>
            )
          }

          <p className="mt-3 text-slate-600">
            Institutional integrity
            monitoring, evidence
            protection analytics,
            verification coverage,
            and provenance health.
          </p>

        </div>

        <div className="mb-8">

          <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">
            Scanner Command Center
          </div>

          <div className="mt-4 mb-6 flex gap-3">

            <button
              onClick={() => {

                setActionMessage(
                  "Integrity scan submitted."
                );

                runIntegrityScan(
                  workspaceId
                )
                  .then(() => {

                    setTimeout(
                      () => load(),
                      5000
                    );

                  })
                  .catch((err: any) => {

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

                  });

                setTimeout(() => {
                  setActionMessage("");
                }, 3000);

              }}
              className="
                rounded-lg
                border
                px-4
                py-2
                font-medium
                bg-white
                hover:bg-slate-50
              "
            >
              Run Integrity Scan
            </button>

          </div>

          

          <div className="grid gap-4 md:grid-cols-4">

            {dashboard &&
              Object.entries(
                dashboard.scanner_status
              ).map(
                ([
                  name,
                  scanner,
                ]) => (

                  <div
                    key={name}
                    className="rounded-xl border bg-white p-5"
                  >

                    <div className="text-sm text-slate-500">
                      {name}
                    </div>

                    <div
                      className={`mt-2 text-xl font-bold ${
                        scanner.status ===
                        "healthy"
                          ? "text-green-600"
                          : "text-amber-600"
                      }`}
                    >
                      {scanner.status}
                    </div>

                    <div className="mt-2 inline-flex rounded-full border px-3 py-1 text-xs font-semibold">
                      {scanner.findings} findings
                    </div>

                  </div>

                )
              )}

          </div>

        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-5">

          <MetricCard
            title="Integrity Score"
            value={
              dashboard?.integrity_score ?? 0
            }
          />

          <MetricCard
            title="Open Findings"
            value={
              dashboard?.open_findings ?? 0
            }
          />

          <MetricCard
            title="Resolved Findings"
            value={
              dashboard?.resolved_findings ?? 0
            }
          />

          <MetricCard
            title="Claims Scanned"
            value={
              dashboard?.claims_scanned ?? 0
            }
          />

          <MetricCard
            title="Total Alerts"
            value={
              dashboard?.total_alerts ?? 0
            }
          />

        </div>

        <div className="mt-8 rounded-xl border bg-white overflow-hidden">

          <div className="mb-8 rounded-xl border bg-white">

            <div className="mt-8 grid gap-4 md:grid-cols-4">

              <MetricCard
                title="Critical"
                value={
                  alerts.filter(
                    a => a.severity === "CRITICAL"
                  ).length
                }
              />

              <MetricCard
                title="High"
                value={
                  alerts.filter(
                    a => a.severity === "HIGH"
                  ).length
                }
              />

              <MetricCard
                title="Investigating"
                value={
                  alerts.filter(
                    a =>
                      a.status ===
                      "investigating"
                  ).length
                }
              />

              <MetricCard
                title="Resolved"
                value={
                  alerts.filter(
                    a =>
                      a.status ===
                      "resolved"
                  ).length
                }
              />

            </div>

            <div
              className="
                divide-y
                max-h-[700px]
                overflow-y-auto
              "
            >

              {dashboard?.recent_findings.map(
                finding => (

                  <div
                    key={finding.id}
                    className="p-5"
                  >

                    <div className="font-semibold">
                      {finding.type}
                    </div>

                    <div className="text-sm text-slate-600">
                      {finding.message}
                    </div>

                    <div className="mt-2 text-xs text-slate-500">
                      {finding.severity}
                      {" • "}
                      {finding.status}
                    </div>

                  </div>

                )
              )}

            </div>

          </div>

          <div className="mb-8 rounded-xl border bg-white">

            <div className="border-b px-6 py-4">

              <h2 className="font-semibold">
                Integrity Alert Operations Center
              </h2>

            </div>

            <div
              className="
                flex
                flex-wrap
                items-center
                gap-3
                p-4
                border-b
              "
            >

              {[
                "all",
                "open",
                "acknowledged",
                "investigating",
                "resolved",
              ].map(filter => (

                <button
                  key={filter}
                  onClick={() =>
                    setAlertFilter(filter)
                  }
                  className="
                    rounded-lg
                    border
                    px-3
                    py-1
                    text-sm
                  "
                >
                  {filter}
                </button>

              ))}

              <div className="flex-1 min-w-[500px]">

                <input
                  value={searchTerm}
                  onChange={(e)=>
                    setSearchTerm(
                      e.target.value
                    )
                  }
                  placeholder="
                  Search alerts, claim ids, hash mismatches, evidence issues...
                  "
                  className="
                    w-full
                    rounded-lg
                    border
                    px-4
                    py-2
                    text-sm
                  "
                />

              </div>

              <select
                value={severityFilter}
                onChange={(e) =>
                  setSeverityFilter(
                    e.target.value
                  )
                }
                className="
                  rounded-lg
                  border
                  px-3
                  py-1
                  text-sm
                "
              >
                <option value="all">
                  All Severity
                </option>

                <option value="WARNING">
                  Warning
                </option>

                <option value="HIGH">
                  High
                </option>

                <option value="CRITICAL">
                  Critical
                </option>

              </select>

            </div>

            <div
              className="
                divide-y
                max-h-[700px]
                overflow-y-auto
              "
            >

              {filteredAlerts
                .slice(0, alertLimit)
                .map(alert => (

                <div
                  key={alert.id}
                  className="
                    px-5
                    py-3
                  "
                >

                  <div className="
                    grid
                    lg:grid-cols-[2fr_1.4fr_1.5fr_1fr_0.8fr]
                    gap-6
                    items-center
                  ">

                    <div className="min-w-0">

                      <div className="font-semibold">
                        {alert.alert_type}
                      </div>

                      <div className="text-sm text-slate-600">
                        {alert.message}
                      </div>

                    </div>

                    <div className="
                      flex
                      gap-2
                      whitespace-nowrap
                    ">

                      <button
                        onClick={async () => {

                          setActionMessage(
                            "Acknowledging alert..."
                          );

                          await acknowledgeAlert(
                            alert.id
                          );

                          await load();

                          setActionMessage(
                            "Alert acknowledged."
                          );

                          setTimeout(() => {
                            setActionMessage("");
                          }, 3000);

                        }}
                        className="
                          rounded-lg
                          border
                          px-4
                          py-2
                          text-sm
                          font-medium
                          transition
                          hover:bg-slate-50
                        "
                      >
                        Acknowledge
                      </button>

                      <button
                        onClick={async () => {

                          setActionMessage(
                            "Starting investigation..."
                          );

                          await investigateAlert(
                            alert.id
                          );

                          await load();

                          setActionMessage(
                            "Investigation started."
                          );

                          setTimeout(() => {
                            setActionMessage("");
                          }, 3000);

                        }}
                        className="
                          rounded-lg
                          border
                          px-4
                          py-2
                          text-sm
                          font-medium
                          transition
                          hover:bg-slate-50
                        "
                      >
                        Investigate
                      </button>

                      <button
                        onClick={async () => {

                          setActionMessage(
                            "Resolving alert..."
                          );

                          await resolveAlert(
                            alert.id
                          );

                          await load();

                          setActionMessage(
                            "Alert resolved."
                          );

                          setTimeout(() => {
                            setActionMessage("");
                          }, 3000);

                        }}
                        className="
                          rounded-lg
                          border
                          px-4
                          py-2
                          text-sm
                          font-medium
                          transition
                          hover:bg-slate-50
                        "
                      >
                        Resolve
                      </button>

                    </div>

                    <div className="
                      text-xs
                      text-slate-500
                      space-y-1
                    ">

                      <div>
                        Created:
                        {" "}
                        {alert.created_at || "-"}
                      </div>

                      <div>
                        Acknowledged:
                        {" "}
                        {alert.acknowledged_at || "-"}
                      </div>

                      <div>
                        Resolved:
                        {" "}
                        {alert.resolved_at || "-"}
                      </div>

                    </div>

                    <div className="
                      text-xs
                      text-slate-500
                      space-y-1
                    ">

                      <div>
                        Owner:
                        {" "}
                        {alert.acknowledged_by || "-"}
                      </div>

                      <div>
                        Resolver:
                        {" "}
                        {alert.resolved_by || "-"}
                      </div>

                    </div>

                    <div className="
                      flex
                      flex-col
                      gap-2
                      items-end
                    ">

                      <div
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                          alert.severity === "HIGH"
                            ? "bg-red-100 text-red-700"
                            : alert.severity === "WARNING"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {alert.severity}
                      </div>

                      <div
                        className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                          alert.status === "resolved"
                            ? "bg-green-100 text-green-700"
                            : alert.status === "investigating"
                            ? "bg-blue-100 text-blue-700"
                            : alert.status === "acknowledged"
                            ? "bg-purple-100 text-purple-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {alert.status}
                      </div>

                    </div>

                  </div>

                </div>

              ))}

            </div>

            {filteredAlerts.length >
              alertLimit && (

              <div className="p-4">

                <button
                  onClick={() =>
                    setAlertLimit(
                      prev =>
                        prev + 20
                    )
                  }
                  className="
                    rounded-lg
                    border
                    px-4
                    py-2
                  "
                >
                  Load More Alerts
                </button>

              </div>

            )}

          </div>

          <div className="mb-8 rounded-xl border bg-white">

            <div className="border-b px-6 py-4 font-semibold">
              Scan History
            </div>

            <div
              className="
                max-h-[600px]
                overflow-y-auto
              "
            >

              <table className="w-full">

              <thead className="bg-slate-100">

                <tr>

                  <th className="p-4 text-left">
                    Scan ID
                  </th>

                  <th className="p-4 text-left">
                    Status
                  </th>

                  <th className="p-4 text-left">
                    Claims
                  </th>

                  <th className="p-4 text-left">
                    Alerts
                  </th>

                  <th className="p-4 text-left">
                    Started
                  </th>

                </tr>

              </thead>

              <tbody>

                {scanHistory
                  .slice(0, scanLimit)
                  .map(scan => (

                    <tr
                      key={scan.id}
                      className="border-t"
                    >

                      <td className="p-4">
                        #{scan.id}
                      </td>

                      <td className="p-4">
                        {scan.status}
                      </td>

                      <td className="p-4">
                        {scan.claims_scanned}
                      </td>

                      <td className="p-4">
                        {scan.alerts_found}
                      </td>

                      <td className="p-4">
                        {new Date(
                          scan.started_at
                        ).toLocaleString()}
                      </td>

                    </tr>

                  ))}

              </tbody>

            </table>
            </div>

            {scanHistory.length > scanLimit && (

              <div className="p-4">

                <button
                  onClick={() =>
                    setScanLimit(
                      prev => prev + 20
                    )
                  }
                  className="
                    rounded-lg
                    border
                    px-4
                    py-2
                  "
                >
                  Load More Scans
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