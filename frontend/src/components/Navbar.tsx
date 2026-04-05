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

  const dashboardHref = `${base}/dashboard`;
  const importHref = `${base}/import`;
  const ledgerHref = `${base}/ledger`;
  const workspaceSchemaHref = `${base}/schema`;
  const claimsHref = `${base}/claims`;
  const evidenceHref = latestClaimId
    ? `${base}/evidence?claimId=${latestClaimId}`
    : `${base}/evidence`;
  const membersHref = `${base}/members`;
  const settingsHref = `${base}/settings`;

  const publicClaimsActive = currentPath === "/claims";
  const leaderboardActive = currentPath === "/leaderboard";
  const schemaBuilderActive = currentPath === "/schema";
  const dashboardActive = startsWithPath(currentPath, dashboardHref);
  const importActive = startsWithPath(currentPath, importHref);
  const ledgerActive = startsWithPath(currentPath, ledgerHref);
  const workspaceSchemaActive = startsWithPath(currentPath, workspaceSchemaHref);
  const claimsActive =
    startsWithPath(currentPath, claimsHref) ||
    startsWithPath(currentPath, `${base}/claim`);
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
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <div className="flex flex-wrap items-center gap-4">
          <Link href="/" className="text-lg font-bold text-slate-900">
            Trading Truth Layer
          </Link>

          <WorkspaceSwitcher />
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
            <span>Public Trust Surfaces</span>
            <div className="h-px w-6 bg-slate-200" />
            <span>Workspace Operations</span>
          </div>

          <nav className="flex flex-wrap items-center gap-2">
          <Link href="/claims" className={navClass(publicClaimsActive)}>
            Public Claims
          </Link>

          <Link href="/leaderboard" className={navClass(leaderboardActive)}>
            Leaderboard
          </Link>

          <Link href="/schema" className={navClass(schemaBuilderActive)}>
            Claim Builder
          </Link>

          <div className="mx-1 hidden h-6 w-px bg-slate-200 md:block" />

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
            Claims
          </Link>

          <Link href={evidenceHref} className={navClass(evidenceActive)}>
            Evidence
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

        <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
          <div className="text-sm">
            <div className="flex items-center gap-2">
              <div className="font-medium text-slate-900">{user?.name || "User"}</div>
              {!loading && workspaceRole ? (
                <span className="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-slate-600">
                  {workspaceRole}
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
    </header>
  );
}