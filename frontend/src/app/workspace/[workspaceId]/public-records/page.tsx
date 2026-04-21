"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";

type PublicClaimRow = {
  claim_schema_id: number;
  claim_hash?: string | null;
  public_view_path?: string | null;
  verify_path?: string | null;
  name?: string | null;
  verification_status?: string | null;
  integrity_status?: string | null;
  trade_count?: number | null;
  net_pnl?: number | null;
  profit_factor?: number | null;
  win_rate?: number | null;
  trust_score?: number | null;
  trust_band?: string | null;
  network_score?: number | null;
  network_weighted_pnl?: number | null;
  disputes_count?: number | null;
  active_disputes_count?: number | null;
  has_active_dispute?: boolean;
  issuer?: {
    id?: number | null;
    name?: string | null;
    type?: string | null;
    network?: string | null;
  } | null;
  lifecycle?: {
    status?: string | null;
    verified_at?: string | null;
    published_at?: string | null;
    locked_at?: string | null;
  } | null;
  scope?: {
    period_start?: string | null;
    period_end?: string | null;
    visibility?: string | null;
    included_members?: number[];
    included_symbols?: string[];
  } | null;
  lineage?: {
    parent_claim_id?: number | null;
    root_claim_id?: number | null;
    version_number?: number | null;
  } | null;
};

function normalizeText(value?: string | null) {
  return String(value || "").trim().toLowerCase();
}

function formatDate(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatUsd(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `$${Number(value).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatPercentRatio(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function statusBadgeClass(status?: string | null) {
  const normalized = normalizeText(status);

  if (normalized === "locked") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }

  if (normalized === "published") {
    return "border-blue-200 bg-blue-50 text-blue-800";
  }

  if (normalized === "verified") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }

  if (normalized === "draft") {
    return "border-slate-200 bg-slate-100 text-slate-700";
  }

  return "border-slate-200 bg-slate-100 text-slate-700";
}

function integrityBadgeClass(status?: string | null) {
  const normalized = normalizeText(status);

  if (normalized === "valid") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }

  if (normalized === "compromised") {
    return "border-red-200 bg-red-50 text-red-800";
  }

  return "border-slate-200 bg-slate-100 text-slate-700";
}

function trustBandBadgeClass(value?: string | null) {
  const normalized = normalizeText(value);

  if (normalized === "high" || normalized === "institutional" || normalized === "strong") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }

  if (normalized === "moderate" || normalized === "developing") {
    return "border-blue-200 bg-blue-50 text-blue-800";
  }

  if (normalized === "contested" || normalized === "fragile" || normalized === "low") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }

  return "border-slate-200 bg-slate-100 text-slate-700";
}

function resolveApiBase() {
  const envBase =
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    process.env.NEXT_PUBLIC_API_BASE ||
    process.env.NEXT_PUBLIC_BACKEND_URL;

  return (envBase || "http://localhost:8000").replace(/\/+$/, "");
}

async function fetchWorkspacePublicClaims(workspaceId: number): Promise<PublicClaimRow[]> {
  const base = resolveApiBase();
  const response = await fetch(`${base}/workspaces/${workspaceId}/public-profile`, {
    method: "GET",
    cache: "no-store",
  });

  if (!response.ok) {
    const raw = await response.text();
    throw new Error(raw || `Failed to load public records (${response.status})`);
  }

  const rows = (await response.json()) as unknown;
  const data = await response.json();
  return Array.isArray(data?.claims) ? data.claims : [];
}

export default function WorkspacePublicRecordsPage() {
  const params = useParams();
  const { user, workspaces, loading: authLoading } = useAuth();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const [rows, setRows] = useState<PublicClaimRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load(targetWorkspaceId: number, refreshOnly = false) {
    try {
      if (refreshOnly) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError(null);
      const result = await fetchWorkspacePublicClaims(targetWorkspaceId);
      setRows(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspace public records.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    if (!workspaceId) return;
    if (!workspaceMembership) return;
    void load(workspaceId);
  }, [workspaceId, workspaceMembership]);

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading public records...</div>
        </main>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace public records page.
          </div>
        </main>
      </div>
    );
  }

  const lockedCount = rows.filter((row) => normalizeText(row.verification_status) === "locked").length;
  const publicCount = rows.filter((row) => normalizeText(row.scope?.visibility) === "public").length;
  const validIntegrityCount = rows.filter((row) => normalizeText(row.integrity_status) === "valid").length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Public Trust Surface</div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Workspace Public Records</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Public claim records for this workspace, including verification posture, integrity status,
              trust score, and verification routes.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => void load(workspaceId, true)}
              disabled={refreshing}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
            >
              {refreshing ? "Refreshing..." : "Refresh Records"}
            </button>

            <Link
              href={`/workspace/${workspaceId}/claims`}
              className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold hover:bg-slate-50"
            >
              Open Claim Library
            </Link>
          </div>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Public Records</div>
            <div className="mt-2 text-2xl font-semibold">{rows.length}</div>
            <div className="mt-2 text-xs text-slate-500">Workspace-scoped public trust entries</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Locked Records</div>
            <div className="mt-2 text-2xl font-semibold">{lockedCount}</div>
            <div className="mt-2 text-xs text-slate-500">Finalized and integrity-anchored outputs</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Public Visibility</div>
            <div className="mt-2 text-2xl font-semibold">{publicCount}</div>
            <div className="mt-2 text-xs text-slate-500">Directly public verification surfaces</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Integrity Valid</div>
            <div className="mt-2 text-2xl font-semibold">{validIntegrityCount}</div>
            <div className="mt-2 text-xs text-slate-500">Records with valid trust integrity state</div>
          </div>
        </div>

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading workspace public records...</div>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">{error}</div>
        ) : rows.length === 0 ? (
          <div className="rounded-2xl border bg-white p-10 shadow-sm">
            <h2 className="text-2xl font-semibold">No public records yet</h2>
            <p className="mt-3 max-w-2xl text-slate-600">
              This workspace does not currently have any published or locked public-facing claims.
              Create, verify, publish, and lock claims to expose them through the public trust layer.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/schema`}
                className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Open Claim Builder
              </Link>

              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
              >
                Open Claim Library
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-5">
            {rows.map((row) => {
              const publicHref = row.public_view_path || `/claim/${row.claim_schema_id}/public`;
              const verifyHref =
                row.verify_path || (row.claim_hash ? `/verify/${row.claim_hash}` : null);

              return (
                <div
                  key={row.claim_schema_id}
                  className="rounded-3xl border bg-white p-6 shadow-sm"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-2xl font-semibold text-slate-900">
                          {row.name || `Claim ${row.claim_schema_id}`}
                        </h2>

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusBadgeClass(
                            row.verification_status
                          )}`}
                        >
                          {row.verification_status || "unknown"}
                        </span>

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${integrityBadgeClass(
                            row.integrity_status
                          )}`}
                        >
                          integrity: {row.integrity_status || "unknown"}
                        </span>

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${trustBandBadgeClass(
                            row.trust_band
                          )}`}
                        >
                          trust: {row.trust_band || "unknown"}
                        </span>
                      </div>

                      <div className="mt-2 text-sm text-slate-500">
                        Claim ID: {row.claim_schema_id}
                        {row.issuer?.name ? ` · Issuer: ${row.issuer.name}` : ""}
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-3">
                      <Link
                        href={publicHref}
                        className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                      >
                        Open Public View
                      </Link>

                      {verifyHref ? (
                        <Link
                          href={verifyHref}
                          className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
                        >
                          Open Verify Route
                        </Link>
                      ) : null}
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Trade Count</div>
                      <div className="mt-1 text-xl font-semibold text-slate-900">
                        {row.trade_count ?? 0}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Net PnL</div>
                      <div className="mt-1 text-xl font-semibold text-slate-900">
                        {formatUsd(row.net_pnl)}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Win Rate</div>
                      <div className="mt-1 text-xl font-semibold text-slate-900">
                        {formatPercentRatio(row.win_rate)}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Profit Factor</div>
                      <div className="mt-1 text-xl font-semibold text-slate-900">
                        {formatNumber(row.profit_factor, 2)}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Trust Score</div>
                      <div className="mt-1 text-xl font-semibold text-slate-900">
                        {formatNumber(row.trust_score, 2)}
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 md:grid-cols-2">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                      <div>
                        <span className="font-medium text-slate-900">Visibility:</span>{" "}
                        {row.scope?.visibility || "—"}
                      </div>
                      <div className="mt-2">
                        <span className="font-medium text-slate-900">Period Start:</span>{" "}
                        {formatDate(row.scope?.period_start)}
                      </div>
                      <div className="mt-2">
                        <span className="font-medium text-slate-900">Period End:</span>{" "}
                        {formatDate(row.scope?.period_end)}
                      </div>
                      <div className="mt-2">
                        <span className="font-medium text-slate-900">Version:</span>{" "}
                        {row.lineage?.version_number ?? "—"}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                      <div>
                        <span className="font-medium text-slate-900">Verified At:</span>{" "}
                        {formatDate(row.lifecycle?.verified_at)}
                      </div>
                      <div className="mt-2">
                        <span className="font-medium text-slate-900">Published At:</span>{" "}
                        {formatDate(row.lifecycle?.published_at)}
                      </div>
                      <div className="mt-2">
                        <span className="font-medium text-slate-900">Locked At:</span>{" "}
                        {formatDate(row.lifecycle?.locked_at)}
                      </div>
                      <div className="mt-2">
                        <span className="font-medium text-slate-900">Active Disputes:</span>{" "}
                        {row.active_disputes_count ?? 0}
                      </div>
                    </div>
                  </div>

                  {row.claim_hash ? (
                    <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Claim Hash</div>
                      <div className="mt-2 break-all font-mono text-sm text-slate-800">
                        {row.claim_hash}
                      </div>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}