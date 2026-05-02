import Link from "next/link";
import Navbar from "../../components/Navbar";
import TradeTable from "../../components/TradeTable";
import { api } from "../../lib/api";
import type { AuditEvent } from "../../lib/api";

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

export default async function LedgerPage() {
  const [trades, usage, latestAuditEvents, workspaceAuditEvents] =
    await Promise.all([
      api.getTrades(1),
      api.getWorkspaceUsage(1),
      api.getLatestAuditEvents(20),
      api.getAuditEventsForWorkspace(1, 50),
    ]);

  // ✅ Metrics extraction
  const used = usage.usage.trades.used;
  const limit = usage.usage.trades.limit;
  const utilization = usage.usage.trades.ratio
    ? Math.round(usage.usage.trades.ratio * 100)
    : 0;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Canonical Ledger</h1>
          <p className="mt-2 text-slate-600">
            Normalized trade records, audit history, and governance events for verification,
            analytics, claim generation, and forensic review.
          </p>
        </div>

        {/* ✅ TRADE CAPACITY (FIXED) */}
        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">Trade Capacity</h2>
              <p className="text-sm text-slate-500">
                Current workspace trade usage against plan allowance.
              </p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <div className="text-sm text-slate-500">Used</div>
              <div className="text-2xl font-semibold">{used}</div>
            </div>

            <div>
              <div className="text-sm text-slate-500">Limit</div>
              <div className="text-2xl font-semibold">{limit}</div>
            </div>

            <div>
              <div className="text-sm text-slate-500">Utilization</div>
              <div className="text-2xl font-semibold">{utilization}%</div>
            </div>
          </div>
        </div>

        {/* SUMMARY CARDS */}
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Workspace</div>
            <div className="mt-2 text-2xl font-semibold">1</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trades in Ledger</div>
            <div className="mt-2 text-2xl font-semibold">
              {trades?.length ?? 0}
            </div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Audit Events Loaded</div>
            <div className="mt-2 text-2xl font-semibold">
              {workspaceAuditEvents.length}
            </div>
          </div>
        </div>

        {/* LATEST AUDIT */}
        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Latest Audit Events</h2>

          {latestAuditEvents.length === 0 ? (
            <div className="text-sm text-slate-500">No audit events found.</div>
          ) : (
            <div className="overflow-x-auto">
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
                  {latestAuditEvents.map((event: AuditEvent) => (
                    <tr key={event.id} className="border-b">
                      <td className="px-3 py-2">{event.id}</td>
                      <td className="px-3 py-2">{event.event_type}</td>
                      <td className="px-3 py-2">{event.entity_type}</td>
                      <td className="px-3 py-2">
                        {event.workspace_id ?? "—"}
                      </td>
                      <td className="px-3 py-2">
                        {formatDateTime(event.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* WORKSPACE AUDIT */}
        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">
            Workspace Audit Ledger
          </h2>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Event</th>
                  <th className="px-3 py-2">Entity</th>
                  <th className="px-3 py-2">Old</th>
                  <th className="px-3 py-2">New</th>
                  <th className="px-3 py-2">Meta</th>
                  <th className="px-3 py-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {workspaceAuditEvents.map((event: AuditEvent) => (
                  <tr key={event.id} className="border-b">
                    <td className="px-3 py-2">{event.id}</td>
                    <td className="px-3 py-2">{event.event_type}</td>
                    <td className="px-3 py-2">{event.entity_type}</td>
                    <td className="px-3 py-2">
                      {summarizeJson(event.old_state)}
                    </td>
                    <td className="px-3 py-2">
                      {summarizeJson(event.new_state)}
                    </td>
                    <td className="px-3 py-2">
                      {summarizeJson(event.metadata_json)}
                    </td>
                    <td className="px-3 py-2">
                      {formatDateTime(event.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* TRADE TABLE */}
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Trade Ledger</h2>
          <TradeTable trades={trades} />
        </div>
      </main>
    </div>
  );
}