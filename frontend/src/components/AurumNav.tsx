"use client";

import Link from "next/link";

export default function AurumNav() {
  return (
    <div className="mt-8 flex gap-4">

      <Link
        href="/aurum"
        className="rounded-xl border px-4 py-2"
      >
        Overview
      </Link>

      <Link
        href="/aurum/users"
        className="rounded-xl border px-4 py-2"
      >
        Users
      </Link>

      <Link
        href="/aurum/workspaces"
        className="rounded-xl border px-4 py-2"
      >
        Workspaces
      </Link>

      <Link
        href="/aurum/claims"
        className="rounded-xl border px-4 py-2"
      >
        Claims
      </Link>

    </div>
  );
}