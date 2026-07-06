type Props = {
  workspaceId: number;
  workspaceName: string;
  role: string;
  plan: string;
  status: string;
  createdAt?: string | null;
  updatedAt?: string | null;
};

function formatDate(value?: string | null) {
  if (!value) return "—";

  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function WorkspaceIdentityCard({
  workspaceId,
  workspaceName,
  role,
  plan,
  status,
  createdAt,
  updatedAt,
}: Props) {
  return (
    <section className="rounded-2xl border bg-white p-6 shadow-sm">

      <div className="flex items-center justify-between">

        <div>

          <div className="text-xs uppercase tracking-[0.25em] text-slate-500">
            Workspace Identity
          </div>

          <h2 className="mt-2 text-2xl font-semibold">
            Workspace Record
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Immutable identity information used across the verification
            infrastructure.
          </p>

        </div>

      </div>

      <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">

        <Metric
          label="Workspace ID"
          value={workspaceId}
        />

        <Metric
          label="Workspace Name"
          value={workspaceName}
        />

        <Metric
          label="Workspace Role"
          value={role}
        />

        <Metric
          label="Current Plan"
          value={plan}
        />

        <Metric
          label="Workspace Status"
          value={status}
        />

        <Metric
          label="Created"
          value={formatDate(createdAt)}
        />

        <Metric
          label="Updated"
          value={formatDate(updatedAt)}
        />

      </div>

    </section>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border bg-slate-50 p-4">

      <div className="text-xs uppercase tracking-wide text-slate-500">
        {label}
      </div>

      <div className="mt-2 text-lg font-semibold">
        {value}
      </div>

    </div>
  );
}