"use client";

import { useState } from "react";
import InviteWorkspaceMemberForm from "./InviteWorkspaceMemberForm";
import WorkspaceInvitesPanel from "./WorkspaceInvitesPanel";
import WorkspaceMembersPanel from "./WorkspaceMembersPanel";

type Props = {
  workspaceId: number;
};

export default function DashboardWorkspacePanels({ workspaceId }: Props) {
  const [refreshKey, setRefreshKey] = useState(0);

  function refresh() {
    setRefreshKey((k) => k + 1);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <InviteWorkspaceMemberForm workspaceId={workspaceId} onInviteCreated={refresh} />
      <WorkspaceMembersPanel workspaceId={workspaceId} refreshKey={refreshKey} />
      <WorkspaceInvitesPanel workspaceId={workspaceId} refreshKey={refreshKey} />
    </div>
  );
}