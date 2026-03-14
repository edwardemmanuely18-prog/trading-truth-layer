"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api, type WorkspaceInvite } from "../lib/api";

type Props = {
  workspaceId: number;
  refreshKey?: number;
};

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function WorkspaceInvitesPanel({ workspaceId, refreshKey = 0 }: Props) {
  const [invites, setInvites] = useState<WorkspaceInvite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedInviteId, setCopiedInviteId] = useState<number | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getWorkspaceInvites(workspaceId);
        setInvites(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load invites");
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [workspaceId, refreshKey]);

  const origin =
    typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";

  async function handleCopy(invite: WorkspaceInvite) {
    const inviteUrl = `${origin}/invite/${invite.token}`;

    try {
      await navigator.clipboard.writeText(inviteUrl);
      setCopiedInviteId(invite.id);
      window.setTimeout(() => setCopiedInviteId(null), 2000);
    } catch {
      setError("Failed to copy invite link");
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">Workspace Invites</h2>

      {loading ? (
        <div className="mt-4 text-sm text-slate-500">Loading invites...</div>
      ) : error ? (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : invites.length === 0 ? (
        <div className="mt-4 text-sm text-slate-500">No invites created yet.</div>
      ) : (
        <div className="mt-4 space-y-3">
          {invites.map((invite) => {
            const invitePath = `/invite/${invite.token}`;
            const inviteUrl = `${origin}${invitePath}`;
            const isAccepted = invite.status === "accepted";

            return (
              <div
                key={invite.id}
                className="rounded-xl border border-slate-200 bg-slate-50 p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="font-semibold text-slate-900">{invite.email}</div>
                  <div className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-700">
                    {invite.status}
                  </div>
                </div>

                <div className="mt-2 text-sm text-slate-600">Role: {invite.role}</div>

                <div className="mt-3">
                  <div className="mb-1 text-xs font-medium text-slate-500">Invite Token</div>
                  <div className="break-all rounded-lg border border-slate-200 bg-white p-3 font-mono text-xs text-slate-700">
                    {invite.token}
                  </div>
                </div>

                <div className="mt-3">
                  <div className="mb-1 text-xs font-medium text-slate-500">Invite Link</div>
                  <div className="break-all rounded-lg border border-slate-200 bg-white p-3 text-xs text-slate-700">
                    {inviteUrl}
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap gap-2">
                  <Link
                    href={invitePath}
                    className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-100"
                  >
                    Open Invite Link
                  </Link>

                  <button
                    type="button"
                    onClick={() => void handleCopy(invite)}
                    className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
                  >
                    {copiedInviteId === invite.id ? "Copied" : "Copy Invite Link"}
                  </button>
                </div>

                <div className="mt-3 text-xs text-slate-500">
                  Created: {formatDateTime(invite.created_at)} · Expires: {formatDateTime(invite.expires_at)}
                  {isAccepted ? ` · Accepted: ${formatDateTime(invite.accepted_at)}` : ""}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}