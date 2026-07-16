"use client";

import type {
    InvestigationReport,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    report: InvestigationReport;

}

interface CoverageRow {

    name: string;

    coverage: number;

    findings: number;

}

function coverageColor(
    coverage: number,
) {

    if (coverage >= 90) {

        return "bg-emerald-100 text-emerald-700";

    }

    if (coverage >= 75) {

        return "bg-blue-100 text-blue-700";

    }

    if (coverage >= 60) {

        return "bg-amber-100 text-amber-700";

    }

    return "bg-red-100 text-red-700";

}

export default function DomainCoverageMatrix({

    report,

}: Props) {

    const rows: CoverageRow[] = [

        {

            name: "Execution",

            coverage:
                report.execution?.confidence ?? 0,

            findings:
                report.execution?.findings.length ?? 0,

        },

        {

            name: "Evidence",

            coverage:
                report.evidence?.confidence ?? 0,

            findings:
                report.evidence?.findings.length ?? 0,

        },

        {

            name: "Verification",

            coverage:
                report.verification?.confidence ?? 0,

            findings:
                report.verification?.findings.length ?? 0,

        },

        {

            name: "Governance",

            coverage:
                report.governance?.confidence ?? 0,

            findings:
                report.governance?.findings.length ?? 0,

        },

        {

            name: "Synchronization",

            coverage:
                report.synchronization?.confidence ?? 0,

            findings:
                report.synchronization?.findings.length ?? 0,

        },

        {

            name: "Broker",

            coverage:
                report.broker?.confidence ?? 0,

            findings:
                report.broker?.findings.length ?? 0,

        },

        {

            name: "Review",

            coverage:
                report.review?.confidence ?? 0,

            findings:
                report.review?.findings.length ?? 0,

        },

        {

            name: "Behavior",

            coverage:
                report.behavior?.confidence ?? 0,

            findings:
                report.behavior?.findings.length ?? 0,

        },

    ];

    return (

        <SectionCard

            title="Domain Coverage Matrix"

            subtitle="Institutional investigation coverage achieved by every reasoning engine."

        >

            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b">

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Domain

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Coverage

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Findings

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {rows.map(

                            row => (

                                <tr

                                    key={row.name}

                                    className="border-b last:border-0"

                                >

                                    <td className="px-4 py-4 font-medium">

                                        {row.name}

                                    </td>

                                    <td className="px-4 py-4">

                                        <span

                                            className={`rounded-full px-3 py-1 font-semibold ${coverageColor(row.coverage)}`}

                                        >

                                            {row.coverage.toFixed(1)}%

                                        </span>

                                    </td>

                                    <td className="px-4 py-4">

                                        {row.findings}

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