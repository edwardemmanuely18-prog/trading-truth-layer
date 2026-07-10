import type {
    GovernanceSummary,
} from "./types";

interface Props {

    summary: GovernanceSummary;

    snapshot?: any;

}

function Status({

    healthy,

    children,

}: {

    healthy: boolean;

    children: React.ReactNode;

}) {

    return (

        <div
            className={
                healthy
                    ? "rounded-xl border border-emerald-200 bg-emerald-50 p-4"
                    : "rounded-xl border border-amber-200 bg-amber-50 p-4"
            }
        >

            <div
                className={
                    healthy
                        ? "font-semibold text-emerald-800"
                        : "font-semibold text-amber-800"
                }
            >

                {healthy ? "Healthy" : "Attention"}

            </div>

            <div className="mt-2 text-sm">

                {children}

            </div>

        </div>

    );

}

export default function GovernanceIntelligence({

    summary,

    snapshot,

}: Props) {

    const health =
        snapshot?.governance_health;

    const hasOwner =
        health?.owner?.healthy

        ??

        (summary.ownerCount > 0);

    const hasOperator =
        health?.operator?.healthy

        ??

        (summary.operatorCount > 0)

    const hasAuditor =
        health?.auditor?.healthy

        ??

        (summary.auditorCount > 0)

    const utilization =
        snapshot?.capacity?.utilization

        ??

        0

    return (

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                Governance Intelligence

            </div>

            <h2 className="mt-2 text-3xl font-bold">

                Operational Governance

            </h2>

            <p className="mt-4 max-w-4xl text-slate-600">

                Institutional assessment of the workspace governance
                posture using canonical identity assignments and
                workspace capacity.

            </p>

            <div className="mt-10 grid gap-5 lg:grid-cols-2">

                <Status healthy={hasOwner}>

                    Workspace owner established.

                </Status>

                <Status healthy={hasOperator}>

                    Operational execution capability available.

                </Status>

                <Status healthy={hasAuditor}>

                    Independent audit capability available.

                </Status>

                <Status healthy={utilization < 90}>

                    Workspace utilization currently {utilization}%.

                </Status>

            </div>

            <div className="mt-10 rounded-2xl border bg-slate-50 p-6">

                <h3 className="text-lg font-semibold">

                    Recommended Governance Actions

                </h3>

                <ul className="mt-5 space-y-3 text-sm">

                    {
                        snapshot?.recommendations?.length
                            ? snapshot.recommendations.map(
                                (item: any) => (

                                    <li key={item.code}>

                                        • {item.message}

                                    </li>

                                )
                            )
                            : (

                                <li>

                                    Workspace governance operating normally.

                                </li>

                            )

                    }

                </ul>

            </div>

        </section>

    );

}