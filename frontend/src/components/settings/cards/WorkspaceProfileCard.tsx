type Props = {

    canEdit: boolean;

    saving: boolean;

    name: string;

    description: string;

    billingEmail: string;

    setName: (value: string) => void;

    setDescription: (value: string) => void;

    setBillingEmail: (value: string) => void;

    onSubmit: () => void;

};

export default function WorkspaceProfileCard({

    canEdit,

    saving,

    name,

    description,

    billingEmail,

    setName,

    setDescription,

    setBillingEmail,

    onSubmit,

}: Props) {

  return (

    <section className="rounded-2xl border bg-white p-6 shadow-sm">

      <div>

        <div className="text-xs uppercase tracking-[0.25em] text-slate-500">
          Workspace Profile
        </div>

        <h2 className="mt-2 text-2xl font-semibold">
          Workspace Information
        </h2>

        <p className="mt-2 text-sm text-slate-500">
          Configure the primary identity of this workspace.
        </p>

      </div>

      <div className="mt-8 space-y-6">

        <div>

          <label className="text-sm font-medium">
            Workspace Name
          </label>

          <input
              className="mt-2 w-full rounded-xl border px-4 py-3"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={!canEdit}
          />

        </div>

        <div>

          <label className="text-sm font-medium">
            Description
          </label>

          <textarea
              rows={5}
              className="mt-2 w-full rounded-xl border px-4 py-3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={!canEdit}
          />

        </div>

        <div>

          <label className="text-sm font-medium">
            Billing Email
          </label>

          <input
              className="mt-2 w-full rounded-xl border px-4 py-3"
              value={billingEmail}
              onChange={(e) => setBillingEmail(e.target.value)}
              disabled={!canEdit}
          />

        </div>

        <div>

          <button
            onClick={onSubmit}
            disabled={!canEdit || saving}
            className="rounded-xl bg-slate-900 px-6 py-3 text-white hover:bg-slate-800 disabled:opacity-60"
          >
            {saving ? "Saving..." : "Save Workspace"}
          </button>

        </div>

      </div>

    </section>

  );
}