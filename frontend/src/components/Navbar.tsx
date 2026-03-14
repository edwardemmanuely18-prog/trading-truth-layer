"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Props = {
  workspaceId?: number;
};

export default function Navbar({ workspaceId = 1 }: Props) {
  const [latestClaimId, setLatestClaimId] = useState<number | null>(null);

  useEffect(() => {
    async function loadLatestClaim() {
      try {
        const res = await fetch("http://localhost:8000/claim-schemas/latest", {
          cache: "no-store",
        });

        if (!res.ok) {
          setLatestClaimId(null);
          return;
        }

        const data = await res.json();
        setLatestClaimId(data.id);
      } catch {
        setLatestClaimId(null);
      }
    }

    loadLatestClaim();
  }, []);

  const base = `/workspace/${workspaceId}`;
  const claimsHref = `${base}/claims`;
  const evidenceHref = latestClaimId ? `${base}/evidence?claimId=${latestClaimId}` : `${base}/evidence`;

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href={`${base}/dashboard`} className="text-lg font-bold text-slate-900">
          Trading Truth Layer
        </Link>

        <nav className="flex flex-wrap gap-2">
          <Link
            href={`${base}/dashboard`}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Dashboard
          </Link>
          <Link
            href={`${base}/import`}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Import
          </Link>
          <Link
            href={`${base}/ledger`}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Ledger
          </Link>
          <Link
            href={`${base}/schema`}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Schema Builder
          </Link>
          <Link
            href={claimsHref}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Claims
          </Link>
          <Link
            href={evidenceHref}
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100"
          >
            Evidence
          </Link>
        </nav>
      </div>
    </header>
  );
}