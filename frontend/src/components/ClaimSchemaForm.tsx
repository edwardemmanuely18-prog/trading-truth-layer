"use client";

import {
  useRouter,
  useSearchParams,
} from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  api,
  getApiErrorCode,
  isApiError,
  type ClaimSchemaCreatePayload,
  type WorkspaceUsageSummary,
} from "../lib/api";
import PaywallModal from "./PaywallModal";
import { useWorkspaceGate } from "../hooks/useWorkspaceGate";

type Props = {
  workspaceId: number;
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

type VisibilityOption = "private";

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


function visibilitySummary() {
  return (
    "Draft claims always begin as private records. " +
    "Published claims become unlisted verification records. " +
    "Locked claims become public trust-grade records."
  );
}

function splitLines(value: string) {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function Pill({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {children}
    </div>
  );
}

function getPlanName(usage?: WorkspaceUsageSummary | null, planCode?: string | null) {
  const normalized = normalizeText(planCode);
  const matched = usage?.plan_catalog?.find((plan) => normalizeText(plan.code) === normalized);
  return matched?.name || planCode || "current plan";
}

export default function ClaimSchemaForm({ workspaceId }: Props) {
  if (!workspaceId) {
    return (
      <section className="rounded-3xl border border-red-200 bg-red-50 p-6">
        <h3 className="text-lg font-semibold text-red-700">
          Workspace context required
        </h3>

        <p className="mt-2 text-sm text-red-600">
          Claim creation requires an active workspace context.
        </p>
      </section>
    );
  }

  const router = useRouter();
  const searchParams =
    useSearchParams();

  const template =
    searchParams.get("template");

  const templateId =
    searchParams.get("templateId");

  const presetId =
    searchParams.get("presetId");

  const mode =
    searchParams.get("mode");

  const isTemplateMode =
    mode === "create-template";
  const { paywallState, closePaywall, openPaywall, gateAndExecute } = useWorkspaceGate();

  const [name, setName] = useState("");
  const [periodStart, setPeriodStart] = useState("");
  const [periodEnd, setPeriodEnd] = useState("");
  const [includedMembers, setIncludedMembers] = useState("");
  const [includedSymbols, setIncludedSymbols] = useState("");
  const [excludedTradeIds, setExcludedTradeIds] = useState("");
  const [methodologyNotes, setMethodologyNotes] = useState("");
  const visibility: VisibilityOption =
    "private";

  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(true);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [errors, setErrors] = useState<FormErrors>({});
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {

    if (template === "monthly") {
      applyMonthlyTemplate();
    }

    if (template === "quarterly") {
      applyQuarterlyTemplate();
    }

    if (template === "annual") {
      applyAnnualTemplate();
    }

  }, [template]);

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

  useEffect(() => {

    if (!templateId) return;

    async function loadTemplate() {

      try {

        const tpl =
          await api.getClaimTemplate(
            Number(templateId)
          );

        setName(
          tpl.name || ""
        );

        setIncludedMembers(
          tpl.included_member_ids_json
            ?.join(", ") || ""
        );

        setIncludedSymbols(
          tpl.included_symbols_json
            ?.join(", ") || ""
        );

        setExcludedTradeIds(
          tpl.excluded_trade_ids_json
            ?.join(", ") || ""
        );

        setMethodologyNotes(
          tpl.methodology_notes || ""
        );

      } catch (err) {

        console.error(
          "Failed to load template",
          err
        );

      }

    }

    loadTemplate();

  }, [templateId]);

  useEffect(() => {

    if (!presetId) return;

    async function loadPreset() {

      try {

        const presets =
          await api.getClaimPresets(
            workspaceId
          ) as any[];

        const preset =
          presets.find(
            (p: any) =>
              String(p.id) ===
              presetId
          );

        if (!preset) return;

        setName(
          preset.name || ""
        );

        setMethodologyNotes(
          preset.methodology_notes || ""
        );

      } catch (err) {

        console.error(err);

      }

    }

    loadPreset();

  }, [
    presetId,
    workspaceId,
  ]);

  const configuredPlanName = getPlanName(
    usage,
    usage?.governance?.configured_plan_code || usage?.plan_code,
  );
  const effectivePlanName = getPlanName(
    usage,
    usage?.governance?.effective_plan_code || usage?.effective_plan_code,
  );
  const billingActivationRecommended = Boolean(usage?.governance?.billing_activation_recommended);
  const recommendedPlanName =
    usage?.upgrade_recommendation?.recommended_plan_name || configuredPlanName;

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

  function applyMonthlyTemplate() {

    const now = new Date();

    const year =
      now.getFullYear();

    const month =
      now.getMonth();

    const start =
      new Date(year, month, 1);

    const end =
      new Date(year, month + 1, 0);

    setName(
      `${start.toLocaleString("default", {
        month: "long",
      })} Verification Window`
    );

    setPeriodStart(
      start.toISOString().slice(0,10)
    );

    setPeriodEnd(
      end.toISOString().slice(0,10)
    );

    setIncludedSymbols("");

    setIncludedMembers("");

    setExcludedTradeIds("");

    setMethodologyNotes(
  `Monthly performance verification.

  All symbols included.

  Canonical ledger source.

  Workspace verification workflow.`
    );
  }

  function applyQuarterlyTemplate() {

    const now =
      new Date();

    const quarter =
      Math.floor(now.getMonth()/3);

    const start =
      new Date(
        now.getFullYear(),
        quarter * 3,
        1
      );

    const end =
      new Date(
        now.getFullYear(),
        quarter * 3 + 3,
        0
      );

    setName(
      `Q${quarter + 1} Verification`
    );

    setPeriodStart(
      start.toISOString().slice(0,10)
    );

    setPeriodEnd(
      end.toISOString().slice(0,10)
    );

    setIncludedSymbols("");

    setIncludedMembers("");

    setExcludedTradeIds("");

    setMethodologyNotes(
  `Quarterly institutional review.

  Governance checkpoint.

  Verification workflow enabled.`
    );
  }

  function applyAnnualTemplate() {

    const year =
      new Date().getFullYear();

    setName(
      `${year} Annual Verification`
    );

    setPeriodStart(
      `${year}-01-01`
    );

    setPeriodEnd(
      `${year}-12-31`
    );

    setIncludedSymbols("");

    setIncludedMembers("");

    setExcludedTradeIds("");

    setMethodologyNotes(
  `Annual trust-grade verification.

  Institutional governance review.

  Full-year performance scope.`
    );
  }

  function applyBlankTemplate() {
    setName("");
    setPeriodStart("");
    setPeriodEnd("");
    setIncludedMembers("");
    setIncludedSymbols("");
    setExcludedTradeIds("");
    setMethodologyNotes("");
    setErrors({});
    setStatus(null);
  }

  function resetForm() {
    applyBlankTemplate();
  }

  function validateForm(): FormErrors {
    const nextErrors: FormErrors = {};

    if (!name.trim()) nextErrors.name = "Claim name is required.";
    if (!periodStart.trim()) nextErrors.periodStart = "Period start is required.";
    if (!periodEnd.trim()) nextErrors.periodEnd = "Period end is required.";

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

  async function submitCreateClaim() {
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
  }

  async function submitCreateTemplate() {

    await api.createClaimTemplate({

      workspace_id: workspaceId,

      name: name.trim(),

      description: methodologyNotes.trim(),

      template_type: "custom",

      included_member_ids_json:
        parseNumberListStrict(
          includedMembers
        ),

      included_symbols_json:
        parseStringList(
          includedSymbols
        ),

      excluded_trade_ids_json:
        parseNumberListStrict(
          excludedTradeIds
        ),

      methodology_notes:
        methodologyNotes.trim(),

      visibility: "private",

      active: true,

    });

    setStatus(
      "Template saved successfully."
    );

    router.push(
      `/workspace/${workspaceId}/claim-templates`
    );

  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus(null);

    const nextErrors = validateForm();
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) return;

    setLoading(true);

    try {
      await gateAndExecute(
        {
          action: "create_claim_version",
          usage,
          workspaceRole: "owner",
        },
        async () => {
          if (isTemplateMode) {

            await submitCreateTemplate();

          } else {

            await submitCreateClaim();

          }
        },
      );
    } catch (err) {
      if (isApiError(err) && err.status === 403) {
        const errorCode = getApiErrorCode(err);

        if (errorCode === "claim_limit_reached") {
          openPaywall({
            reason: "claim_limit_reached",
            actionLabel: "Create draft claim",
            message:
              err.payload?.message ||
              err.payload?.upgrade_hint ||
              "This workspace has reached its total claim limit for the current plan. Upgrade your plan to create more claims.",
          });
          return;
        }

        openPaywall({
          reason: "feature_locked",
          actionLabel: "Create draft claim",
          message:
            err.payload?.message ||
            err.message ||
            "Claim creation is currently blocked for this workspace.",
        });
        return;
      }

      setErrors((prev) => ({
        ...prev,
        submit: err instanceof Error ? err.message : "Failed to create claim schema.",
      }));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <section className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm md:p-7">
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <h3
              className="text-3xl font-bold tracking-tight text-slate-950 md:text-[2.1rem]"
            >
              {
                isTemplateMode
                  ? "Create Claim Template"
                  : "Create Draft Claim"
              }
            </h3>
            <p className="mt-3 max-w-4xl text-base leading-8 text-slate-700">
              {
                isTemplateMode
                  ? (
                    "Create a reusable template that can be applied repeatedly to generate standardized claim drafts."
                  )
                  : (
                    "Define the scope of a verification-ready performance claim. After creation, the draft opens in the internal claim view for review, verification, publishing, and locking."
                  )
              }
            </p>
          </div>

          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-base text-slate-700 shadow-sm">
            <div className="font-medium">Workspace</div>
            <div className="mt-2 text-2xl font-semibold text-slate-950">#{workspaceId}</div>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={applyPresetMarchWindow}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
          >
            Load March preset
          </button>
          <button
            type="button"
            onClick={applyPresetAprilWindow}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
          >
            Load April preset
          </button>
          <button
            type="button"
            onClick={applyBlankTemplate}
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
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
            className="rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
          >
            Use today
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-6">
          <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">
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
                  <label className="mb-2 block text-sm font-medium text-slate-700">Period Start</label>
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
                  <label className="mb-2 block text-sm font-medium text-slate-700">Period End</label>
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
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Initial Visibility
                </label>

                <div className="rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-base font-medium text-slate-700">
                  Private (Draft Default)
                </div>

                <div className="mt-2 text-sm text-slate-500">
                  Draft claims always begin as private records. Visibility is automatically promoted through lifecycle progression.
                </div>
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
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                <h3 className="text-xl font-semibold text-slate-950">Draft Scope Preview</h3>

                <div className="mt-4 space-y-4 text-sm leading-6">
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
                      <Pill className="border-slate-200 bg-slate-50 text-slate-700">
                        private
                      </Pill>
                    </div>
                  </div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-5">
                <h3 className="text-xl font-semibold text-slate-950">Builder Guidance</h3>
                <div className="mt-3 space-y-3 text-sm leading-7 text-slate-700">
                  <p>
                    Claims should be created as drafts first. Scope and methodology should be
                    finalized before verification because downstream lifecycle transitions depend on
                    this definition.
                  </p>
                  <p>
                    Recommended sequence: Create draft → review scope → verify claim → publish claim
                    → lock claim → review public verification surface.
                  </p>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-5">
                <h3 className="text-xl font-semibold text-slate-950">Visibility Guidance</h3>
                <div className="mt-3 text-sm leading-7 text-slate-700">
                  {visibilitySummary()}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-5">
                <h3 className="text-xl font-semibold text-slate-950">Lifecycle Reminder</h3>
                <div className="mt-4 space-y-2.5 text-sm leading-6 text-slate-700">
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

          <div className="mt-6 grid gap-5 xl:grid-cols-[1.7fr_1fr]">
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
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

            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-xl font-semibold text-slate-950">
                {
                  isTemplateMode
                    ? (
                      "The template is stored in the workspace template registry and can be reused to generate future claim drafts."
                    )
                    : (
                      "The created record opens immediately in the internal claim page, where you can inspect evidence, verify integrity, review audit events, and progress lifecycle state."
                    )
                }
              </div>
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

          <div className="mt-7 flex flex-wrap items-center gap-3 border-t border-slate-200 pt-5">
            <button
              type="submit"
              disabled={loading || usageLoading}
              className="rounded-2xl bg-slate-900 px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {
                loading
                  ? "Creating Draft..."
                  : (
                      isTemplateMode
                        ? "Save Template"
                        : "Create Draft Claim"
                    )
              }
            </button>

            <button
              type="button"
              onClick={resetForm}
              disabled={loading}
              className="rounded-2xl border border-slate-300 bg-white px-5 py-3.5 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:opacity-60"
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      <PaywallModal
        open={paywallState.open}
        onClose={closePaywall}
        reason={paywallState.reason}
        actionLabel={paywallState.actionLabel || "Create draft claim"}
        message={paywallState.message}
        currentPlanName={configuredPlanName}
        currentPlanCode={usage?.plan_code || null}
        usageLabel={`Plan: ${effectivePlanName}`}
        recommendedPlanName={billingActivationRecommended ? configuredPlanName : recommendedPlanName}
        onUpgrade={() => {
          router.push(`/workspace/${workspaceId}/settings?tab=billing`);
        }}
      />
    </>
  );
}