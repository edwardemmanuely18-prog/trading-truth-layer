"use client";

import { useCallback, useMemo, useState } from "react";
import type { WorkspaceUsageSummary } from "../lib/api";

type GateReason =
  | "claim_limit_reached"
  | "feature_locked"
  | "lifecycle_action_locked"
  | "edit_locked";

type GateAction =
  | "create_claim_version"
  | "verify_claim"
  | "publish_claim"
  | "lock_claim"
  | "edit_draft"
  | "view_leaderboard"
  | "compare_claims";

type GateContext = {
  action: GateAction;
  usage?: WorkspaceUsageSummary | null;
  workspaceRole?: string | null;
  claimStatus?: string | null;
};

type GateResult =
  | { allowed: true }
  | {
      allowed: false;
      reason: GateReason;
      message?: string;
      actionLabel?: string;
    };

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function isOperator(role?: string | null) {
  const normalized = normalizeText(role);
  return normalized === "owner" || normalized === "operator";
}

function isOwner(role?: string | null) {
  return normalizeText(role) === "owner";
}

function isBillingActive(usage?: WorkspaceUsageSummary | null) {
  return normalizeText(usage?.billing_status) === "active";
}

function getActionLabel(action: GateAction) {
  switch (action) {
    case "create_claim_version":
      return "Create claim version";
    case "verify_claim":
      return "Verify claim";
    case "publish_claim":
      return "Publish claim";
    case "lock_claim":
      return "Lock claim";
    case "edit_draft":
      return "Edit draft";
    case "view_leaderboard":
      return "View leaderboard";
    case "compare_claims":
      return "Compare claims";
    default:
      return "Governed action";
  }
}

function getPlanName(usage?: WorkspaceUsageSummary | null, planCode?: string | null) {
  const normalized = normalizeText(planCode);
  if (!usage?.plan_catalog?.length) {
    return planCode || "current plan";
  }

  const matched = usage.plan_catalog.find(
    (plan) => normalizeText(plan.code) === normalized
  );

  return matched?.name || planCode || "current plan";
}

function buildClaimCapacityMessage(usage?: WorkspaceUsageSummary | null) {
  const governance = usage?.governance;
  const upgrade = usage?.upgrade_recommendation;

  const configuredPlanName = getPlanName(
    usage,
    governance?.configured_plan_code || usage?.plan_code
  );
  const effectivePlanName = getPlanName(
    usage,
    governance?.effective_plan_code || usage?.effective_plan_code
  );
  const recommendedPlanName =
    upgrade?.recommended_plan_name ||
    getPlanName(usage, upgrade?.recommended_plan_code || usage?.plan_code);

  if (governance?.billing_activation_recommended) {
    return `This workspace is already configured on ${configuredPlanName}, but billing is not active yet. Effective enforcement is still falling back to ${effectivePlanName}. Activate billing to continue governed claim version creation.`;
  }

  if (upgrade?.upgrade_required_now && upgrade?.recommended_plan_is_distinct) {
    return `The workspace has reached its governed claim capacity under the current enforced plan posture. Review billing and move to ${recommendedPlanName} to continue governed version creation.`;
  }

  if (upgrade?.already_at_highest_tier) {
    return "The workspace has reached governed capacity on its highest available commercial tier. Review billing posture and operational usage before continuing.";
  }

  return "This workspace has reached its governed claim capacity. Review billing and plan posture before continuing.";
}

function buildLifecycleBlockedMessage(
  action: GateAction,
  claimStatus?: string | null,
  workspaceRole?: string | null
) {
  const normalizedStatus = normalizeText(claimStatus);
  const owner = isOwner(workspaceRole);
  const operator = isOperator(workspaceRole);

  if (action === "edit_draft") {
    if (normalizedStatus !== "draft") {
      return "Draft editing is only available while the claim remains in draft state.";
    }
    if (!operator) {
      return "Only workspace owners and operators can edit draft claims.";
    }
    return "Draft editing is currently blocked for this workspace.";
  }

  if (action === "verify_claim") {
    if (normalizedStatus !== "draft") {
      return "Only draft claims can be verified.";
    }
    if (!operator) {
      return "Only workspace owners and operators can verify claims.";
    }
    return "Claim verification is currently blocked for this workspace.";
  }

  if (action === "publish_claim") {
    if (normalizedStatus !== "verified") {
      return "Only verified claims can be published.";
    }
    if (!owner) {
      return "Only workspace owners can publish claims.";
    }
    return "Claim publication is currently blocked for this workspace.";
  }

  if (action === "lock_claim") {
    if (normalizedStatus !== "published") {
      return "Only published claims can be locked.";
    }
    if (!owner) {
      return "Only workspace owners can lock claims.";
    }
    return "Claim locking is currently blocked for this workspace.";
  }

  if (action === "compare_claims") {
    return "Claim comparison is currently unavailable under the workspace’s current billing posture.";
  }

  if (action === "view_leaderboard") {
    return "Leaderboard access is currently unavailable under the workspace’s current billing posture.";
  }

  return "This governed workflow action is currently blocked.";
}

export function useWorkspaceGate() {
  const [paywallState, setPaywallState] = useState<{
    open: boolean;
    reason: GateReason;
    actionLabel?: string;
    message?: string;
  }>({
    open: false,
    reason: "feature_locked",
  });

  const closePaywall = useCallback(() => {
    setPaywallState((state) => ({ ...state, open: false }));
  }, []);

  const openPaywall = useCallback(
    (payload: {
      reason: GateReason;
      actionLabel?: string;
      message?: string;
    }) => {
      setPaywallState({
        open: true,
        reason: payload.reason,
        actionLabel: payload.actionLabel,
        message: payload.message,
      });
    },
    []
  );

  const checkGate = useCallback((ctx: GateContext): GateResult => {
    const { action, usage, workspaceRole } = ctx;
    const claimStatus = normalizeText(ctx.claimStatus);
    const actionLabel = getActionLabel(action);

    if (action === "publish_claim" || action === "lock_claim") {
      if (!isOwner(workspaceRole)) {
        return {
          allowed: false,
          reason: "feature_locked",
          message: buildLifecycleBlockedMessage(action, ctx.claimStatus, workspaceRole),
          actionLabel,
        };
      }
    } else if (
      action === "verify_claim" ||
      action === "edit_draft" ||
      action === "create_claim_version"
    ) {
      if (!isOperator(workspaceRole)) {
        return {
          allowed: false,
          reason: "feature_locked",
          message: buildLifecycleBlockedMessage(action, ctx.claimStatus, workspaceRole),
          actionLabel,
        };
      }
    }

    if (action === "create_claim_version") {
      if (!usage) {
        return { allowed: true };
      }

      if (!isBillingActive(usage)) {
        return {
          allowed: false,
          reason: "claim_limit_reached",
          message:
            "Billing is not active. Activate billing to enable governed claim creation under the configured plan.",
          actionLabel,
        };
      }

      const claimUsage = usage.usage?.claims;
      const claimLimitReached =
        (claimUsage?.limit ?? 0) > 0 &&
        (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

      if (claimLimitReached) {
        return {
          allowed: false,
          reason: "claim_limit_reached",
          message: buildClaimCapacityMessage(usage),
          actionLabel,
        };
      }

      return { allowed: true };
    }

    if (action === "edit_draft") {
      if (claimStatus !== "draft") {
        return {
          allowed: false,
          reason: "edit_locked",
          message: buildLifecycleBlockedMessage(action, ctx.claimStatus, workspaceRole),
          actionLabel,
        };
      }

      return { allowed: true };
    }

    if (action === "verify_claim") {
      if (claimStatus !== "draft") {
        return {
          allowed: false,
          reason: "lifecycle_action_locked",
          message: buildLifecycleBlockedMessage(action, ctx.claimStatus, workspaceRole),
          actionLabel,
        };
      }

      return { allowed: true };
    }

    if (action === "publish_claim") {
      if (claimStatus !== "verified") {
        return {
          allowed: false,
          reason: "lifecycle_action_locked",
          message: buildLifecycleBlockedMessage(action, ctx.claimStatus, workspaceRole),
          actionLabel,
        };
      }

      return { allowed: true };
    }

    if (action === "lock_claim") {
      if (claimStatus !== "published") {
        return {
          allowed: false,
          reason: "lifecycle_action_locked",
          message: buildLifecycleBlockedMessage(action, ctx.claimStatus, workspaceRole),
          actionLabel,
        };
      }

      return { allowed: true };
    }

    if (action === "compare_claims") {
      if (!isBillingActive(usage)) {
        return {
          allowed: false,
          reason: "feature_locked",
          message: "Claim comparison is available under an active billing plan.",
          actionLabel,
        };
      }

      return { allowed: true };
    }

    if (action === "view_leaderboard") {
      if (!isBillingActive(usage)) {
        return {
          allowed: false,
          reason: "feature_locked",
          message: "Leaderboard access requires an active billing posture.",
          actionLabel,
        };
      }

      return { allowed: true };
    }

    return { allowed: true };
  }, []);

  const gateAndExecute = useCallback(
    async (ctx: GateContext, fn: () => Promise<void> | void) => {
      const result = checkGate(ctx);

      if (!result.allowed) {
        openPaywall({
          reason: result.reason,
          actionLabel: result.actionLabel,
          message: result.message,
        });
        return;
      }

      await fn();
    },
    [checkGate, openPaywall]
  );

  return useMemo(
    () => ({
      checkGate,
      gateAndExecute,
      paywallState,
      openPaywall,
      closePaywall,
    }),
    [checkGate, gateAndExecute, paywallState, openPaywall, closePaywall]
  );
}