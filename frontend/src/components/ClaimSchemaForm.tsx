"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { api, type ClaimSchemaCreatePayload, type WorkspaceUsageSummary } from "../lib/api";

type Props = {
  workspaceId?: number;
};

type FormErrors = {
  name?: string;
  periodStart?: string;
  periodEnd?: string;
  includedMembers?: string;
  includedSymbols?: string;
  excludedTradeIds?: string;
  submit?: string;
};

function parseNumberListStrict(value: string): number[] {
  if (!value.trim()) return [];

  const parts = value
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);

  const parsed = parts.map((x) => Number(x));

  if (parsed.some((x) => Number.isNaN(x) || !Number.isFinite(x))) {
    throw new Error("Member IDs and excluded trade IDs must be comma-separated numbers.");
  }

  return Array.from(new Set(parsed.map((x) => Math.trunc(x))));
}

function parseStringList(value: string): string[] {
  if (!value.trim()) return [];

  return Array.from(
    new Set(
      value
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean)
        .map((x) => x.toUpperCase())
    )
  );
}

export default function ClaimSchemaForm({ workspaceId = 1 }: Props) {
  const router = useRouter();

  const [name, setName] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [includedMembers, setIncludedMembers] = useState("");
  const [includedSymbols, setIncludedSymbols] = useState("");
  const [excludedTradeIds, setExcludedTradeIds] = useState("");
  const [methodologyNotes, setMethodologyNotes] = useState("");
  const [visibility, setVisibility] = useState("private");

  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(true);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(workspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setUsageLoading(false);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId]);

  const claimUsage = usage?.usage?.claims;
  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 &&
    (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  const helperSummary = useMemo(() => {
    const members = includedMembers.trim() ? includedMembers : "All workspace members";
    const symbols = includedSymbols.trim() ? includedSymbols.toUpperCase() : "All symbols";
    const excluded = excludedTradeIds.trim() ? excludedTradeIds : "No exclusions";

    return {
      members,
      symbols,
      excluded,
    };
  }, [includedMembers, includedSymbols, excludedTradeIds]);

  function resetForm() {
    setName("");
    setPeriodStart("");
    setPeriodEnd("");
    setIncludedMembers("");
    setIncludedSymbols("");
    setExcludedTradeIds("");
    setMethodologyNotes("");
    setVisibility("private");
    setErrors({});
    setStatus(null);
  }

  function validateForm(): FormErrors {
    const nextErrors: FormErrors = {};

    if (!name.trim()) {
      nextErrors.name = "Claim name is required.";
    }

    if (!periodStart.trim()) {
      nextErrors.periodStart = "Period start is required.";
    }

    if (!periodEnd.trim()) {
      nextErrors.periodEnd = "Period end is required.";
    }

    if (periodStart && periodEnd && periodStart > periodEnd) {
      nextErrors.periodEnd = "Period end must be on or after period start.";
    }

    try {
      parseNumberListStrict(includedMembers);
    } catch (error) {
      nextErrors.includedMembers =
        error instanceof Error ? error.message : "Invalid included member list.";
    }

    try {
      parseNumberListStrict(excludedTradeIds);
    } catch (error) {
      nextErrors.excludedTradeIds =
        error instanceof Error ? error.message : "Invalid excluded trade list.";
    }

    const parsedSymbols = parseStringList(includedSymbols);
    if (parsedSymbols.some((symbol) => symbol.length > 32)) {
      nextErrors.includedSymbols = "Each included symbol must be reasonably short.";
    }

    return nextErrors;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus(null);

    const nextErrors = validateForm();
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setLoading(true);

    try {
      const payload: ClaimSchemaCreatePayload = {
        workspace_id: workspaceId,
        name: name.trim(),
        period_start: periodStart.trim(),
        period_end: periodEnd.trim(),
        included_member_ids_json: parseNumberListStrict(includedMembers),
        included_symbols_json: parseStringList(includedSymbols),
        excluded_trade_ids_json: parseNumberListStrict(excludedTradeIds),
        methodology_notes: methodologyNotes.trim(),
        visibility,
      };

      const created = await api.createClaimSchema(payload);

      setStatus(`Draft claim created successfully. Redirecting to claim #${created.id}...`);

      router.push(`/workspace/${workspaceId}/claim/${created.id}`);
      router.refresh();
    } catch (err) {
      setErrors((prev) => ({
        ...prev,
        submit: err instanceof Error ? err.message : "Failed to create claim schema.",
      }));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">Create Draft Claim</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            Define the scope of a verification-ready performance claim. After creation, the draft
            will open in the internal claim view for preview, editing, verification, publishing,
            and locking.
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
          <div className="font-medium">Workspace</div>
          <div className="mt-1">#{workspaceId}</div>
        </div>
      </div>

      {usageLoading ? (
        <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
          Loading claim usage...
        </div>
      ) : claimLimitReached ? (
        <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <div className="font-medium">
            Current claim usage: {claimUsage?.used ?? 0} / {claimUsage?.limit ?? 0}
          </div>
          <div className="mt-1">
            Utilization: {typeof claimUsage?.ratio === "number" ? `${(claimUsage.ratio * 100).toFixed(1)}%` : "—"}
          </div>
          <div className="mt-2">
            Claim creation is blocked by plan policy in production, but this local UI keeps the form
            available for workflow testing.
          </div>
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="space-y-6">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Claim Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                placeholder="March Verification Window"
              />
              {errors.name ? <div className="mt-2 text-sm text-red-600">{errors.name}</div> : null}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Period Start
                </label>
                <input
                  type="date"
                  value={periodStart}
                  onChange={(e) => setPeriodStart(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                />
                {errors.periodStart ? (
                  <div className="mt-2 text-sm text-red-600">{errors.periodStart}</div>
                ) : null}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Period End</label>
                <input
                  type="date"
                  value={periodEnd}
                  onChange={(e) => setPeriodEnd(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                />
                {errors.periodEnd ? (
                  <div className="mt-2 text-sm text-red-600">{errors.periodEnd}</div>
                ) : null}
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Included Member IDs
                </label>
                <input
                  value={includedMembers}
                  onChange={(e) => setIncludedMembers(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                  placeholder="201, 202, 203"
                />
                <div className="mt-2 text-xs text-slate-500">
                  Leave blank to include all members in workspace scope.
                </div>
                {errors.includedMembers ? (
                  <div className="mt-2 text-sm text-red-600">{errors.includedMembers}</div>
                ) : null}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Included Symbols
                </label>
                <input
                  value={includedSymbols}
                  onChange={(e) => setIncludedSymbols(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                  placeholder="XAUUSD, SPX, BTCUSD"
                />
                <div className="mt-2 text-xs text-slate-500">
                  Symbols are normalized to uppercase automatically.
                </div>
                {errors.includedSymbols ? (
                  <div className="mt-2 text-sm text-red-600">{errors.includedSymbols}</div>
                ) : null}
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Excluded Trade IDs
              </label>
              <input
                value={excludedTradeIds}
                onChange={(e) => setExcludedTradeIds(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                placeholder="1, 4, 8"
              />
              <div className="mt-2 text-xs text-slate-500">
                Use exclusions to remove specific ledger rows from the claim set.
              </div>
              {errors.excludedTradeIds ? (
                <div className="mt-2 text-sm text-red-600">{errors.excludedTradeIds}</div>
              ) : null}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Visibility</label>
              <select
                value={visibility}
                onChange={(e) => setVisibility(e.target.value)}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
              >
                <option value="private">Private</option>
                <option value="unlisted">Unlisted</option>
                <option value="public">Public</option>
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Methodology Notes
              </label>
              <textarea
                value={methodologyNotes}
                onChange={(e) => setMethodologyNotes(e.target.value)}
                className="min-h-[160px] w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-slate-500"
                placeholder="Describe scope, exclusions, normalization logic, and any verification notes."
              />
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="text-sm font-semibold text-slate-900">Draft Scope Preview</h3>

              <div className="mt-4 space-y-3 text-sm">
                <div>
                  <div className="text-slate-500">Claim Name</div>
                  <div className="mt-1 font-medium">{name.trim() || "—"}</div>
                </div>

                <div>
                  <div className="text-slate-500">Period</div>
                  <div className="mt-1 font-medium">
                    {periodStart || "—"} → {periodEnd || "—"}
                  </div>
                </div>

                <div>
                  <div className="text-slate-500">Included Members</div>
                  <div className="mt-1 font-medium">{helperSummary.members}</div>
                </div>

                <div>
                  <div className="text-slate-500">Included Symbols</div>
                  <div className="mt-1 font-medium break-words">{helperSummary.symbols}</div>
                </div>

                <div>
                  <div className="text-slate-500">Excluded Trades</div>
                  <div className="mt-1 font-medium break-words">{helperSummary.excluded}</div>
                </div>

                <div>
                  <div className="text-slate-500">Visibility</div>
                  <div className="mt-1 font-medium capitalize">{visibility}</div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-4">
              <h3 className="text-sm font-semibold text-slate-900">Lifecycle Reminder</h3>
              <div className="mt-3 space-y-2 text-sm text-slate-600">
                <div>1. Create draft claim</div>
                <div>2. Review internal preview</div>
                <div>3. Edit draft if needed</div>
                <div>4. Verify claim</div>
                <div>5. Publish claim</div>
                <div>6. Lock claim</div>
              </div>
            </div>
          </div>
        </div>

        {errors.submit ? (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errors.submit}
          </div>
        ) : null}

        {status ? (
          <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
            {status}
          </div>
        ) : null}

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={loading}
            className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Creating Draft..." : "Create Draft Claim"}
          </button>

          <button
            type="button"
            onClick={resetForm}
            disabled={loading}
            className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-50 disabled:opacity-60"
          >
            Reset
          </button>
        </div>
      </form>
    </div>
  );
}