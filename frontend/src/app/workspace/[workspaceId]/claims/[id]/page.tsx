"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  api,
  type AuditEvent,
  type ClaimIntegrityResult,
  type ClaimSchema,
  type ClaimSchemaPreview,
  type ClaimVersion,
} from "../../../../../lib/api";
import Navbar from "../../../../../components/Navbar";
import ClaimLifecycleActions from "../../../../../components/ClaimLifecycleActions";
import CreateClaimVersionButton from "../../../../../components/CreateClaimVersionButton";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(digits);
}

function tryParseJson(value?: string | null) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function StatusBadge({ status }: { status?: string | null }) {
  const normalized = (status || "").toLowerCase();

  const className =
    normalized === "locked"
      ? "bg-green-100 text-green-800 border-green-200"
      : normalized === "published"
        ? "bg-blue-100 text-blue-800 border-blue-200"
        : normalized === "verified"
          ? "bg-amber-100 text-amber-800 border-amber-200"
          : "bg-slate-100 text-slate-800 border-slate-200";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function IntegrityBadge({ integrity }: { integrity?: ClaimIntegrityResult | null }) {
  if (!integrity) {
    return (
      <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
        not checked
      </span>
    );
  }

  const ok = integrity.hash_match && integrity.integrity_status === "valid";

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${
        ok
          ? "border-green-200 bg-green-100 text-green-800"
          : "border-red-200 bg-red-100 text-red-800"
      }`}
    >
      {ok ? "integrity valid" : "integrity compromised"}
    </span>
  );
}

export default function WorkspaceClaimDetailPage() {
  const params = useParams();

  const workspaceId = useMemo(
    () => Number(Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId),
    [params]
  );
  const idParam = params?.id;
  const claimId = useMemo(() => Number(Array.isArray(idParam) ? idParam[0] : idParam), [idParam]);

  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [preview, setPreview] = useState<ClaimSchemaPreview | null>(null);
  const [versions, setVersions] = useState<ClaimVersion[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkingIntegrity, setCheckingIntegrity] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadClaimPage = async () => {
    if (!claimId || Number.isNaN(claimId)) return;

    setLoading(true);
    setError(null);

    try {
      const [claimRes, previewRes, versionsRes, auditRes] = await Promise.all([
        api.getClaimSchema(claimId),
        api.getClaimPreview(claimId),
        api.getClaimVersions(claimId),
        api.getAuditEventsForEntity("claim_schema", claimId),
      ]);

      setClaim(claimRes);
      setPreview(previewRes);
      setVersions(versionsRes);
      setAuditEvents(auditRes);

      if (claimRes.status === "locked") {
        try {
          const integrityRes = await api.getClaimIntegrity(claimId);
          setIntegrity(integrityRes);
        } catch {
          setIntegrity(null);
        }
      } else {
        setIntegrity(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load claim");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadClaimPage();
  }, [claimId]);

  const handleRefresh = async () => {
    await loadClaimPage();
  };

  const handleIntegrityCheck = async () => {
    if (!claimId) return;
    setCheckingIntegrity(true);
    try {
      const integrityRes = await api.getClaimIntegrity(claimId);
      setIntegrity(integrityRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Integrity verification failed");
    } finally {
      setCheckingIntegrity(false);
    }
  };

  if (!workspaceId || Number.isNaN(workspaceId)) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (!claimId || Number.isNaN(claimId)) {
    return <div className="p-6 text-red-600">Invalid claim id.</div>;
  }

  if (loading) {
    return <div className="p-6">Loading claim verification screen...</div>;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
        </div>
      </div>
    );
  }

  if (!claim || !preview) {
    return <div className="p-6">Claim not found.</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="space-y-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="mb-2 text-sm text-slate-500">
              <Link href={`/workspace/${workspaceId}/claims`} className="hover:underline">
                Claims
              </Link>
              <span className="mx-2">/</span>
              <span>Claim #{claim.id}</span>
            </div>
            <h1 className="text-3xl font-semibold tracking-tight">{claim.name}</h1>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <StatusBadge status={claim.status} />
              <IntegrityBadge integrity={integrity} />
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={handleRefresh}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Refresh
            </button>

            <button
              onClick={handleIntegrityCheck}
              disabled={claim.status !== "locked" || checkingIntegrity}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {checkingIntegrity ? "Checking..." : "Verify Integrity"}
            </button>

            <Link
              href={`/workspace/${workspaceId}/evidence?claimId=${claim.id}`}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Evidence View
            </Link>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trade Count</div>
            <div className="mt-2 text-2xl font-semibold">{preview.trade_count}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Net PnL</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(preview.net_pnl)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Profit Factor</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(preview.profit_factor, 4)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Win Rate</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(preview.win_rate, 4)}</div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Claim Scope</h2>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Period Start</div>
                  <div className="mt-1 font-medium">{claim.period_start}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Period End</div>
                  <div className="mt-1 font-medium">{claim.period_end}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Visibility</div>
                  <div className="mt-1 font-medium">{claim.visibility}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Workspace</div>
                  <div className="mt-1 font-medium">{claim.workspace_id}</div>
                </div>
              </div>

              <div className="mt-4">
                <div className="text-sm text-slate-500">Methodology Notes</div>
                <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                  {claim.methodology_notes || "—"}
                </div>
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <div>
                  <div className="text-sm text-slate-500">Included Members</div>
                  <div className="mt-1 text-sm font-medium">
                    {claim.included_member_ids_json.length
                      ? claim.included_member_ids_json.join(", ")
                      : "All in scope"}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Included Symbols</div>
                  <div className="mt-1 text-sm font-medium">
                    {claim.included_symbols_json.length
                      ? claim.included_symbols_json.join(", ")
                      : "All in scope"}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Excluded Trade IDs</div>
                  <div className="mt-1 text-sm font-medium">
                    {claim.excluded_trade_ids_json.length
                      ? claim.excluded_trade_ids_json.join(", ")
                      : "None"}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-semibold">Lifecycle & Integrity</h2>
                <CreateClaimVersionButton claimSchemaId={claim.id} workspaceId={workspaceId} />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Status</div>
                  <div className="mt-1 font-medium">{claim.status}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Version Number</div>
                  <div className="mt-1 font-medium">{claim.version_number ?? "—"}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Verified At</div>
                  <div className="mt-1 font-medium">{formatDateTime(claim.verified_at)}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Published At</div>
                  <div className="mt-1 font-medium">{formatDateTime(claim.published_at)}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Locked At</div>
                  <div className="mt-1 font-medium">{formatDateTime(claim.locked_at)}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Parent Claim</div>
                  <div className="mt-1 font-medium">{claim.parent_claim_id ?? "—"}</div>
                </div>
              </div>

              <div className="mt-4">
                <div className="text-sm text-slate-500">Locked Trade Set Hash</div>
                <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                  {claim.locked_trade_set_hash || "—"}
                </div>
              </div>

              {integrity && (
                <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
                  <div className="mb-3 text-sm font-semibold">Integrity Verification Result</div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <div className="text-xs text-slate-500">Integrity Status</div>
                      <div className="mt-1 font-medium">{integrity.integrity_status}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Hash Match</div>
                      <div className="mt-1 font-medium">{String(integrity.hash_match)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Trade Count</div>
                      <div className="mt-1 font-medium">{integrity.trade_count}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-500">Verified At</div>
                      <div className="mt-1 font-medium">{formatDateTime(integrity.verified_at)}</div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-5">
                <ClaimLifecycleActions
                  claimSchemaId={claim.id}
                  workspaceId={claim.workspace_id}
                  status={claim.status}
                />
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Leaderboard</h2>
              {preview.leaderboard.length === 0 ? (
                <div className="mt-4 text-sm text-slate-500">No leaderboard data available.</div>
              ) : (
                <div className="mt-4 overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-slate-500">
                        <th className="px-3 py-2">Rank</th>
                        <th className="px-3 py-2">Member</th>
                        <th className="px-3 py-2">Net PnL</th>
                        <th className="px-3 py-2">Win Rate</th>
                        <th className="px-3 py-2">Profit Factor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {preview.leaderboard.map((row) => (
                        <tr key={`${row.member}-${row.rank}`} className="border-b last:border-0">
                          <td className="px-3 py-2">{row.rank}</td>
                          <td className="px-3 py-2">{row.member}</td>
                          <td className="px-3 py-2">{formatNumber(row.net_pnl)}</td>
                          <td className="px-3 py-2">{formatNumber(row.win_rate, 4)}</td>
                          <td className="px-3 py-2">{formatNumber(row.profit_factor, 4)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Audit Timeline</h2>
              {auditEvents.length === 0 ? (
                <div className="mt-4 text-sm text-slate-500">No audit events found.</div>
              ) : (
                <div className="mt-4 space-y-4">
                  {auditEvents.map((event) => {
                    const oldState = tryParseJson(event.old_state);
                    const newState = tryParseJson(event.new_state);
                    const metadata = tryParseJson(event.metadata_json);

                    return (
                      <div key={event.id} className="rounded-xl border border-slate-200 p-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="font-medium">{event.event_type}</div>
                          <div className="text-xs text-slate-500">{formatDateTime(event.created_at)}</div>
                        </div>

                        <div className="mt-2 text-xs text-slate-500">
                          entity: {event.entity_type} / {event.entity_id} / workspace: {event.workspace_id ?? "—"}
                        </div>

                        <div className="mt-3 grid gap-3 lg:grid-cols-3">
                          <div>
                            <div className="mb-1 text-xs font-medium text-slate-500">Old State</div>
                            <pre className="overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs">
                              {JSON.stringify(oldState, null, 2)}
                            </pre>
                          </div>
                          <div>
                            <div className="mb-1 text-xs font-medium text-slate-500">New State</div>
                            <pre className="overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs">
                              {JSON.stringify(newState, null, 2)}
                            </pre>
                          </div>
                          <div>
                            <div className="mb-1 text-xs font-medium text-slate-500">Metadata</div>
                            <pre className="overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs">
                              {JSON.stringify(metadata, null, 2)}
                            </pre>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Lineage</h2>
              <div className="mt-4 space-y-3 text-sm">
                <div>
                  <div className="text-slate-500">Claim ID</div>
                  <div className="font-medium">{claim.id}</div>
                </div>
                <div>
                  <div className="text-slate-500">Root Claim ID</div>
                  <div className="font-medium">{claim.root_claim_id ?? "—"}</div>
                </div>
                <div>
                  <div className="text-slate-500">Parent Claim ID</div>
                  <div className="font-medium">{claim.parent_claim_id ?? "—"}</div>
                </div>
                <div>
                  <div className="text-slate-500">Version Number</div>
                  <div className="font-medium">{claim.version_number ?? "—"}</div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Versions</h2>
              {versions.length === 0 ? (
                <div className="mt-4 text-sm text-slate-500">No versions found.</div>
              ) : (
                <div className="mt-4 space-y-3">
                  {versions.map((version) => (
                    <Link
                      key={version.id}
                      href={`/workspace/${workspaceId}/claim/${version.id}`}
                      className="block rounded-xl border border-slate-200 p-3 transition hover:bg-slate-50"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="font-medium">{version.name}</div>
                        <StatusBadge status={version.status} />
                      </div>
                      <div className="mt-2 text-xs text-slate-500">
                        version {version.version_number} · root {version.root_claim_id ?? "—"} · parent{" "}
                        {version.parent_claim_id ?? "—"}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>

            <div className="rounded-2xl border bg-white p-5 shadow-sm">
              <h2 className="text-xl font-semibold">Quick Links</h2>
              <div className="mt-4 space-y-2 text-sm">
                <Link
                  href={`/workspace/${workspaceId}/claim/${claim.id}`}
                  className="block rounded-lg border px-3 py-2 hover:bg-slate-50"
                >
                  Refresh current claim page
                </Link>
                <Link
                  href={`/workspace/${workspaceId}/claims`}
                  className="block rounded-lg border px-3 py-2 hover:bg-slate-50"
                >
                  Go to claims list
                </Link>
                <Link
                  href={`/workspace/${workspaceId}/evidence?claimId=${claim.id}`}
                  className="block rounded-lg border px-3 py-2 hover:bg-slate-50"
                >
                  Go to evidence page
                </Link>
                <Link
                  href={`/workspace/${workspaceId}/ledger`}
                  className="block rounded-lg border px-3 py-2 hover:bg-slate-50"
                >
                  Go to ledger page
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}