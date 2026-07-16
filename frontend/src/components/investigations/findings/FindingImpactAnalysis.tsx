"use client";

import type {
    InvestigationSummary,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    summary: InvestigationSummary;

}

function Metric({

    title,

    value,

}:{

    title:string;

    value:number;

}){

    return(

        <div className="rounded-xl border bg-white p-5">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-4xl font-bold">

                {value}

            </div>

        </div>

    );

}

export default function FindingImpactAnalysis({

    summary,

}:Props){

    const affectedClaims =
        summary.affected_claims ?? 0;

    const affectedMembers =
        summary.affected_members ?? 0;

    const affectedAccounts =
        summary.affected_accounts ?? 0;

    const affectedSyncJobs =
        summary.affected_sync_jobs ?? 0;

    const evidenceNodes =
        summary.evidence_nodes ?? 0;

    const timelineEvents =
        summary.timeline_events ?? 0;

    return(

        <SectionCard

            title="Finding Impact Analysis"

            subtitle="Operational impact measured across institutional assets."

        >

            <div className="grid gap-5 lg:grid-cols-3">

                <Metric

                    title="Affected Claims"

                    value={affectedClaims}

                />

                <Metric

                    title="Evidence Nodes"

                    value={evidenceNodes}

                />

                <Metric

                    title="Affected Members"

                    value={affectedMembers}

                />

                <Metric

                    title="Affected Accounts"

                    value={affectedAccounts}

                />

                <Metric

                    title="Affected Sync Jobs"

                    value={affectedSyncJobs}

                />

                <Metric

                    title="Timeline Events"

                    value={timelineEvents}
                    
                />

            </div>

        </SectionCard>

    );

}