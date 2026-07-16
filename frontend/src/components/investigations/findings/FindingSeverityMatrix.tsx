"use client";

import type {
    InvestigationFinding,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    findings: InvestigationFinding[];

}

interface SeverityRow {

    severity: string;

    count: number;

}

function badgeStyle(
    severity: string,
) {

    switch (severity) {

        case "CRITICAL":
            return "bg-red-100 text-red-700";

        case "HIGH":
            return "bg-orange-100 text-orange-700";

        case "MEDIUM":
            return "bg-amber-100 text-amber-700";

        case "LOW":
            return "bg-blue-100 text-blue-700";

        default:
            return "bg-slate-100 text-slate-700";

    }

}

export default function FindingSeverityMatrix({

    findings,

}: Props) {

    const levels = [

        "CRITICAL",

        "HIGH",

        "MEDIUM",

        "LOW",

        "INFORMATION",

    ];

    const rows: SeverityRow[] = levels.map(

        severity => ({

            severity,

            count: findings.filter(

                finding =>

                    finding.severity === severity,

            ).length,

        }),

    );

    const total = findings.length;

    return (

        <SectionCard

            title="Finding Severity Matrix"

            subtitle="Distribution of investigation findings by institutional severity."

        >

            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b">

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Severity

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Findings

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Percentage

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {rows.map(

                            row => (

                                <tr

                                    key={row.severity}

                                    className="border-b last:border-0"

                                >

                                    <td className="px-4 py-4">

                                        <span
                                            className={`rounded-full px-3 py-1 font-semibold ${badgeStyle(
                                                row.severity,
                                            )}`}
                                        >

                                            {row.severity}

                                        </span>

                                    </td>

                                    <td className="px-4 py-4 font-semibold">

                                        {row.count}

                                    </td>

                                    <td className="px-4 py-4">

                                        {

                                            total === 0

                                                ? "0.0"

                                                : (

                                                    (

                                                        row.count /

                                                        total

                                                    ) *

                                                    100

                                                ).toFixed(1)

                                        }

                                        %

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