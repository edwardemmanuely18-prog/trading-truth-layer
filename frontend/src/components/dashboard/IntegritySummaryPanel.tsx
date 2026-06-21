export default function IntegritySummaryPanel({
  integrityScore,
  activeAlerts,
  verificationCoverage,
}: {
  integrityScore: number;
  activeAlerts: number;
  verificationCoverage: number;
}) {
  return (
    <div className="mb-8 rounded-2xl border bg-white p-6 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
        Trust Infrastructure
      </div>

      <h2 className="mt-2 text-2xl font-semibold">
        Integrity Summary
      </h2>

      <div className="mt-5 grid gap-4 md:grid-cols-3">

        <div className="rounded-xl border p-5">
          <div className="text-sm text-slate-500">
            Integrity Score
          </div>

          <div className="mt-2 text-3xl font-bold">
            {integrityScore}%
          </div>
        </div>

        <div className="rounded-xl border p-5">
          <div className="text-sm text-slate-500">
            Active Alerts
          </div>

          <div className="mt-2 text-3xl font-bold">
            {activeAlerts}
          </div>
        </div>

        <div className="rounded-xl border p-5">
          <div className="text-sm text-slate-500">
            Verification Coverage
          </div>

          <div className="mt-2 text-3xl font-bold">
            {verificationCoverage}%
          </div>
        </div>

      </div>
    </div>
  );
}