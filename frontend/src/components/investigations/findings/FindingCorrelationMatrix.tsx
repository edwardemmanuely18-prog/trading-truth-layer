"use client";

import type {
    InvestigationFinding,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    findings: InvestigationFinding[];

}

export default function FindingCorrelationMatrix({

    findings,

}:Props){

    const rows =

        [...findings].sort(

            (a, b) =>

                b.confidence -

                a.confidence,

        );

    return(

        <SectionCard

            title="Finding Correlation Matrix"

            subtitle="Cross-impact analysis of institutional investigation findings."

        >

            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b">

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Finding

                            </th>

                            <th className="px-4 py-3 text-center text-xs uppercase tracking-wide text-slate-500">

                                Severity

                            </th>

                            <th className="px-4 py-3 text-center text-xs uppercase tracking-wide text-slate-500">

                                Confidence

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Recommendation

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {rows.map(

                            finding => (

                                <tr

                                    key={finding.id}

                                    className="border-b last:border-0"

                                >

                                    <td className="px-4 py-4">

                                        <div className="font-semibold">

                                            {finding.title}

                                        </div>

                                    </td>

                                    <td className="px-4 py-4 text-center">

                                        {finding.severity}

                                    </td>

                                    <td className="px-4 py-4 text-center">

                                        {finding.confidence.toFixed(1)}%

                                    </td>

                                    <td className="px-4 py-4">

                                        {finding.recommendation}

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