"use client";

import { useMemo, useState } from "react";
import { api, type WorkspaceInvite } from "../lib/api";

type Props = {
  workspaceId: number;
  rows: WorkspaceInvite[];
  canManage?: boolean;
  onChanged?: () => void | Promise<void>;
};

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function statusBadge(status?: string | null) {
  const normalized = (status || "").toLowerCase();

  const className =
    normalized === "accepted"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "pending"
        ? "border-amber-200 bg-amber-100 text-amber-800"
        : normalized === "expired"
          ? "border-red-200 bg-red-100 text-red-800"
          : normalized === "revoked"
            ? "border-slate-300 bg-slate-100 text-slate-800"
            : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${className}`}>
      {status || "unknown"}
    </span>
  );
}

function dedupeInvites(rows: WorkspaceInvite[]) {
  const seen = new Set<string>();

  return rows.filter((row, index) => {
    const stableKey = `${row.id}-${row.email || ""}-${row.role || ""}-${row.status || ""}-${row.token || ""}`;

    if (!seen.has(stableKey)) {
      seen.add(stableKey);
      return true;
    }

    const fallbackKey = `${stableKey}-${index}`;
    if (!seen.has(fallbackKey)) {
      seen.add(fallbackKey);
      return true;
    }

    return false;
  });
}

export default function WorkspaceInvitesTable({
  workspaceId,
  rows,
  canManage = false,
  onChanged,
}: Props) {
  const safeRows = useMemo(() => dedupeInvites(Array.isArray(rows) ? rows : []), [rows]);
  const [busyInviteId, setBusyInviteId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRevoke(inviteId: number) {
    try {
      setBusyInviteId(inviteId);
      setFeedback(null);
      setError(null);

      await api.revokeWorkspaceInvite(workspaceId, inviteId);

      setFeedback("Invite revoked successfully.");

      if (onChanged) {
        await onChanged();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to revoke invite.");
    } finally {
      setBusyInviteId(null);
    }
  }

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-2xl font-semibold">Workspace Invites</h2>
        <p className="mt-2 text-sm text-slate-600">
          Invite ledger for pending, accepted, expired, and revoked workspace access.
        </p>
      </div>

      {feedback ? (
        <div className="mb-4 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {feedback}
        </div>
      ) : null}

      {error ? (
        <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {safeRows.length === 0 ? (
        <div className="text-sm text-slate-500">
          {canManage ? "No invites found." : "Invite ledger is currently visible to workspace owners only."}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b text-left text-slate-500">
                <th className="px-3 py-3">Invite ID</th>
                <th className="px-3 py-3">Email</th>
                <th className="px-3 py-3">Role</th>
                <th className="px-3 py-3">Status</th>
                <th className="px-3 py-3">Created</th>
                <th className="px-3 py-3">Expires</th>
                <th className="px-3 py-3">Accepted</th>
                <th className="px-3 py-3">Token</th>
                {canManage ? <th className="px-3 py-3">Actions</th> : null}
              </tr>
            </thead>
            <tbody>
              {safeRows.map((row, index) => {
                const canRevoke = canManage && (row.status || "").toLowerCase() === "pending";
                const isBusy = busyInviteId === row.id;

                return (
                  <tr
                    key={`${row.id}-${row.email || "no-email"}-${row.status || "no-status"}-${index}`}
                    className="border-b align-top last:border-0"
                  >
                    <td className="px-3 py-3 font-medium">{row.id}</td>
                    <td className="px-3 py-3">{row.email || "—"}</td>
                    <td className="px-3 py-3">{row.role || "—"}</td>
                    <td className="px-3 py-3">{statusBadge(row.status)}</td>
                    <td className="px-3 py-3">{formatDateTime(row.created_at)}</td>
                    <td className="px-3 py-3">{formatDateTime(row.expires_at)}</td>
                    <td className="px-3 py-3">{formatDateTime(row.accepted_at)}</td>
                    <td className="px-3 py-3">
                      <div className="max-w-[240px] break-all rounded-lg bg-slate-50 p-2 font-mono text-xs text-slate-700">
                        {row.token || "—"}
                      </div>
                    </td>

                    {canManage ? (
                      <td className="px-3 py-3">
                        {canRevoke ? (
                          <button
                            type="button"
                            onClick={() => void handleRevoke(row.id)}
                            disabled={isBusy}
                            className="rounded-lg border border-red-300 px-3 py-2 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            {isBusy ? "Revoking..." : "Revoke"}
                          </button>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                    ) : null}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}