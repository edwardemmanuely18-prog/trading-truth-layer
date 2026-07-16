import Link from "next/link";
import Navbar from "../../../components/Navbar";
import {
  api,
  type PublicClaimDirectoryItem,
  type PublicProfileResponse,
  type PublicTrustProfile,
} from "../../../lib/api";

import ProfileClaimSearch
from "../../../components/profile/ProfileClaimSearch";

const APP_URL =
  process.env.NEXT_PUBLIC_APP_URL || "https://trading-truth-layer.vercel.app";

export const revalidate = 60;

type ExtendedProfile = PublicProfileResponse & {
  contested_claims_count?: number;
};

type PageProps = {

    params: Promise<{
        id:string;
    }>;

    searchParams?: Promise<{
        q?:string;
    }>;

};

function getDisputeLabel(profile: any): string {
  if (!profile) return "No data";

  const count = Number(profile.contested_claims_count || 0);

  if (count === 0) return "No active contested claims";
  if (count < 3) return `${count} contested (low)`;
  if (count < 10) return `${count} contested (moderate)`;

  return `${count} contested (high)`;
}

type ExtendedClaim = PublicClaimDirectoryItem & {
  trust_score?: number;
  network_score?: number;
  trust_band?: string;
  has_active_dispute?: boolean;
  disputes_count?: number;
};

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function formatPercentFromScore(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${Number(value).toFixed(digits)}%`;
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function normalizeText(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function resolveProfileTrustBand(profile?: PublicTrustProfile | null) {
  const band = normalizeText(profile?.trust_profile_band);

  if (band === "institutional") {
    return {
      label: "Institutional",
      className: "border-emerald-300 bg-emerald-100 text-emerald-900",
    };
  }

  if (band === "strong") {
    return {
      label: "Strong",
      className: "border-blue-200 bg-blue-100 text-blue-800",
    };
  }

  if (band === "developing") {
    return {
      label: "Developing",
      className: "border-amber-200 bg-amber-100 text-amber-800",
    };
  }

  return {
    label: "Fragile",
    className: "border-red-200 bg-red-100 text-red-800",
  };
}

function resolveClaimTrustBand(claim: PublicClaimDirectoryItem) {
  const trustBand = normalizeText((claim as any)?.trust_band);

  const trustScore = Number(
    (claim as any)?.trust_score ?? 0
  );

  const hasActiveDispute = Boolean(
    (claim as any)?.has_active_dispute ?? false
  );

  if (hasActiveDispute || trustBand === "contested") {
    return {
      label: "Contested",
      className: "border-red-300 bg-red-100 text-red-800",
    };
  }

  // explicit backend trust band
  if (trustBand === "high") {
    return {
      label: "High Trust",
      className: "border-emerald-200 bg-emerald-100 text-emerald-800",
    };
  }

  if (trustBand === "moderate") {
    return {
      label: "Moderate Trust",
      className: "border-amber-200 bg-amber-100 text-amber-800",
    };
  }

  // fallback derived from numerical score
  if (trustScore >= 80) {
    return {
      label: "High Trust",
      className: "border-emerald-200 bg-emerald-100 text-emerald-800",
    };
  }

  if (trustScore >= 60) {
    return {
      label: "Moderate Trust",
      className: "border-amber-200 bg-amber-100 text-amber-800",
    };
  }

  return {
    label: "Low Trust",
    className: "border-red-200 bg-red-100 text-red-800",
  };
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: React.ReactNode;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-[24px] font-bold leading-none tabular-nums text-slate-950">
        {value}
      </div>
      <div className="mt-3 text-sm leading-6 text-slate-500">{hint}</div>
    </div>
  );
}

function sortClaims(claims: PublicClaimDirectoryItem[]) {
  return [...claims].sort((a, b) => {
    const aTrust = Number((a as any)?.trust_score ?? 0);
    const bTrust = Number((b as any)?.trust_score ?? 0);
    const aNet = Number(a?.net_pnl ?? 0);
    const bNet = Number(b?.net_pnl ?? 0);

    return bTrust - aTrust || bNet - aNet || Number(b.claim_schema_id) - Number(a.claim_schema_id);
  });
}

  export default async function Page({

      params,

      searchParams,

  }: PageProps) {
    const { id } =
      await params;

    const resolvedSearchParams =
        searchParams
            ? await searchParams
            : {};

    const searchQuery =

        resolvedSearchParams.q
            ?.toLowerCase()
            .trim()

        ?? "";
    const workspaceId = Number(id);

  if (!workspaceId || isNaN(workspaceId)) {
    return <div>Invalid profile id</div>;
  }

  let data: any = null;
  let loadError: string | null = null;

  if (!Number.isFinite(workspaceId) || workspaceId <= 0) {
    loadError = "Invalid profile id.";
  } else {
    try {
      data = await api.getPublicProfile(workspaceId);
    } catch (error) {
      loadError =
        error instanceof Error
          ? error.message
          : "Failed to load public profile.";
    }
  }

  const resolvedWorkspaceId =
  Number(data?.workspace_id) || workspaceId;

  const claims = sortClaims(
    (Array.isArray(data?.claims) ? data.claims : []).map((c: any, i: number) => ({
      claim_schema_id:
        c.claim_schema_id ??
        c.root_claim_id ??
        c.id ??
        i,
      claim_hash: c.claim_hash ?? `claim-${c.id ?? i}`,

      root_claim_id:
        c.root_claim_id ??
        c.claim_schema_id ??
        c.id ??
        null,

      public_view_path:
        c.public_view_path ??
        null,

      verify_path:
        c.verify_path ??
        null,
        
      name:
        c.name ??
        `Claim #${
          c.claim_schema_id ??
          c.root_claim_id ??
          c.id ??
          i
        }`,
      verification_status: "locked",

      trade_count: Number(c.trade_count ?? 0),
      net_pnl: Number(c.net_pnl ?? 0),

      trust_score: Number(c.trust_score ?? 0),
      network_score: Number(c.network_score ?? 0),

      disputes_count: Number(c.disputes_count ?? 0),
      has_active_dispute: Boolean(c.has_active_dispute ?? false),

      lifecycle: {
        locked_at: c?.lifecycle?.locked_at ?? null,
      },
    }))
  );

  const filteredClaims = claims.filter((claim) => {

    if (!searchQuery) {

      return true;

    }

    return (

      claim.name
        ?.toLowerCase()
        .includes(searchQuery)

      ||

      String(
        claim.claim_schema_id
      ).includes(searchQuery)

      ||

      claim.claim_hash
        ?.toLowerCase()
        .includes(searchQuery)

    );

  });

  const profile = data
  ? {
      workspace_id: resolvedWorkspaceId,

      name:
        typeof data?.name === "string" && data.name.trim().length > 0
          ? data.name
          : `Workspace #${resolvedWorkspaceId}`,

      type: "workspace",
      network: "internal",
      profile_id: `workspace:${resolvedWorkspaceId}`,

      trust_profile_band:
        Number(data?.stats?.avg_trust ?? 0) >= 80
          ? "institutional"
          : Number(data?.stats?.avg_trust ?? 0) >= 60
          ? "strong"
          : "developing",

      claims_count: claims.length,

      locked_claims_count: claims.length,

      contested_claims_count: claims.filter(
        (c: any) => c.has_active_dispute
      ).length,

      average_trust_score:
        claims.length > 0
          ? claims.reduce(
              (sum, c: any) => sum + Number(c.trust_score ?? 0),
              0
            ) / claims.length
          : 0,

      average_network_score:
        claims.length > 0
          ? claims.reduce(
              (sum, c: any) => sum + Number(c.network_score ?? 0),
              0
            ) / claims.length
          : 0,

      total_net_pnl: claims.reduce(
        (sum, c: any) => sum + Number(c.net_pnl ?? 0),
        0
      ),
    }
  : null;

  const derived = {
    claim_count: claims.length,
    avg_trust:
      claims.length > 0
        ? claims.reduce((sum, c) => sum + Number((c as any).trust_score ?? 0), 0) /
          claims.length
        : 0,
  };

  const profileBand = resolveProfileTrustBand(profile);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <div className="text-sm text-slate-500">Trading Truth Layer · Issuer Verification Profile</div>
          <h1 className="mt-2 text-4xl font-bold">
            {profile?.name || `Workspace #${workspaceId}`}
          </h1>
          <p className="mt-3 max-w-4xl text-slate-600">
            Public issuer-level trust surface aggregating locked claim quality,
            network-aware credibility, dispute posture, and historical claim outputs.
          </p>
        </div>

        {loadError ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
            {loadError}
          </div>
        ) : null}

        {!loadError && profile ? (
          <>

            <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Embed Trust Widget</h2>

              <div className="mt-2 text-sm text-slate-500">
                  Embed this profile’s trust surface into external websites or communities.
              </div>

              <div className="mt-4 overflow-x-auto rounded-lg bg-slate-900 p-4 font-mono text-xs text-green-400">
                <iframe
                  src={`/embed/profile/${workspaceId}`}
                  style={{
                    width: "100%",
                    height: "600px",
                    border: "none",
                    borderRadius: "12px",
                    background: "#fff"
                  }}
                />
              </div>
              </div>

              <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                  <div className="text-sm text-slate-500">Issuer Identity</div>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                      {profile.name}
                  </h2>

                  <div className="mt-4 flex flex-wrap items-center gap-3">
                      <span
                      className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${profileBand.className}`}
                      >
                      {profileBand.label}
                      </span>

                      <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {profile.type}
                      </span>

                      <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {profile.network}
                      </span>

                      <span className="text-xs text-slate-400">
                      {profile.profile_id}
                      </span>
                  </div>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                  <div>
                      <span className="font-medium text-slate-900">Workspace ID:</span>{" "}
                      {profile.workspace_id}
                  </div>
                  <div className="mt-2">
                      <span className="font-medium text-slate-900">Claims surfaced:</span>{" "}
                      {profile.claims_count ?? 0}
                  </div>
                  </div>
                </div>
              </div>

            <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <SummaryCard
                label="Average Trust"
                value={formatNumber(profile.average_trust_score || derived.avg_trust)}
                hint="Average backend-authoritative trust score across locked public claims"
              />
              <SummaryCard
                label="Average Network"
                value={formatNumber(profile.average_network_score)}
                hint="Average network-weighted credibility across profile claims"
              />
              <SummaryCard
                label="Locked Claims"
                value={profile.locked_claims_count || derived.claim_count}
                hint="Claims contributing to public trust posture"
              />
              <SummaryCard
                label="Contested Claims"
                value={profile.contested_claims_count}
                hint="Claims currently carrying active governance challenges"
              />
              <SummaryCard
                label="Total Net PnL"
                value={formatNumber(profile.total_net_pnl)}
                hint="Aggregate net pnl across locked public claims in this profile"
              />
            </div>

            <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Profile Trust Context</h2>
              <div className="mt-2 max-w-4xl text-sm text-slate-500">
                This profile aggregates claim-level trust, verification posture, evidence integrity,
                and governance into a public issuer profile backed by canonical records. 
                High-trust profiles sustain credible public distribution better than isolated claims because performance, governance,
                and verification posture are evaluated across claim history.
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                  <div className="font-semibold text-slate-900">Trust Profile Band</div>
                  <div className="mt-2">{profileBand.label}</div>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                  <div className="font-semibold text-slate-900">Claims Count</div>
                  <div className="mt-2">{profile.claims_count}</div>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                  <div className="font-semibold text-slate-900">Locked Claims Count</div>
                  <div className="mt-2">{profile.locked_claims_count}</div>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
                  <div className="font-semibold text-slate-900">Dispute Concentration</div>
                  <div className="mt-2">
                    {getDisputeLabel(profile)}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Claims Under This Profile</h2>

              <div className="mt-6">

                  <ProfileClaimSearch

                      workspaceId={
                          workspaceId
                      }

                      initialValue={
                          searchQuery
                      }

                  />

              </div>

              <div className="mt-2 text-sm text-slate-500">
                Locked public claims ranked here by trust first, then net pnl.
              </div>

              {!Array.isArray(claims) || filteredClaims.length === 0 ? (
                <div className="mt-4 text-slate-600">No public claims available for this profile.</div>
              ) : (
                <div className="mt-4 max-h-[700px] overflow-auto">
                  <table className="min-w-full border-separate border-spacing-0 text-sm">
                    <thead className="sticky top-0 z-10 bg-white">
                      <tr className="border-b text-left text-slate-500">
                        <th className="px-3 py-3">Claim</th>
                        <th className="px-3 py-3">Status</th>
                        <th className="px-3 py-3">Trades</th>
                        <th className="px-3 py-3">Net PnL</th>
                        <th className="px-3 py-3">Trust Score</th>
                        <th className="px-3 py-3">Network Score</th>
                        <th className="px-3 py-3">Disputes</th>
                        <th className="px-3 py-3">Locked At</th>
                        <th className="px-3 py-3">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredClaims.map((claim) => {
                        const trustBand = resolveClaimTrustBand(claim);
                        const hasActiveDispute = Boolean((claim as ExtendedClaim)?.has_active_dispute ?? false);
                        const trustScore = Number((claim as ExtendedClaim)?.trust_score ?? 0);
                        const networkScore = Number((claim as ExtendedClaim)?.network_score ?? 0);
                        const disputesCount = Number((claim as ExtendedClaim)?.disputes_count ?? 0);

                        const canonicalClaimId =
                          (claim as any)?.root_claim_id ??
                          claim.claim_schema_id;

                        const publicViewPath =
                          (claim as any)?.public_view_path ??
                          `/claim/${canonicalClaimId}/public`;

                        const verifyPath =
                          (claim as any)?.verify_path ??
                          `/verify/${claim.claim_hash}`;

                        return (
                          <tr
                            key={`${claim.claim_schema_id}-${claim.claim_hash}`}
                            className="border-b last:border-0 align-top"
                          >
                            <td className="px-3 py-3">
                              <div className="font-medium text-slate-950">{claim.name}</div>
                              <div className="mt-1 text-xs text-slate-500">
                                claim #{claim.claim_schema_id}
                              </div>
                              <div className="mt-1 font-mono text-xs text-slate-500">
                                {claim.claim_hash}
                              </div>
                              <div className="mt-1 text-[10px] text-blue-500">
                                publicly verifiable · shareable · canonical
                              </div>
                            </td>

                            <td className="px-3 py-3">
                              <div className="flex flex-wrap gap-2">
                                <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                                  {claim.verification_status}
                                </span>
                                <span
                                  className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${trustBand.className}`}
                                >
                                  {trustBand.label}
                                </span>
                              </div>
                            </td>

                            <td className="px-3 py-3 tabular-nums">{claim.trade_count}</td>

                            <td className="px-3 py-3 font-semibold tabular-nums">
                              {formatNumber(claim.net_pnl)}
                            </td>

                            <td className="px-3 py-3">
                              <div className="font-semibold tabular-nums text-slate-950">
                                {formatNumber(trustScore)}
                              </div>
                              <div className="mt-1 text-xs text-slate-500">
                                {formatPercentFromScore(trustScore)}
                              </div>
                            </td>

                            <td className="px-3 py-3">
                              <div className="font-semibold tabular-nums text-slate-950">
                                {formatNumber(networkScore)}
                              </div>
                              <div className="mt-1 text-xs text-slate-500">
                                network-aware credibility
                              </div>
                            </td>

                            <td className="px-3 py-3">
                              {hasActiveDispute ? (
                                <span className="inline-flex rounded-full border border-red-300 bg-red-100 px-3 py-1 text-xs font-semibold text-red-800">
                                  {disputesCount} contested
                                </span>
                              ) : (
                                <span className="inline-flex rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
                                  clean
                                </span>
                              )}
                            </td>

                            <td className="px-3 py-3 text-slate-700">
                              {formatDateTime(claim.lifecycle?.locked_at)}
                            </td>

                            <td className="px-3 py-3">
                              <div className="flex flex-wrap gap-2">
                                <Link
                                  href={publicViewPath}
                                className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                                >
                                  Public Record
                                </Link>

                                <Link
                                  href={verifyPath}
                                  className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                                >
                                  Verify
                                </Link>

                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}