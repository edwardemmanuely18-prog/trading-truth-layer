import Link from "next/link";
import Navbar from "../../../../components/Navbar";
import TradeTable from "../../../../components/TradeTable";
import { api } from "../../../../lib/api";

type PageProps = {
  params: Promise<{
    workspaceId: string;
  }>;
};

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function summarizeJson(value?: string | null) {
  if (!value) return "—";

  try {
    const parsed = JSON.parse(value);

    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      const entries = Object.entries(parsed).slice(0, 3);
      if (entries.length === 0) return "{}";
      return entries
        .map(([k, v]) => `${k}: ${typeof v === "object" ? "[...]" : String(v)}`)
        .join(" | ");
    }

    return JSON.stringify(parsed);
  } catch {
    return value;
  }
}

export default async function WorkspaceLedgerPage({ params }: PageProps) {
  const resolved = await params;
  const workspaceId = Number(resolved.workspaceId);

  if (Number.isNaN(workspaceId)) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  const [trades, latestAuditEvents, workspaceAuditEvents] = await Promise.all([
    api.getTrades(workspaceId),
    api.getLatestAuditEvents(20),
    api.getAuditEventsForWorkspace(workspaceId, 50),
  ]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Canonical Ledger</h1>
          <p className="mt-2 text-slate-600">
            Normalized trade records, audit history, and governance events for workspace {workspaceId}.
          </p>
        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Workspace</div>
            <div className="mt-2 text-2xl font-semibold">{workspaceId}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trades in Ledger</div>
            <div className="mt-2 text-2xl font-semibold">{trades.length}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Audit Events Loaded</div>
            <div className="mt-2 text-2xl font-semibold">{workspaceAuditEvents.length}</div>
          </div>
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Latest Audit Events</h2>

          {latestAuditEvents.length === 0 ? (
            <div className="mt-4 text-sm text-slate-500">No audit events found.</div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="px-3 py-2">ID</th>
                    <th className="px-3 py-2">Event Type</th>
                    <th className="px-3 py-2">Entity</th>
                    <th className="px-3 py-2">Workspace</th>
                    <th className="px-3 py-2">Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {latestAuditEvents.map((event) => (
                    <tr key={event.id} className="border-b last:border-0">
                      <td className="px-3 py-2 font-medium">{event.id}</td>
                      <td className="px-3 py-2">{event.event_type}</td>
                      <td className="px-3 py-2">
                        <div>{event.entity_type}</div>
                        <div className="text-xs text-slate-500">{event.entity_id}</div>
                      </td>
                      <td className="px-3 py-2">{event.workspace_id ?? "—"}</td>
                      <td className="px-3 py-2">{formatDateTime(event.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Workspace Audit Ledger</h2>

          {workspaceAuditEvents.length === 0 ? (
            <div className="mt-4 text-sm text-slate-500">No workspace audit events found.</div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="px-3 py-2">ID</th>
                    <th className="px-3 py-2">Event</th>
                    <th className="px-3 py-2">Entity</th>
                    <th className="px-3 py-2">Old State</th>
                    <th className="px-3 py-2">New State</th>
                    <th className="px-3 py-2">Metadata</th>
                    <th className="px-3 py-2">Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {workspaceAuditEvents.map((event) => (
                    <tr key={event.id} className="align-top border-b last:border-0">
                      <td className="px-3 py-2 font-medium">{event.id}</td>
                      <td className="px-3 py-2">{event.event_type}</td>
                      <td className="px-3 py-2">
                        <div>{event.entity_type}</div>
                        <div className="text-xs text-slate-500">{event.entity_id}</div>
                        {event.entity_type === "claim_schema" && (
                          <div className="mt-2">
                            <Link
                              href={`/claim/${event.entity_id}`}
                              className="text-xs text-blue-600 hover:underline"
                            >
                              Open claim
                            </Link>
                          </div>
                        )}
                      </td>
                      <td className="px-3 py-2 text-xs text-slate-700">{summarizeJson(event.old_state)}</td>
                      <td className="px-3 py-2 text-xs text-slate-700">{summarizeJson(event.new_state)}</td>
                      <td className="px-3 py-2 text-xs text-slate-700">{summarizeJson(event.metadata_json)}</td>
                      <td className="px-3 py-2">{formatDateTime(event.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Trade Ledger</h2>
          <div className="mt-4">
            <TradeTable trades={trades} />
          </div>
        </div>
      </main>
    </div>
  );
}