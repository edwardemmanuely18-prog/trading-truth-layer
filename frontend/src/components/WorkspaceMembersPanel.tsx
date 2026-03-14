"use client";

import { useEffect, useState } from "react";
import { api, type WorkspaceMember } from "../lib/api";

type Props = {
  workspaceId: number;
  refreshKey?: number;
};

export default function WorkspaceMembersPanel({ workspaceId, refreshKey = 0 }: Props) {
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getWorkspaceMembers(workspaceId);
        setMembers(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load members");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [workspaceId, refreshKey]);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">Workspace Members</h2>

      {loading ? (
        <div className="mt-4 text-sm text-slate-500">Loading members...</div>
      ) : error ? (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : members.length === 0 ? (
        <div className="mt-4 text-sm text-slate-500">No members found.</div>
      ) : (
        <div className="mt-4 space-y-3">
          {members.map((member) => (
            <div
              key={`${member.workspace_id}-${member.user_id}`}
              className="rounded-xl border border-slate-200 bg-slate-50 p-4"
            >
              <div className="font-semibold text-slate-900">{member.name}</div>
              <div className="mt-1 text-sm text-slate-600">{member.email}</div>
              <div className="mt-2 text-xs text-slate-500">
                Global role: {member.global_role} · Workspace role: {member.workspace_role}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}