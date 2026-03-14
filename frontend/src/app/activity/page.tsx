"use client";

import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import { api, type AuditEvent } from "../../lib/api";

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
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const result = await api.getLatestAuditEvents(50);
        setEvents(Array.isArray(result) ? result : []);
      } catch {
        setEvents([]);
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-5xl space-y-6 px-6 py-10">
        <div>
          <div className="text-sm text-slate-500">Trading Truth Layer · Activity Feed</div>
          <h1 className="mt-2 text-4xl font-bold">Platform Activity</h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Real-time lifecycle log of claim creation, verification, publishing, locking, and
            governance events across the platform.
          </p>
        </div>

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