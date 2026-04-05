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

function formatPlanLabel(value?: string | null) {
  const text = String(value || "").trim();
  if (!text) return "—";

  return text
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(" ");
}

function resolveDefaultContent(reason: PaywallReason) {
  switch (reason) {
    case "claim_limit_reached":
      return {
        tone: "capacity" as const,
        eyebrow: "Governed capacity reached",
        title: "Public claim capacity has been reached",
        body:
          "This workspace has reached its currently enforced governed claim capacity. Additional public workflow actions require plan review or billing activation before they can continue.",
        primaryLabel: "Open Billing & Upgrade",
      };
    case "lifecycle_action_locked":
      return {
        tone: "workflow" as const,
        eyebrow: "Governed action blocked",
        title: "This governed workflow action is currently blocked",
        body:
          "This action changes governed workflow state and is not currently available under the workspace’s active access, billing, or enforcement posture.",
        primaryLabel: "Review Billing & Workflow Access",
      };
    case "edit_locked":
      return {
        tone: "workflow" as const,
        eyebrow: "Governed action blocked",
        title: "Draft editing is currently blocked",
        body:
          "Draft editing is not currently available under the workspace’s active workflow and entitlement posture.",
        primaryLabel: "Review Editing Access",
      };
    case "feature_locked":
    default:
      return {
        tone: "access" as const,
        eyebrow: "Access restricted",
        title: "This workflow is currently unavailable",
        body:
          "This action is currently restricted by workspace role, billing posture, or governed plan access.",
        primaryLabel: "Review Access & Upgrade",
      };
  }
}

function resolveWhyBlocked(reason: PaywallReason, actionLabel?: string | null) {
  const action = String(actionLabel || "This action").trim();

  switch (reason) {
    case "claim_limit_reached":
      return `${action} is blocked because it would exceed the workspace’s currently enforced governed claim-capacity envelope.`;
    case "lifecycle_action_locked":
      return `${action} is blocked because it changes governed workflow state under the current enforcement posture.`;
    case "edit_locked":
      return `${action} is blocked because the workspace does not currently allow additional governed draft modification under its active workflow posture.`;
    case "feature_locked":
    default:
      return `${action} is blocked because the workspace does not currently meet the required access, entitlement, or billing conditions.`;
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
    recommendedNormalized !== "review catalog" &&
    recommendedNormalized !== "review billing posture";

  if (reason === "claim_limit_reached") {
    if (hasDistinctRecommendation) {
      return "Review billing and move the workspace into a plan posture with more governed public-claim capacity before retrying this action.";
    }

    return "Review billing activation and workspace entitlement posture so enforced limits can match the intended operating tier.";
  }

  if (reason === "lifecycle_action_locked") {
    if (hasDistinctRecommendation) {
      return "Review billing posture, governed workflow availability, and the recommended plan path before retrying this lifecycle action.";
    }

    return "Review the workspace billing posture, access conditions, and governed workflow availability before retrying this action.";
  }

  if (reason === "edit_locked") {
    return "Review workflow posture, editing eligibility, and workspace billing access before attempting further draft changes.";
  }

  return "Review current role access and workspace billing posture to understand what is required for this workflow.";
}

function resolveUpgradeBenefit(params: {
  reason: PaywallReason;
  currentPlanName?: string | null;
  recommendedPlanName?: string | null;
}) {
  const { reason, currentPlanName, recommendedPlanName } = params;

  const currentLabel = formatPlanLabel(currentPlanName);
  const recommendedLabel = formatPlanLabel(recommendedPlanName);

  const currentNormalized = normalizeText(currentPlanName);
  const recommendedNormalized = normalizeText(recommendedPlanName);

  const hasDistinctRecommendation =
    !!recommendedNormalized &&
    !!currentNormalized &&
    recommendedNormalized !== currentNormalized &&
    recommendedNormalized !== "review catalog" &&
    recommendedNormalized !== "review billing posture";

  if (reason === "claim_limit_reached") {
    if (hasDistinctRecommendation) {
      return `Moving from ${currentLabel} toward ${recommendedLabel} gives the workspace more governed claim capacity and restores continuity for blocked public workflow actions.`;
    }

    return "Reviewing billing and activation posture helps align enforced governed capacity with the workspace’s intended operating tier.";
  }

  if (reason === "lifecycle_action_locked" || reason === "edit_locked") {
    if (hasDistinctRecommendation) {
      return `A higher or properly activated plan posture can reopen governed workflow access and reduce interruptions across claim review, publication, and lock-state operations.`;
    }

    return "A properly activated billing posture can restore governed workflow continuity and reduce repeated lifecycle interruptions.";
  }

  return "Billing review helps clarify whether this workflow should be unlocked through plan, role, or access posture changes.";
}

function resolveRecommendationLabel(params: {
  currentPlanName?: string | null;
  recommendedPlanName?: string | null;
}) {
  const currentNormalized = normalizeText(params.currentPlanName);
  const recommendedNormalized = normalizeText(params.recommendedPlanName);

  const hasDistinctRecommendation =
    !!recommendedNormalized &&
    recommendedNormalized !== currentNormalized &&
    recommendedNormalized !== "review catalog" &&
    recommendedNormalized !== "review billing posture";

  if (hasDistinctRecommendation) {
    return formatPlanLabel(params.recommendedPlanName);
  }

  return "Review billing posture";
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value?: string | null;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="text-[11px] uppercase tracking-[0.16em] text-slate-500">
        {label}
      </div>
      <div className="mt-2 text-sm font-semibold text-slate-900">
        {value || "—"}
      </div>
    </div>
  );
}

function TonePill({
  reason,
}: {
  reason: PaywallReason;
}) {
  const label =
    reason === "claim_limit_reached"
      ? "capacity enforcement"
      : reason === "lifecycle_action_locked"
        ? "workflow enforcement"
        : reason === "edit_locked"
          ? "editing restricted"
          : "access restricted";

  const classes =
    reason === "claim_limit_reached"
      ? "border-amber-200 bg-amber-50 text-amber-800"
      : reason === "lifecycle_action_locked" || reason === "edit_locked"
        ? "border-blue-200 bg-blue-50 text-blue-800"
        : "border-slate-200 bg-slate-50 text-slate-700";

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${classes}`}
    >
      {label}
    </span>
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
  const whyBlocked = resolveWhyBlocked(reason, actionLabel);
  const actionGuidance = resolveActionGuidance({
    reason,
    currentPlanName: currentPlanName || currentPlanCode || null,
    recommendedPlanName: recommendedPlanName || null,
  });
  const upgradeBenefit = resolveUpgradeBenefit({
    reason,
    currentPlanName: currentPlanName || currentPlanCode || null,
    recommendedPlanName: recommendedPlanName || null,
  });

  const displayPlan = formatPlanLabel(currentPlanName || currentPlanCode || null);
  const displayRecommendation = resolveRecommendationLabel({
    currentPlanName: currentPlanName || currentPlanCode || null,
    recommendedPlanName: recommendedPlanName || null,
  });
  const displayAction = actionLabel || "Workflow action";

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 px-4 py-6">
      <div className="w-full max-w-3xl overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-2xl ring-1 ring-slate-200/60">
        <div className="border-b border-slate-200 px-6 py-5 sm:px-7">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                {defaults.eyebrow}
              </div>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900 sm:text-3xl">
                {resolvedTitle}
              </h2>
            </div>

            <TonePill reason={reason} />
          </div>

          <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-600">
            {resolvedBody}
          </p>
        <div className="mt-5 flex flex-wrap gap-2">
          <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">
            current: {displayPlan}
          </span>
          <span className="inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-800">
            recommended: {displayRecommendation}
          </span>
          <span className="inline-flex rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
            blocked action: {displayAction}
          </span>
        </div>
        </div>

        <div className="px-6 py-5 sm:px-7">
          <div className="grid gap-3 sm:grid-cols-2">
            <DetailRow label="Current plan" value={displayPlan} />
            <DetailRow label="Usage state" value={usageLabel || "Review current governed usage"} />
            <DetailRow label="Recommended next step" value={displayRecommendation} />
            <DetailRow label="Blocked action" value={displayAction} />
          </div>

          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <div className="text-sm font-semibold text-amber-900">Why this is blocked</div>
            <div className="mt-2 text-sm leading-6 text-amber-800">{whyBlocked}</div>
          </div>

          <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4">
            <div className="text-sm font-semibold text-blue-900">What unlocks after billing recovery</div>
            <div className="mt-2 text-sm leading-6 text-blue-800">{upgradeBenefit}</div>
          </div>

          <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-semibold text-slate-900">What to do next</div>
            <div className="mt-2 text-sm leading-6 text-slate-700">{actionGuidance}</div>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-end gap-3 border-t border-slate-200 px-6 py-4 sm:px-7">
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