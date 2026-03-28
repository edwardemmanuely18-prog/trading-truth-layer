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
  methodologyNotes?: string;
  submit?: string;
};

type VisibilityOption = "private" | "unlisted" | "public";

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
        .map((x) => x.toUpperCase()),
    ),
  );
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function visibilityTone(value: VisibilityOption) {
  if (value === "public") return "border-emerald-200 bg-emerald-50 text-emerald-800";
  if (value === "unlisted") return "border-amber-200 bg-amber-50 text-amber-800";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function visibilitySummary(value: VisibilityOption) {
  if (value === "public") {
    return "Public claim directory exposure after lifecycle progression. Best for discovery and external verification.";
  }
  if (value === "unlisted") {
    return "Direct verification link exposure without public directory listing. Best for controlled sharing.";
  }
  return "Internal-only claim visibility. Best for draft review, internal governance, and pre-public testing.";
}

function splitLines(value: string) {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function Pill({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {children}
    </div>
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
  const [visibility, setVisibility] = useState<VisibilityOption>("private");

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
    (claimUsage?.limit ?? 0) > 0 && (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  const parsedIncludedMembers = useMemo(() => {
    try {
      return parseNumberListStrict(includedMembers);
    } catch {
      return [];
    }
  }, [includedMembers]);

  const parsedIncludedSymbols = useMemo(() => parseStringList(includedSymbols), [includedSymbols]);

  const parsedExcludedTradeIds = useMemo(() => {
    try {
      return parseNumberListStrict(excludedTradeIds);
    } catch {
      return [];
    }
  }, [excludedTradeIds]);

  const methodologyLines = useMemo(() => splitLines(methodologyNotes), [methodologyNotes]);

  const helperSummary = useMemo(() => {
    const members = includedMembers.trim()
      ? `${parsedIncludedMembers.length} selected`
      : "All workspace members";

    const symbols = includedSymbols.trim()
      ? `${parsedIncludedSymbols.length} selected`
      : "All symbols";

    const excluded = excludedTradeIds.trim()
      ? `${parsedExcludedTradeIds.length} excluded`
      : "No exclusions";

    return {
      members,
      symbols,
      excluded,
    };
  }, [
    includedMembers,
    includedSymbols,
    excludedTradeIds,
    parsedIncludedMembers.length,
    parsedIncludedSymbols.length,
    parsedExcludedTradeIds.length,
  ]);

  function applyPresetMarchWindow() {
    setName("March Verification Window");
    setPeriodStart("2026-03-01");
    setPeriodEnd("2026-03-31");
    setIncludedMembers("");
    setIncludedSymbols("");
    setExcludedTradeIds("");
    setVisibility("public");
    setMethodologyNotes(
      [
        "Trades imported from canonical ledger for March 2026 verification window.",
        "All instruments included.",
        "PnL measured using ledger net_pnl field.",
        "No exclusions applied.",
      ].join("\n"),
    );
    setErrors({});
    setStatus(null);
  }

  function applyPresetAprilWindow() {
    setName("April Verification Window");
    setPeriodStart("2026-04-01");
    setPeriodEnd("2026-04-30");
    setIncludedMembers("");
    setIncludedSymbols("");
    setExcludedTradeIds("");
    setVisibility("private");
    setMethodologyNotes(
      [
        "Trades imported from canonical ledger for April 2026 verification window.",
        "All instruments included.",
        "PnL measured using net_pnl field.",
        "No exclusions applied.",
      ].join("\n"),
    );
    setErrors({});
    setStatus(null);
  }

  function applyBlankTemplate() {
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

  function resetForm() {
    applyBlankTemplate();
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

    if (methodologyNotes.trim().length > 4000) {
      nextErrors.methodologyNotes = "Methodology notes are too long.";
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

  const sequence = [
    {
      step: "STEP 1",
      title: "Define Claim Identity",
      detail:
        "Set the claim name and reporting period. This anchors the record and its time-bounded verification scope.",
    },
    {
      step: "STEP 2",
      title: "Build Scope",
      detail:
        "Choose included members, symbols, and explicit exclusions so the evidence set is deterministic and reviewable.",
    },
    {
      step: "STEP 3",
      title: "Set Exposure",
      detail:
        "Choose private, unlisted, or public exposure so later lifecycle actions align with intended verification visibility.",
    },
    {
      step: "STEP 4",
      title: "Progress Lifecycle",
      detail:
        "After creation, move the draft through verify, publish, and lock to create a public trust-grade verification record.",
    },
  ];

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
          <div>
            <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700">
              Guided claim creation
            </div>

            <h2 className="mt-5 text-3xl font-bold tracking-tight text-slate-950">
              Claims Schema Builder
            </h2>

            <p className="mt-4 max-w-4xl text-base leading-8 text-slate-700">
              Define the exact scope, evidence universe, methodology, and exposure posture for a
              lifecycle-governed performance claim. This page is the structured entry point for
              creating claims that can later be verified, published, locked, and publicly audited.
            </p>

            <div className="mt-5 flex flex-wrap gap-2">
              <Pill className="border-slate-200 bg-slate-50 text-slate-700">
                draft-first workflow
              </Pill>
              <Pill className="border-slate-200 bg-slate-50 text-slate-700">
                scope-controlled evidence
              </Pill>
              <Pill className="border-slate-200 bg-slate-50 text-slate-700">
                public verification compatible
              </Pill>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-xl font-semibold text-slate-950">Session State</div>
              <div className="mt-3 text-base text-slate-700">
                Signed in and ready to create a governed draft claim.
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-xl font-semibold text-slate-950">Workspace Readiness</div>
              {usageLoading ? (
                <div className="mt-3 text-base text-slate-600">Loading claim usage…</div>
              ) : (
                <div className="mt-3 space-y-2 text-base text-slate-700">
                  <div>Workspace #{workspaceId} available for claim operations.</div>
                  <div>
                    Claim usage: {claimUsage?.used ?? 0} / {claimUsage?.limit ?? "—"}
                  </div>
                  <div>
                    Utilization:{" "}
                    {typeof claimUsage?.ratio === "number"
                      ? `${(claimUsage.ratio * 100).toFixed(1)}%`
                      : "—"}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-4">
        {sequence.map((item) => (
          <div
            key={item.step}
            className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-medium text-slate-700">
              {item.step}
            </div>
            <div className="mt-4 text-2xl font-semibold tracking-tight text-slate-950">
              {item.title}
            </div>
            <div className="mt-3 text-base leading-7 text-slate-700">{item.detail}</div>
          </div>
        ))}
      </section>

      <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h3 className="text-3xl font-bold tracking-tight text-slate-950">Create Draft Claim</h3>
            <p className="mt-3 max-w-4xl text-base leading-8 text-slate-700">
              Define the scope of a verification-ready performance claim. After creation, the draft
              will open in the internal claim view for preview, editing, verification, publishing,
              and locking.
            </p>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-base text-slate-700">
            <div className="font-medium">Workspace</div>
            <div className="mt-2 text-2xl font-semibold text-slate-950">#{workspaceId}</div>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={applyPresetMarchWindow}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base font-medium text-slate-900 hover:bg-slate-50"
          >
            Load March preset
          </button>
          <button
            type="button"
            onClick={applyPresetAprilWindow}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base font-medium text-slate-900 hover:bg-slate-50"
          >
            Load April preset
          </button>
          <button
            type="button"
            onClick={applyBlankTemplate}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base font-medium text-slate-900 hover:bg-slate-50"
          >
            Start blank
          </button>
          <button
            type="button"
            onClick={() => {
              const today = todayIso();
              setPeriodStart(today);
              setPeriodEnd(today);
              setStatus(null);
            }}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base font-medium text-slate-900 hover:bg-slate-50"
          >
            Use today
          </button>
        </div>

        {claimLimitReached ? (
          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 px-5 py-4 text-base text-amber-800">
            <div className="font-semibold">
              Current claim usage: {claimUsage?.used ?? 0} / {claimUsage?.limit ?? 0}
            </div>
            <div className="mt-2">
              Claim creation is blocked by plan policy in production, but this local UI keeps the
              form available for workflow testing.
            </div>
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="mt-6">
          <div className="grid gap-6 xl:grid-cols-[1.7fr_0.9fr_0.95fr]">
            <div className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Claim Name</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
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
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
                  />
                  {errors.periodStart ? (
                    <div className="mt-2 text-sm text-red-600">{errors.periodStart}</div>
                  ) : null}
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Period End
                  </label>
                  <input
                    type="date"
                    value={periodEnd}
                    onChange={(e) => setPeriodEnd(e.target.value)}
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
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
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
                    placeholder="201, 202, 203"
                  />
                  <div className="mt-2 text-sm text-slate-500">
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
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
                    placeholder="XAUUSD, SPX, BTCUSD"
                  />
                  <div className="mt-2 text-sm text-slate-500">
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
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
                  placeholder="1, 4, 8"
                />
                <div className="mt-2 text-sm text-slate-500">
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
                  onChange={(e) => setVisibility(e.target.value as VisibilityOption)}
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
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
                  className="min-h-[180px] w-full rounded-2xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-slate-500"
                  placeholder="Describe scope, exclusions, normalization logic, and any verification notes."
                />
                {errors.methodologyNotes ? (
                  <div className="mt-2 text-sm text-red-600">{errors.methodologyNotes}</div>
                ) : null}
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <h3 className="text-xl font-semibold text-slate-950">Draft Scope Preview</h3>

                <div className="mt-4 space-y-4 text-sm">
                  <div>
                    <div className="text-slate-500">Claim Name</div>
                    <div className="mt-1 font-medium text-slate-950">{name.trim() || "—"}</div>
                  </div>

                  <div>
                    <div className="text-slate-500">Period</div>
                    <div className="mt-1 font-medium text-slate-950">
                      {periodStart || "—"} → {periodEnd || "—"}
                    </div>
                  </div>

                  <div>
                    <div className="text-slate-500">Included Members</div>
                    <div className="mt-1 font-medium text-slate-950">{helperSummary.members}</div>
                  </div>

                  <div>
                    <div className="text-slate-500">Included Symbols</div>
                    <div className="mt-1 break-words font-medium text-slate-950">
                      {helperSummary.symbols}
                    </div>
                  </div>

                  <div>
                    <div className="text-slate-500">Excluded Trades</div>
                    <div className="mt-1 break-words font-medium text-slate-950">
                      {helperSummary.excluded}
                    </div>
                  </div>

                  <div>
                    <div className="text-slate-500">Visibility</div>
                    <div className="mt-2">
                      <Pill className={visibilityTone(visibility)}>{visibility}</Pill>
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <h3 className="text-xl font-semibold text-slate-950">Lifecycle Reminder</h3>
                <div className="mt-4 space-y-2 text-sm text-slate-700">
                  <div>1. Create draft claim</div>
                  <div>2. Review internal preview</div>
                  <div>3. Edit draft if needed</div>
                  <div>4. Verify claim</div>
                  <div>5. Publish claim</div>
                  <div>6. Lock claim</div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <h3 className="text-xl font-semibold text-slate-950">Builder Rules</h3>
                <div className="mt-3 text-sm leading-7 text-slate-700">
                  Claims should be created as drafts first. Scope and methodology should be
                  finalized before verification, because downstream lifecycle transitions depend on
                  this definition.
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <h3 className="text-xl font-semibold text-slate-950">Visibility Guidance</h3>
                <div className="mt-3 text-sm leading-7 text-slate-700">
                  {visibilitySummary(visibility)}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-4">
                <h3 className="text-xl font-semibold text-slate-950">Recommended Sequence</h3>
                <div className="mt-3 text-sm leading-7 text-slate-700">
                  Create draft → review scope → verify claim → publish claim → lock claim → review
                  public verification surface.
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-4 xl:grid-cols-[1.7fr_1.15fr]">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-xl font-semibold text-slate-950">Live Structured Summary</div>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-sm text-slate-500">Included member IDs</div>
                  <div className="mt-2 text-sm text-slate-900">
                    {parsedIncludedMembers.length > 0
                      ? parsedIncludedMembers.join(", ")
                      : "All workspace members"}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Included symbols</div>
                  <div className="mt-2 break-words text-sm text-slate-900">
                    {parsedIncludedSymbols.length > 0
                      ? parsedIncludedSymbols.join(", ")
                      : "All symbols"}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Excluded trade IDs</div>
                  <div className="mt-2 break-words text-sm text-slate-900">
                    {parsedExcludedTradeIds.length > 0
                      ? parsedExcludedTradeIds.join(", ")
                      : "No exclusions"}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-slate-500">Methodology lines</div>
                  <div className="mt-2 text-sm text-slate-900">
                    {methodologyLines.length > 0 ? methodologyLines.length : 0}
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-xl font-semibold text-slate-950">Creation Outcome</div>
              <div className="mt-3 text-sm leading-7 text-slate-700">
                The created record opens immediately in the internal claim page, where you can
                inspect evidence, verify integrity, review audit events, and progress lifecycle
                state.
              </div>
            </div>
          </div>

          {errors.submit ? (
            <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              {errors.submit}
            </div>
          ) : null}

          {status ? (
            <div className="mt-6 rounded-2xl border border-green-200 bg-green-50 px-5 py-4 text-sm text-green-700">
              {status}
            </div>
          ) : null}

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={loading}
              className="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Creating Draft..." : "Create Draft Claim"}
            </button>

            <button
              type="button"
              onClick={resetForm}
              disabled={loading}
              className="rounded-2xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-50 disabled:opacity-60"
            >
              Reset
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}