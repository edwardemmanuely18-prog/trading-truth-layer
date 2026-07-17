"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import {
  api,
  getWorkspaceEntitlements,
} from "../lib/api";
import { useAuth } from "./AuthProvider";
import WorkspaceSwitcher from "./WorkspaceSwitcher";

import { Lock } from "lucide-react";

import UpgradeRequired from "./UpgradeRequired";

type Props = {
  workspaceId?: number;
};

function normalizePath(value?: string | null) {
  return String(value || "").replace(/\/+$/, "");
}

function startsWithPath(currentPath: string, basePath: string) {
  const current = normalizePath(currentPath);
  const base = normalizePath(basePath);
  return current === base || current.startsWith(`${base}/`);
}

function isPublicTrustPath(currentPath: string) {
  return (
    currentPath === "/claims" ||
    currentPath === "/leaderboard" ||
    currentPath === "/how-it-works" ||
    startsWithPath(currentPath, "/claim") ||
    startsWithPath(currentPath, "/verify") ||
    startsWithPath(currentPath, "/profile") ||
    /^\/workspace\/\d+\/public-records(?:\/|$)/.test(currentPath) ||
    /^\/workspace\/\d+\/leaderboard(?:\/|$)/.test(currentPath)
  );
}

export default function Navbar({ workspaceId }: Props) {
  const pathname = usePathname();
  const { user, logout, getWorkspaceRole, loading, workspaces } = useAuth();

  const [
    entitlements,
    setEntitlements,
  ] = useState<any>(null);

  const [
      upgradeFeature,
      setUpgradeFeature,
  ] = useState<string | null>(null);

  const resolvedWorkspaceId = useMemo(() => {
    if (typeof workspaceId === "number" && !Number.isNaN(workspaceId)) {
      return workspaceId;
    }

    if (Array.isArray(workspaces) && workspaces.length > 0) {
      return workspaces[0].workspace_id;
    }

    return null;
  }, [workspaceId, workspaces]);

  useEffect(() => {

      if (!resolvedWorkspaceId) {
          return;
      }

      let mounted = true;

      async function loadEntitlements() {

          try {

              if (resolvedWorkspaceId == null) {
                  return;
              }

              const result =
                  await getWorkspaceEntitlements(
                      resolvedWorkspaceId,
                  );

              if (mounted) {

                  setEntitlements(
                      result,
                  );

              }

          } catch {

              // Leave navigation visible if
              // entitlements cannot be loaded.

          }

      }

      void loadEntitlements();

      return () => {

          mounted = false;

      };

  }, [
      resolvedWorkspaceId,
  ]);

  const currentPath = normalizePath(pathname);
  const publicTrustActive = isPublicTrustPath(currentPath);

  const workspaceRole = useMemo(() => {
    if (resolvedWorkspaceId == null) return null;
    return getWorkspaceRole(resolvedWorkspaceId);
  }, [getWorkspaceRole, resolvedWorkspaceId]);

  if (!publicTrustActive && !resolvedWorkspaceId) {
    return null;
  }

  const canSeeImport = workspaceRole === "owner" || workspaceRole === "operator";
  const canSeeSchema = workspaceRole === "owner" || workspaceRole === "operator";
  const canSeeMembers =
    workspaceRole === "owner" ||
    workspaceRole === "operator" ||
    workspaceRole === "auditor" ||
    workspaceRole === "member";

  const homeHref = "/";
  const howItWorksHref = "/how-it-works";
  const base = resolvedWorkspaceId ? `/workspace/${resolvedWorkspaceId}` : "";

  const publicClaimsHref = resolvedWorkspaceId
    ? `${base}/public-records`
    : "/claims";

  const leaderboardHref = resolvedWorkspaceId
    ? `${base}/leaderboard`
    : "/leaderboard";

  const publicProfileHref = resolvedWorkspaceId
    ? `/profile/${resolvedWorkspaceId}`
    : "/profile";

  const claimBuilderHref = resolvedWorkspaceId
    ? `${base}/claims`
    : "/claims";
  const dashboardHref = resolvedWorkspaceId ? `${base}/dashboard` : "/";
  const importHref =
    resolvedWorkspaceId
      ? `${base}/import-center`
      : "/";
  const ledgerHref = resolvedWorkspaceId ? `${base}/ledger` : "/";
  const workspaceSchemaHref =
    resolvedWorkspaceId
      ? `${base}/claims`
      : "/";
  const claimsHref = resolvedWorkspaceId ? `${base}/claims` : "/";
  const latestClaimHref = null;
  const evidenceHref =
    resolvedWorkspaceId
      ? `${base}/evidence`
      : "/";
  const membersHref = resolvedWorkspaceId ? `${base}/members` : "/";
  const settingsHref = resolvedWorkspaceId ? `${base}/settings` : "/";

  const homeActive = currentPath === "/";
  const howItWorksActive = currentPath === "/how-it-works";

  const publicClaimsActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, publicClaimsHref) || startsWithPath(currentPath, "/claim")
    : currentPath === "/claims" || startsWithPath(currentPath, "/claim");

  const leaderboardActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, leaderboardHref)
    : currentPath === "/leaderboard";

  const schemaBuilderActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, `${base}/claims`)
    : false;

  const publicProfileActive = startsWithPath(currentPath, "/profile");

  const dashboardActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, dashboardHref)
    : false;
  const importActive = resolvedWorkspaceId ? startsWithPath(currentPath, importHref) : false;
  const ledgerActive = resolvedWorkspaceId ? startsWithPath(currentPath, ledgerHref) : false;
  const workspaceSchemaActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, workspaceSchemaHref)
    : false;
  const claimsActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, claimsHref) ||
      startsWithPath(currentPath, `${base}/claim`)
    : false;
  const latestClaimActive = latestClaimHref
    ? startsWithPath(currentPath, latestClaimHref)
    : false;
  const evidenceActive = resolvedWorkspaceId
    ? startsWithPath(currentPath, `${base}/evidence`) ||
      (startsWithPath(currentPath, `${base}/claim`) && currentPath.endsWith("/evidence"))
    : false;
  const membersActive = resolvedWorkspaceId ? startsWithPath(currentPath, membersHref) : false;
  const settingsActive = resolvedWorkspaceId ? startsWithPath(currentPath, settingsHref) : false;
  const intakeActive =
    startsWithPath(currentPath, `${base}/broker-connections`) ||
    startsWithPath(currentPath, `${base}/import`) ||
    startsWithPath(currentPath, `${base}/import-center`) ||
    startsWithPath(currentPath, `${base}/sync-jobs`) ||
    startsWithPath(currentPath, `${base}/adapter-registry`);

  const registryActive =
    startsWithPath(currentPath, `${base}/ledger`) ||
    startsWithPath(currentPath, `${base}/evidence-records`) ||
    startsWithPath(currentPath, `${base}/import-batches`) ||
    startsWithPath(currentPath, `${base}/audit-timeline`) ||
    startsWithPath(currentPath, `${base}/integrity-registry`);

  const claimOperationsActive =
    currentPath === "/schema" ||
    startsWithPath(currentPath, `${base}/claims`) ||
    startsWithPath(currentPath, `${base}/evidence`) ||
    startsWithPath(currentPath, `${base}/schema`) ||
    startsWithPath(currentPath, `${base}/claim-templates`);

  const trustActive =
    startsWithPath(currentPath, `${base}/trust-scores`) ||
    startsWithPath(currentPath, `${base}/leaderboard`) ||
    startsWithPath(currentPath, `${base}/verification-analytics`) ||
    startsWithPath(currentPath, `${base}/integrity-analytics`) ||
    startsWithPath(currentPath, `${base}/evidence-analytics`) ||
    startsWithPath(currentPath, `${base}/risk-analytics`) ||
    startsWithPath(currentPath, `${base}/due-diligence`) ||
    startsWithPath(currentPath, `${base}/report-center`);

  const investigationActive =
    startsWithPath(
        currentPath,
        `${base}/investigation-overview`,
    ) ||

    startsWithPath(
        currentPath,
        `${base}/investigation-timeline`,
    ) ||

    startsWithPath(
        currentPath,
        `${base}/investigation-evidence`,
    ) ||

    startsWithPath(
        currentPath,
        `${base}/investigation-domains`,
    ) ||

    startsWithPath(
        currentPath,
        `${base}/investigation-findings`,
    ) ||

    startsWithPath(
        currentPath,
        `${base}/investigation-reports`,
    ) ||

    startsWithPath(
        currentPath,
        `${base}/investigations`,
    );


  const publicActive =
    startsWithPath(currentPath, `${base}/public-records`) ||
    startsWithPath(currentPath, `${base}/verification-routes`) ||
    startsWithPath(currentPath, `${base}/trust-directory`) ||
    startsWithPath(currentPath, `${base}/verification-network`) ||
    startsWithPath(currentPath, `${base}/external-reviews`) ||
    startsWithPath(currentPath, `${base}/evidence-graph`) ||
    startsWithPath(currentPath, `${base}/public-profiles`) ||
    startsWithPath(currentPath, "/claim") ||
    startsWithPath(currentPath, "/verify") ||
    startsWithPath(currentPath, "/profile");

  const administrationActive =
    startsWithPath(currentPath, `${base}/members`) ||
    startsWithPath(currentPath, `${base}/roles`) ||
    startsWithPath(currentPath, `${base}/billing`) ||
    startsWithPath(currentPath, `${base}/settings`);
    
  const activeDomain =
    dashboardActive
        ? "dashboard"
        : intakeActive
            ? "intake"
            : registryActive
                ? "registry"
                : claimOperationsActive
                    ? "claims"
                    : trustActive
                        ? "trust"
                        : investigationActive
                            ? "investigation"
                            : publicActive
                                ? "public"
                                : administrationActive
                                    ? "admin"
                                    : "dashboard";

  function pageEnabled(
      page: string,
  ) {

      if (!entitlements) {
          return true;
      }

      if (
          entitlements.navigation_items?.__all__
      ) {
          return true;
      }

      if (
          entitlements.pages?.__all__
      ) {
          return true;
      }

      return Boolean(

          entitlements.navigation_items?.[page] ??

          entitlements.pages?.[page]

      );

  }

  function domainEnabled(
      ...pages: string[]
  ) {

      if (!entitlements) {
          return true;
      }

      if (
          entitlements.navigation_domains?.__all__
      ) {
          return true;
      }

      if (
          entitlements.pages?.__all__
      ) {
          return true;
      }

      return pages.some(

          page =>

              Boolean(

                  entitlements.navigation_domains?.[
                      page
                  ]

                  ??

                  entitlements.pages?.[
                      page
                  ]

              )

      );

  }

  function navClass(active: boolean) {
    return active
      ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm"
      : "rounded-xl px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100";
  }

  function disabledNavClass() {

      return `
          rounded-xl
          border
          border-slate-200
          bg-slate-100
          px-4
          py-2
          text-sm
          font-medium
          text-slate-400
          cursor-not-allowed
          opacity-70
      `;

  }

  function utilityNavClass(active: boolean) {
    return active
      ? "rounded-lg border border-slate-300 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white"
      : "rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:bg-slate-50";
  }

  const dashboardLinks = resolvedWorkspaceId
    ? [
        {
          href: dashboardHref,
          label: "Executive Dashboard",
          active: dashboardActive,
        },
      ]
    : [];

  const intakeLinks =
      resolvedWorkspaceId && canSeeImport
          ? [
              {
                  href: `${base}/broker-connections`,
                  label: "Broker Connections",
                  feature: "broker_connections",
                  active: startsWithPath(
                      currentPath,
                      `${base}/broker-connections`
                  ),
              },
              {
                  href: `${base}/import-center`,
                  label: "Import Center",
                  feature: "import_center",
                  active:
                      startsWithPath(
                          currentPath,
                          `${base}/import-center`
                      ) ||
                      startsWithPath(
                          currentPath,
                          `${base}/import`
                      ),
              },
              {
                  href: `${base}/sync-jobs`,
                  label: "Sync Jobs",
                  feature: "sync_jobs",
                  active: startsWithPath(
                      currentPath,
                      `${base}/sync-jobs`
                  ),
              },
              {
                  href: `${base}/adapter-registry`,
                  label: "Adapter Registry",
                  feature: "adapter_registry",
                  active: startsWithPath(
                      currentPath,
                      `${base}/adapter-registry`
                  ),
              },
          ]
          : [];

  const registryLinks = resolvedWorkspaceId
    ? [
        {
          href: `${base}/ledger`,
          label: "Trade Ledger",
          active: startsWithPath(currentPath, `${base}/ledger`),
          feature: "ledger"
        },
        {
          href: `${base}/evidence-records`,
          label: "Evidence Records",
          active: startsWithPath(currentPath, `${base}/evidence-records`),
          feature: "evidence_records"
        },
        {
          href: `${base}/import-batches`,
          label: "Import Batches",
          active: startsWithPath(currentPath, `${base}/import-batches`),
          feature: "import_batches"
        },
        {
          href: `${base}/audit-timeline`,
          label: "Audit Timeline",
          active: startsWithPath(currentPath, `${base}/audit-timeline`),
          feature: "audit_timeline"
        },
        {
          href: `${base}/integrity-registry`,
          label: "Integrity Registry",
          active: startsWithPath(currentPath, `${base}/integrity-registry`),
          feature: "integrity_registry"
        },
      ]
    : [];

  const claimLinks = resolvedWorkspaceId
    ? [
        {
          href: "/schema",
          label: "Claim Builder",
          active: currentPath === "/schema",
          feature: "claim_builder",
        },

        {
          href: `${base}/claims`,
          label: "Claim Library",
          active: startsWithPath(currentPath, `${base}/claims`),
          feature: "claims",
        },

        {
          href: `${base}/evidence`,
          label: "Evidence Review",
          active: startsWithPath(currentPath, `${base}/evidence`),
          feature: "claim_review",
        },

        {
          href: `${base}/schema`,
          label: "Schema Registry",
          active: startsWithPath(currentPath, `${base}/schema`),
          feature: "schema_registry",
        },

        {
          href: `${base}/claim-templates`,
          label: "Templates",
          active: startsWithPath(currentPath, `${base}/claim-templates`),
          feature: "templates",
        },
      ]
    : [];

  const trustLinks = resolvedWorkspaceId
    ? [
        {
          href: `${base}/trust-scores`,
          label: "Trust Scores",
          active: startsWithPath(currentPath, `${base}/trust-scores`),
          feature: "trust_scores",
        },
        {
          href: `${base}/leaderboard`,
          label: "Leaderboards",
          active: startsWithPath(currentPath, `${base}/leaderboard`),
          feature: "leaderboard",
        },
        {
          href: `${base}/verification-analytics`,
          label: "Verification Analytics",
          active: startsWithPath(currentPath, `${base}/verification-analytics`),
          feature: "verification_analytics",
        },
        {
          href: `${base}/integrity-analytics`,
          label: "Integrity Analytics",
          active: startsWithPath(currentPath, `${base}/integrity-analytics`),
          feature: "integrity_analytics",
        },
        {
          href: `${base}/evidence-analytics`,
          label: "Evidence Analytics",
          active: startsWithPath(
            currentPath,
            `${base}/evidence-analytics`
          ),
          feature: "evidence_analytics",
        },
        {
          href: `${base}/risk-analytics`,
          label: "Risk Analytics",
          active: startsWithPath(currentPath, `${base}/risk-analytics`),
          feature: "risk_analytics",
        },
        {
          href: `${base}/due-diligence`,
          label: "Due Diligence Reports",
          active: startsWithPath(currentPath, `${base}/due-diligence`),
          feature: "allocator_reports",
        },
        {
          href: `${base}/report-center`,
          label: "Report Center",
          active:
            startsWithPath(
              currentPath,
              `${base}/report-center`
            ),
          feature: "report_center",
        },
      ]
    : [];

    const visibleTrustLinks = trustLinks;

  const investigationLinks = resolvedWorkspaceId
    ? [

        {
            href: `${base}/investigation-overview`,
            label: "Overview",
            active: startsWithPath(
                currentPath,
                `${base}/investigation-overview`
            ),
            feature: "investigations",
        },

        {
            href: `${base}/investigation-timeline`,
            label: "Timeline",
            active: startsWithPath(
                currentPath,
                `${base}/investigation-timeline`
            ),
            feature: "investigations",
        },

        {
            href: `${base}/investigation-evidence`,
            label: "Evidence",
            active: startsWithPath(
                currentPath,
                `${base}/investigation-evidence`
            ),
            feature: "investigations",
        },

        {
            href: `${base}/investigation-domains`,
            label: "Domains",
            active: startsWithPath(
                currentPath,
                `${base}/investigation-domains`
            ),
            feature: "investigations",
        },

        {
            href: `${base}/investigation-findings`,
            label: "Findings",
            active: startsWithPath(
                currentPath,
                `${base}/investigation-findings`
            ),
            feature: "investigations",
        },

        {
            href: `${base}/investigation-reports`,
            label: "Reports",
            active: startsWithPath(
                currentPath,
                `${base}/investigation-reports`
            ),
            feature: "investigations",
        },

    ]
    : [];

  const publicLinks = resolvedWorkspaceId
    ? [
        {
          href: `${base}/public-records`,
          label: "Public Records",
          active: startsWithPath(currentPath, `${base}/public-records`),
          feature: "public_records",
        },

        {
          href: `${base}/verification-routes`,
          label: "Verification Routes",
          active:
            startsWithPath(
              currentPath,
              `${base}/verification-routes`
            ) ||
            startsWithPath(
              currentPath,
              "/verify"
            ),
          feature: "verification_routes",
        },

        {
          href: `${base}/trust-directory`,
          label: "Trust Directory",
          active: startsWithPath(currentPath, `${base}/trust-directory`),
          feature: "trust_directory",
        },

        {
          href: `${base}/verification-network`,
          label: "Verification Network",
          active: startsWithPath(
            currentPath,
            `${base}/verification-network`
          ),
          feature: "verification_network",
        },

        {
          href: `${base}/external-reviews`,
          label: "External Reviews",
          active: startsWithPath(
            currentPath,
            `${base}/external-reviews`
          ),
          feature: "external_reviews",
        },

        {
          href: `${base}/evidence-graph`,
          label: "Evidence Graph",
          active: startsWithPath(
            currentPath,
            `${base}/evidence-graph`
          ),
          feature: "evidence_graph",
        },

        {
          href: `/profile/${resolvedWorkspaceId}`,
          label: "Public Profiles",
          active:
            startsWithPath(
              currentPath,
              "/profile"
            ) ||
            startsWithPath(
              currentPath,
              `${base}/public-profiles`
            ),
          feature: "public_profiles",
        },
      ]
    : [];

  const adminLinks = resolvedWorkspaceId
    ? [
        {
          href: `${base}/members`,
          label: "Members",
          active: startsWithPath(currentPath, `${base}/members`),
          feature: "members",
        },
        {
          href: `${base}/roles`,
          label: "Roles",
          active: startsWithPath(currentPath, `${base}/roles`),
          feature: "roles",
        },
        {
          href: `${base}/billing`,
          label: "Billing",
          active: startsWithPath(currentPath, `${base}/billing`),
          feature: "billing",
        },
        {
          href: `${base}/settings`,
          label: "Settings",
          active: startsWithPath(currentPath, `${base}/settings`),
          feature: "settings",
        },
      ]
    : [];

  const contextualLinks =
    activeDomain === "dashboard"
        ? dashboardLinks
        : activeDomain === "intake"
            ? intakeLinks
            : activeDomain === "registry"
                ? registryLinks
                : activeDomain === "claims"
                    ? claimLinks
                    : activeDomain === "trust"
                        ? visibleTrustLinks
                        : activeDomain === "investigation"
                            ? investigationLinks
                            : activeDomain === "public"
                                ? publicLinks
                                : adminLinks;

  function renderTopButton(

      pages: string[],

      href: string,

      label: string,

      active: boolean,

  ) {

      const enabled =
          domainEnabled(
              ...pages,
          );

      const activeClass =
          active
              ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
              : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium";

      if (enabled) {

          return (

              <Link
                  href={href}
                  className={activeClass}
              >
                  {label}
              </Link>

          );

      }

      return (

          <button
              type="button"
              onClick={() =>
                  setUpgradeFeature(
                      label,
                  )
              }
              className={disabledNavClass()}
          >

              <span className="flex items-center gap-2">

                  <Lock className="h-4 w-4" />

                  {label}

              </span>

          </button>

      );

  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-4">
            <Link href={homeHref} className="text-lg font-bold text-slate-900">
              Trading Truth Layer
            </Link>

            <div className="flex flex-wrap items-center gap-2">
              <Link href={homeHref} className={utilityNavClass(homeActive)}>
                Home
              </Link>
              <Link href={howItWorksHref} className={utilityNavClass(howItWorksActive)}>
                How It Works
              </Link>
            </div>

            <WorkspaceSwitcher />

            <div className="hidden rounded-lg border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600 md:block">
              {publicTrustActive
                ? "Public Trust Layer"
                : resolvedWorkspaceId
                  ? `Workspace #${resolvedWorkspaceId}`
                  : "Workspace"}
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
            <div className="text-sm">
              <div className="flex items-center gap-2">
                <div className="font-medium text-slate-900">{user?.name || "User"}</div>

                {!loading && workspaceRole ? (
                  <span className="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
                    {workspaceRole}
                  </span>
                ) : null}

                {resolvedWorkspaceId ? (
                  <span className="text-[10px] text-slate-400">
                    workspace:{resolvedWorkspaceId}
                  </span>
                ) : null}
              </div>

              <div className="flex items-center gap-2 text-xs text-slate-500">

                <span>
                  {user?.email || "—"}
                </span>

                {user?.email_verified ? (
                  <span
                    className="
                    rounded-full
                    bg-green-100
                    px-2
                    py-0.5
                    text-[10px]
                    font-semibold
                    text-green-700
                    "
                  >
                    VERIFIED
                  </span>
                ) : (
                  <span
                    className="
                    rounded-full
                    bg-amber-100
                    px-2
                    py-0.5
                    text-[10px]
                    font-semibold
                    text-amber-700
                    "
                  >
                    UNVERIFIED
                  </span>
                )}

              </div>
            </div>

            <button
              type="button"
              onClick={() => logout()}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="mt-3 text-[10px] text-slate-400">
          {publicTrustActive
            ? "Mode: Public Trust Surface"
            : "Mode: Internal Governance Surface"}
        </div>

        <div className="mt-2 flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            <span>Public Trust Layer</span>
            <div className="h-px w-6 bg-slate-200" />
            <span>Workspace Operations</span>
          </div>

          <div className="flex flex-wrap gap-2">

            {
            renderTopButton(
                [
                    "dashboard",
                ],
                dashboardHref,
                "Dashboard",
                activeDomain==="dashboard",
            )
            }

            {
            renderTopButton(
                [
                    "broker_connections",
                    "import_center",
                    "sync_jobs",
                    "adapter_registry",
                ],
                importHref,
                "Evidence Intake",
                activeDomain==="intake",
            )
            }

            {
            renderTopButton(
                [
                    "ledger",
                    "evidence_records",
                    "import_batches",
                    "audit_timeline",
                    "integrity_registry",
                ],
                ledgerHref,
                "Evidence Registry",
                activeDomain==="registry",
            )
            }

            {
            renderTopButton(
                [
                    "claims",
                    "claim_builder",
                    "claim_review",
                    "schema_registry",
                    "templates",
                ],
                claimsHref,
                "Claim Operations",
                activeDomain==="claims",
            )
            }

            {
            renderTopButton(
                [
                    "trust_scores",
                    "leaderboard",
                    "verification_analytics",
                    "integrity_analytics",
                    "evidence_analytics",
                    "risk_analytics",
                    "allocator_reports",
                    "report_center",
                ],
                leaderboardHref,
                "Trust Intelligence",
                activeDomain==="trust",
            )
            }

            {
            renderTopButton(
                [
                    "investigations",
                ],
                `${base}/investigation-overview`,
                "Investigation Center",
                activeDomain === "investigation",
            )
            }

            {
            renderTopButton(
                [
                    "public_records",
                    "verification_routes",
                    "trust_directory",
                    "verification_network",
                    "external_reviews",
                    "evidence_graph",
                    "public_profiles",
                ],
                publicClaimsHref,
                "Public Trust Layer",
                activeDomain==="public",
            )
            }

            {
            renderTopButton(
                [
                    "members",
                    "roles",
                    "billing",
                    "settings",
                ],
                membersHref,
                "Administration",
                activeDomain==="admin",
            )
            }

          </div>

          <div className="mt-3 border-t border-slate-200 pt-3"></div>

          <nav className="flex flex-wrap gap-2">

              {contextualLinks.map(
                  (
                      item: any,
                      index: number,
                  ) => {

                      const enabled =
                          !item.feature ||
                          pageEnabled(
                              item.feature
                          );

                      if (enabled) {

                          return (

                              <Link
                                  key={index}
                                  href={item.href}
                                  className={navClass(
                                      item.active
                                  )}
                              >
                                  {item.label}
                              </Link>

                          );

                      }

                      return (

                          <button
                              key={index}
                              type="button"
                              onClick={() =>
                                  setUpgradeFeature(
                                      item.label
                                  )
                              }
                              className={disabledNavClass()}
                          >

                              <span className="flex items-center gap-2">

                                  <Lock
                                      className="h-4 w-4"
                                  />

                                  {item.label}

                              </span>

                          </button>

                      );

                  }
              )}

          </nav>
        </div>

        {publicTrustActive ? (
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-800">
            <span>
              Public trust-layer surface for verification, distribution, and external review.
            </span>

            <div className="flex items-center gap-2">
              <Link
                href={howItWorksHref}
                className="rounded-md border border-blue-300 px-2 py-1 hover:bg-blue-100"
              >
                How It Works
              </Link>
              <Link
                href={leaderboardHref}
                className="rounded-md border border-blue-300 px-2 py-1 hover:bg-blue-100"
              >
                Leaderboard
              </Link>
              <Link
                href={publicClaimsHref}
                className="rounded-md border border-blue-300 px-2 py-1 hover:bg-blue-100"
              >
                Public Records
              </Link>
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
}