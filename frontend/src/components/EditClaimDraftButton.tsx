"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { ClaimSchema } from "../lib/api";
import { getApiErrorCode, isApiError } from "../lib/api";
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
  const { getWorkspaceRole } = useAuth();
  const router = useRouter();
  const { gateAndExecute, paywallState, closePaywall, openPaywall } = useWorkspaceGate();

  const workspaceRole = getWorkspaceRole(claim.workspace_id);

  const canEditDraft = useMemo(() => {
    if (normalizeText(claim.status) !== "draft") return false;
    return workspaceRole === "owner" || workspaceRole === "operator";
  }, [claim.status, workspaceRole]);

  const disabledReason = useMemo(() => {
    if (normalizeText(claim.status) !== "draft") {
      return "Editing disabled: this claim is no longer in draft state.";
    }
    if (!(workspaceRole === "owner" || workspaceRole === "operator")) {
      return "Editing restricted: only workspace owners and operators can edit draft claims.";
    }
    return null;
  }, [claim.status, workspaceRole]);

  async function handleOpenEditor() {
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

        openPaywall({
          reason: errorCode === "claim_limit_reached" ? "feature_locked" : "edit_locked",
          actionLabel: "Edit draft",
          message:
            err.payload?.message ||
            err.payload?.upgrade_hint ||
            "This draft editing action is currently blocked for the workspace.",
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
          disabled={!canEditDraft}
          className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
            canEditDraft
              ? "bg-slate-900 text-white hover:bg-slate-800"
              : "cursor-not-allowed border border-slate-300 bg-slate-100 text-slate-500"
          }`}
        >
          Edit Draft
        </button>

        {!canEditDraft && disabledReason ? (
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
        currentPlanName="Current workspace plan"
        currentPlanCode={null}
        usageLabel="Draft editing governed by workflow entitlements"
        recommendedPlanName="Higher workspace plan"
        onUpgrade={() => {
          router.push(`/workspace/${claim.workspace_id}/settings?tab=billing`);
        }}
      />
    </>
  );
}