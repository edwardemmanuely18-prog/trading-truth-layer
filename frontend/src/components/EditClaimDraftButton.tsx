"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { ClaimSchema } from "../lib/api";
import { useAuth } from "./AuthProvider";
import EditClaimDraftModal from "./EditClaimDraftModal";
import PaywallModal from "./PaywallModal";
import { useWorkspaceGate } from "../hooks/useWorkspaceGate";

type Props = {
  claim: ClaimSchema;
  onSaved: (updated: ClaimSchema) => Promise<void> | void;
};

function StatusBadge({ status }: { status: string }) {
  const normalized = status?.toLowerCase?.() || "";

  const cls =
    normalized === "draft"
      ? "bg-amber-100 text-amber-800 border-amber-200"
      : normalized === "locked"
        ? "bg-emerald-100 text-emerald-800 border-emerald-200"
        : "bg-slate-100 text-slate-700 border-slate-200";

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
  const { gateAndExecute, paywallState, closePaywall } = useWorkspaceGate();

  const workspaceRole = getWorkspaceRole(claim.workspace_id);

  const canEditDraft = useMemo(() => {
    if (claim.status !== "draft") return false;
    return workspaceRole === "owner" || workspaceRole === "operator";
  }, [claim.status, workspaceRole]);

  const disabledReason = useMemo(() => {
    if (claim.status !== "draft") {
      return "Editing disabled: claim is no longer in draft state.";
    }
    if (!(workspaceRole === "owner" || workspaceRole === "operator")) {
      return "Editing restricted: insufficient permissions.";
    }
    return null;
  }, [claim.status, workspaceRole]);

  async function handleOpenEditor() {
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
  }

  return (
    <>
      <div className="flex items-center gap-3">
        <StatusBadge status={claim.status} />

        <button
          type="button"
          onClick={() => void handleOpenEditor()}
          disabled={false}
          className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
            canEditDraft
              ? "bg-slate-900 text-white hover:bg-slate-800"
              : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
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
        usageLabel="Controlled by workflow entitlements"
        recommendedPlanName="Pro or Team"
        onUpgrade={() => {
          router.push(`/workspace/${claim.workspace_id}/settings?tab=billing`);
        }}
      />
    </>
  );
}