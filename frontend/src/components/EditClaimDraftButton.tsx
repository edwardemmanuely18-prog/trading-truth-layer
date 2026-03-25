"use client";

import { useMemo, useState } from "react";
import type { ClaimSchema } from "../lib/api";
import { useAuth } from "./AuthProvider";
import EditClaimDraftModal from "./EditClaimDraftModal";

type Props = {
  claim: ClaimSchema;
  onSaved: (updated: ClaimSchema) => Promise<void> | void;
};

export default function EditClaimDraftButton({ claim, onSaved }: Props) {
  const [open, setOpen] = useState(false);
  const { getWorkspaceRole } = useAuth();

  const workspaceRole = getWorkspaceRole(claim.workspace_id);

  const canEditDraft = useMemo(() => {
    if (claim.status !== "draft") return false;
    return workspaceRole === "owner" || workspaceRole === "operator";
  }, [claim.status, workspaceRole]);

  if (!canEditDraft) {
    return null;
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
      >
        Edit Draft
      </button>

      <EditClaimDraftModal
        open={open}
        claim={claim}
        onClose={() => setOpen(false)}
        onSaved={onSaved}
      />
    </>
  );
}