"use client";

import { useMemo, useState } from "react";

type Props = {
  status?: string | null;
  integrityStatus?: string | null;
  claimHash?: string | null;
  tradeSetHash?: string | null;
  verifiedAt?: string | null;
  lockedAt?: string | null;

  // Phase 7 additions
  issuerName?: string | null;
  issuerNetwork?: string | null;
  exposureLevel?: string | null;
  portable?: boolean;
  canonical?: boolean;
  apiAddressable?: boolean;

  compact?: boolean;
};

function normalize(value: unknown) {
  return String(value ?? "").toLowerCase().trim();
}

function shortHash(value?: string | null, head = 12, tail = 8) {
  const text = String(value ?? "").trim();
  if (!text) return "—";
  if (text.length <= head + tail + 3) return text;
  return `${text.slice(0, head)}...${text.slice(-tail)}`;
}

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function CopyButton({
  value,
  label,
}: {
  value?: string | null;
  label: string;
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <button
      type="button"
      onClick={() => void handleCopy()}
      disabled={!value}
      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {copied ? "Copied" : label}
    </button>
  );
}

function SignatureMetaPill({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-full border border-current/15 bg-white/70 px-3 py-1 text-[11px] font-semibold">
      {label}: {value}
    </div>
  );
}

function FingerprintCard({
  title,
  value,
  shortValue,
  copyLabel,
  helper,
}: {
  title: string;
  value?: string | null;
  shortValue?: string;
  copyLabel: string;
  helper: string;
}) {
  return (
    <div className="rounded-2xl bg-white/70 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-medium opacity-80">{title}</div>
          <div className="mt-2 break-all font-mono text-xs">{value || "—"}</div>
          {value ? <div className="mt-2 text-xs opacity-70">{shortValue}</div> : null}
          <div className="mt-3 text-xs leading-5 opacity-75">{helper}</div>
        </div>

        <CopyButton value={value} label={copyLabel} />
      </div>
    </div>
  );
}

function ReadingCard({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-2xl bg-white/70 p-4">
      <div className="text-sm font-medium opacity-80">{title}</div>
      <div className="mt-2 text-sm leading-6 opacity-85">{body}</div>
    </div>
  );
}

export default function ClaimVerificationSignature({
  status,
  integrityStatus,
  claimHash,
  tradeSetHash,
  verifiedAt,
  lockedAt,
  issuerName,
  issuerNetwork,
  exposureLevel,
  portable = false,
  canonical = false,
  apiAddressable = false,
  compact = false,
}: Props) {
  const normalizedStatus = normalize(status);
  const normalizedIntegrity = normalize(integrityStatus);

  const isDraft = normalizedStatus === "draft" || !normalizedStatus;
  const isVerified = normalizedStatus === "verified";
  const isPublished = normalizedStatus === "published";
  const isLocked = normalizedStatus === "locked";

  const isValid = normalizedIntegrity === "valid";
  const isCompromised = normalizedIntegrity === "compromised";
  const integrityChecked = isValid || isCompromised;

  const signature = useMemo(() => {
    if (isLocked && isValid) {
      return {
        title: "Verified • Locked • Hash Match Confirmed",
        tone: "border-green-200 bg-green-50 text-green-800",
        summary:
          "This claim is finalized and the current in-scope trade set matches the stored locked fingerprint.",
        trustState: "High-trust finalized record",
        verificationMeaning:
          "The record has reached locked state and its evidence fingerprint recomputes successfully.",
      };
    }

    if (isLocked && isCompromised) {
      return {
        title: "Locked • Integrity Alert",
        tone: "border-red-200 bg-red-50 text-red-800",
        summary:
          "This claim is locked, but the recomputed trade-set fingerprint does not match the stored locked fingerprint.",
        trustState: "Integrity mismatch detected",
        verificationMeaning:
          "The record is finalized, but its current trade evidence no longer matches the stored locked state.",
      };
    }

    if (isLocked) {
      return {
        title: "Locked • Integrity Pending Confirmation",
        tone: "border-amber-200 bg-amber-50 text-amber-800",
        summary:
          "This claim is locked, but the integrity state has not yet been confirmed on this surface.",
        trustState: "Finalized record awaiting confirmation",
        verificationMeaning:
          "The record is finalized, but this surface has not yet confirmed whether the stored and recomputed fingerprints match.",
      };
    }

    if (isPublished) {
      return {
        title: "Published Verification Surface",
        tone: "border-blue-200 bg-blue-50 text-blue-800",
        summary:
          "This claim is externally presentable and fingerprinted, but it has not yet reached locked finality.",
        trustState: "Externally visible pre-lock state",
        verificationMeaning:
          "This record is shareable, but it should not yet be interpreted as final locked evidence.",
      };
    }

    if (isVerified) {
      return {
        title: "Verified Internal Claim",
        tone: "border-indigo-200 bg-indigo-50 text-indigo-800",
        summary:
          "This claim has passed internal verification and is eligible for lifecycle progression into publication.",
        trustState: "Internally verified state",
        verificationMeaning:
          "The record passed internal verification, but it is not yet a locked public trust artifact.",
      };
    }

    return {
      title: "Draft / Unfinalized Claim",
      tone: "border-slate-200 bg-slate-50 text-slate-700",
      summary:
        "This claim is still editable or incomplete and should not be treated as finalized public evidence.",
      trustState: "Draft state",
      verificationMeaning:
        "This record is still being prepared and should not be used as conclusive verification evidence.",
    };
  }, [isCompromised, isLocked, isPublished, isValid, isVerified]);

  if (compact) {
    return (
      <div className={`rounded-2xl border px-4 py-4 ${signature.tone}`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="max-w-3xl">
            <div className="text-sm font-semibold">{signature.title}</div>
          </div>

          <div className="flex flex-wrap gap-2">
            <SignatureMetaPill label="status" value={status || "unknown"} />
            <SignatureMetaPill
              label="integrity"
              value={integrityStatus || (isDraft ? "not applicable" : "not checked")}
            />
          </div>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl bg-white/70 p-3">
            <div className="text-[11px] uppercase tracking-wide opacity-70">Claim Hash</div>
            <div className="mt-1 font-mono text-xs">{shortHash(claimHash)}</div>
          </div>

          <div className="rounded-xl bg-white/70 p-3">
            <div className="text-[11px] uppercase tracking-wide opacity-70">Trade Set Hash</div>
            <div className="mt-1 font-mono text-xs">{shortHash(tradeSetHash)}</div>
          </div>
        </div>

        {exposureLevel ? (
          <div className="mt-3 text-xs">
            exposure: <span className="font-semibold">{exposureLevel}</span>
          </div>
        ) : null}

        <div className="mt-4 rounded-xl bg-white/70 p-3 text-xs leading-5 opacity-85">
          <span className="font-semibold">Trust state:</span> {signature.trustState}
        </div>
      </div>
    );
  }

  return (
    <div className={`rounded-3xl border p-6 shadow-sm ${signature.tone}`}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-4xl">
          <div className="text-sm opacity-80">Verification Signature</div>
          <div className="mt-1 text-2xl font-semibold tracking-tight">{signature.title}</div>
          <div className="mt-3 text-sm leading-6 opacity-90">
            {signature.summary} This signature consolidates lifecycle state, integrity state,
            locked-fingerprint context, and canonical claim identity into a single trust summary.
          </div>
        </div>

        <div className="rounded-2xl border border-current/15 bg-white/70 px-4 py-3 text-sm">
          <div>
            status: <span className="font-semibold">{status || "unknown"}</span>
          </div>
          <div className="mt-1">
            integrity:{" "}
            <span className="font-semibold">
              {integrityStatus || (isDraft ? "not applicable" : "not checked")}
            </span>
          </div>
          <div className="mt-1">
            trust state: <span className="font-semibold">{signature.trustState}</span>
          </div>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        <SignatureMetaPill label="status" value={status || "unknown"} />
        <SignatureMetaPill
          label="integrity checked"
          value={integrityChecked ? "yes" : "no"}
        />
        <SignatureMetaPill
          label="verified at"
          value={verifiedAt ? "available" : "missing"}
        />
        <SignatureMetaPill
          label="locked at"
          value={lockedAt ? "available" : "missing"}
        />

        {issuerName ? (
          <SignatureMetaPill label="issuer" value={issuerName} />
        ) : null}

        {issuerNetwork ? (
          <SignatureMetaPill label="network" value={issuerNetwork} />
        ) : null}

        {exposureLevel ? (
          <SignatureMetaPill label="exposure" value={exposureLevel} />
        ) : null}
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <FingerprintCard
          title="Claim Hash Fingerprint"
          value={claimHash}
          shortValue={shortHash(claimHash, 18, 12)}
          copyLabel="Copy Claim Hash"
          helper="Canonical identity fingerprint for this claim definition. If the claim definition changes materially, the claim hash should change."
        />

        <FingerprintCard
          title="Trade Set Hash Fingerprint"
          value={tradeSetHash}
          shortValue={shortHash(tradeSetHash, 18, 12)}
          copyLabel="Copy Trade Set Hash"
          helper="Fingerprint of the in-scope trade evidence used by this record. Integrity checks compare the current trade set against this stored value."
        />

        <div className="mt-6 rounded-2xl border border-indigo-200 bg-indigo-50 p-4">
          <div className="text-sm font-medium text-indigo-700">
            Portable Verification Capabilities
          </div>

          <div className="mt-3 grid gap-2 sm:grid-cols-3 text-xs">
            <div>
              canonical:{" "}
              <span className="font-semibold">
                {canonical ? "true" : "false"}
              </span>
            </div>

            <div>
              portable:{" "}
              <span className="font-semibold">
                {portable ? "true" : "false"}
              </span>
            </div>

            <div>
              api-addressable:{" "}
              <span className="font-semibold">
                {apiAddressable ? "true" : "false"}
              </span>
            </div>
          </div>

          <div className="mt-2 text-xs text-indigo-700/80">
            This record can be distributed, verified externally, and consumed by automated systems.
          </div>
        </div>

        <div className="rounded-2xl bg-white/70 p-4">
          <div className="text-sm opacity-70">Verified At</div>
          <div className="mt-2 font-medium">{formatDateTime(verifiedAt)}</div>
        </div>

        <div className="rounded-2xl bg-white/70 p-4">
          <div className="text-sm opacity-70">Locked At</div>
          <div className="mt-2 font-medium">{formatDateTime(lockedAt)}</div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <ReadingCard
          title="What this proves"
          body={signature.verificationMeaning}
        />
        <ReadingCard
          title="Claim hash meaning"
          body="The claim hash identifies the claim definition itself: scope, methodology, and canonical record identity."
        />
        <ReadingCard
          title="Trade-set hash meaning"
          body="The trade-set hash identifies the exact in-scope trade evidence used for verification and later integrity review."
        />
        <ReadingCard
          title="How to read this record"
          body="Start with lifecycle status, then check integrity, then compare claim hash and trade-set hash, then review evidence and leaderboard context."
        />
      </div>
    </div>
  );
}