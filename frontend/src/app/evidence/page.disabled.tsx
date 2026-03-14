"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import DownloadEvidenceButton from "../../components/DownloadEvidenceButton";
import {
  api,
  type ClaimIntegrityResult,
  type ClaimSchema,
  type EvidenceBundle,
  type EvidencePack,
  type PublicClaim,
} from "../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatNumber(value: unknown, digits = 4) {
  if (typeof value !== "number") return "—";
  return value.toFixed(digits);
}

export default function EvidencePage() {
  const searchParams = useSearchParams();
  const claimIdFromQuery = searchParams.get("claimId");

  const [claimId, setClaimId] = useState<number | null>(null);
  const [claim, setClaim] = useState<ClaimSchema | null>(null);
  const [evidencePack, setEvidencePack] = useState<EvidencePack | null>(null);
  const [evidenceBundle, setEvidenceBundle] = useState<EvidenceBundle | null>(null);
  const [publicClaim, setPublicClaim] = useState<PublicClaim | null>(null);
  const [integrity, setIntegrity] = useState<ClaimIntegrityResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const resolvedClaimId = useMemo(() => {
    if (!claimIdFromQuery) return null;
    const parsed = Number(claimIdFromQuery);
    return Number.isNaN(parsed) ? null : parsed;
  }, [claimIdFromQuery]);

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

        const evidenceRes = await api.getEvidencePack(targetClaimId);
        setEvidencePack(evidenceRes);

        try {
          const bundleRes = await api.getEvidenceBundle(targetClaimId);
          setEvidenceBundle(bundleRes);
        } catch {
          setEvidenceBundle(null);
        }

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

  if (loading) {
    return <div className="p-6">Loading evidence pack...</div>;
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
      </div>
    );
  }

  if (!claimId || !claim || !evidencePack) {
    return <div className="p-6">No evidence pack available.</div>;
  }

  const metricsSnapshot = evidencePack.metrics_snapshot as Record<string, unknown>;
  const schemaSnapshot = evidencePack.schema_snapshot as Record<string, unknown>;

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="mb-2 text-sm text-slate-500">
            <Link href="/claims" className="hover:underline">
              Claims
            </Link>
            <span className="mx-2">/</span>
            <Link href={`/claim/${claimId}`} className="hover:underline">
              Claim #{claimId}
            </Link>
            <span className="mx-2">/</span>
            <span>Evidence</span>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Evidence Pack</h1>
          <div className="mt-2 text-slate-600">
            {claim.name} · status: <span className="font-medium">{claim.status}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <DownloadEvidenceButton
            claimSchemaId={claimId}
            claimHash={evidencePack.claim_hash}
            payload={evidencePack}
          />
          <Link
            href={`/claim/${claimId}`}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Back to Claim
          </Link>
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
              <div className="text-sm text-slate-500">Claim Hash</div>
              <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                {evidencePack.claim_hash || "—"}
              </div>
            </div>

            <div>
              <div className="text-sm text-slate-500">Trade Set Hash</div>
              <div className="mt-1 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                {evidencePack.trade_set_hash}
              </div>
            </div>

            <div>
              <div className="text-sm text-slate-500">Methodology Notes</div>
              <div className="mt-1 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                {evidencePack.methodology_notes || "—"}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <div className="text-sm text-slate-500">Status</div>
                <div className="mt-1 font-medium">{claim.status}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Visibility</div>
                <div className="mt-1 font-medium">{claim.visibility}</div>
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
                <div className="text-sm text-slate-500">Root Claim ID</div>
                <div className="mt-1 font-medium">{claim.root_claim_id ?? "—"}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Integrity Verification</h2>

          {!integrity ? (
            <div className="mt-4 text-sm text-slate-500">
              Integrity result not available. Locked claims will show verification details here.
            </div>
          ) : (
            <div className="mt-4 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Integrity Status</div>
                  <div className="mt-1 font-medium">{integrity.integrity_status}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Hash Match</div>
                  <div className="mt-1 font-medium">{String(integrity.hash_match)}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Trade Count</div>
                  <div className="mt-1 font-medium">{integrity.trade_count}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Verified At</div>
                  <div className="mt-1 font-medium">{formatDateTime(integrity.verified_at)}</div>
                </div>
              </div>

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
          )}
        </div>
      </div>

      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">ZIP Bundle Manifest</h2>
        {!evidenceBundle ? (
          <div className="mt-4 text-sm text-slate-500">ZIP bundle preview not available.</div>
        ) : (
          <div className="mt-4 space-y-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <div className="text-sm text-slate-500">Export Version</div>
                <div className="mt-1 font-medium">{evidenceBundle.manifest.export_version}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Exported At</div>
                <div className="mt-1 font-medium">{formatDateTime(evidenceBundle.manifest.exported_at)}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Included Files</div>
                <div className="mt-1 font-medium">{evidenceBundle.manifest.included_files.length}</div>
              </div>
              <div>
                <div className="text-sm text-slate-500">Audit Events</div>
                <div className="mt-1 font-medium">{evidenceBundle.audit_events.event_count}</div>
              </div>
            </div>

            <pre className="overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
              {JSON.stringify(evidenceBundle.manifest, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Schema Snapshot</h2>
          <pre className="mt-4 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
            {JSON.stringify(schemaSnapshot, null, 2)}
          </pre>
        </div>

        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Metrics Snapshot</h2>
          <pre className="mt-4 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
            {JSON.stringify(metricsSnapshot, null, 2)}
          </pre>
        </div>
      </div>

      <div className="rounded-2xl border bg-white p-5 shadow-sm">
        <h2 className="text-xl font-semibold">Public Verification View</h2>
        {!publicClaim ? (
          <div className="mt-4 text-sm text-slate-500">
            Public claim view not available for this claim visibility yet.
          </div>
        ) : (
          <pre className="mt-4 overflow-x-auto rounded-xl bg-slate-50 p-4 text-xs text-slate-700">
            {JSON.stringify(publicClaim, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}