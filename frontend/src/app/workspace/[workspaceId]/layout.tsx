"use client";

import { ReactNode, useEffect, useMemo } from "react";
import { useParams, usePathname, useRouter } from "next/navigation";
import { useAuth } from "../../../components/AuthProvider";

export default function WorkspaceRouteLayout({
  children,
}: {
  children: ReactNode;
}) {
  const params = useParams();
  const pathname = usePathname();
  const router = useRouter();
  const { user, workspaces, loading } = useAuth();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId)
      ? params.workspaceId[0]
      : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  useEffect(() => {
    if (loading) return;

    if (!user) {
      const redirect = pathname || "/";
      router.replace(`/login?redirect=${encodeURIComponent(redirect)}`);
      return;
    }

    if (!workspaceId) {
      router.replace("/");
      return;
    }

    if (!workspaceMembership) {
      const firstWorkspace = workspaces[0];
      if (firstWorkspace) {
        router.replace(`/workspace/${firstWorkspace.workspace_id}/dashboard`);
      } else {
        router.replace("/");
      }
    }
  }, [loading, user, workspaceId, workspaceMembership, workspaces, pathname, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
        <div className="mx-auto max-w-[1200px] rounded-2xl border bg-white p-6 shadow-sm">
          Loading workspace...
        </div>
      </div>
    );
  }

  if (!user || !workspaceId || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 px-6 py-10 text-slate-900">
        <div className="mx-auto max-w-[1200px] rounded-2xl border bg-white p-6 shadow-sm">
          Checking workspace access...
        </div>
      </div>
    );
  }

  return <>{children}</>;
}