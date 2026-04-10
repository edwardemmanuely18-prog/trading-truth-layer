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
    startsWithPath(currentPath, "/profile")
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
  const publicClaimsHref = resolvedWorkspaceId
    ? `/workspace/${resolvedWorkspaceId}/claims`
    : "/claims";

  const leaderboardHref = resolvedWorkspaceId
    ? `/workspace/${resolvedWorkspaceId}/leaderboard`
    : "/leaderboard";
  const publicProfileHref = resolvedWorkspaceId ? `/profile/${resolvedWorkspaceId}` : "/profile";

  const base = resolvedWorkspaceId ? `/workspace/${resolvedWorkspaceId}` : "";
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
  const publicClaimsActive =
    currentPath === "/claims" || startsWithPath(currentPath, "/claim");
  const leaderboardActive = currentPath === "/leaderboard";
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

              <div className="text-xs text-slate-500">{user?.email || "—"}</div>
            </div>

            <button
              type="button"
              onClick={logout}
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

          <nav className="flex flex-wrap items-center gap-2">
            <Link href={publicClaimsHref} className={navClass(publicClaimsActive)}>
              Public Records
            </Link>

            <Link href={leaderboardHref} className={navClass(leaderboardActive)}>
              Trust Leaderboard
            </Link>

            <Link href={publicProfileHref} className={navClass(publicProfileActive)}>
              Profile
            </Link>

            {resolvedWorkspaceId ? (
              <Link href={claimBuilderHref} className={navClass(schemaBuilderActive)}>
                Claim Builder
              </Link>
            ) : null}

            <div className="mx-1 hidden h-6 w-px bg-slate-200 md:block" />

            {resolvedWorkspaceId ? (
              <>
                <Link href={dashboardHref} className={navClass(dashboardActive)}>
                  Dashboard
                </Link>

                {latestClaimHref ? (
                  <Link href={latestClaimHref} className={navClass(latestClaimActive)}>
                    Latest Record
                  </Link>
                ) : null}

                {canSeeImport ? (
                  <Link href={importHref} className={navClass(importActive)}>
                    Import
                  </Link>
                ) : null}

                <Link href={ledgerHref} className={navClass(ledgerActive)}>
                  Ledger
                </Link>

                {canSeeSchema ? (
                  <Link href={workspaceSchemaHref} className={navClass(workspaceSchemaActive)}>
                    Schema Registry
                  </Link>
                ) : null}

                <Link href={claimsHref} className={navClass(claimsActive)}>
                  Claim Library
                </Link>

                <Link href={evidenceHref} className={navClass(evidenceActive)}>
                  Evidence Review
                </Link>

                {canSeeMembers ? (
                  <Link href={membersHref} className={navClass(membersActive)}>
                    Members
                  </Link>
                ) : null}

                <Link href={settingsHref} className={navClass(settingsActive)}>
                  Settings & Billing
                </Link>
              </>
            ) : null}
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