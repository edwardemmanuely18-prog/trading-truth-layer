"use client";

import type {
    InvestigationFinding,
} from "@/lib/api";

import SectionCard
from "../common/SectionCard";

interface Props {

    findings: InvestigationFinding[];

}

function severityClass(
    severity: string,
) {

    switch (severity.toUpperCase()) {

        case "CRITICAL":
            return "border-red-300 bg-red-50";

        case "HIGH":
            return "border-orange-300 bg-orange-50";

        default:
            return "border-slate-200 bg-slate-50";

    }

}

export default function CriticalFindingsPanel({

    findings,

}: Props) {

    const priority = findings.filter(

        finding =>

            finding.severity === "CRITICAL" ||

            finding.severity === "HIGH",

    );

    return (

        <SectionCard

            title="Priority Findings"

            subtitle="Critical institutional issues requiring immediate review."

        >

            {priority.length === 0 ? (

                <div className="rounded-lg border bg-emerald-50 p-6">

                    <div className="text-xl font-semibold text-emerald-700">

                        No Critical Findings

                    </div>

                    <p className="mt-3 leading-7 text-slate-600">

                        IIS did not identify any HIGH or CRITICAL
                        institutional findings.

                    </p>

                </div>

            ) : (

                <div className="space-y-5">

                    {priority.map(

                        finding => (

                            <div

                                key={finding.id}

                                className={`rounded-xl border p-6 ${severityClass(
                                    finding.severity,
                                )}`}

                            >

                                <div className="flex items-center justify-between">

                                    <div>

                                        <div className="text-xl font-semibold">

                                            {finding.title}

                                        </div>

                                        <div className="mt-1 text-sm text-slate-500">

                                            Confidence:

                                            {" "}

                                            {finding.confidence.toFixed(1)}%

                                        </div>

                                    </div>

                                    <span
                                        className="rounded-full bg-white px-3 py-1 text-sm font-semibold"
                                    >

                                        {finding.severity}

                                    </span>

                                </div>

                                <div className="mt-5 leading-7 text-slate-700">

                                    {finding.description}

                                </div>

                                {finding.recommendation && (

                                    <div className="mt-6 rounded-lg border bg-white p-4">

                                        <div className="text-xs uppercase tracking-wide text-slate-500">

                                            Institutional Recommendation

                                        </div>

                                        <div className="mt-2">

                                            {finding.recommendation}

                                        </div>

                                    </div>

                                )}

                            </div>

                        ),

                    )}

                </div>

            )}

        </SectionCard>

    );

}