type Props = {

    canEdit: boolean;

    saving: boolean;

    name: string;

    description: string;

    currency: string;

    setCurrency: (value: string) => void;

    setName: (value: string) => void;

    setDescription: (value: string) => void;

    onSubmit: () => void;

};

export default function WorkspaceProfileCard({

    canEdit,

    saving,

    name,

    description,

    currency,

    setCurrency,

    setName,

    setDescription,

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
                    Configure the primary identity and reporting
                    preferences of this workspace.
                </p>

            </div>

            <div className="mt-8 space-y-6">

                {/* Workspace Name */}

                <div>

                    <label className="text-sm font-medium">
                        Workspace Name
                    </label>

                    <input
                        className="mt-2 w-full rounded-xl border px-4 py-3"
                        value={name}
                        onChange={(e) =>
                            setName(
                                e.target.value
                            )
                        }
                        disabled={!canEdit}
                    />

                </div>

                {/* Description */}

                <div>

                    <label className="text-sm font-medium">
                        Description
                    </label>

                    <textarea
                        rows={5}
                        className="mt-2 w-full rounded-xl border px-4 py-3"
                        value={description}
                        onChange={(e) =>
                            setDescription(
                                e.target.value
                            )
                        }
                        disabled={!canEdit}
                    />

                </div>

                {/* Reporting Currency */}

                <div>

                    <label className="text-sm font-medium">
                        Reporting Currency
                    </label>

                    <p className="mt-1 text-sm text-slate-500">

                        Select the canonical reporting currency used
                        by the Trading Performance System for
                        workspace analytics, normalized performance
                        metrics and institutional reports.

                    </p>

                    <select
                        value={currency}
                        onChange={(e) =>
                            setCurrency(
                                e.target.value
                            )
                        }
                        disabled={!canEdit}
                        className="mt-3 w-full rounded-xl border px-4 py-3"
                    >

                        <option value="USD">USD</option>
                        <option value="EUR">EUR</option>
                        <option value="GBP">GBP</option>
                        <option value="JPY">JPY</option>
                        <option value="CHF">CHF</option>
                        <option value="CAD">CAD</option>
                        <option value="AUD">AUD</option>
                        <option value="NZD">NZD</option>
                        <option value="SGD">SGD</option>
                        <option value="HKD">HKD</option>
                        <option value="SEK">SEK</option>
                        <option value="NOK">NOK</option>
                        <option value="DKK">DKK</option>
                        <option value="ZAR">ZAR</option>
                        <option value="TZS">TZS</option>

                    </select>

                </div>

                {/* Save Button */}

                <div>

                    <button
                        onClick={onSubmit}
                        disabled={
                            !canEdit ||
                            saving
                        }
                        className="rounded-xl bg-slate-900 px-6 py-3 text-white hover:bg-slate-800 disabled:opacity-60"
                    >

                        {saving
                            ? "Saving..."
                            : "Save Settings"}

                    </button>

                </div>

            </div>

        </section>

    );

}