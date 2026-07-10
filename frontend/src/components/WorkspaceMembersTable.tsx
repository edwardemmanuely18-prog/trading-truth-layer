"use client";

import { useMemo, useState } from "react";
import { api, type WorkspaceMember, type WorkspaceMemberRole } from "../lib/api";

import KPI from "./governance/KPI";

import IdentityCard from "./governance/IdentityCard";
import AuthorityCard from "./governance/AuthorityCard";
import PermissionSummary from "./governance/PermissionSummary";

type Props = {
  workspaceId: number;
  rows: WorkspaceMember[];
  currentUserId?: number | null;
  canManage?: boolean;
  onChanged?: () => void | Promise<void>;
};

function roleBadge(role?: string | null) {
  const normalized = (role || "").toLowerCase();

  const className =
    normalized === "owner"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "operator"
        ? "border-blue-200 bg-blue-100 text-blue-800"
        : normalized === "auditor"
          ? "border-purple-200 bg-purple-100 text-purple-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${className}`}>
      {role || "unknown"}
    </span>
  );
}

const ROLE_METADATA = {

  owner: {

    authority: "High",

    scope:
      "Governance • Billing • Identity",

    status: "Critical",

  },

  operator: {

    authority: "Medium",

    scope:
      "Evidence • Claims • Reports",

    status: "Operational",

  },

  auditor: {

    authority: "Read Only",

    scope:
      "Verification • Audit",

    status: "Independent",

  },

  member: {

    authority: "Limited",

    scope:
      "Workspace Participation",

    status: "Standard",

  },

} as const;

function roleMetadata(role?: string | null) {

  return (
    ROLE_METADATA[
      (
        role ||
        "member"
      ).toLowerCase() as keyof typeof ROLE_METADATA
    ] ??
    ROLE_METADATA.member
  );

}

function initials(name?: string | null) {

  if (!name) return "?";

  return name
    .split(" ")
    .map(part => part[0])
    .join("")
    .substring(0, 2)
    .toUpperCase();

}

function dedupeMembers(rows: WorkspaceMember[]) {
  const seen = new Set<string>();

  return rows.filter((row, index) => {
    const stableKey = `${row.workspace_id}-${row.user_id}-${row.email || ""}-${row.workspace_role || ""}`;

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

export default function WorkspaceMembersTable({
  workspaceId,
  rows,
  currentUserId = null,
  canManage = false,
  onChanged,
}: Props) {
  const safeRows = useMemo(() => dedupeMembers(Array.isArray(rows) ? rows : []), [rows]);
  const [busyMemberId, setBusyMemberId] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] =

      useState("");

  const [roleFilter, setRoleFilter] =

      useState("all");

  const visibleRows =

      safeRows.filter(row => {

          const searchMatch =

              `${row.name} ${row.email}`

                  .toLowerCase()

                  .includes(

                      search.toLowerCase()

                  );

          const roleMatch =

              roleFilter === "all"

                  ||

              row.workspace_role === roleFilter;

          return (

              searchMatch

              &&

              roleMatch

          );

      });

  async function handleRoleChange(userId: number, role: WorkspaceMemberRole) {
    try {
      setBusyMemberId(userId);
      setFeedback(null);
      setError(null);

      await api.updateWorkspaceMemberRole(workspaceId, userId, { role });

      setFeedback("Workspace member role updated successfully.");

      if (onChanged) {
        await onChanged();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update member role.");
    } finally {
      setBusyMemberId(null);
    }
  }

  async function handleRemove(userId: number) {
    try {
      setBusyMemberId(userId);
      setFeedback(null);
      setError(null);

      await api.removeWorkspaceMember(workspaceId, userId);

      setFeedback("Workspace member removed successfully.");

      if (onChanged) {
        await onChanged();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove member.");
    } finally {
      setBusyMemberId(null);
    }
  }

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-3xl font-bold">

        Institutional Identity Registry

        </h2>

        <p className="mt-3 text-slate-600">

        Canonical registry of governed workspace
        identities, authority assignments,
        operational responsibilities and
        institutional permissions.

        </p>
        <p className="mt-2 text-sm text-slate-600">
          Current member directory and effective roles inside this workspace.
        </p>
      </div>

      <div className="mb-8 grid gap-4 md:grid-cols-4">

        <KPI

          title="Identities"

          value={safeRows.length}

        />

        <KPI

          title="Owners"

          value={
            safeRows.filter(
              r => r.workspace_role === "owner"
            ).length
          }

        />

        <KPI

          title="Operators"

          value={
            safeRows.filter(
              r => r.workspace_role === "operator"
            ).length
          }

        />

        <KPI

          title="Auditors"

          value={
            safeRows.filter(
              r => r.workspace_role === "auditor"
            ).length
          }

        />

      </div>

      <div className="mb-6 flex flex-wrap gap-4">

      <input

          value={search}

          onChange={e =>

              setSearch(

                  e.target.value

              )

          }

          placeholder="Search identity..."

          className="rounded-xl border px-4 py-3"

      />

      <select

          value={roleFilter}

          onChange={e =>

              setRoleFilter(

                  e.target.value

              )

          }

          className="rounded-xl border px-4 py-3"

      >

      <option value="all">

      All Roles

      </option>

      <option value="owner">

      Owner

      </option>

      <option value="operator">

      Operator

      </option>

      <option value="auditor">

      Auditor

      </option>

      <option value="member">

      Member

      </option>

      </select>

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
        <div className="text-sm text-slate-500">No workspace members found.</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>

            <tr className="border-b text-left text-slate-500">

            <th className="w-[360px] px-4 py-3">

            Identity

            </th>

            <th className="w-[180px] px-4 py-3">

            Governance

            </th>

            <th className="w-[220px] px-4 py-3">

            Authority

            </th>

            <th className="w-[140px] px-4 py-3">

            Role

            </th>

            <th className="w-[240px] px-4 py-3">

            Permissions

            </th>

            {canManage && (

            <th className="w-[170px] px-4 py-3">

            Manage

            </th>

            )}

            {canManage && (

            <th className="w-[130px] px-4 py-3">

            Actions

            </th>

            )}

            </tr>

            </thead>
            
            <tbody>
              {visibleRows.map((row, index) => {
                const isBusy = busyMemberId === row.user_id;
                const isSelf = currentUserId === row.user_id;
                const currentRole = (row.workspace_role || "member") as WorkspaceMemberRole;

                return (
                  <tr
                    key={`${row.workspace_id}-${row.user_id}-${row.email || "no-email"}-${row.workspace_role || "no-role"}-${index}`}
                    className="border-b last:border-0"
                  >
                    <td className="px-3 py-3 font-medium">{row.user_id}</td>
                    <td className="px-3 py-5">

                    <IdentityCard

                    member={row}

                    />

                    </td>
                    
                    <td className="px-4 py-5 align-top">

                        <div className="flex flex-col gap-3">

                        <div>

                        {roleBadge(row.global_role)}

                        </div>

                        <div>

                        {roleBadge(row.workspace_role)}

                        </div>

                        </div>

                    </td>

                    <td className="px-4 py-5 align-top">

                    <AuthorityCard
                        authority={roleMetadata(row.workspace_role).authority}
                        scope={roleMetadata(row.workspace_role).scope}
                        status={roleMetadata(row.workspace_role).status}
                    />

                    </td>

                    <td className="px-4 py-5 align-top">

                        {roleBadge(row.workspace_role)}

                    </td>

                    <td className="px-3 py-5">

                    <PermissionSummary

                    role={
                    row.workspace_role
                    }

                    />

                    </td>

                    {canManage ? (
                      <td className="px-4 py-5 align-top">
                        <select
                          value={currentRole}
                          disabled={isBusy}
                          onChange={(e) =>
                            void handleRoleChange(row.user_id, e.target.value as WorkspaceMemberRole)
                          }
                          className="rounded-lg border border-slate-300 px-3 py-2 text-xs outline-none focus:border-slate-500 disabled:cursor-not-allowed disabled:bg-slate-100"
                        >
                          <option value="owner">owner</option>
                          <option value="operator">operator</option>
                          <option value="member">member</option>
                          <option value="auditor">auditor</option>
                        </select>
                      </td>
                    ) : null}

                    {canManage ? (
                      <td className="px-4 py-5 align-top">
                        <button
                          type="button"
                          onClick={() => void handleRemove(row.user_id)}
                          disabled={isBusy || isSelf}
                          className="rounded-lg border border-red-300 px-3 py-2 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {isBusy ? "Working..." : isSelf ? "Current User" : "Remove"}
                        </button>
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