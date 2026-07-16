"use client";

import type {
    InvestigationReport,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    report: InvestigationReport;

}

interface ConsensusRow {

    name: string;

    confidence: number;

}

function badge(score: number) {

    if (score >= 90) {

        return "bg-emerald-100 text-emerald-700";

    }

    if (score >= 75) {

        return "bg-blue-100 text-blue-700";

    }

    if (score >= 60) {

        return "bg-amber-100 text-amber-700";

    }

    return "bg-red-100 text-red-700";

}

export default function CrossDomainConsensus({

    report,

}: Props) {

    const domains: ConsensusRow[] = [

        {
            name: "Execution",
            confidence: report.execution?.confidence ?? 0,
        },

        {
            name: "Evidence",
            confidence: report.evidence?.confidence ?? 0,
        },

        {
            name: "Verification",
            confidence: report.verification?.confidence ?? 0,
        },

        {
            name: "Governance",
            confidence: report.governance?.confidence ?? 0,
        },

        {
            name: "Synchronization",
            confidence: report.synchronization?.confidence ?? 0,
        },

        {
            name: "Broker",
            confidence: report.broker?.confidence ?? 0,
        },

        {
            name: "Review",
            confidence: report.review?.confidence ?? 0,
        },

        {
            name: "Behavior",
            confidence: report.behavior?.confidence ?? 0,
        },

    ];

    const scores = domains.map(

        d => d.confidence,

    );

    const average =

        scores.reduce(

            (a, b) => a + b,

            0,

        ) /

        scores.length;

    const spread =

        Math.max(...scores) -

        Math.min(...scores);

    let verdict = "Strong Consensus";

    if (spread > 25) {

        verdict = "Moderate Consensus";

    }

    if (spread > 45) {

        verdict = "Weak Consensus";

    }

    return (

        <SectionCard

            title="Cross-Domain Consensus"

            subtitle="Institutional agreement between investigation engines."

        >

            <div className="grid gap-6 lg:grid-cols-3">

                <div className="rounded-lg border bg-slate-50 p-5">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Average Confidence

                    </div>

                    <div className="mt-3 text-4xl font-bold">

                        {average.toFixed(1)}%

                    </div>

                </div>

                <div className="rounded-lg border bg-slate-50 p-5">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Confidence Spread

                    </div>

                    <div className="mt-3 text-4xl font-bold">

                        {spread.toFixed(1)}

                    </div>

                </div>

                <div className="rounded-lg border bg-slate-50 p-5">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Consensus

                    </div>

                    <div className="mt-3 text-2xl font-semibold">

                        {verdict}

                    </div>

                </div>

            </div>

            <div className="mt-8 overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b">

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Domain

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Confidence

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {domains.map(

                            domain => (

                                <tr
                                    key={domain.name}
                                    className="border-b last:border-0"
                                >

                                    <td className="px-4 py-4 font-medium">

                                        {domain.name}

                                    </td>

                                    <td className="px-4 py-4">

                                        <span

                                            className={`rounded-full px-3 py-1 font-semibold ${badge(domain.confidence)}`}

                                        >

                                            {domain.confidence.toFixed(1)}%

                                        </span>

                                    </td>

                                </tr>

                            ),

                        )}

                    </tbody>

                </table>

            </div>

        </SectionCard>

    );

}