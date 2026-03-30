"use client";

type PaywallReason =
  | "claim_limit_reached"
  | "feature_locked"
  | "lifecycle_action_locked"
  | "edit_locked";

type Props = {
  open: boolean;
  onClose: () => void;
  title?: string;
  reason: PaywallReason;
  currentPlanName?: string | null;
  currentPlanCode?: string | null;
  usageLabel?: string | null;
  recommendedPlanName?: string | null;
  actionLabel?: string | null;
  message?: string | null;
  onUpgrade?: () => void;
};

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function resolveDefaultContent(reason: PaywallReason) {
  switch (reason) {
    case "claim_limit_reached":
      return {
        eyebrow: "Plan limit reached",
        title: "Plan action required to continue",
        body:
          "This workspace has reached a governed plan limit. Review billing and plan posture before continuing this workflow.",
        primaryLabel: "Open Billing & Plans",
      };
    case "lifecycle_action_locked":
      return {
        eyebrow: "Governed action blocked",
        title: "This workflow action is currently blocked",
        body:
          "This action changes governed workflow state and is not currently available under the workspace’s active enforcement posture.",
        primaryLabel: "Review Billing & Access",
      };
    case "edit_locked":
      return {
        eyebrow: "Governed action blocked",
        title: "Draft editing is currently blocked",
        body:
          "Draft editing is not currently available under the workspace’s active workflow and entitlement posture.",
        primaryLabel: "Review Billing & Access",
      };
    case "feature_locked":
    default:
      return {
        eyebrow: "Access restricted",
        title: "This workflow is currently unavailable",
        body:
          "This action is currently restricted by workspace role, billing posture, or governed plan access.",
        primaryLabel: "Review Access & Billing",
      };
  }
}

function resolveWhyBlocked(reason: PaywallReason) {
  switch (reason) {
    case "claim_limit_reached":
      return "This action is blocked because it would exceed currently enforced workspace capacity.";
    case "lifecycle_action_locked":
    case "edit_locked":
      return "This action is blocked because it changes governed workflow state under the current enforcement posture.";
    case "feature_locked":
    default:
      return "This action is blocked because the workspace does not currently meet the required access or entitlement conditions.";
  }
}

function resolveActionGuidance(params: {
  reason: PaywallReason;
  currentPlanName?: string | null;
  recommendedPlanName?: string | null;
}) {
  const { reason, currentPlanName, recommendedPlanName } = params;

  const currentNormalized = normalizeText(currentPlanName);
  const recommendedNormalized = normalizeText(recommendedPlanName);

  const hasDistinctRecommendation =
    !!recommendedNormalized &&
    !!currentNormalized &&
    recommendedNormalized !== currentNormalized &&
    recommendedNormalized !== "review catalog";

  if (reason === "claim_limit_reached") {
    if (hasDistinctRecommendation) {
      return "The next best step is to review billing and move the workspace into a plan posture that supports more capacity.";
    }

    return "The next best step is to review billing activation or current workspace entitlement posture so enforced limits can match the intended operating tier.";
  }

  if (reason === "lifecycle_action_locked" || reason === "edit_locked") {
    return "Review the workspace billing posture, access conditions, and governed workflow availability before retrying this action.";
  }

  return "Review current role access and workspace billing posture to understand what is required for this workflow.";
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value?: string | null;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-sm font-semibold text-slate-900">{value || "—"}</div>
    </div>
  );
}

export default function PaywallModal({
  open,
  onClose,
  title,
  reason,
  currentPlanName,
  currentPlanCode,
  usageLabel,
  recommendedPlanName,
  actionLabel,
  message,
  onUpgrade,
}: Props) {
  if (!open) return null;

  const defaults = resolveDefaultContent(reason);
  const resolvedTitle = title || defaults.title;
  const resolvedBody = message || defaults.body;
  const whyBlocked = resolveWhyBlocked(reason);
  const actionGuidance = resolveActionGuidance({
    reason,
    currentPlanName: currentPlanName || currentPlanCode || null,
    recommendedPlanName: recommendedPlanName || null,
  });

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/50 px-4 py-6">
      <div className="w-full max-w-2xl rounded-3xl border border-slate-200 bg-white shadow-2xl">
        <div className="border-b border-slate-200 px-6 py-5">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            {defaults.eyebrow}
          </div>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
            {resolvedTitle}
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{resolvedBody}</p>
        </div>

        <div className="px-6 py-5">
          <div className="grid gap-3 sm:grid-cols-2">
            <DetailRow label="Current plan" value={currentPlanName || currentPlanCode || "—"} />
            <DetailRow label="Usage state" value={usageLabel || "—"} />
            <DetailRow label="Recommended next step" value={recommendedPlanName || "Review billing posture"} />
            <DetailRow label="Blocked action" value={actionLabel || "Workflow action"} />
          </div>

          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <div className="text-sm font-semibold text-amber-900">Why this is blocked</div>
            <div className="mt-2 text-sm leading-6 text-amber-800">{whyBlocked}</div>
          </div>

          <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-semibold text-slate-900">What to do next</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">{actionGuidance}</div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-end gap-3 border-t border-slate-200 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Close
          </button>

          <button
            type="button"
            onClick={() => {
              onClose();
              onUpgrade?.();
            }}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
          >
            {defaults.primaryLabel}
          </button>
        </div>
      </div>
    </div>
  );
}