type Props = {
  integrityScore: number;
  totalAlerts: number;
  claimsScanned: number;
};

export default function IntegrityExecutivePanel({
  integrityScore,
  totalAlerts,
  claimsScanned,
}: Props) {
  return (
    <div className="rounded-xl border bg-white p-6">

      <h2 className="text-xl font-semibold">
        Integrity Executive Summary
      </h2>

      <div className="mt-6 grid md:grid-cols-3 gap-4">

        <Metric
          title="Integrity Score"
          value={integrityScore}
        />

        <Metric
          title="Alerts"
          value={totalAlerts}
        />

        <Metric
          title="Claims Scanned"
          value={claimsScanned}
        />

      </div>

    </div>
  );
}

function Metric({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {
  return (
    <div className="rounded-lg border p-4">
      <div className="text-xs text-slate-500">
        {title}
      </div>

      <div className="mt-2 text-3xl font-bold">
        {value}
      </div>
    </div>
  );
}