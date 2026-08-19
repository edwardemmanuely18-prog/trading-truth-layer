"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowLeft,
  ChevronDown,
  ChevronRight,
  Copy,
  RefreshCw,
} from "lucide-react";

import {
  useParams,
  useRouter,
} from "next/navigation";

import Navbar from "../../../../../components/Navbar";
import {
  api,
  type V2EvidenceRegistryDetail,
} from "../../../../../lib/api";

function displayValue(
  value: unknown,
): string {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Not captured";
  }

  return String(value);
}

function hasValue(value: unknown): boolean {
  return !(
    value === null ||
    value === undefined ||
    value === ""
  );
}

// ============================================================================
// Evidence Field Applicability
// ============================================================================
//
// This matrix defines which business fields are semantically applicable to
// each canonical evidence type.
//
// IMPORTANT:
// - "applicable" means the field belongs to that evidence type.
// - A null value for an applicable field means the source did not provide it.
// - A field absent from the matrix is not rendered.
//
// This is a presentation contract for the canonical evidence detail page.
// The authoritative backend applicability policy should eventually consume
// the same contract.
//

type EvidenceFieldGroup =
  | "identifiers"
  | "instrument"
  | "execution"
  | "financial";

type EvidenceField =
  | "ticket"
  | "order"
  | "deal"
  | "position"
  | "execution"
  | "symbol"
  | "asset_class"
  | "market"
  | "exchange"
  | "side"
  | "volume"
  | "entry_price"
  | "exit_price"
  | "executed_at"
  | "order_id"
  | "deal_id"
  | "position_id"
  | "profit"
  | "commission"
  | "swap"
  | "fees"
  | "balance"
  | "equity";

type EvidenceApplicability = Record<
  EvidenceFieldGroup,
  readonly EvidenceField[]
>;

const EVIDENCE_FIELD_APPLICABILITY: Record<
  string,
  EvidenceApplicability
> = {
  POSITION: {
    identifiers: [
      "position",
    ],
    instrument: [
      "symbol",
      "asset_class",
      "market",
      "exchange",
    ],
    execution: [
      "side",
      "volume",
      "entry_price",
      "exit_price",
      "executed_at",
      "position_id",
    ],
    financial: [
      "profit",
      "commission",
      "swap",
      "fees",
    ],
  },

  DEAL: {
    identifiers: [
      "order",
      "deal",
    ],
    instrument: [
      "symbol",
      "asset_class",
      "market",
      "exchange",
    ],
    execution: [
      "side",
      "volume",
      "entry_price",
      "exit_price",
      "executed_at",
      "order_id",
      "deal_id",
      "position_id",
    ],
    financial: [
      "profit",
      "commission",
      "swap",
      "fees",
    ],
  },

  ACCOUNT: {
    identifiers: [],
    instrument: [],
    execution: [],
    financial: [
      "balance",
      "equity",
    ],
  },

  BALANCE: {
    identifiers: [
      "ticket",
      "order",
      "deal",
    ],
    instrument: [],
    execution: [],
    financial: [
      "profit",
      "commission",
      "swap",
      "fees",
      "balance",
    ],
  },

  MARGIN: {
    identifiers: [],
    instrument: [],
    execution: [],
    financial: [
      "balance",
      "equity",
    ],
  },

  EQUITY: {
    identifiers: [],
    instrument: [],
    execution: [],
    financial: [
      "balance",
      "equity",
    ],
  },

  HISTORY: {
    identifiers: [
      "ticket",
      "order",
      "deal",
      "position",
      "execution",
    ],
    instrument: [
      "symbol",
      "asset_class",
      "market",
      "exchange",
    ],
    execution: [
      "side",
      "volume",
      "entry_price",
      "exit_price",
      "executed_at",
      "order_id",
      "deal_id",
      "position_id",
    ],
    financial: [
      "profit",
      "commission",
      "swap",
      "fees",
      "balance",
      "equity",
    ],
  },

  SYMBOL: {
    identifiers: [],
    instrument: [
      "symbol",
      "asset_class",
      "market",
      "exchange",
    ],
    execution: [],
    financial: [],
  },

  CUSTOM: {
    identifiers: [],
    instrument: [],
    execution: [],
    financial: [],
  },
};

function isFieldApplicable(
  evidenceType: string,
  group: EvidenceFieldGroup,
  field: EvidenceField,
): boolean {
  return Boolean(
    EVIDENCE_FIELD_APPLICABILITY[evidenceType]?.[group]?.includes(field),
  );
}

function formatTimestamp(
  value: string | null,
): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-GB",
    {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      timeZoneName: "short",
      hour12: false,
    },
  ).format(date);
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-6 py-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
          {title}
        </h2>
      </div>

      <div className="px-6 py-5">
        {children}
      </div>
    </section>
  );
}

function Field({
  label,
  value,
  mono = false,
  applicable = true,
}: {
  label: string;
  value: unknown;
  mono?: boolean;
  applicable?: boolean;
}) {
  if (!applicable || !hasValue(value)) {
    return null;
  }

  return (
    <div className="min-w-0">
      <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </div>

      <div
        className={`mt-1 break-words text-sm text-slate-800 ${
          mono ? "font-mono text-xs" : ""
        }`}
      >
        {displayValue(value)}
      </div>
    </div>
  );
}

function JsonViewer({
  value,
}: {
  value: unknown;
}) {
  if (value === null || value === undefined) {
    return (
      <div className="text-sm text-slate-500">
        No payload available.
      </div>
    );
  }

  return (
    <pre className="max-h-[520px] overflow-auto rounded-xl border border-slate-200 bg-slate-950 p-5 text-xs leading-6 text-slate-100">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

export default function EvidenceDetailPage() {
  const params = useParams<{
    workspaceId: string;
    canonicalEvidenceId: string;
  }>();

  const router = useRouter();

  const workspaceId = Number(
    params.workspaceId,
  );

  const canonicalEvidenceId =
    decodeURIComponent(
      params.canonicalEvidenceId,
    );

  const [record, setRecord] =
    useState<V2EvidenceRegistryDetail | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [showCanonical, setShowCanonical] =
    useState(false);

  const [showProvenance, setShowProvenance] =
    useState(false);

  const [copied, setCopied] =
    useState(false);

  async function loadRecord() {
    try {
      setLoading(true);
      setError(null);

      const response =
        await api.getV2EvidenceRecord(
          workspaceId,
          canonicalEvidenceId,
        );

      setRecord(response);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Unable to load the evidence record.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (
      !Number.isFinite(workspaceId) ||
      !canonicalEvidenceId
    ) {
      setError(
        "Invalid evidence record.",
      );

      setLoading(false);
      return;
    }

    void loadRecord();
  }, [
    workspaceId,
    canonicalEvidenceId,
  ]);

  const canonical =
    record?.canonical_payload ?? null;

  const evidenceType =
    record?.evidence_type ??
    (
      canonical &&
      typeof canonical.evidence_type === "string"
        ? canonical.evidence_type
        : ""
    );

  const applicability =
    EVIDENCE_FIELD_APPLICABILITY[evidenceType] ?? {
      identifiers: [],
      instrument: [],
      execution: [],
      financial: [],
    };

  const provenance =
    record?.provenance_payload ?? null;

  const instrument =
    canonical &&
    typeof canonical.instrument === "object" &&
    canonical.instrument !== null
      ? canonical.instrument as Record<
          string,
          unknown
        >
      : null;

  const execution =
    canonical &&
    typeof canonical.execution === "object" &&
    canonical.execution !== null
      ? canonical.execution as Record<
          string,
          unknown
        >
      : null;

  const financial =
    canonical &&
    typeof canonical.financial === "object" &&
    canonical.financial !== null
      ? canonical.financial as Record<
          string,
          unknown
        >
      : null;

  const identity =
    canonical &&
    typeof canonical.identity === "object" &&
    canonical.identity !== null
      ? canonical.identity as Record<
          string,
          unknown
        >
      : null;

  const synchronizedAt = useMemo(() => {
    if (
      canonical &&
      typeof canonical.synchronized_at === "string"
    ) {
      return canonical.synchronized_at;
    }

    return null;
  }, [canonical]);

  const showIdentifiers =
    (
      isFieldApplicable(evidenceType, "identifiers", "ticket") &&
      hasValue(record?.provider.original_ticket_id)
    ) ||
    (
      isFieldApplicable(evidenceType, "identifiers", "order") &&
      hasValue(record?.provider.original_order_id)
    ) ||
    (
      isFieldApplicable(evidenceType, "identifiers", "deal") &&
      hasValue(record?.provider.original_deal_id)
    ) ||
    (
      isFieldApplicable(evidenceType, "identifiers", "position") &&
      hasValue(record?.provider.original_position_id)
    ) ||
    (
      isFieldApplicable(evidenceType, "identifiers", "execution") &&
      hasValue(record?.provider.original_execution_id)
    );

  const showInstrument =
    (
      isFieldApplicable(evidenceType, "instrument", "symbol") &&
      hasValue(instrument?.symbol)
    ) ||
    (
      isFieldApplicable(evidenceType, "instrument", "asset_class") &&
      hasValue(instrument?.asset_class)
    ) ||
    (
      isFieldApplicable(evidenceType, "instrument", "market") &&
      hasValue(instrument?.market)
    ) ||
    (
      isFieldApplicable(evidenceType, "instrument", "exchange") &&
      hasValue(instrument?.exchange)
    );

  const showExecution =
    (
      isFieldApplicable(evidenceType, "execution", "side") &&
      hasValue(execution?.side)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "volume") &&
      hasValue(execution?.volume)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "entry_price") &&
      hasValue(execution?.entry_price)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "exit_price") &&
      hasValue(execution?.exit_price)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "executed_at") &&
      hasValue(execution?.executed_at)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "order_id") &&
      hasValue(execution?.order_id)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "deal_id") &&
      hasValue(execution?.deal_id)
    ) ||
    (
      isFieldApplicable(evidenceType, "execution", "position_id") &&
      hasValue(execution?.position_id)
    );

  const showFinancial =
    (
      isFieldApplicable(evidenceType, "financial", "profit") &&
      hasValue(financial?.profit)
    ) ||
    (
      isFieldApplicable(evidenceType, "financial", "commission") &&
      hasValue(financial?.commission)
    ) ||
    (
      isFieldApplicable(evidenceType, "financial", "swap") &&
      hasValue(financial?.swap)
    ) ||
    (
      isFieldApplicable(evidenceType, "financial", "fees") &&
      hasValue(financial?.fees)
    ) ||
    (
      isFieldApplicable(evidenceType, "financial", "balance") &&
      hasValue(financial?.balance)
    ) ||
    (
      isFieldApplicable(evidenceType, "financial", "equity") &&
      hasValue(financial?.equity)
    );

  async function copyEvidenceId() {
    try {
      await navigator.clipboard.writeText(
        canonicalEvidenceId,
      );

      setCopied(true);

      window.setTimeout(
        () => setCopied(false),
        1500,
      );
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-8">
          <button
            type="button"
            onClick={() =>
              router.push(
                `/workspace/${workspaceId}/evidence-explorer`,
              )
            }
            className="mb-5 inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-950"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Evidence Explorer
          </button>

          <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
            Evidence Registry
          </div>

          <div className="mt-2 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold text-slate-950">
                Evidence Detail
              </h1>

              <div className="mt-3 flex flex-wrap items-center gap-3">
                <span className="rounded-lg bg-slate-100 px-3 py-1.5 font-mono text-xs text-slate-700">
                  {canonicalEvidenceId}
                </span>

                <button
                  type="button"
                  onClick={() =>
                    void copyEvidenceId()
                  }
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
                >
                  <Copy className="h-3.5 w-3.5" />
                  {copied ? "Copied" : "Copy ID"}
                </button>
              </div>
            </div>

            <button
              type="button"
              onClick={() => void loadRecord()}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              <RefreshCw className="h-4 w-4" />
              Refresh
            </button>
          </div>

          <p className="mt-4 max-w-4xl text-sm leading-6 text-slate-600">
            Authoritative V2 evidence record retrieved directly
            from the durable evidence registry.
          </p>
        </div>

        {loading && (
          <div className="rounded-2xl border border-slate-200 bg-white p-16 text-center shadow-sm">
            <div className="text-lg font-semibold text-slate-700">
              Loading Evidence Record...
            </div>

            <div className="mt-2 text-sm text-slate-500">
              Retrieving the canonical evidence record.
            </div>
          </div>
        )}

        {!loading && error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
            <div className="text-sm font-semibold text-red-800">
              Evidence Record Unavailable
            </div>

            <div className="mt-2 text-sm text-red-700">
              {error}
            </div>

            <button
              type="button"
              onClick={() => void loadRecord()}
              className="mt-4 rounded-lg bg-red-700 px-4 py-2 text-sm font-semibold text-white hover:bg-red-800"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && record && (
          <div className="space-y-6">
            {/* ========================================================= */}
            {/* Identity */}
            {/* ========================================================= */}

            <Section title="Identity">
              <div className="grid gap-6 md:grid-cols-3">
                <Field
                  label="Evidence ID"
                  value={
                    record.canonical_evidence_id
                  }
                  mono
                />

                <Field
                  label="Evidence Type"
                  value={
                    record.evidence_type
                  }
                />

                <Field
                  label="Lifecycle"
                  value={
                    record.lifecycle
                  }
                />

                <Field
                  label="Evidence Version"
                  value={
                    record.evidence_version
                  }
                />

                <Field
                  label="Workspace ID"
                  value={
                    record.workspace_id
                  }
                  mono
                />

                <Field
                  label="Provider ID"
                  value={
                    record.provider_id
                  }
                  mono
                />
              </div>
            </Section>

            {/* ========================================================= */}
            {/* Provider */}
            {/* ========================================================= */}

            <Section title="Provider">
              <div className="grid gap-6 md:grid-cols-3">
                <Field
                  label="Provider"
                  value={
                    record.provider.provider_name
                  }
                />

                <Field
                  label="Platform"
                  value={
                    record.provider.provider_platform
                  }
                />

                <Field
                  label="Broker / Server"
                  value={
                    record.provider.broker_server
                  }
                />

                <Field
                  label="Account"
                  value={
                    record.provider.broker_account_id
                  }
                  mono
                />

                <Field
                  label="Account Name"
                  value={
                    record.provider.broker_account_name
                  }
                />

                <Field
                  label="Environment / State"
                  value={
                    record.provider.account_state
                  }
                />

                <Field
                  label="Currency"
                  value={
                    record.provider.account_currency
                  }
                />
              </div>
            </Section>

            {/* ========================================================= */}
            {/* Synchronization */}
            {/* ========================================================= */}

            <Section title="Synchronization">
              <div className="grid gap-6 md:grid-cols-3">
                <Field
                  label="Session"
                  value={
                    record.synchronization_session
                  }
                  mono
                />

                <Field
                  label="Batch"
                  value={
                    record.synchronization_batch
                  }
                  mono
                />

                <Field
                  label="Registered At"
                  value={
                    record.registered_at_utc
                      ? `${formatTimestamp(
                          record.registered_at_utc,
                        )} UTC`
                      : null
                  }
                />

                <Field
                  label="Synchronized At"
                  value={
                    synchronizedAt
                      ? formatTimestamp(
                          synchronizedAt,
                        )
                      : null
                  }
                />

                <Field
                  label="Registry Timezone"
                  value={
                    record.registered_at_timezone
                  }
                />
              </div>
            </Section>

            {/* ========================================================= */}
            {/* Identifiers */}
            {/* ========================================================= */}

            {showIdentifiers && (
            <Section title="Identifiers">
              <div className="grid gap-6 md:grid-cols-3">
                <Field
                  label="Ticket"
                  value={record.provider.original_ticket_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "identifiers",
                    "ticket",
                  )}
                />

                <Field
                  label="Order"
                  value={record.provider.original_order_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "identifiers",
                    "order",
                  )}
                />

                <Field
                  label="Deal"
                  value={record.provider.original_deal_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "identifiers",
                    "deal",
                  )}
                />

                <Field
                  label="Position"
                  value={record.provider.original_position_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "identifiers",
                    "position",
                  )}
                />

                <Field
                  label="Execution"
                  value={record.provider.original_execution_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "identifiers",
                    "execution",
                  )}
                />
              </div>
            </Section>
            )}

            {/* ========================================================= */}
            {/* Instrument */}
            {/* ========================================================= */}

            {showInstrument && (
            <Section title="Instrument">
              <div className="grid gap-6 md:grid-cols-4">
                <Field
                  label="Symbol"
                  value={instrument?.symbol}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "instrument",
                    "symbol",
                  )}
                />

                <Field
                  label="Asset Class"
                  value={instrument?.asset_class}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "instrument",
                    "asset_class",
                  )}
                />

                <Field
                  label="Market"
                  value={instrument?.market}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "instrument",
                    "market",
                  )}
                />

                <Field
                  label="Exchange"
                  value={instrument?.exchange}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "instrument",
                    "exchange",
                  )}
                />
              </div>
            </Section>
            )}

            {/* ========================================================= */}
            {/* Execution */}
            {/* ========================================================= */}

            {showExecution && (
            <Section title="Execution">
              <div className="grid gap-6 md:grid-cols-4">
                <Field
                  label="Side"
                  value={execution?.side}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "side",
                  )}
                />

                <Field
                  label="Volume"
                  value={execution?.volume}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "volume",
                  )}
                />

                <Field
                  label="Entry Price"
                  value={execution?.entry_price}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "entry_price",
                  )}
                />

                <Field
                  label="Exit Price"
                  value={execution?.exit_price}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "exit_price",
                  )}
                />

                <Field
                  label="Executed At"
                  value={
                    typeof execution?.executed_at === "string"
                      ? formatTimestamp(execution.executed_at)
                      : execution?.executed_at
                  }
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "executed_at",
                  )}
                />

                <Field
                  label="Order ID"
                  value={execution?.order_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "order_id",
                  )}
                />

                <Field
                  label="Deal ID"
                  value={execution?.deal_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "deal_id",
                  )}
                />

                <Field
                  label="Position ID"
                  value={execution?.position_id}
                  mono
                  applicable={isFieldApplicable(
                    evidenceType,
                    "execution",
                    "position_id",
                  )}
                />
              </div>
            </Section>
            )}

            {/* ========================================================= */}
            {/* Financial */}
            {/* ========================================================= */}

            {showFinancial && (
            <Section title="Financial">
              <div className="grid gap-6 md:grid-cols-3">
                <Field
                  label="Profit"
                  value={financial?.profit}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "financial",
                    "profit",
                  )}
                />

                <Field
                  label="Commission"
                  value={financial?.commission}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "financial",
                    "commission",
                  )}
                />

                <Field
                  label="Swap"
                  value={financial?.swap}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "financial",
                    "swap",
                  )}
                />

                <Field
                  label="Fees"
                  value={financial?.fees}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "financial",
                    "fees",
                  )}
                />

                <Field
                  label="Balance"
                  value={financial?.balance}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "financial",
                    "balance",
                  )}
                />

                <Field
                  label="Equity"
                  value={financial?.equity}
                  applicable={isFieldApplicable(
                    evidenceType,
                    "financial",
                    "equity",
                  )}
                />
              </div>
            </Section>
            )}

            {/* ========================================================= */}
            {/* Integrity */}
            {/* ========================================================= */}

            <Section title="Integrity">
              <div className="grid gap-6 md:grid-cols-3">
                <Field
                  label="Evidence Hash"
                  value={
                    record.evidence_hash
                  }
                  mono
                />

                <Field
                  label="Payload Hash"
                  value={
                    record.payload_hash
                  }
                  mono
                />

                <Field
                  label="Evidence Version"
                  value={
                    record.evidence_version
                  }
                />

                <Field
                  label="Payload Size"
                  value={
                    record.evidence_payload_size !==
                    null
                      ? `${record.evidence_payload_size} bytes`
                      : null
                  }
                />
              </div>
            </Section>

            {/* ========================================================= */}
            {/* Canonical Identity */}
            {/* ========================================================= */}

            {identity && (
              <Section title="Canonical Identity">
                <div className="grid gap-6 md:grid-cols-3">
                  <Field
                    label="Canonical Evidence ID"
                    value={
                      identity.canonical_evidence_id
                    }
                    mono
                  />

                  <Field
                    label="Evidence Hash"
                    value={
                      identity.evidence_hash
                    }
                    mono
                  />

                  <Field
                    label="Evidence Version"
                    value={
                      identity.evidence_version
                    }
                  />
                </div>
              </Section>
            )}

            {/* ========================================================= */}
            {/* Provenance */}
            {/* ========================================================= */}

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <button
                type="button"
                onClick={() =>
                  setShowProvenance(
                    (value) => !value,
                  )
                }
                className="flex w-full items-center justify-between px-6 py-4 text-left"
              >
                <div>
                  <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Provenance
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Immutable lineage and acquisition provenance.
                  </p>
                </div>

                {showProvenance ? (
                  <ChevronDown className="h-5 w-5 text-slate-400" />
                ) : (
                  <ChevronRight className="h-5 w-5 text-slate-400" />
                )}
              </button>

              {showProvenance && (
                <div className="border-t border-slate-200 p-6">
                  <JsonViewer value={provenance} />
                </div>
              )}
            </section>

            {/* ========================================================= */}
            {/* Canonical Evidence */}
            {/* ========================================================= */}

            <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <button
                type="button"
                onClick={() =>
                  setShowCanonical(
                    (value) => !value,
                  )
                }
                className="flex w-full items-center justify-between px-6 py-4 text-left"
              >
                <div>
                  <h2 className="text-sm font-semibold uppercase tracking-[0.14em] text-slate-500">
                    Raw / Canonical Evidence
                  </h2>

                  <p className="mt-1 text-xs text-slate-500">
                    Expandable audit representation of the persisted canonical payload.
                  </p>
                </div>

                {showCanonical ? (
                  <ChevronDown className="h-5 w-5 text-slate-400" />
                ) : (
                  <ChevronRight className="h-5 w-5 text-slate-400" />
                )}
              </button>

              {showCanonical && (
                <div className="border-t border-slate-200 p-6">
                  <JsonViewer value={canonical} />
                </div>
              )}
            </section>
          </div>
        )}
      </main>
    </div>
  );
}