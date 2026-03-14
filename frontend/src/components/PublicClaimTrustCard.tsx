type Props = {
  name: string;
  claimSchemaId: number;
  verificationStatus: string;
  integrityStatus: "valid" | "compromised";
  tradeCount: number;
  netPnl: number;
  profitFactor: number;
  winRate: number;
  periodStart: string;
  periodEnd: string;
  claimHash: string;
};

function formatNumber(value?: number | null, digits = 2) {
  if (value === null || value === undefined) return "—";
  return Number(value).toFixed(digits);
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();

  const className =
    normalized === "locked"
      ? "bg-green-100 text-green-800 border-green-200"
      : normalized === "published"
        ? "bg-blue-100 text-blue-800 border-blue-200"
        : normalized === "verified"
          ? "bg-amber-100 text-amber-800 border-amber-200"
          : "bg-slate-100 text-slate-800 border-slate-200";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      {status}
    </span>
  );
}

function IntegrityBadge({ status }: { status: "valid" | "compromised" }) {
  const className =
    status === "valid"
      ? "bg-green-100 text-green-800 border-green-200"
      : "bg-red-100 text-red-800 border-red-200";

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-sm font-medium ${className}`}>
      integrity {status}
    </span>
  );
}

export default function PublicClaimTrustCard({
  name,
  claimSchemaId,
  verificationStatus,
  integrityStatus,
  tradeCount,
  netPnl,
  profitFactor,
  winRate,
  periodStart,
  periodEnd,
  claimHash,
}: Props) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-sm font-medium text-slate-500">Trading Truth Layer</div>
          <h2 className="mt-2 text-3xl font-bold tracking-tight">{name}</h2>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge status={verificationStatus} />
            <IntegrityBadge status={integrityStatus} />
            <span className="inline-flex rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
              claim #{claimSchemaId}
            </span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-right shadow-sm">
          <div className="text-xs uppercase tracking-wide text-slate-500">Verification Window</div>
          <div className="mt-1 text-sm font-semibold text-slate-900">
            {periodStart} → {periodEnd}
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-sm text-slate-500">Trade Count</div>
          <div className="mt-1 text-2xl font-bold">{tradeCount}</div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-sm text-slate-500">Net PnL</div>
          <div className="mt-1 text-2xl font-bold">{formatNumber(netPnl)}</div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-sm text-slate-500">Profit Factor</div>
          <div className="mt-1 text-2xl font-bold">{formatNumber(profitFactor, 4)}</div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-sm text-slate-500">Win Rate</div>
          <div className="mt-1 text-2xl font-bold">{formatNumber(winRate, 4)}</div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-[1.2fr_2fr]">
        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-sm text-slate-500">Trust Statement</div>
          <div className="mt-2 text-sm leading-7 text-slate-700">
            This claim is lifecycle-governed, hash-verifiable, and evidence-exportable through the
            Trading Truth Layer verification engine.
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-sm text-slate-500">Claim Hash</div>
          <div className="mt-2 break-all font-mono text-xs text-slate-700">{claimHash}</div>
        </div>
      </div>
    </section>
  );
}