"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { useAuth } from "../../components/AuthProvider";

const ImportForm = dynamic(() => import("../../components/ImportForm"), {
  ssr: false,
  loading: () => (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading import form...</div>
  ),
});

export default function ImportPage() {
  const { user, workspaces, loading, logout } = useAuth();

  const firstWorkspace = workspaces[0] ?? null;
  const workspaceHref = firstWorkspace
    ? `/workspace/${firstWorkspace.workspace_id}/dashboard`
    : "/";

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <div className="text-lg font-bold tracking-tight">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">Trade Import</div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
            >
              Home
            </Link>

            <Link
              href="/claims"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
            >
              Public Claims
            </Link>

            {loading ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-500">
                Loading session...
              </div>
            ) : user ? (
              <>
                <Link
                  href={workspaceHref}
                  className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  Open Workspace
                </Link>

                <button
                  onClick={logout}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
                >
                  Sign Out
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Trade Import</h1>
          <p className="mt-2 text-slate-600">
            Add manual trades now. CSV ingestion will plug into this workflow next.
          </p>
        </div>

        <ImportForm />
      </main>
    </div>
  );
}