"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";
import { api } from "../lib/api";
import { useAuth } from "./AuthProvider";
import WorkspaceSwitcher from "./WorkspaceSwitcher";

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
  const [latestClaimId, setLatestClaimId] = useState<number | null>(null);
  const { user, logout, getWorkspaceRole, loading, workspaces } = useAuth();

  const resolvedWorkspaceId = useMemo(() => {
    if (typeof workspaceId === "number" && !Number.isNaN(workspaceId)) {
      return workspaceId;
    }

    if (Array.isArray(workspaces) && workspaces.length > 0) {
      return workspaces[0].workspace_id;
    }

    return null;
  }, [workspaceId, workspaces]);

  const currentPath = normalizePath(pathname);
  const publicTrustActive = isPublicTrustPath(currentPath);

  useEffect(() => {
    if (resolvedWorkspaceId == null) {
      setLatestClaimId(null);
      return;
    }

    const workspaceIdForFetch = resolvedWorkspaceId;
    let active = true;

    async function loadLatestWorkspaceClaim() {
      try {
        const rows = await api.getWorkspaceClaims(workspaceIdForFetch);
        if (!active) return;

        const latest =
          Array.isArray(rows) && rows.length > 0
            ? [...rows].sort((a, b) => b.claim_schema_id - a.claim_schema_id)[0]
            : null;

        setLatestClaimId(latest?.claim_schema_id ?? null);
      } catch {
        if (!active) return;
        setLatestClaimId(null);
      }
    }

    void loadLatestWorkspaceClaim();

    return () => {
      active = false;
    };
  }, [resolvedWorkspaceId]);

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

  const claimBuilderHref = resolvedWorkspaceId ? `${base}/schema` : "/claims";
  const dashboardHref = resolvedWorkspaceId ? `${base}/dashboard` : "/";
  const importHref = resolvedWorkspaceId ? `${base}/import` : "/";
  const ledgerHref = resolvedWorkspaceId ? `${base}/ledger` : "/";
  const workspaceSchemaHref = resolvedWorkspaceId ? `${base}/schema` : "/";
  const claimsHref = resolvedWorkspaceId ? `${base}/claims` : "/";
  const latestClaimHref =
    resolvedWorkspaceId && latestClaimId ? `${base}/claim/${latestClaimId}` : null;
  const evidenceHref =
    resolvedWorkspaceId && latestClaimId
      ? `${base}/evidence?claimId=${latestClaimId}`
      : resolvedWorkspaceId
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
    ? startsWithPath(currentPath, claimBuilderHref)
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
  const activeDomain =
    dashboardActive
      ? "dashboard"
      : importActive
        ? "intake"
        : ledgerActive || evidenceActive || latestClaimActive
          ? "registry"
          : claimsActive || workspaceSchemaActive || schemaBuilderActive
            ? "claims"
            : leaderboardActive
              ? "trust"
              : publicClaimsActive || publicProfileActive
                ? "public"
                : membersActive || settingsActive
                  ? "admin"
                  : "dashboard";

  function navClass(active: boolean) {
    return active
      ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm"
      : "rounded-xl px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100";
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
            href: importHref,
            label: "Import Center",
            active: importActive,
          },
        ]
      : [];

  const registryLinks = resolvedWorkspaceId
    ? [
        {
          href: ledgerHref,
          label: "Trade Ledger",
          active: ledgerActive,
        },

        ...(latestClaimHref
          ? [
              {
                href: latestClaimHref,
                label: "Latest Record",
                active: latestClaimActive,
              },
            ]
          : []),

        {
          href: evidenceHref,
          label: "Evidence Review",
          active: evidenceActive,
        },

        {
          href: "#",
          label: "Evidence Records",
          active: false,
          disabled: true,
        },

        {
          href: "#",
          label: "Import Batches",
          active: false,
          disabled: true,
        },

        {
          href: "#",
          label: "Integrity Registry",
          active: false,
          disabled: true,
        },

        {
          href: "#",
          label: "Audit Timeline",
          active: false,
          disabled: true,
        },
      ]
    : [];

  const claimLinks = resolvedWorkspaceId
    ? [
        {
          href: claimBuilderHref,
          label: "Create Claim",
          active: schemaBuilderActive,
        },
        {
          href: claimsHref,
          label: "Claim Library",
          active: claimsActive,
        },
        ...(canSeeSchema
          ? [
              {
                href: workspaceSchemaHref,
                label: "Schema Registry",
                active: workspaceSchemaActive,
              },
            ]
          : []),
      ]
    : [];

  const trustLinks = [
    {
      href: leaderboardHref,
      label: "Trust Leaderboard",
      active: leaderboardActive,
    },
  ];

  const publicLinks = [
    {
      href: publicClaimsHref,
      label: "Public Records",
      active: publicClaimsActive,
    },
    {
      href: publicProfileHref,
      label: "Public Profile",
      active: publicProfileActive,
    },
  ];

  const adminLinks = resolvedWorkspaceId
    ? [
        ...(canSeeMembers
          ? [
              {
                href: membersHref,
                label: "Members",
                active: membersActive,
              },
            ]
          : []),
        {
          href: settingsHref,
          label: "Settings & Billing",
          active: settingsActive,
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
              ? trustLinks
              : activeDomain === "public"
                ? publicLinks
                : adminLinks;

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

            <Link
              href={dashboardHref}
              className={
                activeDomain === "dashboard"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Dashboard
            </Link>

            <Link
              href={importHref}
              className={
                activeDomain === "intake"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Evidence Intake
            </Link>

            <Link
              href={ledgerHref}
              className={
                activeDomain === "registry"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Evidence Registry
            </Link>

            <Link
              href={claimsHref}
              className={
                activeDomain === "claims"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Claim Operations
            </Link>

            <Link
              href={leaderboardHref}
              className={
                activeDomain === "trust"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Trust Intelligence
            </Link>

            <Link
              href={publicClaimsHref}
              className={
                activeDomain === "public"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Public Trust Layer
            </Link>

            <Link
              href={membersHref}
              className={
                activeDomain === "admin"
                  ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  : "rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium"
              }
            >
              Administration
            </Link>

          </div>

          <div className="mt-3 border-t border-slate-200 pt-3"></div>

          <nav className="flex flex-wrap items-center gap-2">
            {contextualLinks.map((item) =>
              (item as any).disabled ? (
                <span
                  key={item.label}
                  className="
                    rounded-xl
                    border
                    border-dashed
                    border-slate-300
                    bg-slate-50
                    px-4
                    py-2
                    text-sm
                    text-slate-400
                  "
                >
                  {item.label}
                </span>
              ) : (
                <Link
                  key={item.href}
                  href={item.href}
                  className={navClass(item.active)}
                >
                  {item.label}
                </Link>
              )
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