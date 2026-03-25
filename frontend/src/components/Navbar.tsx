"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import { api } from "../lib/api";
import { useAuth } from "./AuthProvider";
import WorkspaceSwitcher from "./WorkspaceSwitcher";

type Props = {
  workspaceId?: number;
};

function normalizePath(value?: string | null) {
  return String(value || "").replace(/\/+$/, "");
}

export default function Navbar({ workspaceId = 1 }: Props) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [latestClaimId, setLatestClaimId] = useState<number | null>(null);
  const { user, logout, getWorkspaceRole, loading } = useAuth();

  const base = `/workspace/${workspaceId}`;
  const currentPath = normalizePath(pathname);
  const isSettingsPage = currentPath === normalizePath(`${base}/settings`);

  useEffect(() => {
    let active = true;

    if (isSettingsPage) {
      setLatestClaimId(null);
      return () => {
        active = false;
      };
    }

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
  }, [workspaceId, isSettingsPage]);

  const claimsHref = `${base}/claims`;
  const evidenceHref = latestClaimId
    ? `${base}/evidence?claimId=${latestClaimId}`
    : `${base}/evidence`;

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

  const currentClaimIdFromEvidenceQuery = searchParams.get("claimId");

  function isDashboardActive() {
    return currentPath === normalizePath(`${base}/dashboard`);
  }

  function isImportActive() {
    return currentPath === normalizePath(`${base}/import`);
  }

  function isLedgerActive() {
    return currentPath === normalizePath(`${base}/ledger`);
  }

  function isSchemaActive() {
    return currentPath === normalizePath(`${base}/schema`);
  }

  function isClaimsActive() {
    if (currentPath === normalizePath(`${base}/claims`)) return true;
    if (currentPath.startsWith(normalizePath(`${base}/claim/`))) return true;
    return false;
  }

  function isEvidenceActive() {
    if (currentPath === normalizePath(`${base}/evidence`)) return true;

    if (
      currentPath.startsWith(normalizePath(`${base}/claim/`)) &&
      currentPath.endsWith("/evidence")
    ) {
      return true;
    }

    if (
      currentPath.startsWith(normalizePath(`${base}/claim/`)) &&
      currentClaimIdFromEvidenceQuery
    ) {
      return false;
    }

    return false;
  }

  function isMembersActive() {
    return currentPath === normalizePath(`${base}/members`);
  }

  function isSettingsActive() {
    return currentPath === normalizePath(`${base}/settings`);
  }

  function navClass(active: boolean) {
    return active
      ? "rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white transition"
      : "rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100";
  }

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
        <div className="flex items-center gap-4">
          <Link href={`${base}/dashboard`} className="text-lg font-bold text-slate-900">
            Trading Truth Layer
          </Link>

          <WorkspaceSwitcher />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <nav className="flex flex-wrap gap-2">
            <Link href={`${base}/dashboard`} className={navClass(isDashboardActive())}>
              Dashboard
            </Link>

            {canSeeImport && (
              <Link href={`${base}/import`} className={navClass(isImportActive())}>
                Import
              </Link>
            )}

            <Link href={`${base}/ledger`} className={navClass(isLedgerActive())}>
              Ledger
            </Link>

            {canSeeSchema && (
              <Link href={`${base}/schema`} className={navClass(isSchemaActive())}>
                Schema Builder
              </Link>
            )}

            <Link href={claimsHref} className={navClass(isClaimsActive())}>
              Claims
            </Link>

            <Link href={evidenceHref} className={navClass(isEvidenceActive())}>
              Evidence
            </Link>

            {canSeeMembers && (
              <Link href={`${base}/members`} className={navClass(isMembersActive())}>
                Members
              </Link>
            )}

            <Link href={`${base}/settings`} className={navClass(isSettingsActive())}>
              Settings & Billing
            </Link>
          </nav>

          <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
            <div className="text-sm">
              <div className="font-medium text-slate-900">{user?.name || "Unknown User"}</div>
              <div className="text-xs text-slate-500">
                {user?.email || "No email"}
                {!loading && workspaceRole ? ` · ${workspaceRole}` : ""}
              </div>
            </div>

            <button
              onClick={logout}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-white"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}