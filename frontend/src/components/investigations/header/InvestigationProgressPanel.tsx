"use client";

import { InvestigationReport } from "@/lib/api";

interface InvestigationProgressPanelProps {
    report: InvestigationReport;
}

export default function InvestigationProgressPanel({
    report,
}: InvestigationProgressPanelProps) {

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

    const stage =
        report.allocator
            ? "COMPLETE"
            : "ANALYZING";

    const allocatorReady =
        report.allocator
            ? "READY"
            : "WAITING";

    const findings =
        report.findings.length;

    const recommendations =
        report.recommendations.length;

    const evidenceCoverage =
        report.summary.investigation_confidence;

    const cards = [
        {
            title: "Stage",
            value: stage,
        },
        {
            title: "Completed Domains",
            value: `${completedDomains} / 8`,
        },
        {
            title: "Evidence Coverage",
            value: `${evidenceCoverage.toFixed(1)}%`,
        },
        {
            title: "Findings",
            value: findings,
        },
        {
            title: "Recommendations",
            value: recommendations,
        },
        {
            title: "Allocator",
            value: allocatorReady,
        },
        {
            title: "Runtime",
            value: "Ready",
        },
    ];

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                    Investigation Progress

                </div>

                <h2 className="mt-2 text-2xl font-semibold">

                    Institutional Investigation Pipeline

                </h2>

                <p className="mt-2 max-w-4xl text-sm leading-7 text-slate-600">

                    Live institutional progress showing investigation
                    completion, evidence readiness, findings processing,
                    recommendation generation and allocator readiness.

                </p>

            </div>

            <div className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-7">

                {cards.map((card) => (

                    <div
                        key={card.title}
                        className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                    >

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            {card.title}

                        </div>

                        <div className="mt-3 text-2xl font-bold text-slate-900">

                            {card.value}

                        </div>

                    </div>

                ))}

            </div>

        </section>

    );

}