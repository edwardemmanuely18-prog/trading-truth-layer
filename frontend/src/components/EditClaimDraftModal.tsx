"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type ClaimSchema, type ClaimSchemaUpdatePayload } from "../lib/api";

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

  return Array.from(new Set(parsed));
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

export default function EditClaimDraftModal({ open, claim, onClose, onSaved }: Props) {
  const [form, setForm] = useState<FormState>(() => buildInitialFormState(claim));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setForm(buildInitialFormState(claim));
      setError(null);
      setSaving(false);
    }
  }, [open, claim]);

  const canEdit = useMemo(() => claim.status === "draft", [claim.status]);

  if (!open) return null;

  const setField = (key: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async () => {
    setError(null);

    if (!canEdit) {
      setError("Only draft claims can be edited.");
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
      <div className="w-full max-w-3xl rounded-2xl border bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-xl font-semibold">Edit Draft Claim</h2>
            <div className="mt-1 text-sm text-slate-500">
              Safe editing is available only while the claim is in draft status.
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Close
          </button>
        </div>

        <div className="max-h-[80vh] overflow-y-auto px-6 py-5">
          {!canEdit && (
            <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              This claim is no longer editable because its status is <strong>{claim.status}</strong>.
            </div>
          )}

          {error && (
            <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">Claim Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setField("name", e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                placeholder="March verified FX performance"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Period Start</label>
              <input
                type="text"
                value={form.period_start}
                onChange={(e) => setField("period_start", e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                placeholder="2026-03-01"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Period End</label>
              <input
                type="text"
                value={form.period_end}
                onChange={(e) => setField("period_end", e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                placeholder="2026-03-31"
              />
            </div>

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
                placeholder="XAUUSD, EURUSD, BTCUSD"
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

            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Methodology Notes
              </label>
              <textarea
                value={form.methodology_notes}
                onChange={(e) => setField("methodology_notes", e.target.value)}
                className="min-h-[140px] w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                placeholder="Describe methodology, filters, exclusions, and interpretation notes."
              />
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-t px-6 py-4">
          <div className="text-xs text-slate-500">
            Saving will update the draft and write a <span className="font-medium">claim_schema_updated</span> audit event.
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
              disabled={saving || !canEdit}
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
