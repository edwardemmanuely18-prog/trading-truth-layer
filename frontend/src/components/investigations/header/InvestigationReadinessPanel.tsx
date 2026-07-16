"use client";

import { InvestigationReport } from "@/lib/api";

interface InvestigationReadinessPanelProps {
    report: InvestigationReport;
}

interface ReadinessItem {
    label: string;
    ready: boolean;
}

export default function InvestigationReadinessPanel({
    report,
}: InvestigationReadinessPanelProps) {

    const checks: ReadinessItem[] = [
        {
            label: "Execution",
            ready: !!report.execution,
        },
        {
            label: "Evidence",
            ready: !!report.evidence,
        },
        {
            label: "Verification",
            ready: !!report.verification,
        },
        {
            label: "Governance",
            ready: !!report.governance,
        },
        {
            label: "Broker",
            ready: !!report.broker,
        },
        {
            label: "Synchronization",
            ready: !!report.synchronization,
        },
        {
            label: "Review",
            ready: !!report.review,
        },
        {
            label: "Behavior",
            ready: !!report.behavior,
        },
        {
            label: "Allocator",
            ready: !!report.allocator,
        },
    ];

    const readyCount = checks.filter(
        item => item.ready,
    ).length;

    const readiness =
        (readyCount / checks.length) * 100;

    const decisionReady =
        readiness === 100;

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                    Investigation Readiness

                </div>

                <h2 className="mt-2 text-2xl font-semibold">

                    Institutional Decision Readiness

                </h2>

                <p className="mt-2 max-w-4xl text-sm leading-7 text-slate-600">

                    Institutional readiness assessment showing whether every
                    investigation subsystem has completed successfully and
                    whether the allocator decision can be relied upon.

                </p>

            </div>

            <div className="grid gap-4 p-6 md:grid-cols-3 xl:grid-cols-5">

                {checks.map(item => (

                    <div
                        key={item.label}
                        className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                    >

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            {item.label}

                        </div>

                        <div
                            className={`mt-3 inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
                                item.ready
                                    ? "bg-emerald-100 text-emerald-700"
                                    : "bg-red-100 text-red-700"
                            }`}
                        >

                            {item.ready
                                ? "READY"
                                : "BLOCKED"}

                        </div>

                    </div>

                ))}

            </div>

            <div className="border-t border-slate-200 p-6">

                <div className="grid gap-6 lg:grid-cols-2">

                    <div className="rounded-lg border border-slate-200 bg-slate-50 p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Overall Readiness

                        </div>

                        <div className="mt-3 text-4xl font-bold">

                            {readiness.toFixed(0)}%

                        </div>

                        <div className="mt-2 text-sm text-slate-500">

                            {readyCount} of {checks.length} institutional
                            subsystems are decision-ready.

                        </div>

                    </div>

                    <div
                        className={`rounded-lg border p-5 ${
                            decisionReady
                                ? "border-emerald-200 bg-emerald-50"
                                : "border-amber-200 bg-amber-50"
                        }`}
                    >

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Decision Status

                        </div>

                        <div
                            className={`mt-3 text-2xl font-bold ${
                                decisionReady
                                    ? "text-emerald-700"
                                    : "text-amber-700"
                            }`}
                        >

                            {decisionReady
                                ? "READY FOR INSTITUTIONAL DECISION"
                                : "INVESTIGATION STILL IN PROGRESS"}

                        </div>

                        <p className="mt-3 text-sm leading-7 text-slate-600">

                            The allocator should only be relied upon once every
                            institutional investigation subsystem has completed
                            successfully.

                        </p>

                    </div>

                </div>

            </div>

        </section>

    );

}