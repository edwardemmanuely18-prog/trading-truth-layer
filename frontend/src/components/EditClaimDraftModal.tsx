"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type ClaimSchema, type ClaimSchemaUpdatePayload } from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  open: boolean;
  claim: ClaimSchema;
  onClose: () => void;
  onSaved: (updated: ClaimSchema) => Promise<void> | void;
};

type FormState = {
  name: string;
  period_start: string;
  period_end: string;
  included_member_ids_text: string;
  included_symbols_text: string;
  excluded_trade_ids_text: string;
  methodology_notes: string;
  visibility: string;
};

function buildInitialFormState(claim: ClaimSchema): FormState {
  return {
    name: claim.name || "",
    period_start: claim.period_start || "",
    period_end: claim.period_end || "",
    included_member_ids_text: (claim.included_member_ids_json || []).join(", "),
    included_symbols_text: (claim.included_symbols_json || []).join(", "),
    excluded_trade_ids_text: (claim.excluded_trade_ids_json || []).join(", "),
    methodology_notes: claim.methodology_notes || "",
    visibility: claim.visibility || "private",
  };
}

function parseNumberList(value: string): number[] {
  if (!value.trim()) return [];

  const tokens = value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

  const parsed = tokens.map((token) => Number(token));

  if (parsed.some((num) => Number.isNaN(num))) {
    throw new Error("Member IDs and excluded trade IDs must be comma-separated numbers.");
  }

  return Array.from(new Set(parsed.map((num) => Math.trunc(num))));
}

function parseStringList(value: string): string[] {
  if (!value.trim()) return [];

  return Array.from(
    new Set(
      value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
        .map((item) => item.toUpperCase())
    )
  );
}

function VisibilityBadge({ visibility }: { visibility?: string }) {
  const normalized = String(visibility || "").toLowerCase().trim();

  const className =
    normalized === "public"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : normalized === "unlisted"
        ? "border-violet-200 bg-violet-50 text-violet-800"
        : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${className}`}>
      {visibility || "private"}
    </span>
  );
}

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
        {subtitle ? <div className="mt-1 text-sm text-slate-500">{subtitle}</div> : null}
      </div>
      {children}
    </div>
  );
}

function SummaryRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-900 break-words">{value}</div>
    </div>
  );
}

function detectIssues(form: FormState) {
  const issues: string[] = [];

  if (!form.name.trim()) issues.push("Claim name is missing.");
  if (!form.period_start.trim()) issues.push("Period start is missing.");
  if (!form.period_end.trim()) issues.push("Period end is missing.");
  if (
    form.period_start.trim() &&
    form.period_end.trim() &&
    form.period_start.trim() > form.period_end.trim()
  ) {
    issues.push("Period end is earlier than period start.");
  }

  if (!["private", "unlisted", "public"].includes(form.visibility)) {
    issues.push("Visibility value is invalid.");
  }

  return issues;
}

export default function EditClaimDraftModal({ open, claim, onClose, onSaved }: Props) {
  const { getWorkspaceRole } = useAuth();

  const [form, setForm] = useState<FormState>(() => buildInitialFormState(claim));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const workspaceRole = getWorkspaceRole(claim.workspace_id);

  useEffect(() => {
    if (open) {
      setForm(buildInitialFormState(claim));
      setError(null);
      setSaving(false);
    }
  }, [open, claim]);

  const canEdit = useMemo(() => {
    if (claim.status !== "draft") return false;
    return workspaceRole === "owner" || workspaceRole === "operator";
  }, [claim.status, workspaceRole]);

  const helperSummary = useMemo(() => {
    const includedMembers = form.included_member_ids_text.trim()
      ? form.included_member_ids_text
      : "All members in scope";

    const includedSymbols = form.included_symbols_text.trim()
      ? form.included_symbols_text.toUpperCase()
      : "All symbols in scope";

    const excludedTrades = form.excluded_trade_ids_text.trim()
      ? form.excluded_trade_ids_text
      : "No excluded trade IDs";

    return {
      includedMembers,
      includedSymbols,
      excludedTrades,
    };
  }, [
    form.included_member_ids_text,
    form.included_symbols_text,
    form.excluded_trade_ids_text,
  ]);

  const issues = useMemo(() => detectIssues(form), [form]);

  const methodologyLength = form.methodology_notes.trim().length;

  if (!open) return null;

  const setField = (key: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async () => {
    setError(null);

    if (!canEdit) {
      setError("Only workspace owners and operators can edit draft claims.");
      return;
    }

    if (!form.name.trim()) {
      setError("Claim name is required.");
      return;
    }

    if (!form.period_start.trim()) {
      setError("Period start is required.");
      return;
    }

    if (!form.period_end.trim()) {
      setError("Period end is required.");
      return;
    }

    if (form.period_start.trim() > form.period_end.trim()) {
      setError("Period end must be on or after period start.");
      return;
    }

    try {
      setSaving(true);

      const payload: ClaimSchemaUpdatePayload = {
        name: form.name.trim(),
        period_start: form.period_start.trim(),
        period_end: form.period_end.trim(),
        included_member_ids_json: parseNumberList(form.included_member_ids_text),
        included_symbols_json: parseStringList(form.included_symbols_text),
        excluded_trade_ids_json: parseNumberList(form.excluded_trade_ids_text),
        methodology_notes: form.methodology_notes,
        visibility: form.visibility,
      };

      const updated = await api.updateClaimSchema(claim.id, payload);
      await onSaved(updated);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update claim draft.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
      <div className="w-full max-w-7xl rounded-3xl border border-slate-200 bg-slate-50 shadow-2xl">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b bg-white px-6 py-5">
          <div>
            <div className="text-sm text-slate-500">Draft Claim Editor</div>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight">Edit Draft Claim</h2>
            <div className="mt-2 text-sm text-slate-500">
              Guided editing surface for claim definition, scope design, exposure controls, and methodology.
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
              role: {workspaceRole || "unknown"}
            </span>
            <span className="inline-flex rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
              status: {claim.status}
            </span>
            <VisibilityBadge visibility={form.visibility} />
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50"
            >
              Close
            </button>
          </div>
        </div>

        <div className="max-h-[82vh] overflow-y-auto px-6 py-6">
          {!canEdit && (
            <div className="mb-5 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              This claim cannot be edited in your current access state. Draft editing is limited to workspace owners and operators while the claim is still in draft status.
            </div>
          )}

          {error && (
            <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid gap-6 xl:grid-cols-[1.55fr_0.95fr]">
            <div className="space-y-5">
              <SectionCard
                title="Claim Identity"
                subtitle="Define the core identity and reporting period of the claim."
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <label className="mb-1 block text-sm font-medium text-slate-700">Claim Name</label>
                    <input
                      type="text"
                      value={form.name}
                      onChange={(e) => setField("name", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      placeholder="April Verified FX Performance"
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">Period Start</label>
                    <input
                      type="text"
                      value={form.period_start}
                      onChange={(e) => setField("period_start", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      placeholder="2026-04-01"
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">Period End</label>
                    <input
                      type="text"
                      value={form.period_end}
                      onChange={(e) => setField("period_end", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      placeholder="2026-04-30"
                    />
                  </div>
                </div>
              </SectionCard>

              <SectionCard
                title="Scope Builder"
                subtitle="Define who and what is included in the verified evidence set."
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">
                      Included Member IDs
                    </label>
                    <input
                      type="text"
                      value={form.included_member_ids_text}
                      onChange={(e) => setField("included_member_ids_text", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      placeholder="1, 2, 3"
                    />
                    <div className="mt-1 text-xs text-slate-500">
                      Leave blank to include all members in scope.
                    </div>
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">
                      Included Symbols
                    </label>
                    <input
                      type="text"
                      value={form.included_symbols_text}
                      onChange={(e) => setField("included_symbols_text", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      placeholder="EURUSD, GBPJPY, XAUUSD"
                    />
                    <div className="mt-1 text-xs text-slate-500">
                      Leave blank to include all symbols in scope.
                    </div>
                  </div>

                  <div className="sm:col-span-2">
                    <label className="mb-1 block text-sm font-medium text-slate-700">
                      Excluded Trade IDs
                    </label>
                    <input
                      type="text"
                      value={form.excluded_trade_ids_text}
                      onChange={(e) => setField("excluded_trade_ids_text", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      placeholder="101, 205, 301"
                    />
                    <div className="mt-1 text-xs text-slate-500">
                      Use this to remove specific trades from the claim set.
                    </div>
                  </div>
                </div>
              </SectionCard>

              <SectionCard
                title="Exposure Controls"
                subtitle="Control how this claim can later be exposed after lifecycle progression."
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-slate-700">Visibility</label>
                    <select
                      value={form.visibility}
                      onChange={(e) => setField("visibility", e.target.value)}
                      className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                    >
                      <option value="private">private</option>
                      <option value="unlisted">unlisted</option>
                      <option value="public">public</option>
                    </select>
                  </div>

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    <div className="font-medium text-slate-900">Visibility impact</div>
                    <div className="mt-2 space-y-1">
                      <div><span className="font-medium">private</span> → internal only</div>
                      <div><span className="font-medium">unlisted</span> → direct verify route only</div>
                      <div><span className="font-medium">public</span> → public directory + verify route</div>
                    </div>
                  </div>
                </div>
              </SectionCard>

              <SectionCard
                title="Methodology Narrative"
                subtitle="Document how the claim should be interpreted and what rules shaped it."
              >
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">
                    Methodology Notes
                  </label>
                  <textarea
                    value={form.methodology_notes}
                    onChange={(e) => setField("methodology_notes", e.target.value)}
                    className="min-h-[220px] w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                    placeholder="Describe methodology, inclusion rules, exclusions, risk framing, and interpretation notes."
                  />
                  <div className="mt-2 text-xs text-slate-500">
                    Current length: {methodologyLength} characters
                  </div>
                </div>
              </SectionCard>
            </div>

            <div className="space-y-5">
              <SectionCard
                title="Live Claim Preview"
                subtitle="This is the shape of the draft if saved now."
              >
                <div className="space-y-4 text-sm">
                  <SummaryRow label="Claim Name" value={form.name.trim() || "—"} />
                  <SummaryRow
                    label="Period"
                    value={`${form.period_start || "—"} → ${form.period_end || "—"}`}
                  />
                  <SummaryRow label="Included Members" value={helperSummary.includedMembers} />
                  <SummaryRow label="Included Symbols" value={helperSummary.includedSymbols} />
                  <SummaryRow label="Excluded Trades" value={helperSummary.excludedTrades} />
                  <SummaryRow
                    label="Visibility"
                    value={<VisibilityBadge visibility={form.visibility} />}
                  />
                </div>
              </SectionCard>

              <SectionCard
                title="Validation Check"
                subtitle="Save only when the configuration is logically consistent."
              >
                {issues.length === 0 ? (
                  <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
                    Draft configuration looks valid and ready to save.
                  </div>
                ) : (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                    <div className="font-medium">Resolve these issues first:</div>
                    <ul className="mt-2 list-disc space-y-1 pl-5">
                      {issues.map((issue) => (
                        <li key={issue}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </SectionCard>

              <SectionCard
                title="Editing Rules"
                subtitle="Lifecycle constraints that govern this editor."
              >
                <div className="space-y-2 text-sm text-slate-600">
                  <div>1. Editing is allowed only in draft state.</div>
                  <div>2. Scope changes affect the final evidence set and downstream metrics.</div>
                  <div>3. Visibility determines future public exposure routes.</div>
                  <div>4. Saving writes a claim update audit event.</div>
                </div>
              </SectionCard>

              <SectionCard
                title="Lifecycle Reminder"
                subtitle="This claim still needs governed progression after editing."
              >
                <div className="space-y-2 text-sm text-slate-600">
                  <div>Draft → Verify → Publish → Lock</div>
                  <div>
                    Once the claim leaves draft state, this editor should no longer be used.
                  </div>
                </div>
              </SectionCard>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t bg-white px-6 py-4">
          <div className="text-xs text-slate-500">
            Saving will update the draft and write a{" "}
            <span className="font-medium">claim_schema_updated</span> audit event.
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={saving || !canEdit || issues.length > 0}
              className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Draft Changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}