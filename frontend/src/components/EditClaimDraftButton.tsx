"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  api,
  getApiErrorCode,
  isApiError,
  type ClaimSchema,
  type WorkspaceUsageSummary,
} from "../lib/api";
import { useAuth } from "./AuthProvider";
import EditClaimDraftModal from "./EditClaimDraftModal";
import PaywallModal from "./PaywallModal";
import { useWorkspaceGate } from "../hooks/useWorkspaceGate";

type Props = {
  claim: ClaimSchema;
  onSaved: (updated: ClaimSchema) => Promise<void> | void;
};

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function StatusBadge({ status }: { status: string }) {
  const normalized = normalizeText(status);

  const cls =
    normalized === "draft"
      ? "border-amber-200 bg-amber-100 text-amber-800"
      : normalized === "locked"
        ? "border-emerald-200 bg-emerald-100 text-emerald-800"
        : "border-slate-200 bg-slate-100 text-slate-700";

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold ${cls}`}
    >
      {status}
    </span>
  );
}

export default function EditClaimDraftButton({ claim, onSaved }: Props) {
  const [open, setOpen] = useState(false);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const { getWorkspaceRole } = useAuth();
  const router = useRouter();
  const { gateAndExecute, paywallState, closePaywall, openPaywall } = useWorkspaceGate();

  const workspaceRole = getWorkspaceRole(claim.workspace_id);
  const normalizedStatus = normalizeText(claim.status);

  useEffect(() => {
    let active = true;

    async function loadUsage() {
      try {
        const result = await api.getWorkspaceUsage(claim.workspace_id);
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
  }, [claim.workspace_id]);

  const isOwner = workspaceRole === "owner";
  const isOperator = workspaceRole === "operator";

  const roleAllowed = isOwner || isOperator;
  const stateAllowed = normalizedStatus === "draft";
  const disabled = !roleAllowed || !stateAllowed;

  const currentPlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.plan_code)
    )?.name || usage?.plan_code || "—";

  const effectivePlanName =
    usage?.plan_catalog?.find(
      (plan) => normalizeText(plan.code) === normalizeText(usage?.effective_plan_code)
    )?.name || usage?.effective_plan_code || currentPlanName;

  const billingActivationRecommended = Boolean(
    (usage?.governance as { billing_activation_recommended?: boolean } | undefined)
      ?.billing_activation_recommended
  );

  const recommendedPlanName = billingActivationRecommended
    ? currentPlanName
    : usage?.upgrade_recommendation?.recommended_plan_name || "Review billing posture";

  const claimUsage = usage?.usage?.claims;
  const usageLabel = claimUsage
    ? `${claimUsage.used} / ${claimUsage.limit}${
        claimUsage.ratio !== null && claimUsage.ratio !== undefined
          ? ` · ${formatPercent(claimUsage.ratio)}`
          : ""
      }`
    : `Effective plan: ${effectivePlanName}`;

  const disabledReason = useMemo(() => {
    if (!stateAllowed) {
      return "Editing disabled: this claim is no longer in draft state.";
    }
    if (!roleAllowed) {
      return "Editing restricted: only workspace owners and operators can edit draft claims.";
    }
    return null;
  }, [stateAllowed, roleAllowed]);

  async function handleOpenEditor() {
    if (disabled) return;

    try {
      await gateAndExecute(
        {
          action: "edit_draft",
          workspaceRole,
          claimStatus: claim.status,
        },
        async () => {
          setOpen(true);
        }
      );
    } catch (err) {
      if (isApiError(err) && err.status === 403) {
        const errorCode = getApiErrorCode(err);

        if (errorCode === "claim_limit_reached") {
          openPaywall({
            reason: "claim_limit_reached",
            actionLabel: "Edit draft",
            message:
              err.payload?.message ||
              err.payload?.upgrade_hint ||
              "This workspace has reached its governed claim capacity. Review billing and plan posture to continue editing workflows.",
          });
          return;
        }

        openPaywall({
          reason: "lifecycle_action_locked",
          actionLabel: "Edit draft",
          message:
            err.payload?.message ||
            err.message ||
            "Draft editing is currently blocked for this workspace.",
        });
        return;
      }

      throw err;
    }
  }

  return (
    <>
      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge status={claim.status} />

        <button
          type="button"
          onClick={() => void handleOpenEditor()}
          disabled={disabled}
          className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
            !disabled
              ? "bg-slate-900 text-white hover:bg-slate-800"
              : "cursor-not-allowed border border-slate-300 bg-slate-100 text-slate-500"
          }`}
        >
          Edit Draft
        </button>

        {disabled && disabledReason ? (
          <div className="text-xs text-slate-500">{disabledReason}</div>
        ) : null}

        <EditClaimDraftModal
          open={open}
          claim={claim}
          onClose={() => setOpen(false)}
          onSaved={onSaved}
        />
      </div>

      <PaywallModal
        open={paywallState.open}
        onClose={closePaywall}
        reason={paywallState.reason}
        actionLabel={paywallState.actionLabel || "Edit draft"}
        message={paywallState.message}
        currentPlanName={currentPlanName}
        currentPlanCode={usage?.plan_code || null}
        usageLabel={usageLabel}
        recommendedPlanName={recommendedPlanName}
        onUpgrade={() => {
          router.push(`/workspace/${claim.workspace_id}/settings?tab=billing`);
        }}
      />
    </>
  );
}