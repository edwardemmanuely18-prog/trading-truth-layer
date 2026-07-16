"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface InvestigationStatusBannerProps {
    report: InvestigationReport;
}

function decisionColor(decision: string) {
    switch (decision.toUpperCase()) {
        case "ACCEPT":
            return "bg-emerald-100 text-emerald-700";

        case "CONDITIONAL_ACCEPT":
            return "bg-amber-100 text-amber-700";

        case "REJECT":
            return "bg-red-100 text-red-700";

        default:
            return "bg-slate-100 text-slate-700";
    }
}

export default function InvestigationStatusBanner({
    report,
}: InvestigationStatusBannerProps) {

    const completedDomains = [

        report.execution,
        report.evidence,
        report.verification,
        report.governance,
        report.broker,
        report.synchronization,
        report.review,
        report.behavior,

    ].filter(Boolean).length;

    const confidence =
        report.summary.investigation_confidence;

    const decision =
        report.allocator?.decision ??
        "UNKNOWN";

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-4">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Investigation Status

                </div>

                <div className="mt-2 text-2xl font-semibold">

                    Institutional Investigation Completed

                </div>

                <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-500">

                    This investigation has completed every institutional
                    reasoning engine and produced a canonical allocator
                    decision from the Investigation Context.

                </p>

            </div>

            <div className="grid gap-6 p-6 md:grid-cols-5">

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Status

                    </div>

                    <div className="mt-2 text-2xl font-bold text-emerald-600">

                        COMPLETE

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Investigation Confidence

                    </div>

                    <div className="mt-2 text-3xl font-bold">

                        {confidence.toFixed(1)}%

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Domains Completed

                    </div>

                    <div className="mt-2 text-3xl font-bold">

                        {completedDomains}/8

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Findings

                    </div>

                    <div className="mt-2 text-3xl font-bold">

                        {report.summary.total_findings}

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Decision

                    </div>

                    <div className="mt-3">

                        <span
                            className={`rounded-full px-4 py-2 text-sm font-semibold ${decisionColor(
                                decision,
                            )}`}
                        >

                            {decision.replaceAll("_", " ")}

                        </span>

                    </div>

                </div>

            </div>

        </section>

    );

}