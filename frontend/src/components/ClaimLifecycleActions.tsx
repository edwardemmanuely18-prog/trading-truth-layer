"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  api,
  getApiErrorCode,
  isApiError,
  type WorkspaceUsageSummary,
} from "../lib/api";
import { useAuth } from "./AuthProvider";
import PaywallModal from "./PaywallModal";
import { useWorkspaceGate } from "../hooks/useWorkspaceGate";

type Props = {
  claimSchemaId: number;
  workspaceId: number;
  status: string;
};

type LifecycleActionKey = "verify" | "publish" | "lock";

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function getUsageWarning(claimUsage?: WorkspaceUsageSummary["usage"]["claims"] | null) {
  if (!claimUsage) return null;

  const ratio = Number(claimUsage.ratio ?? 0);
  if (ratio >= 1) {
    return {
      tone: "critical" as const,
      title: "Governed claim limit reached",
      message:
        "This workspace has reached its governed claim capacity. Additional public lifecycle actions require upgrade review.",
    };
  }

  if (ratio >= 0.8) {
    return {
      tone: "warning" as const,
      title: "Approaching governed claim limit",
      message:
        "This workspace is approaching its governed claim capacity. The next public workflow action may require upgrade.",
    };
  }

  return null;
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function canExposePublicView(status?: string | null) {
  const normalized = normalizeText(status);
  return normalized === "published" || normalized === "locked";
}

async function copyText(value: string) {
  if (typeof navigator === "undefined" || !navigator.clipboard) {
    throw new Error("Clipboard is not available in this browser.");
  }
  await navigator.clipboard.writeText(value);
}

function StatusPill({ status }: { status: string }) {
  const normalized = normalizeText(status);

  const className =
    normalized === "locked"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "published"
        ? "border-blue-200 bg-blue-100 text-blue-800"
        : normalized === "verified"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${className}`}>
      {status}
    </span>
  );
}

function StepCard({
  title,
  description,
  stateLabel,
  isAvailableNow,
  isCompleted,
  disabled,
  loading,
  actionLabel,
  disabledReason,
  accent,
  onClick,
}: {
  title: string;
  description: string;
  stateLabel: string;
  isAvailableNow: boolean;
  isCompleted: boolean;
  disabled: boolean;
  loading: boolean;
  actionLabel: string;
  disabledReason?: string | null;
  accent: "amber" | "blue" | "green";
  onClick: () => Promise<void> | void;
}) {
  const accentMap = {
    amber: {
      activeShell: "border-amber-300 bg-amber-50",
      completeShell: "border-slate-200 bg-white",
      idleShell: "border-slate-200 bg-white",
      activeTitle: "text-amber-950",
      completeTitle: "text-slate-900",
      idleTitle: "text-slate-900",
      activeText: "text-amber-800",
      completeText: "text-slate-600",
      idleText: "text-slate-600",
      activeButton:
        "bg-amber-900 text-white hover:bg-amber-800 disabled:cursor-not-allowed disabled:opacity-50",
      inactiveButton:
        "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50",
      activeBadge: "border-amber-300 bg-white text-amber-900",
      completeBadge: "border-green-200 bg-green-50 text-green-700",
      idleBadge: "border-slate-200 bg-slate-50 text-slate-600",
    },
    blue: {
      activeShell: "border-blue-300 bg-blue-50",
      completeShell: "border-slate-200 bg-white",
      idleShell: "border-slate-200 bg-white",
      activeTitle: "text-blue-950",
      completeTitle: "text-slate-900",
      idleTitle: "text-slate-900",
      activeText: "text-blue-800",
      completeText: "text-slate-600",
      idleText: "text-slate-600",
      activeButton:
        "bg-blue-900 text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50",
      inactiveButton:
        "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50",
      activeBadge: "border-blue-300 bg-white text-blue-900",
      completeBadge: "border-green-200 bg-green-50 text-green-700",
      idleBadge: "border-slate-200 bg-slate-50 text-slate-600",
    },
    green: {
      activeShell: "border-green-300 bg-green-50",
      completeShell: "border-slate-200 bg-white",
      idleShell: "border-slate-200 bg-white",
      activeTitle: "text-green-950",
      completeTitle: "text-slate-900",
      idleTitle: "text-slate-900",
      activeText: "text-green-800",
      completeText: "text-slate-600",
      idleText: "text-slate-600",
      activeButton:
        "bg-green-900 text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-50",
      inactiveButton:
        "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50",
      activeBadge: "border-green-300 bg-white text-green-900",
      completeBadge: "border-green-200 bg-green-50 text-green-700",
      idleBadge: "border-slate-200 bg-slate-50 text-slate-600",
    },
  };

  const styles = accentMap[accent];

  const shellClass = isAvailableNow
    ? styles.activeShell
    : isCompleted
      ? styles.completeShell
      : styles.idleShell;

  const titleClass = isAvailableNow
    ? styles.activeTitle
    : isCompleted
      ? styles.completeTitle
      : styles.idleTitle;

  const textClass = isAvailableNow
    ? styles.activeText
    : isCompleted
      ? styles.completeText
      : styles.idleText;

  const badgeClass = isAvailableNow
    ? styles.activeBadge
    : isCompleted
      ? styles.completeBadge
      : styles.idleBadge;

  const buttonClass = isAvailableNow ? styles.activeButton : styles.inactiveButton;

  return (
    <div className={`rounded-2xl border p-4 shadow-sm ${shellClass}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className={`text-sm font-semibold ${titleClass}`}>{title}</div>
          <div className={`mt-2 text-xs leading-5 ${textClass}`}>{description}</div>
        </div>

        <span className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-semibold ${badgeClass}`}>
          {stateLabel}
        </span>
      </div>

      <button
        type="button"
        disabled={disabled}
        onClick={() => void onClick()}
        className={`mt-4 rounded-xl px-4 py-2 text-sm font-semibold transition ${buttonClass}`}
      >
        {loading ? "Working..." : actionLabel}
      </button>

      {disabledReason ? <div className={`mt-2 text-xs ${textClass}`}>{disabledReason}</div> : null}
    </div>
  );
}

function getLifecycleActionLabel(action: LifecycleActionKey) {
  switch (action) {
    case "verify":
      return "Verify claim";
    case "publish":
      return "Publish claim";
    case "lock":
      return "Lock claim";
    default:
      return "Claim lifecycle action";
  }
}

function getLifecyclePaywallReason(_action: LifecycleActionKey) {
  return "lifecycle_action_locked" as const;
}

function getActionAvailability(params: {
  action: LifecycleActionKey;
  normalizedStatus: string;
  workspaceRole: string | null;
  loadingAction: LifecycleActionKey | null;
}) {
  const { action, normalizedStatus, workspaceRole, loadingAction } = params;

  const isOwner = workspaceRole === "owner";
  const isOperator = workspaceRole === "operator";

  const canVerifyByRole = isOwner || isOperator;
  const canPublishByRole = isOwner;
  const canLockByRole = isOwner;

  const verifyAvailable = normalizedStatus === "draft";
  const publishAvailable = normalizedStatus === "verified";
  const lockAvailable = normalizedStatus === "published";

  const verifyCompleted =
    normalizedStatus === "verified" ||
    normalizedStatus === "published" ||
    normalizedStatus === "locked";

  const publishCompleted = normalizedStatus === "published" || normalizedStatus === "locked";
  const lockCompleted = normalizedStatus === "locked";

  if (action === "verify") {
    const roleAllowed = canVerifyByRole;
    const stateAvailable = verifyAvailable;
    const completed = verifyCompleted;

    return {
      roleAllowed,
      stateAvailable,
      completed,
      disabled: loadingAction !== null || !roleAllowed || !stateAvailable,
      disabledReason: !roleAllowed
        ? "Only workspace owners and operators can verify claims."
        : !stateAvailable
          ? completed
            ? "This claim has already moved beyond verification."
            : "Only draft claims can move into verified state."
          : null,
      stateLabel: completed ? "completed" : stateAvailable ? "available" : "not available",
    };
  }

  if (action === "publish") {
    const roleAllowed = canPublishByRole;
    const stateAvailable = publishAvailable;
    const completed = publishCompleted;

    return {
      roleAllowed,
      stateAvailable,
      completed,
      disabled: loadingAction !== null || !roleAllowed || !stateAvailable,
      disabledReason: !roleAllowed
        ? "Only workspace owners can publish claims."
        : !stateAvailable
          ? completed
            ? "This claim has already moved beyond publication."
            : "Only verified claims can move into published state."
          : null,
      stateLabel: completed ? "completed" : stateAvailable ? "available" : "not available",
    };
  }

  const roleAllowed = canLockByRole;
  const stateAvailable = lockAvailable;
  const completed = lockCompleted;

  return {
    roleAllowed,
    stateAvailable,
    completed,
    disabled: loadingAction !== null || !roleAllowed || !stateAvailable,
    disabledReason: !roleAllowed
      ? "Only workspace owners can lock claims."
      : !stateAvailable
        ? completed
          ? "This claim is already locked."
          : "Only published claims can move into locked state."
        : null,
    stateLabel: completed ? "completed" : stateAvailable ? "available" : "not available",
  };
}

export default function ClaimLifecycleActions({
  claimSchemaId,
  workspaceId,
  status,
}: Props) {
  const router = useRouter();
  const { getWorkspaceRole } = useAuth();
  const { gateAndExecute, paywallState, closePaywall, openPaywall } = useWorkspaceGate();

  const [loadingAction, setLoadingAction] = useState<LifecycleActionKey | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [linkMessage, setLinkMessage] = useState<string | null>(null);
  const [copyingLink, setCopyingLink] = useState(false);

  const workspaceRole = getWorkspaceRole(workspaceId);
  const normalizedStatus = normalizeText(status);
  const publicViewAvailable = canExposePublicView(status);
  const publicViewPath = `/claim/${claimSchemaId}/public`;

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      try {
        const result = await api.getWorkspaceUsage(workspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId]);

  const verifyConfig = useMemo(() => {
    return getActionAvailability({
      action: "verify",
      normalizedStatus,
      workspaceRole,
      loadingAction,
    });
  }, [normalizedStatus, workspaceRole, loadingAction]);

  const publishConfig = useMemo(() => {
    return getActionAvailability({
      action: "publish",
      normalizedStatus,
      workspaceRole,
      loadingAction,
    });
  }, [normalizedStatus, workspaceRole, loadingAction]);

  const lockConfig = useMemo(() => {
    return getActionAvailability({
      action: "lock",
      normalizedStatus,
      workspaceRole,
      loadingAction,
    });
  }, [normalizedStatus, workspaceRole, loadingAction]);

  const currentPlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage.plan_code)
    )?.name || usage?.plan_code || "—";

  const effectivePlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage.effective_plan_code)
    )?.name || usage?.effective_plan_code || currentPlanName;

  const governanceBillingActivationRecommended = Boolean(
    (usage?.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );

  const recommendedPlanName = governanceBillingActivationRecommended
    ? currentPlanName
    : usage?.upgrade_recommendation?.recommended_plan_name || "Review billing posture";
  
  const claimUsage = usage?.usage?.claims;

  const usageWarning = useMemo(() => getUsageWarning(claimUsage), [claimUsage]);

  const usageLabel = claimUsage
    ? `${claimUsage.used} of ${claimUsage.limit} governed claims used${
        claimUsage.ratio !== null && claimUsage.ratio !== undefined
          ? ` · ${formatPercent(claimUsage.ratio)}`
          : ""
      }`
    : `Effective plan: ${effectivePlanName}`;

  async function handleBackendDenied(err: unknown, action: LifecycleActionKey) {
    const actionLabel = getLifecycleActionLabel(action);

    if (isApiError(err) && err.status === 403) {
      const errorCode = getApiErrorCode(err);

      if (errorCode === "claim_limit_reached") {
        openPaywall({
          reason: "claim_limit_reached",
          actionLabel,
          message:
            action === "publish"
              ? err.payload?.message ||
                err.payload?.upgrade_hint ||
                "Publishing is blocked because the workspace has reached its governed public-claim capacity."
              : err.payload?.message ||
                err.payload?.upgrade_hint ||
                "This action is blocked because the workspace has reached its governed claim capacity.",
        });
        return true;
      }

      openPaywall({
        reason: getLifecyclePaywallReason(action),
        actionLabel,
        message:
          err.payload?.message ||
          err.message ||
          "This lifecycle action is currently blocked for the workspace.",
      });
      return true;
    }

    return false;
  }

  async function runLifecycleAction(action: LifecycleActionKey, request: () => Promise<unknown>) {
    try {
      setLoadingAction(action);
      setError(null);
      setLinkMessage(null);
      await request();
      window.location.reload();
    } catch (err) {
      console.error(err);

      const handled = await handleBackendDenied(err, action);
      if (!handled) {
        setError(
          err instanceof Error ? err.message : `Failed to ${getLifecycleActionLabel(action).toLowerCase()}.`
        );
      }
    } finally {
      setLoadingAction(null);
    }
  }
  
  {usageWarning ? (
    <div
      className={`rounded-2xl border p-4 text-sm ${
        usageWarning.tone === "critical"
          ? "border-amber-300 bg-amber-50 text-amber-900"
          : "border-blue-200 bg-blue-50 text-blue-900"
      }`}
    >
      <div className="font-semibold">{usageWarning.title}</div>
      <div className="mt-1">{usageWarning.message}</div>
    </div>
  ) : null}

  async function handleVerify() {
    if (verifyConfig.disabled) return;

    await gateAndExecute(
      {
        action: "verify_claim",
        workspaceRole,
        claimStatus: status,
      },
      async () => {
        await runLifecycleAction("verify", () => api.verifyClaimSchema(claimSchemaId));
      }
    );
  }

  async function handlePublish() {
    if (publishConfig.disabled) return;

    await gateAndExecute(
      {
        action: "publish_claim",
        workspaceRole,
        claimStatus: status,
      },
      async () => {
        await runLifecycleAction("publish", () => api.publishClaimSchema(claimSchemaId));
      }
    );
  }

  async function handleLock() {
    if (lockConfig.disabled) return;

    await gateAndExecute(
      {
        action: "lock_claim",
        workspaceRole,
        claimStatus: status,
      },
      async () => {
        await runLifecycleAction("lock", () => api.lockClaimSchema(claimSchemaId));
      }
    );
  }

  function handleOpenPublicView() {
    if (!publicViewAvailable) return;
    router.push(publicViewPath);
  }

  async function handleCopyPublicLink() {
    if (!publicViewAvailable) return;

    try {
      setCopyingLink(true);
      setLinkMessage(null);

      const origin =
        typeof window !== "undefined" && window.location?.origin
          ? window.location.origin
          : "";

      const fullUrl = origin ? `${origin}${publicViewPath}` : publicViewPath;
      await copyText(fullUrl);
      setLinkMessage("Public link copied.");
    } catch (err) {
      setLinkMessage(
        err instanceof Error ? err.message : "Failed to copy public link."
      );
    } finally {
      setCopyingLink(false);
    }
  }

  return (
    <>
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm text-slate-500">Lifecycle governance</div>
              <div className="mt-1 text-base font-semibold text-slate-900">
                Controlled state progression for verified claim publication
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <StatusPill status={status || "unknown"} />
              <span className="inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                role: {workspaceRole || "unknown"}
              </span>
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">Step 1</div>
              <div className="mt-1 font-semibold text-slate-900">Verify</div>
              <div className="mt-1 text-xs text-slate-600">
                Confirms the draft and freezes the calculated verification snapshot for lifecycle progression.
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">Step 2</div>
              <div className="mt-1 font-semibold text-slate-900">Publish</div>
              <div className="mt-1 text-xs text-slate-600">
                Moves the verified claim into publishable state for public or controlled exposure.
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <div className="text-xs text-slate-500">Step 3</div>
              <div className="mt-1 font-semibold text-slate-900">Lock</div>
              <div className="mt-1 text-xs text-slate-600">
                Finalizes the claim and stores the locked trade-set fingerprint for integrity checks.
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 text-xs leading-6 text-slate-600">
            Role and lifecycle state determine whether an action is operationally available. Workspace
            billing and governed capacity are enforced at execution time through the blocked-action and
            paywall flow.
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
            <div className="text-xs uppercase tracking-wide text-slate-500">Public trust surface</div>

            {publicViewAvailable ? (
              <>
                <div className="mt-2 text-sm text-slate-700">
                  This claim is eligible for public viewing and shareable distribution.
                </div>

                <div className="mt-3 flex flex-wrap gap-3">
                  <button
                    type="button"
                    onClick={handleOpenPublicView}
                    className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                  >
                    Open Public View
                  </button>

                  <button
                    type="button"
                    onClick={() => void handleCopyPublicLink()}
                    disabled={copyingLink}
                    className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {copyingLink ? "Copying..." : "Copy Public Link"}
                  </button>
                </div>
              </>
            ) : (
              <div className="mt-2 text-sm text-slate-500">
                Public link becomes available after the claim reaches published or locked state.
              </div>
            )}

            {linkMessage ? (
              <div className="mt-3 text-xs text-slate-500">{linkMessage}</div>
            ) : null}
          </div>
        </div>

        {usage ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-xs uppercase tracking-wide text-slate-500">Workspace billing posture</div>
                <div className="mt-2 text-lg font-semibold text-slate-900">
                  {effectivePlanName}
                </div>
                <div className="mt-1 text-sm text-slate-600">
                  Current workspace plan and governed claim-capacity posture.
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <div className="text-xs uppercase tracking-wide text-slate-500">Usage state</div>
                <div className="mt-1 font-semibold text-slate-900">{usageLabel}</div>
              </div>
            </div>

            {claimUsage ? (
              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Governed claim usage</span>
                  <span>
                    {claimUsage.used} / {claimUsage.limit}
                  </span>
                </div>
                <div className="mt-2 h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-slate-900 transition-all"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, Number(((claimUsage.ratio ?? 0) * 100).toFixed(1)))
                      )}%`,
                    }}
                  />
                </div>
              </div>
           ) : null}

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => router.push(`/workspace/${workspaceId}/settings?tab=billing`)}
                className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Review Billing & Access
              </button>
            </div>
          </div>
        ) : null}


        <div className="grid gap-3 md:grid-cols-3">
          <StepCard
            title="Verify"
            description="Moves a draft claim into verified state."
            stateLabel={verifyConfig.stateLabel}
            isAvailableNow={verifyConfig.stateAvailable}
            isCompleted={verifyConfig.completed}
            disabled={verifyConfig.disabled}
            loading={loadingAction === "verify"}
            actionLabel="Verify"
            disabledReason={verifyConfig.disabledReason}
            accent="amber"
            onClick={handleVerify}
          />

          <StepCard
            title="Publish"
            description="Moves a verified claim into governed external exposure and shareable trust-surface eligibility."
            stateLabel={publishConfig.stateLabel}
            isAvailableNow={publishConfig.stateAvailable}
            isCompleted={publishConfig.completed}
            disabled={publishConfig.disabled}
            loading={loadingAction === "publish"}
            actionLabel="Publish"
            disabledReason={publishConfig.disabledReason}
            accent="blue"
            onClick={handlePublish}
          />

          <StepCard
            title="Lock"
            description="Finalizes the claim, stores the locked evidence fingerprint, and enables audit-grade integrity review."
            stateLabel={lockConfig.stateLabel}
            isAvailableNow={lockConfig.stateAvailable}
            isCompleted={lockConfig.completed}
            disabled={lockConfig.disabled}
            loading={loadingAction === "lock"}
            actionLabel="Lock"
            disabledReason={lockConfig.disabledReason}
            accent="green"
            onClick={handleLock}
          />
        </div>

        {error ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}
      </div>

      <PaywallModal
        open={paywallState.open}
        onClose={closePaywall}
        reason={paywallState.reason}
        actionLabel={paywallState.actionLabel || "Claim lifecycle action"}
        message={paywallState.message}
        currentPlanName={currentPlanName}
        currentPlanCode={usage?.plan_code || null}
        usageLabel={usageLabel}
        recommendedPlanName={recommendedPlanName}
        onUpgrade={() => {
          router.push(`/workspace/${workspaceId}/settings?tab=billing`);
        }}
      />
    </>
  );
}