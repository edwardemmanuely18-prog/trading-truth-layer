"use client";

import { useMemo, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "./AuthProvider";

type Props = {
  claimSchemaId: number;
  workspaceId: number;
  status: string;
};

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
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

export default function ClaimLifecycleActions({
  claimSchemaId,
  workspaceId,
  status,
}: Props) {
  const { getWorkspaceRole } = useAuth();

  const [loadingAction, setLoadingAction] = useState<"verify" | "publish" | "lock" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const workspaceRole = getWorkspaceRole(workspaceId);
  const normalizedStatus = normalizeText(status);

  const permissions = useMemo(() => {
    return {
      canVerify: workspaceRole === "owner" || workspaceRole === "operator",
      canPublish: workspaceRole === "owner",
      canLock: workspaceRole === "owner",
    };
  }, [workspaceRole]);

  const verifyAvailable = normalizedStatus === "draft";
  const publishAvailable = normalizedStatus === "verified";
  const lockAvailable = normalizedStatus === "published";

  const verifyCompleted =
    normalizedStatus === "verified" ||
    normalizedStatus === "published" ||
    normalizedStatus === "locked";

  const publishCompleted =
    normalizedStatus === "published" || normalizedStatus === "locked";

  const lockCompleted = normalizedStatus === "locked";

  const verifyDisabled = loadingAction !== null || !verifyAvailable || !permissions.canVerify;
  const publishDisabled = loadingAction !== null || !publishAvailable || !permissions.canPublish;
  const lockDisabled = loadingAction !== null || !lockAvailable || !permissions.canLock;

  const verifyReason =
    !permissions.canVerify
      ? "Only workspace owners and operators can verify claims."
      : !verifyAvailable
        ? "Only draft claims can be verified."
        : null;

  const publishReason =
    !permissions.canPublish
      ? "Only workspace owners can publish claims."
      : !publishAvailable
        ? "Only verified claims can be published."
        : null;

  const lockReason =
    !permissions.canLock
      ? "Only workspace owners can lock claims."
      : !lockAvailable
        ? "Only published claims can be locked."
        : null;

  const verifyClaim = async () => {
    try {
      setLoadingAction("verify");
      setError(null);
      await api.verifyClaimSchema(claimSchemaId);
      window.location.reload();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to verify claim.");
    } finally {
      setLoadingAction(null);
    }
  };

  const publishClaim = async () => {
    try {
      setLoadingAction("publish");
      setError(null);
      await api.publishClaimSchema(claimSchemaId);
      window.location.reload();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to publish claim.");
    } finally {
      setLoadingAction(null);
    }
  };

  const lockClaim = async () => {
    try {
      setLoadingAction("lock");
      setError(null);
      await api.lockClaimSchema(claimSchemaId);
      window.location.reload();
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to lock claim.");
    } finally {
      setLoadingAction(null);
    }
  };

  return (
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
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <StepCard
          title="Verify"
          description="Moves a draft claim into verified state."
          stateLabel={
            verifyCompleted
              ? "completed"
              : verifyAvailable
                ? "available"
                : "not available"
          }
          isAvailableNow={verifyAvailable}
          isCompleted={verifyCompleted}
          disabled={verifyDisabled}
          loading={loadingAction === "verify"}
          actionLabel="Verify"
          disabledReason={verifyReason}
          accent="amber"
          onClick={verifyClaim}
        />

        <StepCard
          title="Publish"
          description="Makes a verified claim publishable for external use."
          stateLabel={
            publishCompleted
              ? "completed"
              : publishAvailable
                ? "available"
                : "not available"
          }
          isAvailableNow={publishAvailable}
          isCompleted={publishCompleted}
          disabled={publishDisabled}
          loading={loadingAction === "publish"}
          actionLabel="Publish"
          disabledReason={publishReason}
          accent="blue"
          onClick={publishClaim}
        />

        <StepCard
          title="Lock"
          description="Finalizes the claim and stores the locked trade-set hash."
          stateLabel={
            lockCompleted
              ? "completed"
              : lockAvailable
                ? "available"
                : "not available"
          }
          isAvailableNow={lockAvailable}
          isCompleted={lockCompleted}
          disabled={lockDisabled}
          loading={loadingAction === "lock"}
          actionLabel="Lock"
          disabledReason={lockReason}
          accent="green"
          onClick={lockClaim}
        />
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
    </div>
  );
}