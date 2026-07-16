"use client";

import {
    InvestigationDecision,
} from "@/lib/api";

interface AllocatorPanelProps {
    allocator?: InvestigationDecision | null;
}

function verdict(confidence: number) {

    if (confidence >= 90) {
        return {
            badge: "bg-emerald-100 text-emerald-700",
        };
    }

    if (confidence >= 75) {
        return {
            badge: "bg-amber-100 text-amber-700",
        };
    }

    return {
        badge: "bg-red-100 text-red-700",
    };
}

function decisionColor(decision: string): string {

    switch (decision.toUpperCase()) {

        case "ACCEPT":
            return "text-emerald-700";

        case "CONDITIONAL_ACCEPT":
            return "text-amber-700";

        case "REJECT":
            return "text-red-700";

        default:
            return "text-slate-700";

    }

}

export default function AllocatorPanel({

    allocator,

}: AllocatorPanelProps) {

    if (!allocator) {

        return (

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

                <h2 className="text-xl font-semibold">

                    Institutional Allocator Decision

                </h2>

                <p className="mt-4 text-slate-500">

                    Allocator decision unavailable.

                </p>

            </div>

        );

    }

    const result = verdict(
        allocator.confidence,
    );

    const actions =
        allocator.required_actions ?? [];

    const metadata = allocator.metadata ?? {};

    const completedDomains =
        Number(metadata.completed_domains ?? 0);

    const weakDomains =
        Array.isArray(metadata.weak_domains)
            ? metadata.weak_domains
            : [];

    const domainBreakdown = Array.isArray(
        metadata.domain_breakdown,
    )
        ? metadata.domain_breakdown
        : [];

    const averageConfidence = Number(
        metadata.average_confidence ?? 0,
    );

    const evaluationMethod = String(
        metadata.evaluation_method ??
        "Institutional Domain Consensus",
    );

    const decisionEngine = String(
        metadata.decision_engine ??
        "Allocator",
    );

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="flex items-center justify-between">

                    <div>

                        <h2 className="text-2xl font-semibold">

                            Institutional Allocator Decision

                        </h2>

                        <p className="mt-1 text-sm text-slate-500">

                            Final institutional decision generated
                            after evaluating every investigation
                            domain.

                        </p>

                    </div>

                    <span
                        className={`rounded-full px-4 py-2 text-sm font-semibold ${result.badge}`}
                    >
                        {allocator.decision}
                    </span>

                </div>

            </div>

            <div className="grid gap-6 p-6 lg:grid-cols-5">

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Confidence

                    </div>

                    <div className="mt-2 text-4xl font-bold">

                        {allocator.confidence.toFixed(1)}%

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Residual Risk

                    </div>

                    <div className="mt-2 text-lg font-semibold">

                        {allocator.residual_risk}

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Required Actions

                    </div>

                    <div className="mt-2 text-4xl font-bold">

                        {actions.length}

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Domains Evaluated

                    </div>

                    <div className="mt-2 text-4xl font-bold">

                        {completedDomains}

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Weak Domains

                    </div>

                    <div className="mt-2 text-4xl font-bold">

                        {weakDomains.length}

                    </div>

                </div>

                {weakDomains.length > 0 && (

                <div className="border-t border-slate-100 px-6 py-5">

                    <div className="mb-3 text-xs uppercase tracking-wide text-slate-500">

                        Weak Investigation Domains

                    </div>

                    <div className="flex flex-wrap gap-2">

                        {weakDomains.map(domain => (

                            <span
                                key={domain}
                                className="rounded-full bg-red-100 px-3 py-1 text-sm text-red-700"
                            >

                                {domain}

                            </span>

                        ))}

                    </div>

                </div>

                )}

            </div>

            <div className="px-6 pb-2">

                <div
                    className={`text-3xl font-bold ${decisionColor(
                        allocator.decision,
                    )}`}
                >

                    {allocator.decision.replaceAll("_", " ")}

                </div>

            </div>

            <div className="border-t border-slate-100 px-6 py-5">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Decision Rationale

                </div>

                <p className="mt-3 text-slate-700 leading-7">

                    {allocator.rationale}

                </p>

            </div>

            {actions.length > 0 && (

                <div className="border-t border-slate-100 px-6 py-5">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Required Actions

                    </div>

                    <ul className="mt-3 list-disc space-y-2 pl-6">

                        {actions.map(

                            (action) => (

                                <li
                                    key={action}
                                    className="text-slate-700"
                                >
                                    {action}
                                </li>

                            ),

                        )}

                    </ul>

                </div>

            )}

            <div className="border-t border-slate-100 px-6 py-5">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Institutional Summary

                </div>

                <div className="mt-3 rounded-lg bg-slate-50 p-5 leading-8">

                    The Institutional Investigation System evaluated{" "}

                    <strong>{completedDomains}</strong>{" "}

                    investigation domain(s).

                    The allocator produced a decision of{" "}

                    <strong>{allocator.decision}</strong>{" "}

                    with{" "}

                    <strong>{allocator.confidence.toFixed(1)}%</strong>{" "}

                    confidence while identifying{" "}

                    <strong>{weakDomains.length}</strong>{" "}

                    domain(s) requiring additional institutional review.

                </div>

            </div>

            <div className="border-t border-slate-100 px-6 py-5">

                <div className="mb-4 text-xs uppercase tracking-wide text-slate-500">

                    Allocator Diagnostics

                </div>

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

                    <div className="rounded-lg bg-slate-50 p-4">

                        <div className="text-xs uppercase text-slate-500">

                            Decision Engine

                        </div>

                        <div className="mt-2 font-semibold">

                            {decisionEngine}

                        </div>

                    </div>

                    <div className="rounded-lg bg-slate-50 p-4">

                        <div className="text-xs uppercase text-slate-500">

                            Evaluation Method

                        </div>

                        <div className="mt-2 font-semibold">

                            {evaluationMethod}

                        </div>

                    </div>

                    <div className="rounded-lg bg-slate-50 p-4">

                        <div className="text-xs uppercase text-slate-500">

                            Average Confidence

                        </div>

                        <div className="mt-2 font-semibold">

                            {averageConfidence.toFixed(1)}%

                        </div>

                    </div>

                    <div className="rounded-lg bg-slate-50 p-4">

                        <div className="text-xs uppercase text-slate-500">

                            Domains Evaluated

                        </div>

                        <div className="mt-2 font-semibold">

                            {completedDomains}

                        </div>

                    </div>

                </div>

            </div>

            {domainBreakdown.length > 0 && (

            <div className="border-t border-slate-100 px-6 py-5">

                <div className="mb-4 text-xs uppercase tracking-wide text-slate-500">

                    Institutional Domain Contribution

                </div>

                <div className="space-y-3">

                    {domainBreakdown.map((domain: any) => (

                        <div
                            key={domain.name}
                            className="rounded-lg border border-slate-200 p-4"
                        >

                            <div className="flex items-center justify-between">

                                <div>

                                    <div className="font-semibold">

                                        {domain.name}

                                    </div>

                                    <div className="mt-1 text-sm text-slate-500">

                                        {domain.finding_count} finding(s)

                                    </div>

                                </div>

                                <div className="text-right">

                                    <div className="text-lg font-bold">

                                        {Number(
                                            domain.confidence,
                                        ).toFixed(1)}%

                                    </div>

                                    <div className="text-xs uppercase text-slate-500">

                                        {domain.status}

                                    </div>

                                </div>

                            </div>

                            <div className="mt-3 flex items-center justify-between">

                                <span className="text-xs uppercase text-slate-500">

                                    Highest Severity

                                </span>

                                <span className="font-medium">

                                    {domain.highest_severity}

                                </span>

                            </div>

                        </div>

                    ))}

                </div>

            </div>

            )}

        </section>

    );

}