"use client";

import { useState } from "react";
import { useAuth } from "./AuthProvider";

import InviteWorkspaceMemberForm from "./InviteWorkspaceMemberForm";
import WorkspaceInvitesPanel from "./WorkspaceInvitesPanel";
import WorkspaceMembersPanel from "./WorkspaceMembersPanel";

type Props = {
  workspaceId: number;
};

export default function DashboardWorkspacePanels({ workspaceId }: Props) {
  const { getWorkspaceRole } = useAuth();

  const [refreshKey, setRefreshKey] = useState(0);

  const workspaceRole = getWorkspaceRole(workspaceId);

  const canManageMembers =
    workspaceRole === "owner" || workspaceRole === "operator";

  function refresh() {
    setRefreshKey((k) => k + 1);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {canManageMembers ? (
        <InviteWorkspaceMemberForm
          workspaceId={workspaceId}
          onInviteCreated={refresh}
        />
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Workspace Invites</h2>

          <p className="mt-2 text-sm text-slate-600">
            Only workspace owners and operators can invite new members.
          </p>

          <div className="mt-3 text-sm text-slate-500">
            Your role: <span className="font-medium">{workspaceRole || "unknown"}</span>
          </div>
        </div>
      )}

      <WorkspaceMembersPanel
        workspaceId={workspaceId}
        refreshKey={refreshKey}
      />

      {canManageMembers ? (
        <WorkspaceInvitesPanel
          workspaceId={workspaceId}
          refreshKey={refreshKey}
        />
      ) : (
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Pending Invites</h2>

          <p className="mt-2 text-sm text-slate-600">
            Invite records are visible only to workspace owners and operators.
          </p>

          <div className="mt-3 text-sm text-slate-500">
            Your role: <span className="font-medium">{workspaceRole || "unknown"}</span>
          </div>
        </div>
      )}
    </div>
  );
}