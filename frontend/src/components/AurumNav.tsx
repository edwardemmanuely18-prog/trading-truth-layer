"use client";

import Link from "next/link";

export default function AurumNav() {
  return (
    <div className="mb-8 border-b pb-4">
      <div className="flex gap-3 flex-wrap">

        <Link
          href="/aurum"
          className="rounded-lg border px-4 py-2 text-sm font-medium"
        >
          Dashboard
        </Link>

        <Link
          href="/aurum/users"
          className="rounded-lg border px-4 py-2 text-sm font-medium"
        >
          Users
        </Link>

        <Link
          href="/aurum/workspaces"
          className="rounded-lg border px-4 py-2 text-sm font-medium"
        >
          Workspaces
        </Link>

        <Link
          href="/aurum/claims"
          className="rounded-lg border px-4 py-2 text-sm font-medium"
        >
          Claims
        </Link>

      </div>
    </div>
  );
}