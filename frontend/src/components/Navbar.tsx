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
    currentPath === "/schema" ||
    startsWithPath(currentPath, "/claim") ||
    startsWithPath(currentPath, "/verify") ||
    startsWithPath(currentPath, "/profile")
  );
}

export default function Navbar({ workspaceId = 1 }: Props) {
  const pathname = usePathname();
  const [latestClaimId, setLatestClaimId] = useState<number | null>(null);
  const { user, logout, getWorkspaceRole, loading } = useAuth();

  useEffect(() => {
    let active = true;

    async function loadLatestWorkspaceClaim() {
      try {
        const rows = await api.getWorkspaceClaims(workspaceId);
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
  }, [workspaceId]);

  const workspaceRole = useMemo(() => {
    return getWorkspaceRole(workspaceId);
  }, [getWorkspaceRole, workspaceId]);

  const canSeeImport = workspaceRole === "owner" || workspaceRole === "operator";
  const canSeeSchema = workspaceRole === "owner" || workspaceRole === "operator";
  const canSeeMembers =
    workspaceRole === "owner" ||
    workspaceRole === "operator" ||
    workspaceRole === "auditor" ||
    workspaceRole === "member";

  const currentPath = normalizePath(pathname);
  const base = `/workspace/${workspaceId}`;

  const publicClaimsHref = "/claims";
  const leaderboardHref = "/leaderboard";
  const claimBuilderHref = "/schema";
  const publicProfileHref = `/profile/${workspaceId}`;

  const dashboardHref = `${base}/dashboard`;
  const importHref = `${base}/import`;
  const ledgerHref = `${base}/ledger`;
  const workspaceSchemaHref = `${base}/schema`;
  const claimsHref = `${base}/claims`;
  const latestClaimHref = latestClaimId ? `${base}/claim/${latestClaimId}` : null;
  const evidenceHref = latestClaimId
    ? `${base}/evidence?claimId=${latestClaimId}`
    : `${base}/evidence`;
  const membersHref = `${base}/members`;
  const settingsHref = `${base}/settings`;

  const publicClaimsActive =
    currentPath === "/claims" || startsWithPath(currentPath, "/claim");
  const leaderboardActive = currentPath === "/leaderboard";
  const schemaBuilderActive = currentPath === "/schema";
  const publicProfileActive = startsWithPath(currentPath, "/profile");
  const publicTrustActive = isPublicTrustPath(currentPath);

  const dashboardActive = startsWithPath(currentPath, dashboardHref);
  const importActive = startsWithPath(currentPath, importHref);
  const ledgerActive = startsWithPath(currentPath, ledgerHref);
  const workspaceSchemaActive = startsWithPath(currentPath, workspaceSchemaHref);
  const claimsActive =
    startsWithPath(currentPath, claimsHref) ||
    startsWithPath(currentPath, `${base}/claim`);
  const latestClaimActive = latestClaimHref
    ? startsWithPath(currentPath, latestClaimHref)
    : false;
  const evidenceActive =
    startsWithPath(currentPath, `${base}/evidence`) ||
    (startsWithPath(currentPath, `${base}/claim`) && currentPath.endsWith("/evidence"));
  const membersActive = startsWithPath(currentPath, membersHref);
  const settingsActive = startsWithPath(currentPath, settingsHref);

  function navClass(active: boolean) {
    return active
      ? "rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm"
      : "rounded-xl px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100";
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-4">
            <Link href="/" className="text-lg font-bold text-slate-900">
              Trading Truth Layer
            </Link>

            <WorkspaceSwitcher />

            <div className="hidden rounded-lg border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600 md:block">
              {publicTrustActive ? "Public Trust Layer" : `Workspace #${workspaceId}`}
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

                <span className="text-[10px] text-slate-400">workspace:{workspaceId}</span>
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

            <Link href={claimBuilderHref} className={navClass(schemaBuilderActive)}>
              Claim Builder
            </Link>

            <div className="mx-1 hidden h-6 w-px bg-slate-200 md:block" />

            {latestClaimHref ? (
              <Link href={latestClaimHref} className={navClass(latestClaimActive)}>
                Latest Claim
              </Link>
            ) : null}

            <Link href={dashboardHref} className={navClass(dashboardActive)}>
              Dashboard
            </Link>

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
              Internal Claims
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
          </nav>
        </div>

        {publicTrustActive ? (
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-800">
            <span>
              Public trust-layer surface (verification, distribution, external review).
            </span>

            <div className="flex items-center gap-2">
              <Link
                href="/leaderboard"
                className="rounded-md border border-blue-300 px-2 py-1 hover:bg-blue-100"
              >
                Leaderboard
              </Link>
              <Link
                href="/claims"
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