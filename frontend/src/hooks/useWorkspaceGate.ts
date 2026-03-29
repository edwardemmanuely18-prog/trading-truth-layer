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
  | "edit_draft";

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

function isOperator(role?: string | null) {
  return role === "owner" || role === "operator";
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
    setPaywallState((s) => ({ ...s, open: false }));
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
    const { action, usage, workspaceRole, claimStatus } = ctx;

    // ---------- ROLE GATING ----------
    if (!isOperator(workspaceRole)) {
      return {
        allowed: false,
        reason: "feature_locked",
        message: "You do not have permission to perform this action.",
        actionLabel: action,
      };
    }

    // ---------- ACTION-SPECIFIC LOGIC ----------
    if (action === "create_claim_version") {
      if (!usage) {
        return { allowed: true };
      }

      const claimUsage = usage?.usage?.claims;
      const claimLimitReached =
        (claimUsage?.limit ?? 0) > 0 &&
        (claimUsage?.used ?? 0) >= (claimUsage?.limit ?? 0);

      if (claimLimitReached) {
        return {
          allowed: false,
          reason: "claim_limit_reached",
          message: "Claim limit reached for this workspace.",
          actionLabel: "Create claim version",
        };
      }

      return { allowed: true };
    }

    if (action === "edit_draft") {
      if (claimStatus !== "draft") {
        return {
          allowed: false,
          reason: "edit_locked",
          message: "Only draft claims can be edited.",
          actionLabel: "Edit draft",
        };
      }

      return { allowed: true };
    }

    if (action === "verify_claim") {
      if (claimStatus !== "draft") {
        return {
          allowed: false,
          reason: "lifecycle_action_locked",
          message: "Only draft claims can be verified.",
          actionLabel: "Verify claim",
        };
      }
      return { allowed: true };
    }

    if (action === "publish_claim") {
      if (claimStatus !== "verified") {
        return {
          allowed: false,
          reason: "lifecycle_action_locked",
          message: "Claim must be verified before publishing.",
          actionLabel: "Publish claim",
        };
      }
      return { allowed: true };
    }

    if (action === "lock_claim") {
      if (claimStatus !== "published") {
        return {
          allowed: false,
          reason: "lifecycle_action_locked",
          message: "Only published claims can be locked.",
          actionLabel: "Lock claim",
        };
      }
      return { allowed: true };
    }

    return { allowed: true };
  }, []);

  const gateAndExecute = useCallback(
    async (
      ctx: GateContext,
      fn: () => Promise<void> | void
    ) => {
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