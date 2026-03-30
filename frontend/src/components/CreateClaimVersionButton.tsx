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
  workspaceId?: number;
  currentVersionNumber?: number | null;
  rootClaimId?: number | null;
  parentClaimId?: number | null;
};

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function GovernanceBadge({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-1 font-semibold text-slate-900">{value}</div>
    </div>
  );
}

function resolveGovernanceState(params: {
  loading: boolean;
  usageLoading: boolean;
  canCloneByRole: boolean;
  claimLimitReached: boolean;
  billingActivationRecommended: boolean;
}) {
  const { loading, usageLoading, canCloneByRole, claimLimitReached, billingActivationRecommended } = params;

  if (loading) return "creating version";
  if (usageLoading) return "loading governance";
  if (!canCloneByRole) return "role restricted";
  if (billingActivationRecommended) return "billing activation needed";
  if (claimLimitReached) return "upgrade required";
  return "available";
}

export default function CreateClaimVersionButton({
  claimSchemaId,
  workspaceId,
  currentVersionNumber,
  rootClaimId,
  parentClaimId,
}: Props) {
  const router = useRouter();
  const { getWorkspaceRole } = useAuth();
  const { gateAndExecute, paywallState, closePaywall, openPaywall } = useWorkspaceGate();

  const [loading, setLoading] = useState(false);
  const [usageLoading, setUsageLoading] = useState(Boolean(workspaceId));
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const workspaceRole = workspaceId ? getWorkspaceRole(workspaceId) : null;

  const canCloneByRole = useMemo(() => {
    return workspaceRole === "owner" || workspaceRole === "operator";
  }, [workspaceRole]);

  const claimUsage = usage?.usage?.claims;
  const claimLimitReached =
    (claimUsage?.limit ?? 0) > 0 && (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

  const billingActivationRecommended = Boolean(
    (usage?.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );

  const nextVersionNumber = useMemo(() => {
    if (typeof currentVersionNumber === "number" && currentVersionNumber > 0) {
      return currentVersionNumber + 1;
    }
    return null;
  }, [currentVersionNumber]);

  const governanceState = useMemo(() => {
    return resolveGovernanceState({
      loading,
      usageLoading,
      canCloneByRole,
      claimLimitReached,
      billingActivationRecommended,
    });
  }, [loading, usageLoading, canCloneByRole, claimLimitReached, billingActivationRecommended]);

  useEffect(() => {
    if (!workspaceId) {
      setUsageLoading(false);
      return;
    }

    const resolvedWorkspaceId = workspaceId;
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(resolvedWorkspaceId);
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

  async function createVersion() {
    try {
      setLoading(true);
      setError(null);

      const created = await api.cloneClaimSchema(claimSchemaId);

      if (workspaceId) {
        router.push(`/workspace/${workspaceId}/claim/${created.id}`);
      } else {
        router.push(`/claim/${created.id}`);
      }

      router.refresh();
    } catch (cloneError) {
      if (isApiError(cloneError) && cloneError.status === 403) {
        const errorCode = getApiErrorCode(cloneError);

        if (errorCode === "claim_limit_reached") {
          openPaywall({
            reason: "claim_limit_reached",
            actionLabel: "Create claim version",
            message:
              cloneError.payload?.message ||
              cloneError.payload?.upgrade_hint ||
              "This workspace has reached its governed claim capacity. Review billing and plan posture to continue version creation.",
          });
          return;
        }

        openPaywall({
          reason: "lifecycle_action_locked",
          actionLabel: "Create claim version",
          message:
            cloneError.payload?.message ||
            cloneError.message ||
            "This workspace cannot create another governed claim version right now.",
        });
        return;
      }

      setError(
        cloneError instanceof Error ? cloneError.message : "Failed to create claim version."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleClone() {
    if (loading || usageLoading || !canCloneByRole) return;

    await gateAndExecute(
      {
        action: "create_claim_version",
        usage,
        workspaceRole,
      },
      async () => {
        await createVersion();
      }
    );
  }

  const currentPlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.plan_code)
    )?.name || usage?.plan_code || "—";

  const effectivePlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.effective_plan_code)
    )?.name ||
    usage?.effective_plan_code ||
    currentPlanName;

  const recommendedPlanName = billingActivationRecommended
    ? currentPlanName
    : usage?.upgrade_recommendation?.recommended_plan_name || "Review billing posture";

  const disabled = loading || usageLoading || !canCloneByRole;

  const usageLabel =
    workspaceId && !usageLoading && claimUsage
      ? `${claimUsage.used} / ${claimUsage.limit}${
          claimUsage.ratio !== null && claimUsage.ratio !== undefined
            ? ` · ${formatPercent(claimUsage.ratio)}`
            : ""
        }`
      : `Effective plan: ${effectivePlanName}`;

  const planMismatch =
    normalizeText(usage?.effective_plan_code) &&
    normalizeText(usage?.plan_code) &&
    normalizeText(usage?.effective_plan_code) !== normalizeText(usage?.plan_code);

  return (
    <>
      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-sm font-semibold text-slate-900">Versioning Action</div>
            <div className="mt-1 text-xs leading-5 text-slate-600">
              Create a new governed claim version instead of overwriting the current record. This
              preserves lineage continuity, historical comparability, and downstream audit traceability.
            </div>
          </div>

          <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-semibold text-slate-700">
            {governanceState}
          </span>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <GovernanceBadge label="Workspace role" value={workspaceRole || "unknown"} />
          <GovernanceBadge label="Configured plan" value={currentPlanName} />
          <GovernanceBadge label="Effective plan" value={effectivePlanName} />
          <GovernanceBadge
            label="Claim usage"
            value={
              workspaceId && !usageLoading && claimUsage
                ? `${claimUsage.used} / ${claimUsage.limit}`
                : "—"
            }
          />
          <GovernanceBadge
            label="Usage ratio"
            value={
              workspaceId && !usageLoading && claimUsage
                ? formatPercent(claimUsage.ratio)
                : "—"
            }
          />
          <GovernanceBadge
            label="Current version"
            value={typeof currentVersionNumber === "number" ? currentVersionNumber : "—"}
          />
          <GovernanceBadge
            label="Next version"
            value={typeof nextVersionNumber === "number" ? nextVersionNumber : "auto"}
          />
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div className="text-xs text-slate-500">Root claim</div>
            <div className="mt-1 font-semibold text-slate-900">{rootClaimId ?? claimSchemaId}</div>
            <div className="mt-1 text-xs text-slate-500">
              Governing lineage anchor for the full claim family.
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div className="text-xs text-slate-500">Parent claim</div>
            <div className="mt-1 font-semibold text-slate-900">
              {parentClaimId ?? "current claim becomes parent"}
            </div>
            <div className="mt-1 text-xs text-slate-500">
              Each new version preserves history instead of mutating prior evidence.
            </div>
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-xs leading-6 text-slate-600">
          <div className="font-semibold text-slate-900">Governance effect</div>
          <div className="mt-2">
            Creating a version should preserve lineage continuity, keep the prior claim state intact,
            and support later version-by-version comparison without destroying earlier audit evidence.
          </div>
        </div>

        {planMismatch ? (
          <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
            This workspace is configured on <span className="font-semibold">{currentPlanName}</span>,
            but governed actions currently follow the effective plan posture of{" "}
            <span className="font-semibold">{effectivePlanName}</span>.
          </div>
        ) : null}

        {billingActivationRecommended ? (
          <div className="mt-3 rounded-xl border border-blue-200 bg-blue-50 p-3 text-xs text-blue-800">
            The configured plan already provides the intended capacity posture. The next operational
            step is billing activation so effective enforcement can match{" "}
            <span className="font-semibold">{currentPlanName}</span>.
          </div>
        ) : null}

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            disabled={disabled}
            onClick={() => void handleClone()}
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? "Creating Version..." : "Create New Version"}
          </button>
        </div>

        {!canCloneByRole && workspaceId ? (
          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
            Only workspace owners and operators can create new governed claim versions.
          </div>
        ) : null}

        {claimLimitReached ? (
          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
            Claim capacity has been reached on the current effective workspace plan. Use this action
            to review billing posture and continue governed version creation.
          </div>
        ) : null}

        {error ? (
          <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
            {error}
          </div>
        ) : null}
      </div>

      <PaywallModal
        open={paywallState.open}
        onClose={closePaywall}
        reason={paywallState.reason}
        actionLabel={paywallState.actionLabel || "Create claim version"}
        message={paywallState.message}
        currentPlanName={currentPlanName}
        currentPlanCode={usage?.plan_code || null}
        usageLabel={usageLabel}
        recommendedPlanName={recommendedPlanName}
        onUpgrade={() => {
          if (workspaceId) {
            router.push(`/workspace/${workspaceId}/settings?tab=billing`);
          } else {
            router.push(`/settings?tab=billing`);
          }
        }}
      />
    </>
  );
}