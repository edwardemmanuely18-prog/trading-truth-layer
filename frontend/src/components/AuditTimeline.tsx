"use client";

import { useMemo, useState } from "react";
import type { AuditEvent } from "../lib/api";

type Props = {
  events: AuditEvent[];
};

type TimelineTone = "green" | "blue" | "amber" | "violet" | "slate" | "red";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function parseMetadata(value?: string | null): Record<string, unknown> | null {
  if (!value) return null;
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function parseState(value?: string | null): Record<string, unknown> | null {
  if (!value) return null;
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function formatKeyLabel(key: string) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

function getToneForEvent(eventType?: string | null): TimelineTone {
  const normalized = normalizeText(eventType);

  if (normalized.includes("locked")) return "green";
  if (normalized.includes("published")) return "blue";
  if (normalized.includes("verified")) return "amber";
  if (normalized.includes("created")) return "violet";
  if (normalized.includes("failed") || normalized.includes("error")) return "red";
  return "slate";
}

function getToneClasses(tone: TimelineTone) {
  switch (tone) {
    case "green":
      return {
        dot: "bg-green-500",
        badge: "border-green-200 bg-green-50 text-green-800",
        card: "border-green-100",
      };
    case "blue":
      return {
        dot: "bg-blue-500",
        badge: "border-blue-200 bg-blue-50 text-blue-800",
        card: "border-blue-100",
      };
    case "amber":
      return {
        dot: "bg-amber-500",
        badge: "border-amber-200 bg-amber-50 text-amber-800",
        card: "border-amber-100",
      };
    case "violet":
      return {
        dot: "bg-violet-500",
        badge: "border-violet-200 bg-violet-50 text-violet-800",
        card: "border-violet-100",
      };
    case "red":
      return {
        dot: "bg-red-500",
        badge: "border-red-200 bg-red-50 text-red-800",
        card: "border-red-100",
      };
    default:
      return {
        dot: "bg-slate-500",
        badge: "border-slate-200 bg-slate-50 text-slate-700",
        card: "border-slate-200",
      };
  }
}

function eventTitle(eventType?: string | null) {
  const normalized = normalizeText(eventType);

  if (normalized.includes("claim_schema_created")) return "Claim created";
  if (normalized.includes("claim_schema_updated")) return "Draft updated";
  if (normalized.includes("claim_schema_verified")) return "Claim verified";
  if (normalized.includes("claim_schema_published")) return "Claim published";
  if (normalized.includes("claim_schema_locked")) return "Claim locked";
  if (normalized.includes("claim_schema_cloned")) return "New version created";
  if (normalized.includes("evidence")) return "Evidence artifact generated";

  return eventType || "Audit event";
}

function eventNarrative(event: AuditEvent) {
  const normalized = normalizeText(event.event_type);
  const metadata = parseMetadata(event.metadata_json);

  if (normalized.includes("claim_schema_created")) {
    const periodStart = formatValue(metadata?.period_start);
    const periodEnd = formatValue(metadata?.period_end);
    return `A new draft claim record was created and entered into governed lineage.${periodStart !== "—" && periodEnd !== "—" ? ` Initial period: ${periodStart} → ${periodEnd}.` : ""}`;
  }

  if (normalized.includes("claim_schema_updated")) {
    const changedFields = Array.isArray(metadata?.changed_fields)
      ? (metadata?.changed_fields as unknown[]).map(String)
      : [];
    return changedFields.length
      ? `Draft scope was updated. Changed fields: ${changedFields.join(", ")}.`
      : "Draft claim configuration was edited.";
  }

  if (normalized.includes("claim_schema_verified")) {
    return "The draft passed internal verification and moved into verified state.";
  }

  if (normalized.includes("claim_schema_published")) {
    return "The verified claim was promoted to publishable state for controlled external exposure.";
  }

  if (normalized.includes("claim_schema_locked")) {
    const tradeCount = formatValue(metadata?.trade_count);
    return `The claim was finalized and locked with a canonical trade-set fingerprint${tradeCount !== "—" ? ` across ${tradeCount} in-scope trades` : ""}.`;
  }

  if (normalized.includes("claim_schema_cloned")) {
    const parentId = formatValue(metadata?.parent_claim_id);
    const versionNumber = formatValue(metadata?.version_number);
    return `A new governed version was created from a prior claim record${parentId !== "—" ? ` (parent claim ${parentId})` : ""}${versionNumber !== "—" ? ` as version ${versionNumber}` : ""}.`;
  }

  return "Governed event recorded in audit history.";
}

function summarizeMetadata(metadata: Record<string, unknown> | null) {
  if (!metadata) return [];

  const preferredOrder = [
    "actor_id",
    "workspace_id",
    "claim_id",
    "parent_claim_id",
    "root_claim_id",
    "version_number",
    "trade_count",
    "period_start",
    "period_end",
    "source",
  ];

  const picked: Array<{ key: string; value: string }> = [];

  for (const key of preferredOrder) {
    const value = metadata[key];
    if (value === null || value === undefined || value === "") continue;
    if (Array.isArray(value) || typeof value === "object") continue;
    picked.push({ key, value: formatValue(value) });
  }

  return picked;
}

function diffStates(
  oldState: Record<string, unknown> | null,
  newState: Record<string, unknown> | null
) {
  if (!oldState && !newState) return [];

  const keys = Array.from(
    new Set([...(oldState ? Object.keys(oldState) : []), ...(newState ? Object.keys(newState) : [])])
  );

  return keys
    .map((key) => {
      const before = oldState?.[key];
      const after = newState?.[key];

      const beforeString = formatValue(before);
      const afterString = formatValue(after);

      if (beforeString === afterString) return null;

      return {
        key,
        before: beforeString,
        after: afterString,
      };
    })
    .filter(Boolean) as Array<{ key: string; before: string; after: string }>;
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-slate-900">{value}</div>
    </div>
  );
}

export default function AuditTimeline({ events }: Props) {
  const [expandedIds, setExpandedIds] = useState<number[]>([]);

  const sortedEvents = useMemo(() => {
    return [...events].sort((a, b) => {
      const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
      const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
      return bTime - aTime;
    });
  }, [events]);

  const lifecycleCounts = useMemo(() => {
    let created = 0;
    let updated = 0;
    let verified = 0;
    let published = 0;
    let locked = 0;

    for (const event of sortedEvents) {
      const normalized = normalizeText(event.event_type);
      if (normalized.includes("created")) created += 1;
      else if (normalized.includes("updated")) updated += 1;
      else if (normalized.includes("verified")) verified += 1;
      else if (normalized.includes("published")) published += 1;
      else if (normalized.includes("locked")) locked += 1;
    }

    return { created, updated, verified, published, locked };
  }, [sortedEvents]);

  function toggleExpanded(id: number) {
    setExpandedIds((current) =>
      current.includes(id) ? current.filter((value) => value !== id) : [...current, id]
    );
  }

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Audit Timeline</h2>
          <div className="mt-1 text-sm text-slate-500">
            Governed event history for claim state transitions, edits, and lineage actions.
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-6">
          <StatCard label="Events" value={sortedEvents.length} />
          <StatCard label="Created" value={lifecycleCounts.created} />
          <StatCard label="Updated" value={lifecycleCounts.updated} />
          <StatCard label="Verified" value={lifecycleCounts.verified} />
          <StatCard label="Published" value={lifecycleCounts.published} />
          <StatCard label="Locked" value={lifecycleCounts.locked} />
        </div>
      </div>

      {sortedEvents.length === 0 ? (
        <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
          No audit events recorded yet.
        </div>
      ) : (
        <div className="mt-6">
          <div className="relative ml-3 border-l border-slate-200">
            {sortedEvents.map((event, index) => {
              const expanded = expandedIds.includes(event.id);
              const metadata = parseMetadata(event.metadata_json);
              const oldState = parseState(event.old_state);
              const newState = parseState(event.new_state);
              const stateDiff = diffStates(oldState, newState);
              const metadataSummary = summarizeMetadata(metadata);
              const tone = getToneForEvent(event.event_type);
              const toneClasses = getToneClasses(tone);

              return (
                <div key={event.id} className={`relative pl-8 ${index === sortedEvents.length - 1 ? "" : "pb-6"}`}>
                  <div className={`absolute -left-[9px] top-2 h-4 w-4 rounded-full border-2 border-white ${toneClasses.dot}`} />

                  <div className={`rounded-2xl border bg-white p-5 shadow-sm ${toneClasses.card}`}>
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-lg font-semibold text-slate-900">
                            {eventTitle(event.event_type)}
                          </h3>
                          <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${toneClasses.badge}`}>
                            {event.event_type}
                          </span>
                          {index === 0 ? (
                            <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600">
                              most recent
                            </span>
                          ) : null}
                        </div>

                        <div className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                          {eventNarrative(event)}
                        </div>
                      </div>

                      <div className="text-sm text-slate-500">{formatDateTime(event.created_at)}</div>
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                      <div className="rounded-xl bg-slate-50 px-4 py-3">
                        <div className="text-xs uppercase tracking-wide text-slate-500">Entity</div>
                        <div className="mt-1 text-sm font-medium text-slate-900">
                          {event.entity_type || "—"}
                        </div>
                        <div className="mt-1 text-xs text-slate-500">entity id: {event.entity_id || "—"}</div>
                      </div>

                      <div className="rounded-xl bg-slate-50 px-4 py-3">
                        <div className="text-xs uppercase tracking-wide text-slate-500">Actor</div>
                        <div className="mt-1 text-sm font-medium text-slate-900">
                          {event.actor_id || "system"}
                        </div>
                      </div>

                      <div className="rounded-xl bg-slate-50 px-4 py-3">
                        <div className="text-xs uppercase tracking-wide text-slate-500">Workspace</div>
                        <div className="mt-1 text-sm font-medium text-slate-900">
                          {event.workspace_id || "—"}
                        </div>
                      </div>

                      <div className="rounded-xl bg-slate-50 px-4 py-3">
                        <div className="text-xs uppercase tracking-wide text-slate-500">Recorded at</div>
                        <div className="mt-1 text-sm font-medium text-slate-900">
                          {formatDateTime(event.created_at)}
                        </div>
                      </div>
                    </div>

                    {metadataSummary.length > 0 ? (
                      <div className="mt-4 flex flex-wrap gap-2">
                        {metadataSummary.map((item) => (
                          <span
                            key={`${event.id}-${item.key}`}
                            className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700"
                          >
                            {formatKeyLabel(item.key)}: {item.value}
                          </span>
                        ))}
                      </div>
                    ) : null}

                    {(stateDiff.length > 0 || event.metadata_json || event.old_state || event.new_state) ? (
                      <div className="mt-4">
                        <button
                          type="button"
                          onClick={() => toggleExpanded(event.id)}
                          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                        >
                          {expanded ? "Hide governance detail" : "Show raw audit payload"}
                        </button>

                        {expanded ? (
                          <div className="mt-4 space-y-4">
                            {stateDiff.length > 0 ? (
                              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                                <div className="mb-3 text-sm font-semibold text-slate-900">
                                  State diff
                                </div>
                                <div className="space-y-3">
                                  {stateDiff.map((row) => (
                                    <div
                                      key={`${event.id}-${row.key}`}
                                      className="grid gap-3 rounded-xl border border-slate-200 bg-white p-3 md:grid-cols-3"
                                    >
                                      <div>
                                        <div className="text-xs uppercase tracking-wide text-slate-500">
                                          Field
                                        </div>
                                        <div className="mt-1 text-sm font-medium text-slate-900">
                                          {formatKeyLabel(row.key)}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-xs uppercase tracking-wide text-slate-500">
                                          Before
                                        </div>
                                        <div className="mt-1 break-words rounded-lg bg-slate-50 p-2 text-xs text-slate-700">
                                          {row.before}
                                        </div>
                                      </div>
                                      <div>
                                        <div className="text-xs uppercase tracking-wide text-slate-500">
                                          After
                                        </div>
                                        <div className="mt-1 break-words rounded-lg bg-slate-50 p-2 text-xs text-slate-700">
                                          {row.after}
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ) : null}

                            {event.metadata_json ? (
                              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                                <div className="mb-2 text-sm font-semibold text-slate-900">
                                  Metadata JSON
                                </div>
                                <pre className="overflow-x-auto rounded-lg bg-white p-3 text-xs text-slate-700">
                                  {event.metadata_json}
                                </pre>
                              </div>
                            ) : null}

                            {event.old_state ? (
                              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                                <div className="mb-2 text-sm font-semibold text-slate-900">
                                  Old state
                                </div>
                                <pre className="overflow-x-auto rounded-lg bg-white p-3 text-xs text-slate-700">
                                  {event.old_state}
                                </pre>
                              </div>
                            ) : null}

                            {event.new_state ? (
                              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                                <div className="mb-2 text-sm font-semibold text-slate-900">
                                  New state
                                </div>
                                <pre className="overflow-x-auto rounded-lg bg-white p-3 text-xs text-slate-700">
                                  {event.new_state}
                                </pre>
                              </div>
                            ) : null}
                          </div>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}