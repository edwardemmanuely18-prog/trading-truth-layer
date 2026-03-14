type Props = {
  name: string;
  claimSchemaId: number;
  verificationStatus: string;
  integrityStatus: "valid" | "compromised";
  tradeCount: number;
  netPnl: number;
  profitFactor: number;
  winRate: number;
  claimHash: string;
  verifyHref: string;
};

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(digits);
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();

  const className =
    normalized === "locked"
      ? "border-green-200 bg-green-100 text-green-800"
      : normalized === "published"
        ? "border-blue-200 bg-blue-100 text-blue-800"
        : normalized === "verified"
          ? "border-amber-200 bg-amber-100 text-amber-800"
          : "border-slate-200 bg-slate-100 text-slate-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${className}`}>
      {status}
    </span>
  );
}

function IntegrityBadge({ status }: { status: "valid" | "compromised" }) {
  const className =
    status === "valid"
      ? "border-green-200 bg-green-100 text-green-800"
      : "border-red-200 bg-red-100 text-red-800";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium ${className}`}>
      integrity {status}
    </span>
  );
}

export default function VerificationBadgeCard({
  name,
  claimSchemaId,
  verificationStatus,
  integrityStatus,
  tradeCount,
  netPnl,
  profitFactor,
  winRate,
  claimHash,
  verifyHref,
}: Props) {
  return (
    <section className="w-full max-w-[560px] rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Trading Truth Layer
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900">{name}</h1>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={verificationStatus} />
            <IntegrityBadge status={integrityStatus} />
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              claim #{claimSchemaId}
            </span>
          </div>
        </div>

        <a
          href={verifyHref}
          className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
        >
          Open Verification
        </a>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-2xl bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Trades</div>
          <div className="mt-1 text-lg font-bold text-slate-900">{tradeCount}</div>
        </div>

        <div className="rounded-2xl bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Net PnL</div>
          <div className="mt-1 text-lg font-bold text-slate-900">{formatNumber(netPnl)}</div>
        </div>

        <div className="rounded-2xl bg-slate-50 p-3">
          <div className="text-xs text-slate-500">PF</div>
          <div className="mt-1 text-lg font-bold text-slate-900">
            {formatNumber(profitFactor, 4)}
          </div>
        </div>

        <div className="rounded-2xl bg-slate-50 p-3">
          <div className="text-xs text-slate-500">Win Rate</div>
          <div className="mt-1 text-lg font-bold text-slate-900">{formatNumber(winRate, 4)}</div>
        </div>
      </div>

      <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-xs text-slate-500">Claim Hash</div>
        <div className="mt-2 break-all font-mono text-xs text-slate-700">{claimHash}</div>
      </div>

      <div className="mt-4 text-xs leading-6 text-slate-500">
        Lifecycle-governed, publicly verifiable, and evidence-exportable trading claim.
      </div>
    </section>
  );
}
