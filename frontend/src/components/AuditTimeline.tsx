"use client";

import { useMemo, useState } from "react";
import type { AuditEvent } from "../lib/api";

type Props = {
  events: AuditEvent[];
  title?: string;
  compact?: boolean;
};

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function tryParseJson(value?: string | null) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function humanizeEventType(eventType?: string | null) {
  const normalized = normalizeText(eventType);

  switch (normalized) {
    case "claim_schema_created":
      return "Claim created";
    case "claim_schema_updated":
      return "Draft updated";
    case "claim_schema_verified":
      return "Claim verified";
    case "claim_schema_published":
      return "Claim published";
    case "claim_schema_locked":
      return "Claim locked";
    case "claim_schema_cloned":
      return "New version created";
    default:
      return eventType || "Unknown event";
  }
}

function eventAccent(eventType?: string | null) {
  const normalized = normalizeText(eventType);

  if (normalized.includes("locked")) {
    return {
      dot: "bg-green-600",
      badge: "border-green-200 bg-green-50 text-green-800",
    };
  }

  if (normalized.includes("published")) {
    return {
      dot: "bg-blue-600",
      badge: "border-blue-200 bg-blue-50 text-blue-800",
    };
  }

  if (normalized.includes("verified")) {
    return {
      dot: "bg-amber-500",
      badge: "border-amber-200 bg-amber-50 text-amber-800",
    };
  }

  if (normalized.includes("updated")) {
    return {
      dot: "bg-slate-700",
      badge: "border-slate-200 bg-slate-100 text-slate-800",
    };
  }

  if (normalized.includes("created") || normalized.includes("cloned")) {
    return {
      dot: "bg-violet-600",
      badge: "border-violet-200 bg-violet-50 text-violet-800",
    };
  }

  return {
    dot: "bg-slate-500",
    badge: "border-slate-200 bg-slate-100 text-slate-800",
  };
}

function summarizeMetadata(metadata: unknown) {
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) {
    return [];
  }

  const record = metadata as Record<string, unknown>;
  const rows: string[] = [];

  if (record.actor_user_id !== undefined && record.actor_user_id !== null) {
    rows.push(`actor user: ${String(record.actor_user_id)}`);
  }

  if (record.trade_count !== undefined && record.trade_count !== null) {
    rows.push(`trade count: ${String(record.trade_count)}`);
  }

  if (record.period_start && record.period_end) {
    rows.push(`period: ${String(record.period_start)} → ${String(record.period_end)}`);
  }

  if (record.source) {
    rows.push(`source: ${String(record.source)}`);
  }

  return rows;
}

function deriveChangeSummary(
  eventType?: string | null,
  oldState?: unknown,
  newState?: unknown,
  metadata?: unknown
) {
  const normalized = normalizeText(eventType);

  const oldRecord =
    oldState && typeof oldState === "object" && !Array.isArray(oldState)
      ? (oldState as Record<string, unknown>)
      : null;

  const newRecord =
    newState && typeof newState === "object" && !Array.isArray(newState)
      ? (newState as Record<string, unknown>)
      : null;

  const metadataRecord =
    metadata && typeof metadata === "object" && !Array.isArray(metadata)
      ? (metadata as Record<string, unknown>)
      : null;

  if (normalized === "claim_schema_created") {
    return "A new draft claim record was created and entered into governed lineage.";
  }

  if (normalized === "claim_schema_cloned") {
    const sourceClaimId = oldRecord?.source_claim_id;
    const newVersionNumber = newRecord?.version_number;
    return `A new claim version was created from claim ${sourceClaimId ?? "—"}${
      newVersionNumber !== undefined ? ` as version ${String(newVersionNumber)}` : ""
    }.`;
  }

  if (normalized === "claim_schema_verified") {
    return "The draft passed internal verification and moved into verified state.";
  }

  if (normalized === "claim_schema_published") {
    return "The verified claim was promoted to publishable state for controlled external exposure.";
  }

  if (normalized === "claim_schema_locked") {
    const tradeCount = metadataRecord?.trade_count;
    return `The claim was finalized and locked with a canonical trade-set fingerprint${
      tradeCount !== undefined ? ` across ${String(tradeCount)} in-scope trades` : ""
    }.`;
  }

  if (normalized === "claim_schema_updated") {
    const changedFields: string[] = [];

    if (oldRecord && newRecord) {
      const keysToCheck = [
        "name",
        "period_start",
        "period_end",
        "visibility",
        "methodology_notes",
        "included_member_ids_json",
        "included_symbols_json",
        "excluded_trade_ids_json",
      ];

      for (const key of keysToCheck) {
        const oldValue = JSON.stringify(oldRecord[key] ?? null);
        const newValue = JSON.stringify(newRecord[key] ?? null);
        if (oldValue !== newValue) {
          changedFields.push(key);
        }
      }
    }

    if (changedFields.length > 0) {
      return `Draft scope was updated. Changed fields: ${changedFields.join(", ")}.`;
    }

    return "Draft claim content was updated.";
  }

  return "Audit event recorded for this claim.";
}

function JsonPanel({
  title,
  value,
}: {
  title: string;
  value: unknown;
}) {
  return (
    <div>
      <div className="mb-1 text-xs font-medium text-slate-500">{title}</div>
      <pre className="overflow-x-auto rounded-lg bg-slate-50 p-3 text-xs text-slate-700">
        {JSON.stringify(value, null, 2)}
      </pre>
    </div>
  );
}

function AuditEventCard({
  event,
  compact,
  isFirst,
  isLast,
}: {
  event: AuditEvent;
  compact: boolean;
  isFirst: boolean;
  isLast: boolean;
}) {
  const [expanded, setExpanded] = useState(false);

  const oldState = tryParseJson(event.old_state);
  const newState = tryParseJson(event.new_state);
  const metadata = tryParseJson(event.metadata_json);

  const accent = eventAccent(event.event_type);
  const eventLabel = humanizeEventType(event.event_type);
  const metadataSummary = summarizeMetadata(metadata);
  const summary = deriveChangeSummary(event.event_type, oldState, newState, metadata);

  return (
    <div className="relative pl-8">
      {!isLast ? (
        <div className="absolute left-[11px] top-6 h-[calc(100%+12px)] w-px bg-slate-200" />
      ) : null}

      <div className={`absolute left-0 top-2 h-6 w-6 rounded-full border-4 border-white ${accent.dot}`} />

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <div className="font-semibold text-slate-900">{eventLabel}</div>
              <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold ${accent.badge}`}>
                {event.event_type}
              </span>
              {isFirst ? (
                <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-semibold text-slate-700">
                  most recent
                </span>
              ) : null}
            </div>

            <div className="mt-2 text-sm text-slate-600">{summary}</div>
          </div>

          <div className="text-xs text-slate-500">{formatDateTime(event.created_at)}</div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
          <span>entity: {event.entity_type}</span>
          <span>entity id: {event.entity_id}</span>
          <span>workspace: {event.workspace_id ?? "—"}</span>
        </div>

        {metadataSummary.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {metadataSummary.map((row) => (
              <span
                key={row}
                className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-medium text-slate-700"
              >
                {row}
              </span>
            ))}
          </div>
        ) : null}

        {!compact ? (
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setExpanded((prev) => !prev)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
            >
              {expanded ? "Hide raw audit payload" : "Show raw audit payload"}
            </button>

            {expanded ? (
              <div className="mt-4 grid gap-3 lg:grid-cols-3">
                <JsonPanel title="Old State" value={oldState} />
                <JsonPanel title="New State" value={newState} />
                <JsonPanel title="Metadata" value={metadata} />
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default function AuditTimeline({
  events,
  title = "Audit Timeline",
  compact = false,
}: Props) {
  const ordered = useMemo(() => {
    return [...events].sort((a, b) => {
      const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
      const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
      return bTime - aTime;
    });
  }, [events]);

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">{title}</h2>
          <div className="mt-1 text-sm text-slate-500">
            Governed event history for claim state transitions, edits, and lineage actions.
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
          <div className="text-slate-500">Events</div>
          <div className="mt-1 font-semibold">{ordered.length}</div>
        </div>
      </div>

      {ordered.length === 0 ? (
        <div className="mt-4 text-sm text-slate-500">No audit events found.</div>
      ) : (
        <div className="mt-5 space-y-4">
          {ordered.map((event, index) => (
            <AuditEventCard
              key={event.id}
              event={event}
              compact={compact}
              isFirst={index === 0}
              isLast={index === ordered.length - 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}