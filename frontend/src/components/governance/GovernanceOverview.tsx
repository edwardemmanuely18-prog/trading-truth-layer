import {
    GovernanceSummary,
} from "./types";

export default function GovernanceOverview({

    summary,

    snapshot,

}: {

    summary: GovernanceSummary;

    snapshot?: any;

}) {

    const utilization =

    snapshot?.capacity?.utilization

    ??

    0;

    return (

        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Governance Overview
            </div>

            <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

                <OverviewCard
                    title="Workspace Plan"
                    value={snapshot?.workspace?.plan

                            ??

                            summary.plan}
                />

                <OverviewCard
                    title="Member Utilization"
                    value={`${utilization}%`}
                />

                <OverviewCard
                    title="Pending Invitations"
                    value={String(snapshot?.governance_health
                                  ?.invitation
                                  ?.findings
                                  ?.length

                                  ??

                                  summary.pendingInvites)}
                />

                <OverviewCard
                    title="Governance Health"
                    value={String(

                                  snapshot?.governance_health
                                  ?.overall_score

                                  ??

                                  summary.governanceHealth

                                  )}
                />

            </div>

        </div>

    );

}

function OverviewCard({

    title,

    value,

}: {

    title: string;

    value: string;

}) {

    return (

        <div className="rounded-xl border border-slate-200 p-5">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-xl font-semibold">

                {value}

            </div>

        </div>

    );

}