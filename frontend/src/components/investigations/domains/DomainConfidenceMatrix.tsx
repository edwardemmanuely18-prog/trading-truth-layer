"use client";

import type {
    InvestigationReport,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    report: InvestigationReport;

}

interface DomainRow {

    name: string;

    confidence: number;

    status: string;

}

function confidenceColor(
    confidence: number,
) {

    if (confidence >= 90) {

        return "bg-emerald-100 text-emerald-700";

    }

    if (confidence >= 75) {

        return "bg-blue-100 text-blue-700";

    }

    if (confidence >= 60) {

        return "bg-amber-100 text-amber-700";

    }

    return "bg-red-100 text-red-700";

}

export default function DomainConfidenceMatrix({

    report,

}: Props) {

    const domains: DomainRow[] = [

        {

            name: "Execution",

            confidence:
                report.execution?.confidence ?? 0,

            status:
                report.execution
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Evidence",

            confidence:
                report.evidence?.confidence ?? 0,

            status:
                report.evidence
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Verification",

            confidence:
                report.verification?.confidence ?? 0,

            status:
                report.verification
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Governance",

            confidence:
                report.governance?.confidence ?? 0,

            status:
                report.governance
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Synchronization",

            confidence:
                report.synchronization?.confidence ?? 0,

            status:
                report.synchronization
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Broker",

            confidence:
                report.broker?.confidence ?? 0,

            status:
                report.broker
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Review",

            confidence:
                report.review?.confidence ?? 0,

            status:
                report.review
                    ? "READY"
                    : "UNAVAILABLE",

        },

        {

            name: "Behavior",

            confidence:
                report.behavior?.confidence ?? 0,

            status:
                report.behavior
                    ? "READY"
                    : "UNAVAILABLE",

        },

    ];

    return (

        <SectionCard

            title="Domain Confidence Matrix"

            subtitle="Institutional confidence assigned to every IIS reasoning engine."

        >

            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b">

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-500">

                                Investigation Domain

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-500">

                                Confidence

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-500">

                                Status

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

                                            className={`rounded-full px-3 py-1 text-sm font-semibold ${confidenceColor(domain.confidence)}`}

                                        >

                                            {domain.confidence.toFixed(1)}%

                                        </span>

                                    </td>

                                    <td className="px-4 py-4">

                                        {domain.status}

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