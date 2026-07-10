import {
    GovernanceSummary,
} from "./types";

interface Props {

    summary: GovernanceSummary;

    snapshot?: any;

}

export default function GovernanceHero({

    summary,

    snapshot,

}: Props) {

    return (

        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Identity Governance
            </div>

            <h1 className="mt-3 text-3xl font-bold text-slate-950">
                Identity Governance Center
            </h1>

            <p className="mt-4 max-w-4xl text-slate-600 leading-7">

                Govern workspace identities,
                operational responsibilities,
                institutional permissions,
                invitation workflows,
                and access governance from
                a single institutional surface.

            </p>

            <div className="mt-8 grid gap-4 md:grid-cols-5">

                <HeroMetric
                    title="Members"
                    value={`${snapshot?.capacity?.members
                                ??
                            summary.memberCount}/${snapshot?.capacity?.member_limit
                                ??
                            summary.memberLimit}`}
                />

                <HeroMetric
                    title="Owners"
                    value={String(snapshot?.identity_summary?.owners
																			??
																	summary.ownerCount)}
                />

                <HeroMetric
                    title="Operators"
                    value={String(snapshot?.identity_summary?.operators
																			??
																	summary.operatorCount)}
                />

								<HeroMetric
                    title="Auditor"
                    value={String(snapshot?.identity_summary?.auditors
																			??
																	summary.auditorCount)}
                />

                <HeroMetric
                    title="Pending Invites"
                    value={
										String(

										snapshot?.governance_health
										?.invitation
										?.findings
										?.length

										??

										summary.pendingInvites

										)

										}
                />

                <HeroMetric
                    title="Governance"
                    value={snapshot?.governance_health
														?.overall_score

														??

														summary.governanceHealth}
                />

            </div>

        </div>

    );

}

function HeroMetric({

    title,

    value,

}: {

    title: string;

    value: string;

}) {

    return (

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

            <div className="text-xs uppercase tracking-wide text-slate-500">
                {title}
            </div>

            <div className="mt-2 text-2xl font-semibold text-slate-900">
                {value}
            </div>

        </div>

    );

}