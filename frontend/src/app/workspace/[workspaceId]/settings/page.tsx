"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import { useAuth } from "../../../../components/AuthProvider";
import {
  api,
  type BillingCheckoutResponse,
  type BillingPortalResponse,
  type PlanCatalogItem,
  type WorkspaceBillingFoundation,
  type WorkspaceSettings,
  type WorkspaceUsageSummary,
} from "../../../../lib/api";

const PLAN_ORDER = ["starter", "pro", "growth", "business"] as const;

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatUsd(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `$${Number(value).toLocaleString()}`;
}

function isOverLimit(used?: number, limit?: number) {
  if (used === undefined || limit === undefined) return false;
  if (limit <= 0) return false;
  return used > limit;
}

function isAtOrOverLimit(used?: number, limit?: number) {
  if (used === undefined || limit === undefined) return false;
  if (limit <= 0) return false;
  return used >= limit;
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function formatDimensionLabel(value: string) {
  switch (value) {
    case "storage_mb":
      return "Storage";
    case "claims":
      return "Claims";
    case "trades":
      return "Trades";
    case "members":
      return "Members";
    default:
      return value;
  }
}

function formatPlanCodeLabel(value?: string | null) {
  const normalized = normalizeText(value);
  if (!normalized) return "Starter";
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function formatBooleanLabel(value?: boolean) {
  return value ? "yes" : "no";
}

function getNextPlanCode(planCode?: string | null): string | null {
  const normalized = normalizeText(planCode);
  const index = PLAN_ORDER.findIndex((item) => item === normalized);
  if (index < 0) return null;
  return PLAN_ORDER[index + 1] ?? null;
}

function getPlanFromCatalog(
  planCatalog: PlanCatalogItem[],
  planCode?: string | null
): PlanCatalogItem | null {
  const normalized = normalizeText(planCode);
  return planCatalog.find((item) => normalizeText(item.code) === normalized) ?? null;
}

function getUsageRatio(used?: number, limit?: number): number | null {
  if (used === undefined || limit === undefined || limit <= 0) return null;
  return used / limit;
}

function isNearLimit(used?: number, limit?: number): boolean {
  const ratio = getUsageRatio(used, limit);
  if (ratio === null) return false;
  return ratio >= 0.8 && ratio <= 1;
}

function PlanBadge({ plan }: { plan?: string | null }) {
  const normalized = normalizeText(plan);

  const className =
    normalized === "pro" || normalized === "growth" || normalized === "business" || normalized === "team"
      ? "border-blue-200 bg-blue-50 text-blue-800"
      : "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {plan || "starter"}
    </span>
  );
}

function BillingBadge({ status }: { status?: string | null }) {
  const normalized = normalizeText(status);

  const className =
    normalized === "active"
      ? "border-green-200 bg-green-50 text-green-800"
      : normalized === "pending_manual_review"
        ? "border-blue-200 bg-blue-50 text-blue-800"
        : normalized === "past_due" || normalized === "trialing"
          ? "border-amber-200 bg-amber-50 text-amber-800"
          : normalized === "canceled"
            ? "border-red-200 bg-red-50 text-red-800"
            : "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {status || "inactive"}
    </span>
  );
}

function UsageCard({
  label,
  used,
  limit,
  ratio,
  atOrOver,
  hint,
}: {
  label: string;
  used?: number;
  limit?: number;
  ratio?: number | null;
  atOrOver: boolean;
  hint?: string;
}) {
  const safeUsed = used ?? 0;
  const safeLimit = limit ?? 0;
  const numericRatio =
    typeof ratio === "number" && Number.isFinite(ratio)
      ? Math.max(0, Math.min(1, ratio))
      : safeLimit > 0
        ? Math.max(0, Math.min(1, safeUsed / safeLimit))
        : 0;

  return (
    <div
      className={`rounded-2xl border p-4 ${
        atOrOver ? "border-amber-200 bg-amber-50" : "border-slate-200 bg-slate-50"
      }`}
    >
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-xl font-semibold">
        {safeUsed} / {safeLimit}
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white">
        <div
          className={`h-full rounded-full ${atOrOver ? "bg-amber-400" : "bg-slate-900"}`}
          style={{ width: `${numericRatio * 100}%` }}
        />
      </div>
      <div className="mt-2 text-sm text-slate-500">Utilization: {formatPercent(ratio)}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  const textValue = String(value);

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div
        className={`mt-2 break-words font-semibold text-slate-900 ${
          textValue.length > 24 ? "text-lg leading-7" : "text-2xl"
        }`}
      >
        {textValue}
      </div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

function PriceCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-xl font-semibold text-slate-900">{value}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

function PlanCard({
  plan,
  configuredPlanCode,
  effectivePlanCode,
  selectedPlanCode,
  onSelect,
}: {
  plan: PlanCatalogItem;
  configuredPlanCode?: string | null;
  effectivePlanCode?: string | null;
  selectedPlanCode?: string | null;
  onSelect: (planCode: string) => void;
}) {
  const isConfigured = normalizeText(plan.code) === normalizeText(configuredPlanCode);
  const isEffective = normalizeText(plan.code) === normalizeText(effectivePlanCode);
  const isSelected = normalizeText(plan.code) === normalizeText(selectedPlanCode);

  const monthlyPrice = plan.billing?.monthly_price_usd;
  const annualPrice = plan.billing?.annual_price_usd;

  return (
    <div
      className={`rounded-2xl border p-5 shadow-sm ${
        isSelected
          ? "border-blue-300 bg-blue-50 text-slate-900"
          : isConfigured
            ? "border-slate-900 bg-slate-900 text-white"
            : "border-slate-200 bg-white text-slate-900"
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <div className="text-lg font-semibold">{plan.name}</div>
        {isConfigured ? (
          <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold">
            configured
          </span>
        ) : null}
        {isEffective && !isConfigured ? (
          <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
            effective
          </span>
        ) : null}
        {isSelected ? (
          <span className="rounded-full border border-blue-300 bg-white px-3 py-1 text-xs font-semibold text-blue-800">
            selected
          </span>
        ) : null}
      </div>

      <p className={`mt-2 text-sm ${isConfigured && !isSelected ? "text-slate-200" : "text-slate-600"}`}>
        {plan.description}
      </p>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className={`rounded-xl p-3 ${isConfigured && !isSelected ? "bg-white/10" : "bg-slate-50"}`}>
          <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
            Monthly
          </div>
          <div className="mt-1 font-semibold">{formatUsd(monthlyPrice)}</div>
        </div>
        <div className={`rounded-xl p-3 ${isConfigured && !isSelected ? "bg-white/10" : "bg-slate-50"}`}>
          <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
            Annual
          </div>
          <div className="mt-1 font-semibold">{formatUsd(annualPrice)}</div>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className={`rounded-xl p-3 ${isConfigured && !isSelected ? "bg-white/10" : "bg-slate-50"}`}>
          <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
            Claims
          </div>
          <div className="mt-1 font-semibold">{plan.limits.claim_limit}</div>
        </div>
        <div className={`rounded-xl p-3 ${isConfigured && !isSelected ? "bg-white/10" : "bg-slate-50"}`}>
          <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
            Trades
          </div>
          <div className="mt-1 font-semibold">{plan.limits.trade_limit}</div>
        </div>
        <div className={`rounded-xl p-3 ${isConfigured && !isSelected ? "bg-white/10" : "bg-slate-50"}`}>
          <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
            Members
          </div>
          <div className="mt-1 font-semibold">{plan.limits.member_limit}</div>
        </div>
        <div className={`rounded-xl p-3 ${isConfigured && !isSelected ? "bg-white/10" : "bg-slate-50"}`}>
          <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
            Storage MB
          </div>
          <div className="mt-1 font-semibold">{plan.limits.storage_limit_mb}</div>
        </div>
      </div>

      <div className="mt-4">
        <div className={`text-xs ${isConfigured && !isSelected ? "text-slate-300" : "text-slate-500"}`}>
          Recommended for
        </div>
        <div className="mt-2 flex flex-wrap gap-2">
          {plan.recommended_for.map((item) => (
            <span
              key={`${plan.code}-${item}`}
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                isConfigured && !isSelected ? "bg-white/10 text-slate-100" : "bg-slate-100 text-slate-700"
              }`}
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {!isSelected ? (
        <div className="mt-5">
          <button
            type="button"
            onClick={() => onSelect(plan.code)}
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-slate-50"
          >
            Select Plan
          </button>
        </div>
      ) : null}
    </div>
  );
}

function ManualPaymentCard({
  billingFoundation,
  selectedPlanCode,
  selectedBillingCycle,
}: {
  billingFoundation: WorkspaceBillingFoundation | null;
  selectedPlanCode: string;
  selectedBillingCycle: string;
}) {
  const details = billingFoundation?.manual_payment_details ?? null;
  const manualBilling = billingFoundation?.manual_billing ?? null;

  if (!manualBilling?.enabled || !details) {
    return null;
  }

  return (
    <div className="rounded-3xl border border-blue-200 bg-blue-50 p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-blue-950">Manual Payment Instructions</h2>
          <p className="mt-1 text-sm text-blue-900">
            Stripe is not active for this deployment. Subscribers should pay manually using the
            details below, then you verify payment and activate access internally.
          </p>
        </div>

        <span className="rounded-full border border-blue-300 bg-white px-3 py-1 text-xs font-semibold text-blue-800">
          Manual billing active
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Payment Method</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {details.payment_method || "Bank transfer"}
          </div>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Selected Billing Target</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {formatPlanCodeLabel(selectedPlanCode)} · {formatPlanCodeLabel(selectedBillingCycle)}
          </div>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Account Name</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {details.account_name || "—"}
          </div>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Account Number</div>
          <div className="mt-1 break-all font-mono text-lg font-semibold text-slate-900">
            {details.account_number || "—"}
          </div>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Bank Name</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {details.bank_name || "—"}
          </div>
        </div>

        <div className="rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Phone Number</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {details.phone_number || "—"}
          </div>
        </div>
      </div>

      {details.notes ? (
        <div className="mt-4 rounded-2xl border border-blue-200 bg-white p-4">
          <div className="text-sm text-slate-500">Payment Notes</div>
          <div className="mt-2 whitespace-pre-wrap text-sm text-slate-700">{details.notes}</div>
        </div>
      ) : null}

      <div className="mt-4 rounded-2xl border border-blue-200 bg-white p-4 text-sm text-slate-700">
        After receiving payment, update the subscriber workspace internally and grant the correct
        paid plan access.
      </div>
    </div>
  );
}

function resolvePrimaryBillingAction(params: {
  configuredPlanCode: string;
  selectedPlanCode: string;
  billingStatus?: string | null;
  canSeeUpgrade: boolean;
  checkoutLoading: boolean;
  billingStatusIsPaid?: boolean;
}) {
  const {
    configuredPlanCode,
    selectedPlanCode,
    billingStatus,
    canSeeUpgrade,
    checkoutLoading,
    billingStatusIsPaid,
  } = params;

  const configured = normalizeText(configuredPlanCode);
  const selected = normalizeText(selectedPlanCode);
  const billing = normalizeText(billingStatus);

  const paidPlan = configured !== "starter";
  const billingInactive =
    billingStatusIsPaid === undefined ? !["active", "trialing"].includes(billing) : !billingStatusIsPaid;

  let label = "Upgrade Workspace";
  let helper: string | null = null;
  let disabled = !canSeeUpgrade || checkoutLoading;

  if (paidPlan && billingInactive) {
    if (selected === configured) {
      label = "Activate Billing";
      helper = "Complete billing for the currently configured paid workspace tier.";
      disabled = !canSeeUpgrade || checkoutLoading;
    } else if (PLAN_ORDER.findIndex((p) => p === selected) > PLAN_ORDER.findIndex((p) => p === configured)) {
      label = "Upgrade and Activate";
      helper = "Move to a higher commercial tier and start billing for that upgraded plan.";
      disabled = !canSeeUpgrade || checkoutLoading;
    } else {
      label = "Change Billing Target";
      helper = "Select a different target tier before starting checkout.";
      disabled = !canSeeUpgrade || checkoutLoading;
    }
  } else if (selected === configured) {
    label = "Current Plan Selected";
    helper = "Choose a different plan to start a new upgrade checkout.";
    disabled = true;
  }

  return { label, helper, disabled };
}

function UpgradeSummaryPanel({
  workspaceId,
  settings,
  usage,
  billingFoundation,
  planCatalog,
  configuredPlanItem,
  selectedPlanCode,
  selectedBillingCycle,
  canSeeUpgrade,
  onStartCheckout,
  onReturnToClaims,
  checkoutLoading,
}: {
  workspaceId: number;
  settings: WorkspaceSettings | null;
  usage: WorkspaceUsageSummary | null;
  billingFoundation: WorkspaceBillingFoundation | null;
  planCatalog: PlanCatalogItem[];
  configuredPlanItem: PlanCatalogItem | null;
  selectedPlanCode: string;
  selectedBillingCycle: string;
  canSeeUpgrade: boolean;
  onStartCheckout: () => void;
  onReturnToClaims: () => void;
  checkoutLoading: boolean;
}) {
  const claimUsed = usage?.usage?.claims?.used ?? 0;
  const tradeUsed = usage?.usage?.trades?.used ?? 0;
  const memberUsed = usage?.usage?.members?.used ?? 0;

  const configuredPlanCode = settings?.plan_code || "starter";
  const effectivePlanCode =
    usage?.effective_plan_code || settings?.effective_plan_code || "starter";

  const configuredPlanName =
    configuredPlanItem?.name ||
    settings?.plan_detail?.name ||
    formatPlanCodeLabel(configuredPlanCode);

  const effectivePlanName =
    usage?.effective_plan_detail?.name ||
    settings?.effective_plan_detail?.name ||
    formatPlanCodeLabel(effectivePlanCode);

  const configuredClaimLimit =
    configuredPlanItem?.limits.claim_limit ?? usage?.usage?.claims?.limit ?? 0;
  const configuredTradeLimit =
    configuredPlanItem?.limits.trade_limit ?? usage?.usage?.trades?.limit ?? 0;
  const configuredMemberLimit =
    configuredPlanItem?.limits.member_limit ?? usage?.usage?.members?.limit ?? 0;

  const claimBlocked = isAtOrOverLimit(claimUsed, configuredClaimLimit);
  const planMismatch =
    Boolean(billingFoundation?.plan_mismatch) ||
    normalizeText(configuredPlanCode) !== normalizeText(effectivePlanCode);

  const upgradeRecommendation = usage?.upgrade_recommendation;
  const governance = usage?.governance;
  const recommendedPlanName =
    upgradeRecommendation?.recommended_plan_name ||
    formatPlanCodeLabel(upgradeRecommendation?.recommended_plan_code);

  const checkoutIntent =
    normalizeText(
      normalizeText(selectedPlanCode) === normalizeText(configuredPlanCode) &&
        !billingFoundation?.billing_status_is_paid &&
        normalizeText(configuredPlanCode) !== "starter"
        ? "billing_activation"
        : normalizeText(selectedPlanCode) === normalizeText(configuredPlanCode)
          ? "no_op"
          : "plan_change"
    );

  const primaryAction = resolvePrimaryBillingAction({
    configuredPlanCode,
    selectedPlanCode,
    billingStatus: settings?.billing_status,
    billingStatusIsPaid: billingFoundation?.billing_status_is_paid,
    canSeeUpgrade,
    checkoutLoading,
  });

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Upgrade Summary</h2>
          <p className="mt-1 text-sm text-slate-500">
            This should be the clearest next step for users arriving from blocked claim actions.
          </p>
        </div>

        <span
          className={`rounded-full border px-3 py-1 text-xs font-semibold ${
            governance?.billing_activation_recommended
              ? "border-blue-200 bg-blue-50 text-blue-800"
              : claimBlocked
                ? "border-amber-200 bg-amber-50 text-amber-800"
                : "border-green-200 bg-green-50 text-green-800"
          }`}
        >
          {governance?.billing_activation_recommended
            ? "billing activation needed"
            : claimBlocked
              ? "claim capacity blocked"
              : "capacity available"}
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Configured plan</div>
          <div className="mt-1 text-xl font-semibold text-slate-900">{configuredPlanName}</div>
          <div className="mt-2 text-sm text-slate-600">
            Claims: {claimUsed} / {configuredClaimLimit}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">
            Selected billing target
          </div>
          <div className="mt-1 text-xl font-semibold text-slate-900">
            {formatPlanCodeLabel(selectedPlanCode)}
          </div>
          <div className="mt-2 text-sm text-slate-600">
            Billing cycle: {formatPlanCodeLabel(selectedBillingCycle)}
          </div>
        </div>
      </div>

      {planMismatch ? (
        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <div className="font-medium">Billing not active yet</div>
          <div className="mt-2">
            This workspace is configured as <span className="font-semibold">{configuredPlanName}</span>,
            but billing is still inactive. Enforcement may currently fall back to{" "}
            <span className="font-semibold">{effectivePlanName}</span> until billing activates.
          </div>
        </div>
      ) : null}

      {governance?.billing_activation_recommended ? (
        <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900">
          <div className="font-medium">Activate billing first</div>
          <div className="mt-2">
            The configured plan already provides the intended commercial posture. The next step is to
            activate billing so the workspace can enforce{" "}
            <span className="font-semibold">{configuredPlanName}</span>.
          </div>
        </div>
      ) : null}

      {governance?.upgrade_required_now || governance?.upgrade_recommended_soon ? (
        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <div className="font-medium">
            {governance?.upgrade_required_now ? "Upgrade required now" : "Upgrade recommended soon"}
          </div>
          <div className="mt-2">
            {governance?.upgrade_required_now
              ? "This workspace has reached or exceeded configured plan capacity in one or more governed dimensions. Some workflows may now be blocked."
              : "This workspace is approaching configured plan capacity limits. Upgrading early protects workflow continuity."}
          </div>
          {upgradeRecommendation?.recommended_plan_is_distinct && recommendedPlanName ? (
            <div className="mt-2">
              Recommended next plan: <span className="font-semibold">{recommendedPlanName}</span>
            </div>
          ) : upgradeRecommendation?.already_at_highest_tier ? (
            <div className="mt-2">This workspace is already on the highest commercial tier.</div>
          ) : null}
        </div>
      ) : null}

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Claims</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {claimUsed} / {configuredClaimLimit}
          </div>
          <div className="mt-1 text-xs text-slate-500">
            Public trust-surface and governed claim-capacity envelope
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Trades</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {tradeUsed} / {configuredTradeLimit}
          </div>
          <div className="mt-1 text-xs text-slate-500">Evidence ingestion capacity</div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs uppercase tracking-wide text-slate-500">Members</div>
          <div className="mt-1 text-lg font-semibold text-slate-900">
            {memberUsed} / {configuredMemberLimit}
          </div>
          <div className="mt-1 text-xs text-slate-500">Workspace collaborator capacity</div>
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        <div className="font-medium text-slate-900">What billing unlocks</div>
        <div className="mt-2">
          A successfully activated commercial plan increases governed claim capacity, reduces blocked
          lineage workflows, and gives the workspace more operational room for evidence ingestion and
          collaborator growth.
        </div>
      </div>

      {primaryAction.helper ? (
        <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          {primaryAction.helper}
          <span className="block mt-1 text-xs text-blue-700">
            Checkout intent: {checkoutIntent}
          </span>
        </div>
      ) : null}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onStartCheckout}
          disabled={primaryAction.disabled}
          className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {checkoutLoading ? "Preparing Billing..." : primaryAction.label}
        </button>

        <button
          type="button"
          onClick={() => {
            const el = document.getElementById("plan-ladder");
            el?.scrollIntoView({ behavior: "smooth", block: "start" });
          }}
          className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
        >
          Compare Plans
        </button>

        <button
          type="button"
          onClick={onReturnToClaims}
          className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
        >
          Back to Claims
        </button>
      </div>

      {!canSeeUpgrade ? (
        <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Only workspace owners can start checkout or change billing.
        </div>
      ) : null}
    </div>
  );
}

export default function WorkspaceSettingsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, workspaces, loading: authLoading, getWorkspaceRole } = useAuth();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const workspaceRole = workspaceId ? getWorkspaceRole(workspaceId) : null;
  const canEdit = workspaceRole === "owner";
  const canSeeUpgrade = workspaceRole === "owner";

  const checkoutStatus = searchParams.get("checkout");
  const checkoutSessionId = searchParams.get("session_id");
  const portalStatus = searchParams.get("portal");
  const activeTab = searchParams.get("tab");

  const [settings, setSettings] = useState<WorkspaceSettings | null>(null);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [billingFoundation, setBillingFoundation] = useState<WorkspaceBillingFoundation | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [billingEmail, setBillingEmail] = useState("");

  const [selectedPlanCode, setSelectedPlanCode] = useState("starter");
  const [selectedBillingCycle, setSelectedBillingCycle] = useState("monthly");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [portalLoading, setPortalLoading] = useState(false);
  const [refreshingBillingState, setRefreshingBillingState] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [billingMessage, setBillingMessage] = useState<string | null>(null);

  const handledQueryStateRef = useRef<string | null>(null);

  async function loadPage(targetWorkspaceId: number) {
    try {
      setLoading(true);
      setError(null);

      const [settingsRes, usageRes, billingFoundationRes] = await Promise.all([
        api.getWorkspaceSettings(targetWorkspaceId),
        api.getWorkspaceUsage(targetWorkspaceId),
        api.getWorkspaceBillingFoundation(targetWorkspaceId),
      ]);

      setSettings(settingsRes);
      setUsage(usageRes);
      setBillingFoundation(billingFoundationRes);

      setName(settingsRes.name || "");
      setDescription(settingsRes.description || "");
      setBillingEmail(settingsRes.billing_email || "");
      setSelectedPlanCode(settingsRes.plan_code || "starter");
      setSelectedBillingCycle("monthly");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspace settings.");
    } finally {
      setLoading(false);
    }
  }

  async function refreshBillingState(targetWorkspaceId: number) {
    try {
      setRefreshingBillingState(true);

      const [settingsRes, usageRes, billingFoundationRes] = await Promise.all([
        api.getWorkspaceSettings(targetWorkspaceId),
        api.getWorkspaceUsage(targetWorkspaceId),
        api.getWorkspaceBillingFoundation(targetWorkspaceId),
      ]);

      setSettings(settingsRes);
      setUsage(usageRes);
      setBillingFoundation(billingFoundationRes);

      setName(settingsRes.name || "");
      setDescription(settingsRes.description || "");
      setBillingEmail(settingsRes.billing_email || "");
      setSelectedPlanCode(settingsRes.plan_code || "starter");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh billing state.");
    } finally {
      setRefreshingBillingState(false);
    }
  }

  useEffect(() => {
    if (!workspaceId) return;
    if (!workspaceMembership) return;
    void loadPage(workspaceId);
  }, [workspaceId, workspaceMembership]);

  useEffect(() => {
    if (!workspaceId || loading) return;

    const stateKey = `${checkoutStatus || ""}|${checkoutSessionId || ""}|${portalStatus || ""}`;
    if (handledQueryStateRef.current === stateKey) return;

    if (!checkoutStatus && !portalStatus) return;

    handledQueryStateRef.current = stateKey;

    void (async () => {
      await refreshBillingState(workspaceId);

      if (checkoutStatus === "success") {
        setError(null);
        setSuccess("Checkout completed. Workspace billing state was refreshed.");
        setBillingMessage(
          checkoutSessionId
            ? `Checkout session completed successfully. Session ID: ${checkoutSessionId}`
            : "Checkout completed successfully."
        );
      } else if (checkoutStatus === "cancelled") {
        setSuccess(null);
        setBillingMessage("Checkout was cancelled. No billing change was finalized.");
      } else if (portalStatus === "returned") {
        setSuccess("Returned from billing portal. Workspace billing state was refreshed.");
        setBillingMessage("Billing portal session ended and workspace billing state was reloaded.");
      }

      const next = new URLSearchParams(searchParams.toString());
      next.delete("checkout");
      next.delete("session_id");
      next.delete("portal");

      const nextQuery = next.toString();
      router.replace(
        `/workspace/${workspaceId}/settings${nextQuery ? `?${nextQuery}` : ""}`,
        { scroll: false }
      );
    })();
  }, [workspaceId, loading, checkoutStatus, checkoutSessionId, portalStatus, router, searchParams]);

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!workspaceId || !canEdit) return;

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const updated = await api.updateWorkspaceSettings(workspaceId, {
        name,
        description,
        billing_email: billingEmail,
      });

      setSettings(updated);
      setSuccess("Workspace settings updated successfully.");

      const [refreshedUsage, refreshedBillingFoundation] = await Promise.all([
        api.getWorkspaceUsage(workspaceId),
        api.getWorkspaceBillingFoundation(workspaceId),
      ]);

      setUsage(refreshedUsage);
      setBillingFoundation(refreshedBillingFoundation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update workspace settings.");
    } finally {
      setSaving(false);
    }
  }

  async function handleStartCheckout() {
    if (!workspaceId || !canSeeUpgrade) return;

    try {
      setCheckoutLoading(true);
      setBillingMessage(null);
      setError(null);
      setSuccess(null);

      const response: BillingCheckoutResponse = await api.createBillingCheckoutSession(workspaceId, {
        plan_code: selectedPlanCode,
        billing_cycle: selectedBillingCycle,
      });

      if (response.url) {
        window.location.href = response.url;
        return;
      }

      const manualDetails = response.manual_payment_details;
      const manualMessage = manualDetails
        ? ` Payment method: ${manualDetails.payment_method || "Manual transfer"}. Account name: ${
            manualDetails.account_name || "—"
          }. Account number: ${manualDetails.account_number || "—"}. Bank: ${
            manualDetails.bank_name || "—"
          }. Phone: ${manualDetails.phone_number || "—"}.`
        : "";

      const diagnosticMessage =
        response.diagnostics && response.mode === "placeholder_until_checkout"
          ? ` Paddle enabled=${formatBooleanLabel(
              response.diagnostics.paddle_enabled
            )}, Stripe package=${formatBooleanLabel(
              response.diagnostics.stripe_package_installed
            )}, Stripe billing enabled=${formatBooleanLabel(
              response.diagnostics.stripe_billing_enabled
            )}, Manual billing enabled=${formatBooleanLabel(
              response.diagnostics.manual_billing_enabled
            )}.`
          : "";

      const intentMessage = response.checkout_intent
        ? ` Checkout intent: ${response.checkout_intent}.`
        : "";

      setBillingMessage(
        (response.message ||
          `Checkout foundation is ready, but no redirect URL was returned for ${selectedPlanCode} (${selectedBillingCycle}).`) +
          intentMessage +
          manualMessage +
          diagnosticMessage
      );

      const refreshedBillingFoundation = await api.getWorkspaceBillingFoundation(workspaceId);
      setBillingFoundation(refreshedBillingFoundation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start billing checkout.");
    } finally {
      setCheckoutLoading(false);
    }
  }

  async function handleOpenBillingPortal() {
    if (!workspaceId || !canSeeUpgrade) return;

    try {
      setPortalLoading(true);
      setBillingMessage(null);
      setError(null);
      setSuccess(null);

      const response: BillingPortalResponse = await api.createBillingPortalSession(workspaceId);

      if (response.url) {
        window.location.href = response.url;
        return;
      }

      const manualDetails = response.manual_payment_details;
      const manualMessage = manualDetails
        ? ` Payment method: ${manualDetails.payment_method || "Manual transfer"}. Account name: ${
            manualDetails.account_name || "—"
          }. Account number: ${manualDetails.account_number || "—"}. Bank: ${
            manualDetails.bank_name || "—"
          }. Phone: ${manualDetails.phone_number || "—"}.`
        : "";

      setBillingMessage((response.message || "Billing portal did not return a redirect URL.") + manualMessage);

      const refreshedBillingFoundation = await api.getWorkspaceBillingFoundation(workspaceId);
      setBillingFoundation(refreshedBillingFoundation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to open billing portal.");
    } finally {
      setPortalLoading(false);
    }
  }

  const planCatalog = usage?.plan_catalog ?? [];
  const configuredPlanCode = settings?.plan_code || "starter";
  const effectivePlanCode =
    usage?.effective_plan_code || settings?.effective_plan_code || "starter";

  const configuredPlanItem = getPlanFromCatalog(planCatalog, configuredPlanCode);
  const configuredPlanName =
    configuredPlanItem?.name ||
    settings?.plan_detail?.name ||
    formatPlanCodeLabel(configuredPlanCode);

  const effectivePlanName =
    usage?.effective_plan_detail?.name ||
    settings?.effective_plan_detail?.name ||
    formatPlanCodeLabel(effectivePlanCode);

  const configuredClaimLimit = configuredPlanItem?.limits.claim_limit ?? usage?.usage.claims.limit ?? 0;
  const configuredTradeLimit = configuredPlanItem?.limits.trade_limit ?? usage?.usage.trades.limit ?? 0;
  const configuredMemberLimit = configuredPlanItem?.limits.member_limit ?? usage?.usage.members.limit ?? 0;
  const configuredStorageLimit =
    configuredPlanItem?.limits.storage_limit_mb ?? usage?.usage.storage_mb.limit ?? 0;

  const claimsRatio = getUsageRatio(usage?.usage.claims.used, configuredClaimLimit);
  const tradesRatio = getUsageRatio(usage?.usage.trades.used, configuredTradeLimit);
  const membersRatio = getUsageRatio(usage?.usage.members.used, configuredMemberLimit);
  const storageRatio = getUsageRatio(usage?.usage.storage_mb.used, configuredStorageLimit);

  const membersOverLimit = isOverLimit(usage?.usage.members.used, configuredMemberLimit);
  const tradesOverLimit = isOverLimit(usage?.usage.trades.used, configuredTradeLimit);
  const claimsOverLimit = isOverLimit(usage?.usage.claims.used, configuredClaimLimit);
  const storageOverLimit = isOverLimit(usage?.usage.storage_mb.used, configuredStorageLimit);

  const membersAtOrOverLimit = isAtOrOverLimit(usage?.usage.members.used, configuredMemberLimit);
  const tradesAtOrOverLimit = isAtOrOverLimit(usage?.usage.trades.used, configuredTradeLimit);
  const claimsAtOrOverLimit = isAtOrOverLimit(usage?.usage.claims.used, configuredClaimLimit);
  const storageAtOrOverLimit = isAtOrOverLimit(usage?.usage.storage_mb.used, configuredStorageLimit);

  const hasAnyOverLimit =
    membersOverLimit || tradesOverLimit || claimsOverLimit || storageOverLimit;

  const planMismatch =
    Boolean(billingFoundation?.plan_mismatch) ||
    normalizeText(configuredPlanCode) !== normalizeText(effectivePlanCode);

  const upgradeRecommendation = usage?.upgrade_recommendation;
  const governance = usage?.governance;

  const recommendedPlanName =
    upgradeRecommendation?.recommended_plan_name ||
    formatPlanCodeLabel(upgradeRecommendation?.recommended_plan_code);

  const currentPlanBilling = configuredPlanItem?.billing || settings?.plan_detail?.billing;

  const primaryAction = resolvePrimaryBillingAction({
    configuredPlanCode,
    selectedPlanCode,
    billingStatus: settings?.billing_status,
    billingStatusIsPaid: billingFoundation?.billing_status_is_paid,
    canSeeUpgrade,
    checkoutLoading,
  });

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            Loading workspace settings...
          </div>
        </main>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace settings page.
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">
              Trading Truth Layer · Workspace Settings & Billing
            </div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">
              Workspace Billing & Governance
            </h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Billing, plan posture, and governed capacity control surface for workspace growth,
              blocked workflow recovery, and commercial activation.
            </p>
            {activeTab === "billing" ? (
              <div className="mt-4 inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-800">
                billing focus
              </div>
            ) : null}
          </div>

          <div className="rounded-2xl border bg-white px-5 py-4 shadow-sm">
            <div className="text-sm text-slate-500">Workspace Role</div>
            <div className="mt-2 text-xl font-semibold">{workspaceRole || "unknown"}</div>
          </div>
        </div>

        {activeTab === "billing" ? (
          <div className="mb-6 rounded-3xl border border-blue-200 bg-blue-50 p-6 text-blue-900 shadow-sm">
            <h2 className="text-xl font-semibold">Billing Review Required</h2>
            <p className="mt-2 text-sm">
              You arrived here from a governed workflow action that requires billing review,
              plan activation, or additional workspace capacity before it can proceed.
            </p>
          </div>
        ) : null}

        {refreshingBillingState ? (
          <div className="mb-6 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
            Refreshing billing state...
          </div>
        ) : null}

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            Loading workspace settings...
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        ) : (
          <>
            <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <SummaryCard
                label="Configured Plan"
                value={configuredPlanName}
                hint="Commercial tier assigned to this workspace"
              />
              <SummaryCard
                label="Billing Status"
                value={settings?.billing_status || "inactive"}
                hint="Subscription state"
              />
              <SummaryCard
                label="Effective Active Plan"
                value={effectivePlanName}
                hint="Plan currently enforcing limits and entitlements"
              />
              <SummaryCard
                label="Billing Mode"
                value={
                  billingFoundation?.manual_billing?.enabled &&
                  billingFoundation?.checkout_state?.mode === "manual_billing_ready"
                    ? "Manual billing"
                    : billingFoundation?.checkout_state.mode ||
                      usage?.stripe_ready.integration_status ||
                      "ready_for_stripe_foundation"
                }
                hint="Checkout mode / foundation state"
              />
              <SummaryCard
                label="Claims Used"
                value={`${usage?.usage.claims.used ?? 0} / ${configuredClaimLimit}`}
                hint="Governed claim-capacity position"
              />
            </div>

            {(success || billingMessage) && (
              <div className="mb-6 space-y-3">
                {success ? (
                  <div className="rounded-2xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
                    {success}
                  </div>
                ) : null}

                {billingMessage ? (
                  <div className="rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
                    {billingMessage}
                  </div>
                ) : null}
              </div>
            )}

            {(governance?.upgrade_required_now ||
              governance?.upgrade_recommended_soon ||
              governance?.billing_activation_recommended ||
              planMismatch) && (
              <div className="mb-6 rounded-3xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
                <h2 className="text-xl font-semibold">
                  {governance?.billing_activation_recommended
                    ? "Billing Activation Needed"
                    : governance?.upgrade_required_now
                      ? "Upgrade Required"
                      : governance?.upgrade_recommended_soon
                        ? "Upgrade Recommendation"
                        : "Billing Not Active Yet"}
                </h2>

                <p className="mt-2 text-sm">
                  {governance?.billing_activation_recommended
                    ? `This workspace is configured as ${configuredPlanName}, but billing is not active yet. Until activation is completed, governed enforcement may still operate under ${effectivePlanName}.`
                    : governance?.upgrade_required_now
                      ? "This workspace is now constrained by configured plan limits. Some workflows may be blocked until the plan is upgraded."
                      : governance?.upgrade_recommended_soon
                        ? "This workspace is approaching one or more configured plan ceilings. Upgrading now will protect workflow continuity."
                        : `This workspace is configured as ${configuredPlanName}, but billing is still inactive, so active enforcement may temporarily fall back to ${effectivePlanName}.`}
                </p>

                {upgradeRecommendation?.recommended_plan_is_distinct && recommendedPlanName ? (
                  <div className="mt-3 text-sm">
                    Recommended next plan: <span className="font-semibold">{recommendedPlanName}</span>
                  </div>
                ) : upgradeRecommendation?.already_at_highest_tier ? (
                  <div className="mt-3 text-sm">
                    This workspace is already on the highest commercial tier.
                  </div>
                ) : null}

                {upgradeRecommendation?.breached_dimensions?.length ? (
                  <div className="mt-4">
                    <div className="text-sm font-medium">Exceeded dimensions</div>
                    <div className="mt-2 flex flex-wrap gap-2 text-sm">
                      {upgradeRecommendation.breached_dimensions.map((item) => (
                        <span
                          key={`breach-${item}`}
                          className="rounded-full border border-amber-300 bg-white px-3 py-1 font-medium"
                        >
                          {formatDimensionLabel(item)}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}

                {upgradeRecommendation?.near_limit_dimensions?.length ? (
                  <div className="mt-4">
                    <div className="text-sm font-medium">Near-limit dimensions</div>
                    <div className="mt-2 flex flex-wrap gap-2 text-sm">
                      {upgradeRecommendation.near_limit_dimensions.map((item) => (
                        <span
                          key={`near-${item}`}
                          className="rounded-full border border-amber-300 bg-white px-3 py-1 font-medium"
                        >
                          {formatDimensionLabel(item)}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            )}

            <div className="grid gap-6 lg:grid-cols-[1.2fr_0.95fr]">
              <div className="space-y-6">
                <UpgradeSummaryPanel
                  workspaceId={workspaceId}
                  settings={settings}
                  usage={usage}
                  billingFoundation={billingFoundation}
                  planCatalog={planCatalog}
                  configuredPlanItem={configuredPlanItem}
                  selectedPlanCode={selectedPlanCode}
                  selectedBillingCycle={selectedBillingCycle}
                  canSeeUpgrade={canSeeUpgrade}
                  onStartCheckout={() => void handleStartCheckout()}
                  onReturnToClaims={() => router.push(`/workspace/${workspaceId}/claims`)}
                  checkoutLoading={checkoutLoading}
                />

                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                  <div className="mb-4 flex items-center justify-between gap-4">
                    <div>
                      <h2 className="text-2xl font-semibold">Workspace Profile</h2>
                      <p className="mt-1 text-sm text-slate-500">
                        Maintain workspace identity and billing contact metadata.
                      </p>
                    </div>

                    {!canEdit ? (
                      <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-sm font-medium text-amber-700">
                        Read only
                      </span>
                    ) : null}
                  </div>

                  <form onSubmit={handleSave} className="space-y-4">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-700">
                        Workspace Name
                      </label>
                      {canEdit ? (
                        <input
                          type="text"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          disabled={saving}
                          className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500 disabled:bg-slate-100"
                        />
                      ) : (
                        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-800">
                          {name || "—"}
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-700">
                        Description
                      </label>
                      {canEdit ? (
                        <textarea
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          disabled={saving}
                          rows={5}
                          className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500 disabled:bg-slate-100"
                        />
                      ) : (
                        <div className="min-h-[132px] rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-800 whitespace-pre-wrap">
                          {description || "—"}
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-700">
                        Billing Email
                      </label>
                      {canEdit ? (
                        <input
                          type="email"
                          value={billingEmail}
                          onChange={(e) => setBillingEmail(e.target.value)}
                          disabled={saving}
                          className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500 disabled:bg-slate-100"
                        />
                      ) : (
                        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-800">
                          {billingEmail || "—"}
                        </div>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-3">
                      {canEdit ? (
                        <button
                          type="submit"
                          disabled={saving}
                          className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
                        >
                          {saving ? "Saving..." : "Save Settings"}
                        </button>
                      ) : null}

                      <Link
                        href={`/workspace/${workspaceId}/dashboard`}
                        className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
                      >
                        Back to Dashboard
                      </Link>
                    </div>
                  </form>
                </div>

                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <h2 className="text-2xl font-semibold">Billing Foundation</h2>
                      <p className="mt-1 text-sm text-slate-500">
                        Current plan state, checkout readiness, portal access, and monetization foundations.
                      </p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <PlanBadge plan={settings?.plan_code} />
                      <BillingBadge status={settings?.billing_status} />
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-2">
                    <PriceCard
                      label="Configured Monthly Price"
                      value={formatUsd(currentPlanBilling?.monthly_price_usd)}
                      hint="Commercial tier monthly price"
                    />
                    <PriceCard
                      label="Configured Annual Price"
                      value={formatUsd(currentPlanBilling?.annual_price_usd)}
                      hint="Commercial tier annual price"
                    />
                  </div>

                  <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    <div>
                      <span className="font-medium text-slate-900">Configured plan:</span>{" "}
                      {configuredPlanName}
                    </div>
                    <div className="mt-2">
                      <span className="font-medium text-slate-900">Effective active plan:</span>{" "}
                      {effectivePlanName}
                    </div>
                    <div className="mt-2">
                      <span className="font-medium text-slate-900">Entitlement state:</span>{" "}
                      {planMismatch
                        ? "Billing inactive, enforcement may temporarily fall back to the effective active plan"
                        : "Configured plan and active entitlements aligned"}
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4 md:grid-cols-[1fr_220px]">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-700">
                        Selected Upgrade Plan
                      </label>
                      <select
                        value={selectedPlanCode}
                        onChange={(e) => {
                          setSelectedPlanCode(e.target.value);
                          setBillingMessage(null);
                        }}
                        className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      >
                        {planCatalog.map((plan) => (
                          <option key={plan.code} value={plan.code}>
                            {formatPlanCodeLabel(plan.code)}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-700">
                        Billing Cycle
                      </label>
                      <select
                        value={selectedBillingCycle}
                        onChange={(e) => {
                          setSelectedBillingCycle(e.target.value);
                          setBillingMessage(null);
                        }}
                        className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
                      >
                        <option value="monthly">Monthly</option>
                        <option value="annual">Annual</option>
                      </select>
                    </div>
                  </div>

                  {primaryAction.helper ? (
                    <div className="mt-4 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
                      {primaryAction.helper}
                    </div>
                  ) : null}

                  <div className="mt-4 grid gap-4 md:grid-cols-2">
                    <div className="rounded-xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Stripe Customer</div>
                      <div className="mt-1 break-all font-mono text-xs text-slate-700">
                        {settings?.stripe_customer_id || "Not connected"}
                      </div>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-4">
                      <div className="text-sm text-slate-500">Stripe Subscription</div>
                      <div className="mt-1 break-all font-mono text-xs text-slate-700">
                        {settings?.stripe_subscription_id || "Not connected"}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                    <div>
                      Subscription Period End:{" "}
                      <span className="font-medium">
                        {formatDateTime(settings?.subscription_current_period_end)}
                      </span>
                    </div>
                    <div className="mt-2">
                      Stripe Integration Status:{" "}
                      <span className="font-medium">
                        {billingFoundation?.stripe_ready.integration_status || "ready_for_stripe_foundation"}
                      </span>
                    </div>
                    <div className="mt-2">
                      Checkout Mode:{" "}
                      <span className="font-medium">
                        {billingFoundation?.checkout_state.mode || "placeholder_until_checkout"}
                      </span>
                    </div>
                    <div className="mt-2">
                      Billing Enabled:{" "}
                      <span className="font-medium">
                        {formatBooleanLabel(billingFoundation?.stripe_ready.billing_enabled)}
                      </span>
                    </div>
                    <div className="mt-2">
                      Billing Status Is Paid:{" "}
                      <span className="font-medium">
                        {formatBooleanLabel(billingFoundation?.billing_status_is_paid)}
                      </span>
                    </div>
                    <div className="mt-2">
                      Plan Mismatch:{" "}
                      <span className="font-medium">
                        {formatBooleanLabel(billingFoundation?.plan_mismatch)}
                      </span>
                    </div>
                    <div className="mt-2">
                      Secret Key Configured:{" "}
                      <span className="font-medium">
                        {formatBooleanLabel(billingFoundation?.stripe_ready.secret_key_configured)}
                      </span>
                    </div>
                    <div className="mt-2">
                      Stripe Package Installed:{" "}
                      <span className="font-medium">
                        {formatBooleanLabel(billingFoundation?.stripe_ready.package_installed)}
                      </span>
                    </div>
                    <div className="mt-2">
                      Customer Connected:{" "}
                      <span className="font-medium">
                        {billingFoundation?.stripe_ready.has_customer_id ? "yes" : "no"}
                      </span>
                    </div>
                    <div className="mt-2">
                      Subscription Connected:{" "}
                      <span className="font-medium">
                        {billingFoundation?.stripe_ready.has_subscription_id ? "yes" : "no"}
                      </span>
                    </div>
                    <div className="mt-2">
                      Portal Available:{" "}
                      <span className="font-medium">
                        {billingFoundation?.checkout_state.portal_available ? "yes" : "no"}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() => void handleStartCheckout()}
                      disabled={primaryAction.disabled}
                      className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
                    >
                      {checkoutLoading ? "Preparing Billing..." : primaryAction.label}
                    </button>

                    <button
                      type="button"
                      onClick={() => void handleOpenBillingPortal()}
                      disabled={!canSeeUpgrade || portalLoading}
                      className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
                    >
                      {portalLoading ? "Opening Portal..." : "Open Billing Portal"}
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        if (workspaceId) {
                          void refreshBillingState(workspaceId);
                        }
                      }}
                      disabled={refreshingBillingState}
                      className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100"
                    >
                      {refreshingBillingState ? "Refreshing..." : "Refresh Billing State"}
                    </button>
                  </div>

                  {!canSeeUpgrade ? (
                    <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                      Only workspace owners can start checkout or manage billing.
                    </div>
                  ) : null}
                </div>

                <ManualPaymentCard
                  billingFoundation={billingFoundation}
                  selectedPlanCode={selectedPlanCode}
                  selectedBillingCycle={selectedBillingCycle}
                />

                {planCatalog.length > 0 ? (
                  <div id="plan-ladder" className="rounded-3xl border bg-white p-6 shadow-sm">
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <h2 className="text-2xl font-semibold">Plan Ladder</h2>
                        <p className="mt-1 text-sm text-slate-500">
                          Workspace monetization tiers, pricing placeholders, and operational capacity ranges.
                        </p>
                      </div>

                      {upgradeRecommendation?.recommended_plan_is_distinct && recommendedPlanName ? (
                        <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
                          Recommended next plan: <span className="font-semibold">{recommendedPlanName}</span>
                        </div>
                      ) : null}
                    </div>

                    <div className="mt-5 grid gap-4 xl:grid-cols-2">
                      {planCatalog.map((plan) => (
                        <PlanCard
                          key={plan.code}
                          plan={plan}
                          configuredPlanCode={settings?.plan_code}
                          effectivePlanCode={effectivePlanCode}
                          selectedPlanCode={selectedPlanCode}
                          onSelect={(planCode) => {
                            setSelectedPlanCode(planCode);
                            setBillingMessage(null);
                          }}
                        />
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="space-y-6">
                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                  <h2 className="text-2xl font-semibold">Plan Limits</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    Current usage position against configured workspace plan limits.
                  </p>

                  {planMismatch ? (
                    <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
                      These cards show the configured commercial plan limits for{" "}
                      <span className="font-semibold">{configuredPlanName}</span>. Billing is still inactive,
                      so backend enforcement may temporarily apply the effective active plan{" "}
                      <span className="font-semibold">{effectivePlanName}</span>.
                    </div>
                  ) : null}

                  <div className="mt-4 space-y-4">

                    <UsageCard
                      label="Claims"
                      used={usage?.usage.claims.used}
                      limit={configuredClaimLimit}
                      ratio={claimsRatio}
                      atOrOver={claimsAtOrOverLimit}
                      hint="Governed public-claim and lifecycle exposure capacity"
                    />

                    <UsageCard
                      label="Members"
                      used={usage?.usage.members.used}
                      limit={configuredMemberLimit}
                      ratio={membersRatio}
                      atOrOver={membersAtOrOverLimit}
                      hint="Workspace collaborator capacity"
                    />

                    <UsageCard
                      label="Trades"
                      used={usage?.usage.trades.used}
                      limit={configuredTradeLimit}
                      ratio={tradesRatio}
                      atOrOver={tradesAtOrOverLimit}
                      hint="Evidence ingestion and operational throughput"
                    />
          
                    <UsageCard
                      label="Storage (MB)"
                      used={usage?.usage.storage_mb.used}
                      limit={configuredStorageLimit}
                      ratio={storageRatio}
                      atOrOver={storageAtOrOverLimit}
                      hint="Artifact and workspace storage budget"
                    />
                  </div>
                </div>

                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                  <h2 className="text-2xl font-semibold">Claim Governance Unlocks</h2>
                  <div className="mt-4 space-y-4 text-sm text-slate-700">
                    <div className="rounded-xl bg-slate-50 p-4">
                      <div className="font-medium">Governed version capacity</div>
                      <div className="mt-1 text-slate-600">
                        Higher plans increase available claim capacity so users can continue versioning
                        instead of hitting blocked lineage actions.
                      </div>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-4">
                      <div className="font-medium">Workflow continuity</div>
                      <div className="mt-1 text-slate-600">
                        Upgrading before limits are reached prevents interruption of claim creation,
                        verification preparation, and governance review workflows.
                      </div>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-4">
                      <div className="font-medium">Operational headroom</div>
                      <div className="mt-1 text-slate-600">
                        Claims, trades, members, and storage all contribute to how much governed trust
                        infrastructure the workspace can support.
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-3xl border bg-white p-6 shadow-sm">
                  <h2 className="text-2xl font-semibold">Workspace Record</h2>
                  <div className="mt-4 space-y-3 text-sm text-slate-600">
                    <div>
                      <span className="font-medium text-slate-900">Workspace ID:</span>{" "}
                      {settings?.workspace_id || workspaceId}
                    </div>
                    <div>
                      <span className="font-medium text-slate-900">Created:</span>{" "}
                      {formatDateTime(settings?.created_at)}
                    </div>
                    <div>
                      <span className="font-medium text-slate-900">Updated:</span>{" "}
                      {formatDateTime(settings?.updated_at)}
                    </div>
                    {settings?.plan_detail?.description ? (
                      <div>
                        <span className="font-medium text-slate-900">Plan Description:</span>{" "}
                        {settings.plan_detail.description}
                      </div>
                    ) : null}
                  </div>
                </div>

                {!canEdit ? (
                  <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6 text-amber-800 shadow-sm">
                    Your current role is <span className="font-semibold">{workspaceRole}</span>.
                    Only workspace owners can update settings, billing contact details, and upgrade
                    workspace plans.
                  </div>
                ) : null}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}