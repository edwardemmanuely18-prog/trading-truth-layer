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

function resolveDefaultContent(reason: PaywallReason) {
  switch (reason) {
    case "claim_limit_reached":
      return {
        eyebrow: "Plan limit reached",
        title: "Upgrade required to continue version governance",
        body:
          "This workspace has reached its current claim capacity. Upgrade the workspace plan to create another governed claim version without breaking your lineage workflow.",
        primaryLabel: "Upgrade Workspace",
      };
    case "lifecycle_action_locked":
      return {
        eyebrow: "Lifecycle action gated",
        title: "Upgrade required for advanced claim lifecycle actions",
        body:
          "This action is part of the governed verification workflow and is not available on the current workspace plan.",
        primaryLabel: "View Upgrade Options",
      };
    case "edit_locked":
      return {
        eyebrow: "Editing gated",
        title: "Upgrade required for governed draft editing",
        body:
          "Draft editing on this workspace is currently gated. Upgrade the workspace plan to continue governed claim iteration.",
        primaryLabel: "Upgrade Workspace",
      };
    case "feature_locked":
    default:
      return {
        eyebrow: "Feature gated",
        title: "Upgrade required to access this workflow",
        body:
          "This action is not available on the current workspace plan. Upgrade to continue with the full verification workflow.",
        primaryLabel: "Upgrade Workspace",
      };
  }
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
            <DetailRow label="Recommended plan" value={recommendedPlanName || "Review catalog"} />
            <DetailRow label="Blocked action" value={actionLabel || "Workflow action"} />
          </div>

          <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <div className="text-sm font-semibold text-amber-900">Why this is blocked</div>
            <div className="mt-2 text-sm leading-6 text-amber-800">
              Your workspace can still inspect existing claim records, but this action changes
              governance state or creates additional claim capacity. Those are controlled by plan
              entitlements and usage limits.
            </div>
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