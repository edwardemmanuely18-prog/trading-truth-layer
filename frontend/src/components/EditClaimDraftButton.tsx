"use client";

import { useState } from "react";
import type { ClaimSchema } from "../lib/api";
import EditClaimDraftModal from "./EditClaimDraftModal";

type Props = {
  claim: ClaimSchema;
  onSaved: (updated: ClaimSchema) => Promise<void> | void;
};

export default function EditClaimDraftButton({ claim, onSaved }: Props) {
  const [open, setOpen] = useState(false);

  if (claim.status !== "draft") {
    return null;
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
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
