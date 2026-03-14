"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import DownloadEvidenceButton from "../../../../components/DownloadEvidenceButton";
import EvidenceCard from "../../../../components/EvidenceCard";
import {
  api,
  type AuditEvent,
  type ClaimIntegrityResult,
  type ClaimSchema,
  type EvidenceBundle,
  type EvidencePack,
  type PublicClaim,
} from "../../../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value: unknown, digits = 4) {
  if (typeof value !== "number" || Number.isNaN(value)) return "—";
  return value.toFixed(digits);
}

function safeJson(value: unknown) {
  return JSON.stringify(value ?? {}, null, 2);
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
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "published"
        ? "border-blue-200 bg-blue-100 text-blue-800"
        : normalized === "verified"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

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

export default function WorkspaceEvidencePage() {
  const params = useParams();
  const searchParams = useSearchParams();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const claimIdFromQuery = searchParams.get("claimId");

  const resolvedClaimId = useMemo(() => {
    if (!claimIdFromQuery) return null;
    const parsed = Number(claimIdFromQuery);
    return Number.isNaN(parsed) ? null : parsed;
  }, [claimIdFromQuery]);

  const [claimId, setClaimId] = useState<number | null>(null);
  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [evidencePack, setEvidencePack] = useState<EvidencePack | null>(null);
  const [evidenceBundle, setEvidenceBundle] = useState<EvidenceBundle | null>(null);
  const [publicClaim, setPublicClaim] = useState<PublicClaim | null>(null);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);

      try {
        let targetClaimId = resolvedClaimId;

        if (!targetClaimId) {
          const latest = await api.getLatestClaimSchema();
          targetClaimId = latest.id;
        }

        setClaimId(targetClaimId);

        const claimRes = await api.getClaimSchema(targetClaimId);
        setClaim(claimRes);

        const [evidenceRes, bundleRes, auditRes] = await Promise.all([
          api.getEvidencePack(targetClaimId),
          api.getEvidenceBundle(targetClaimId).catch(() => null),
          api.getAuditEventsForEntity("claim_schema", targetClaimId).catch(() => []),
        ]);

        setEvidencePack(evidenceRes);
        setEvidenceBundle(bundleRes);
        setAuditEvents(Array.isArray(auditRes) ? auditRes : []);

        try {
          const publicRes = await api.getPublicClaim(targetClaimId);
          setPublicClaim(publicRes);
        } catch {
          setPublicClaim(null);
        }

        if (claimRes.status === "locked") {
          try {
            const integrityRes = await api.getClaimIntegrity(targetClaimId);
            setIntegrity(integrityRes);
          } catch {
            setIntegrity(null);
          }
        } else {
          setIntegrity(null);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load evidence page");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [resolvedClaimId]);

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading evidence pack...</div>
      </div>
    );
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

  if (!claimId || !claim || !evidencePack) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">No evidence pack available.</div>
      </div>
    );
  }

  const metricsSnapshot = (evidencePack.metrics_snapshot ?? {}) as Record<string, unknown>;
  const schemaSnapshot = (evidencePack.schema_snapshot ?? {}) as Record<string, unknown>;
  const lifecycle = evidencePack.lifecycle ?? {
    status: claim.status,
    verified_at: claim.verified_at,
    published_at: claim.published_at,
    locked_at: claim.locked_at,
    locked_trade_set_hash: claim.locked_trade_set_hash,
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] space-y-6 px-6 py-10">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="mb-2 text-sm text-slate-500">
              <Link href={`/workspace/${workspaceId}/claims`} className="hover:underline">
                Claims
              </Link>
              <span className="mx-2">/</span>
              <Link href={`/workspace/${workspaceId}/claim/${claimId}`} className="hover:underline">
                Claim #{claimId}
              </Link>
              <span className="mx-2">/</span>
              <span>Evidence</span>
            </div>

            <h1 className="text-3xl font-semibold tracking-tight">Evidence Center</h1>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              <StatusBadge status={claim.status} />
              <IntegrityBadge integrity={integrity} />
            </div>

            <div className="mt-2 text-slate-600">{claim.name}</div>
          </div>

          <div className="flex flex-wrap gap-2">
            <DownloadEvidenceButton
              claimSchemaId={claimId}
              claimHash={evidencePack.claim_hash}
              payload={evidencePack}
            />

            <Link
              href={`/workspace/${workspaceId}/claim/${claimId}`}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Open Claim
            </Link>

            {publicClaim?.claim_hash ? (
              <Link
                href={`/verify/${publicClaim.claim_hash}`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Public Verify
              </Link>
            ) : null}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Claim ID</div>
            <div className="mt-2 text-2xl font-semibold">{claimId}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trade Count</div>
            <div className="mt-2 text-2xl font-semibold">
              {typeof metricsSnapshot.trade_count === "number" ? metricsSnapshot.trade_count : "—"}
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Net PnL</div>
            <div className="mt-2 text-2xl font-semibold">{formatNumber(metricsSnapshot.net_pnl, 2)}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Profit Factor</div>
            <div className="mt-2 text-2xl font-semibold">
              {formatNumber(metricsSnapshot.profit_factor, 4)}
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Evidence Summary</h2>

            <div className="mt-4 space-y-4">
              <div>
                <div className="text-sm text-slate-500">Exported At</div>
                <div className="mt-1 font-medium">{formatDateTime(evidencePack.exported_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Export Version</div>
                <div className="mt-1 font-medium">{evidencePack.export_version || "—"}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Claim Hash</div>
                <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                  {evidencePack.claim_hash || "—"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Trade Set Hash</div>
                <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                  {evidencePack.trade_set_hash || "—"}
                </div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Methodology Notes</div>
                <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                  {evidencePack.methodology_notes || "—"}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Lifecycle & Integrity</h2>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <div className="text-sm text-slate-500">Status</div>
                <div className="mt-1 font-medium">{lifecycle.status || "—"}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Integrity Status</div>
                <div className="mt-1 font-medium">{integrity?.integrity_status || "not checked"}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Verified At</div>
                <div className="mt-1 font-medium">{formatDateTime(lifecycle.verified_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Published At</div>
                <div className="mt-1 font-medium">{formatDateTime(lifecycle.published_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Locked At</div>
                <div className="mt-1 font-medium">{formatDateTime(lifecycle.locked_at)}</div>
              </div>

              <div>
                <div className="text-sm text-slate-500">Hash Match</div>
                <div className="mt-1 font-medium">
                  {integrity ? String(integrity.hash_match) : "—"}
                </div>
              </div>
            </div>

            {integrity ? (
              <div className="mt-4 space-y-3">
                <div>
                  <div className="text-sm text-slate-500">Stored Hash</div>
                  <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                    {integrity.stored_hash}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Recomputed Hash</div>
                  <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                    {integrity.recomputed_hash}
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 text-sm text-slate-500">
                Integrity result is available after lock state verification.
              </div>
            )}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <EvidenceCard title="Schema Snapshot" value={safeJson(schemaSnapshot)} />
          <EvidenceCard title="Metrics Snapshot" value={safeJson(metricsSnapshot)} />
          <EvidenceCard
            title="Bundle Manifest"
            value={evidenceBundle ? safeJson(evidenceBundle.manifest) : "ZIP bundle preview not available."}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Audit Timeline Preview</h2>

            {auditEvents.length === 0 ? (
              <div className="mt-4 text-sm text-slate-500">No audit events found for this claim.</div>
            ) : (
              <div className="mt-4 space-y-4">
                {auditEvents.slice(0, 6).map((event) => {
                  const metadata = tryParseJson(event.metadata_json);

                  return (
                    <div key={event.id} className="rounded-xl border border-slate-200 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="font-medium">{event.event_type}</div>
                        <div className="text-xs text-slate-500">{formatDateTime(event.created_at)}</div>
                      </div>

                      <div className="mt-2 text-xs text-slate-500">
                        entity: {event.entity_type} / {event.entity_id}
                      </div>

                      <pre className="mt-3 overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
                        {JSON.stringify(metadata, null, 2)}
                      </pre>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <h2 className="text-xl font-semibold">Public Verification Snapshot</h2>

            {!publicClaim ? (
              <div className="mt-4 text-sm text-slate-500">
                Public claim view is not available for this claim yet.
              </div>
            ) : (
              <div className="mt-4 space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <div className="text-sm text-slate-500">Public Visibility</div>
                    <div className="mt-1 font-medium">{publicClaim.scope.visibility || "—"}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-500">Public Route Ready</div>
                    <div className="mt-1 font-medium">
                      {publicClaim.is_publicly_accessible ? "yes" : "yes"}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Public Claim Payload Preview</div>
                  <pre className="mt-2 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
                    {safeJson(publicClaim)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
