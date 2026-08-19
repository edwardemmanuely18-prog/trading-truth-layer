import type { ProviderFormDefinition } from "../../types";

export const metaTrader4FormDefinition: ProviderFormDefinition = {
    provider: "MetaTrader 4",
    engine: "desktop_engine",

    title: "MetaTrader 4 Desktop Bridge",

    description:
        "MetaTrader 4 connects through the Trading Truth Layer Desktop Trading Engine bridge. No MT4 username, password, broker server, terminal path, or bridge endpoint is required from the user. The active MT4 bridge provides the terminal, account and broker context automatically.",

    fields: [],

    emptyState: (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
            <div className="text-lg font-semibold text-slate-900">
                No MT4 credentials required
            </div>

            <p className="mt-2 leading-7 text-slate-600">
                Make sure the MetaTrader 4 terminal is running and the
                Trading Truth Layer MT4 bridge is active. TTL will
                automatically discover the connected terminal, account,
                broker and server information during Test Connection.
            </p>

            <div className="mt-4 grid gap-3 md:grid-cols-3">
                <div className="rounded-xl bg-white p-4">
                    <div className="font-semibold text-slate-900">
                        Terminal
                    </div>
                    <div className="mt-1 text-sm text-slate-600">
                        Discovered automatically
                    </div>
                </div>

                <div className="rounded-xl bg-white p-4">
                    <div className="font-semibold text-slate-900">
                        Account
                    </div>
                    <div className="mt-1 text-sm text-slate-600">
                        Discovered automatically
                    </div>
                </div>

                <div className="rounded-xl bg-white p-4">
                    <div className="font-semibold text-slate-900">
                        Broker / Server
                    </div>
                    <div className="mt-1 text-sm text-slate-600">
                        Discovered automatically
                    </div>
                </div>
            </div>
        </div>
    ),
};

export default metaTrader4FormDefinition;