// frontend/src/app/profile/[id]/page.tsx

import Link from "next/link";
import Navbar from "../../../components/Navbar";
import {
  api,
  type PublicClaimDirectoryItem,
  type PublicProfileResponse,
  type PublicTrustProfile,
} from "../../../lib/api";

type PageProps = {
  params: Promise<{
    id: string;
  }>;
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
  const hasActiveDispute = Boolean((claim as any)?.has_active_dispute ?? false);

  if (hasActiveDispute || trustBand === "contested") {
    return {
      label: "Contested",
      className: "border-red-300 bg-red-100 text-red-800",
    };
  }

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

export default async function PublicProfilePage({ params }: PageProps) {
  const resolvedParams = await params;
  const workspaceId = Number(resolvedParams.id);

  let data: PublicProfileResponse | null = null;
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

  const profile = data?.profile ?? null;
  const claims = sortClaims(data?.claims ?? []);
  const profileBand = resolveProfileTrustBand(profile);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <div className="text-sm text-slate-500">Trading Truth Layer · Public Trust Profile</div>
          <h1 className="mt-2 text-4xl font-bold">
            {profile?.name || `Profile #${resolvedParams.id}`}
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
            <div className="mb-8 rounded-2xl border border-blue-200 bg-blue-50 p-6 shadow-sm">
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div>
                    <div className="text-sm font-semibold text-blue-900">
                        Public Trust Proof
                    </div>
                    <div className="mt-1 text-sm text-blue-800">
                        This profile is a verifiable public trust surface backed by locked claims,
                        audit history, and network-aware scoring.
                    </div>

                    <div className="mt-3 text-xs text-blue-700 font-mono">
                        https://tradingtruthlayer.com/profile/{profile.workspace_id}
                    </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                    <button
                        onClick={() =>
                        navigator.clipboard.writeText(
                            `${typeof window !== "undefined" ? window.location.origin : ""}/profile/${profile.workspace_id}`
                        )
                        }
                        className="rounded-lg border border-blue-300 bg-white px-3 py-2 text-xs font-medium hover:bg-blue-100"
                    >
                        Copy Link
                    </button>

                    <a
                        href={`https://twitter.com/intent/tweet?text=Verified%20Trading%20Profile&url=${encodeURIComponent(
                        `/profile/${profile.workspace_id}`
                        )}`}
                        target="_blank"
                        className="rounded-lg border border-blue-300 bg-white px-3 py-2 text-xs font-medium hover:bg-blue-100"
                    >
                        Share
                      </a>
                    </div>
                  </div>
                </div>

              <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
                <h2 className="text-xl font-semibold">Embed Trust Widget</h2>

                <div className="mt-2 text-sm text-slate-500">
                    Embed this profile’s trust surface into external websites or communities.
                </div>

                <div className="mt-4 rounded-lg bg-slate-900 p-4 text-xs text-green-400 font-mono overflow-x-auto">
              {`<iframe src="${typeof window !== "undefined" ? window.location.origin : ""}/profile/${profile.workspace_id}" width="100%" height="600" />`}
                </div>
              </div>
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
                    {data?.claims_count ?? 0}
                  </div>
                  <div className="mt-2">
                    <Link
                      href="/leaderboard"
                      className="text-slate-900 underline underline-offset-4"
                    >
                      Back to Leaderboard
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <SummaryCard
                label="Average Trust"
                value={formatNumber(profile.average_trust_score)}
                hint="Average backend-authoritative trust score across locked public claims"
              />
              <SummaryCard
                label="Average Network"
                value={formatNumber(profile.average_network_score)}
                hint="Average network-weighted credibility across profile claims"
              />
              <SummaryCard
                label="Locked Claims"
                value={profile.locked_claims_count}
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
                This profile aggregates claim-level trust, dispute pressure, and network-aware
                reputation into a public issuer surface. High-trust profiles sustain credible
                public distribution better than isolated claims because performance, governance,
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
                    {profile.contested_claims_count > 0
                      ? `${profile.contested_claims_count} contested`
                      : "No active contested claims"}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <h2 className="text-2xl font-semibold">Claims Under This Profile</h2>
              <div className="mt-2 text-sm text-slate-500">
                Locked public claims ranked here by trust first, then net pnl.
              </div>

              {claims.length === 0 ? (
                <div className="mt-4 text-slate-600">No public claims available for this profile.</div>
              ) : (
                <div className="mt-4 overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
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
                      {claims.map((claim) => {
                        const trustBand = resolveClaimTrustBand(claim);
                        const hasActiveDispute = Boolean((claim as any)?.has_active_dispute ?? false);
                        const trustScore = Number((claim as any)?.trust_score ?? 0);
                        const networkScore = Number((claim as any)?.network_score ?? 0);
                        const disputesCount = Number((claim as any)?.disputes_count ?? 0);

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
                                    href={`/claim/${claim.claim_schema_id}/public`}
                                    className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                                >
                                    Public Record
                                </Link>

                                <Link
                                    href={`/verify/${claim.claim_hash}`}
                                    className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                                >
                                    Verify
                                </Link>

                                <button
                                    onClick={() =>
                                    navigator.clipboard.writeText(
                                        `${typeof window !== "undefined" ? window.location.origin : ""}/verify/${claim.claim_hash}`
                                    )
                                    }
                                    className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-medium hover:bg-slate-50"
                                >
                                    Copy Proof
                                </button>
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