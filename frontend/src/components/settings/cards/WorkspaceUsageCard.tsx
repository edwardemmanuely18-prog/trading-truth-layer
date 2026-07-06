"use client";

type UsageCardProps = {
  label: string;
  used: number;
  limit: number;
  ratio: number;
  hint: string;
};

function UsageBar({
  ratio,
}: {
  ratio: number;
}) {
  const width = Math.min(
    Math.max(ratio * 100, 0),
    100
  );

  return (
    <div className="mt-2 h-2 overflow-hidden rounded-full bg-white">
      <div
        className="h-full rounded-full bg-slate-900"
        style={{
          width: `${width}%`,
        }}
      />
    </div>
  );
}

function UsageMetric({
  label,
  used,
  limit,
  ratio,
  hint,
}: UsageCardProps) {
  const warning =
    limit > 0 &&
    used >= limit;

  return (
    <div
      className={`rounded-2xl border p-4 ${
        warning
          ? "border-amber-300 bg-amber-50"
          : "border-slate-200 bg-slate-50"
      }`}
    >
      <div className="text-sm text-slate-500">
        {label}
      </div>

      <div className="mt-2 text-xl font-semibold">
        {used} / {limit}
      </div>

      <UsageBar ratio={ratio} />

      <div className="mt-2 text-sm text-slate-500">
        {(ratio * 100).toFixed(1)}%
      </div>

      <div className="mt-2 text-xs text-slate-500">
        {hint}
      </div>
    </div>
  );
}

type Props = {

    usage: {

        claims: number;

        trades: number;

        members: number;

        storage_mb: number;

    };

    limits: {

        claims: number;

        trades: number;

        members: number;

        storage_mb: number;

    };

};

export default function WorkspaceUsageCard({
  usage,
  limits,
}: Props) {
  return (
    <div className="rounded-3xl border bg-white p-6 shadow-sm">

      <h2 className="text-2xl font-semibold">

          Workspace Capacity

      </h2>

      <p className="mt-1 text-sm text-slate-500">
        Current operational utilization against your commercial workspace capacity.
      </p>

      <div className="mt-5 space-y-4">

        <UsageMetric

            label="Claims"

            used={usage.claims}

            limit={limits.claims}

            ratio={
                limits.claims > 0
                    ? usage.claims / limits.claims
                    : 0
            }

            hint="Verification Claims"

        />

        <UsageMetric

            label="Members"

            used={usage.members}

            limit={limits.members}

            ratio={
                limits.members > 0
                    ? usage.members / limits.members
                    : 0
            }

            hint="Workspace Members"

        />

        <UsageMetric

            label="Trades"

            used={usage.trades}

            limit={limits.trades}

            ratio={
                limits.trades > 0
                    ? usage.trades / limits.trades
                    : 0
            }

            hint="Evidence Records"

        />

        <UsageMetric

            label="Storage"

            used={usage.storage_mb}

            limit={limits.storage_mb}

            ratio={
                limits.storage_mb > 0
                    ? usage.storage_mb / limits.storage_mb
                    : 0
            }

            hint="Evidence Storage"

        />

      </div>

    </div>
  );
}