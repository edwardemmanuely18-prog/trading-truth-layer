"use client";

import { use } from "react";
import { useEffect, useState } from "react";

import Navbar from "../../../../components/Navbar";

import {
  AuditEvent,
  getAuditEvents,
} from "../../../../lib/api";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {

  const resolvedParams =
    use(params);

  const workspaceId =
    Number(
      resolvedParams.workspaceId
    );

  const [events, setEvents] =
    useState<AuditEvent[]>([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    async function load() {

      try {

        const data =
          await getAuditEvents(
            workspaceId
          );

        setEvents(data);

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }

    }

    load();

  }, [workspaceId]);

  const importEvents =
    events.filter(
      e =>
        e.event_type.includes(
          "import"
        )
    ).length;

  const securityEvents =
    events.filter(
      e =>
        e.entity_type ===
        "security"
    ).length;

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Governance Ledger
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Audit Timeline
          </h1>

          <p className="mt-3 text-slate-600">
            Immutable governance and
            operational activity feed
            across the workspace.
          </p>

        </div>

        <div className="grid gap-4 md:grid-cols-4 mb-8">

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Total Events
            </div>

            <div className="mt-2 text-3xl font-bold">
              {events.length}
            </div>

          </div>

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Import Events
            </div>

            <div className="mt-2 text-3xl font-bold">
              {importEvents}
            </div>

          </div>

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Security Events
            </div>

            <div className="mt-2 text-3xl font-bold">
              {securityEvents}
            </div>

          </div>

          <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">
              Latest Event
            </div>

            <div className="mt-2 text-sm font-medium">
              {events[0]?.created_at
                ?.substring(0, 19) || "-"}
            </div>

          </div>

        </div>

        <div className="rounded-xl border bg-white overflow-hidden">

          <table className="w-full">

            <thead className="bg-slate-100">

              <tr>

                <th className="p-4 text-left">
                  Event
                </th>

                <th className="p-4 text-left">
                  Entity
                </th>

                <th className="p-4 text-left">
                  Entity ID
                </th>

                <th className="p-4 text-left">
                  Actor
                </th>

                <th className="p-4 text-left">
                  Created
                </th>

              </tr>

            </thead>

            <tbody>

              {loading && (

                <tr>

                  <td
                    colSpan={5}
                    className="p-6"
                  >
                    Loading...
                  </td>

                </tr>

              )}

              {!loading &&
                events.map(event => (

                  <tr
                    key={event.id}
                    className="border-t"
                  >

                    <td className="p-4">
                      {event.event_type}
                    </td>

                    <td className="p-4">
                      {event.entity_type}
                    </td>

                    <td className="p-4">
                      {event.entity_id}
                    </td>

                    <td className="p-4">
                      {event.actor_id ||
                        (() => {
                          try {
                            const meta =
                              event.metadata_json
                                ? JSON.parse(event.metadata_json)
                                : null;

                            return (
                              meta?.actor_user_id ??
                              "-"
                            );
                          } catch {
                            return "-";
                          }
                        })()}
                    </td>

                    <td className="p-4">
                      {event.created_at
                        ?.substring(0, 19)}
                    </td>

                  </tr>

                ))}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );

}