"use client";

import { useEffect, useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "./AuthProvider";

const ACTIVE_WORKSPACE_KEY = "ttl_active_workspace_id";

export default function WorkspaceSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { workspaces, loading } = useAuth();

  const currentWorkspaceId = useMemo(() => {
    if (!pathname) return null;

    const match = pathname.match(/^\/workspace\/(\d+)/);
    if (!match) return null;

    const parsed = Number(match[1]);
    return Number.isNaN(parsed) ? null : parsed;
  }, [pathname]);

  const storedWorkspaceId = useMemo(() => {
    if (typeof window === "undefined") return null;
    const raw = window.localStorage.getItem(ACTIVE_WORKSPACE_KEY);
    if (!raw) return null;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [pathname]);

  const currentSuffix = useMemo(() => {
    if (!pathname || currentWorkspaceId === null) return "/dashboard";
    return pathname.replace(/^\/workspace\/\d+/, "") || "/dashboard";
  }, [pathname, currentWorkspaceId]);

  const currentQuery = useMemo(() => {
    const raw = searchParams?.toString();
    return raw ? `?${raw}` : "";
  }, [searchParams]);

  const selectedWorkspaceId = useMemo(() => {
    if (currentWorkspaceId && workspaces.some((w) => w.workspace_id === currentWorkspaceId)) {
      return currentWorkspaceId;
    }

    if (storedWorkspaceId && workspaces.some((w) => w.workspace_id === storedWorkspaceId)) {
      return storedWorkspaceId;
    }

    return workspaces.length > 0 ? workspaces[0].workspace_id : null;
  }, [currentWorkspaceId, storedWorkspaceId, workspaces]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!selectedWorkspaceId) return;
    window.localStorage.setItem(ACTIVE_WORKSPACE_KEY, String(selectedWorkspaceId));
  }, [selectedWorkspaceId]);

  if (loading || workspaces.length === 0 || selectedWorkspaceId === null) {
    return null;
  }

  function handleChange(nextWorkspaceId: string) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(ACTIVE_WORKSPACE_KEY, nextWorkspaceId);
    }
    router.push(`/workspace/${nextWorkspaceId}${currentSuffix}${currentQuery}`);
  }

  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-slate-500">Workspace</label>
      <select
        value={String(selectedWorkspaceId)}
        onChange={(e) => handleChange(e.target.value)}
        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-slate-500"
      >
        {workspaces.map((workspace) => (
          <option key={workspace.workspace_id} value={workspace.workspace_id}>
            {workspace.workspace_name} · {workspace.workspace_role}
          </option>
        ))}
      </select>
    </div>
  );
}