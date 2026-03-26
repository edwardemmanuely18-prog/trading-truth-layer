"use client";

import { useEffect, useMemo, useState } from "react";
import {
  api,
  type WorkspaceMemberRole,
  type WorkspaceUsageSummary,
} from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  workspaceId: number;
  onInviteCreated?: () => void;
};

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

export default function InviteWorkspaceMemberForm({
  workspaceId,
  onInviteCreated,
}: Props) {
  const { getWorkspaceRole } = useAuth();

  const [email, setEmail] = useState("");
  const [role, setRole] = useState<WorkspaceMemberRole>("member");
  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(true);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const workspaceRole = getWorkspaceRole(workspaceId);
  const isOwner = useMemo(() => workspaceRole === "owner", [workspaceRole]);

  const memberUsage = usage?.usage?.members;
  const memberLimitReached =
    (memberUsage?.limit ?? 0) > 0 && (memberUsage?.used ?? 0) >= (memberUsage?.limit ?? 0);

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(workspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setUsageLoading(false);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!isOwner) {
      setError("Only workspace owners can create invites.");
      setSuccessMessage(null);
      return;
    }

    if (memberLimitReached) {
      setError("Member limit reached. Upgrade workspace plan before inviting more users.");
      setSuccessMessage(null);
      return;
    }

    if (!email.trim()) {
      setError("Invite email is required.");
      setSuccessMessage(null);
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const invite = await api.createWorkspaceInvite(workspaceId, {
        email: email.trim().toLowerCase(),
        role,
      });

      setSuccessMessage(`Invite created for ${invite.email}`);
      setEmail("");
      setRole("member");
      onInviteCreated?.();

      try {
        const refreshedUsage = await api.getWorkspaceUsage(workspaceId);
        setUsage(refreshedUsage);
      } catch {
        // preserve existing usage state if refresh fails
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create invite");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">Invite Member</h2>

      <p className="mt-2 text-sm text-slate-600">
        Create a workspace invite for a new member, operator, or auditor.
      </p>

      {usageLoading ? (
        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
          Loading invite permissions and member usage...
        </div>
      ) : null}

      {!isOwner ? (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          Only workspace owners can create invites. Your current role is{" "}
          <span className="font-medium">{workspaceRole || "unknown"}</span>.
        </div>
      ) : memberLimitReached ? (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <div className="font-medium">Member limit reached</div>
          <div className="mt-1">
            This workspace is currently using{" "}
            <span className="font-semibold">{memberUsage?.used ?? 0}</span> of{" "}
            <span className="font-semibold">{memberUsage?.limit ?? 0}</span> allowed members.
          </div>
          <div className="mt-1">
            Utilization: <span className="font-medium">{formatPercent(memberUsage?.ratio)}</span>
          </div>
          <div className="mt-2">
            Upgrade the workspace plan before creating additional invites.
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          {memberUsage ? (
            <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
              <div>
                Current member usage:{" "}
                <span className="font-semibold">
                  {memberUsage.used} / {memberUsage.limit}
                </span>
              </div>
              <div className="mt-1 text-slate-500">
                Utilization: {formatPercent(memberUsage.ratio)}
              </div>
            </div>
          ) : null}

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="member@example.com"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none ring-0 focus:border-slate-500"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as WorkspaceMemberRole)}
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none ring-0 focus:border-slate-500"
            >
              <option value="member">Member</option>
              <option value="operator">Operator</option>
              <option value="auditor">Auditor</option>
              <option value="owner">Owner</option>
            </select>
          </div>

          {error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          {successMessage ? (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              {successMessage}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loading || memberLimitReached}
            className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Creating Invite..." : "Create Invite"}
          </button>
        </form>
      )}
    </div>
  );
}