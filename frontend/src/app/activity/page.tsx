"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type AuditEvent } from "../../lib/api";
import { useAuth } from "../../components/AuthProvider";

function formatDate(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function parseJson(value?: string | null) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

export default function ActivityPage() {
  const { user, workspaces, loading: authLoading, logout } = useAuth();

  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const firstWorkspace = workspaces[0] ?? null;
  const workspaceHref = firstWorkspace
    ? `/workspace/${firstWorkspace.workspace_id}/dashboard`
    : "/";

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await api.getLatestAuditEvents(50);
        if (!active) return;
        setEvents(Array.isArray(result) ? result : []);
      } catch (err) {
        if (!active) return;
        setEvents([]);
        setError(err instanceof Error ? err.message : "Failed to load activity.");
      } finally {
        if (!active) return;
        setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <div className="text-lg font-bold tracking-tight">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">Platform Activity Feed</div>
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

            {authLoading ? (
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
                  onClick={() => logout()}
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

      <main className="mx-auto max-w-5xl space-y-6 px-6 py-10">
        <div>
          <div className="text-sm text-slate-500">Trading Truth Layer · Activity Feed</div>
          <h1 className="mt-2 text-4xl font-bold">Platform Activity</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Lifecycle log of claim creation, verification, publishing, locking, and governance
            events across the platform.
          </p>
        </div>

        {error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700 shadow-sm">
            {error}
          </div>
        ) : null}

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading activity...</div>
        ) : events.length === 0 ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm text-slate-500">
            No activity recorded yet.
          </div>
        ) : (
          <div className="space-y-4">
            {events.map((event) => {
              const oldState = parseJson(event.old_state);
              const newState = parseJson(event.new_state);
              const metadata = parseJson(event.metadata_json);

              return (
                <div key={event.id} className="rounded-2xl border bg-white p-5 shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="text-lg font-semibold">{event.event_type}</div>
                    <div className="text-xs text-slate-500">{formatDate(event.created_at)}</div>
                  </div>

                  <div className="mt-2 text-sm text-slate-500">
                    entity: {event.entity_type} / {event.entity_id} / workspace:{" "}
                    {event.workspace_id ?? "—"}
                  </div>

                  <div className="mt-4 grid gap-4 lg:grid-cols-3">
                    <div>
                      <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                        Old State
                      </div>
                      <pre className="overflow-x-auto rounded-xl bg-slate-50 p-3 text-xs text-slate-700">
                        {JSON.stringify(oldState, null, 2)}
                      </pre>
                    </div>

                    <div>
                      <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                        New State
                      </div>
                      <pre className="overflow-x-auto rounded-xl bg-slate-50 p-3 text-xs text-slate-700">
                        {JSON.stringify(newState, null, 2)}
                      </pre>
                    </div>

                    <div>
                      <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                        Metadata
                      </div>
                      <pre className="overflow-x-auto rounded-xl bg-slate-50 p-3 text-xs text-slate-700">
                        {JSON.stringify(metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}