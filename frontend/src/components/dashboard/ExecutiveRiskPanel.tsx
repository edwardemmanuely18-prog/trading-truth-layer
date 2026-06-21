type Props = {
  integrityHealth?: string;
  activeAlerts?: number;
  verificationCoverage?: number;
};

export default function ExecutiveRiskPanel({
  integrityHealth,
  activeAlerts,
  verificationCoverage,
}: Props) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <div className="text-xs uppercase tracking-widest text-slate-500">
        Executive Risk
      </div>

      <h2 className="mt-2 text-2xl font-bold">
        Risk & Trust Status
      </h2>

      <div className="mt-6 grid gap-4 md:grid-cols-4">

        <Metric
          label="Integrity"
          value={
            integrityHealth === "healthy"
              ? "Healthy"
              : "Warning"
          }
        />

        <Metric
          label="Open Alerts"
          value={activeAlerts ?? 0}
        />

        <Metric
          label="Verification"
          value={`${verificationCoverage ?? 0}%`}
        />

        <Metric
          label="Trust Status"
          value={
            (activeAlerts ?? 0) > 0
              ? "Attention"
              : "Operational"
          }
        />

      </div>

    </div>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl border p-4">
      <div className="text-xs text-slate-500">
        {label}
      </div>

      <div className="mt-2 text-xl font-bold">
        {value}
      </div>
    </div>
  );
}