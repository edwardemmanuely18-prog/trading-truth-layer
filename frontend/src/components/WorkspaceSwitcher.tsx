"use client";

import { useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "./AuthProvider";

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

  const currentSuffix = useMemo(() => {
    if (!pathname || currentWorkspaceId === null) return "/dashboard";
    return pathname.replace(/^\/workspace\/\d+/, "") || "/dashboard";
  }, [pathname, currentWorkspaceId]);

  const currentQuery = useMemo(() => {
    const raw = searchParams?.toString();
    return raw ? `?${raw}` : "";
  }, [searchParams]);

  if (loading || workspaces.length === 0) {
    return null;
  }

  const selectedValue =
    currentWorkspaceId && workspaces.some((w) => w.workspace_id === currentWorkspaceId)
      ? String(currentWorkspaceId)
      : String(workspaces[0].workspace_id);

  function handleChange(nextWorkspaceId: string) {
    router.push(`/workspace/${nextWorkspaceId}${currentSuffix}${currentQuery}`);
  }

  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-slate-500">Workspace</label>
      <select
        value={selectedValue}
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