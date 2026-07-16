"use client";

import { InvestigationDomain } from "@/lib/api";

interface DomainCardProps {
    title: string;
    domain?: InvestigationDomain | null;
}

function confidenceStatus(confidence: number): string {
    if (confidence >= 95) return "Healthy";
    if (confidence >= 80) return "Stable";
    if (confidence >= 60) return "Watch";
    return "Attention";
}

function statusColor(confidence: number): string {
    if (confidence >= 95) {
        return "bg-emerald-100 text-emerald-700";
    }

    if (confidence >= 80) {
        return "bg-blue-100 text-blue-700";
    }

    if (confidence >= 60) {
        return "bg-amber-100 text-amber-700";
    }

    return "bg-red-100 text-red-700";
}

function severityColor(severity?: string): string {

    switch ((severity ?? "").toUpperCase()) {

        case "CRITICAL":
            return "bg-red-100 text-red-700";

        case "HIGH":
            return "bg-orange-100 text-orange-700";

        case "MEDIUM":
            return "bg-amber-100 text-amber-700";

        case "LOW":
            return "bg-blue-100 text-blue-700";

        default:
            return "bg-emerald-100 text-emerald-700";

    }

}

export default function DomainCard({
    title,
    domain,
}: DomainCardProps) {

    if (!domain) {
        return (
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <h3 className="text-lg font-semibold">
                    {title}
                </h3>

                <div className="mt-6 text-sm text-slate-500">
                    Investigation not available.
                </div>
            </div>
        );
    }

    const metadataEntries = Object.entries(
        domain.metadata ?? {},
    );

    const findings = domain.findings ?? [];

    const highestSeverity =
        findings.length > 0
            ? findings[0].severity
            : "Information";

    const metadataCount =
        metadataEntries.length;

    const findingCount =
        findings.length;

    return (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">

            <div className="flex items-center justify-between">

                <h3 className="text-lg font-semibold text-slate-900">
                    {title}
                </h3>

                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${statusColor(
                        domain.confidence,
                    )}`}
                >
                    {confidenceStatus(domain.confidence)}
                </span>

            </div>

            <div className="mt-5 grid grid-cols-2 gap-4">

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">
                        Confidence
                    </div>

                    <div className="mt-1 text-2xl font-bold">
                        {domain.confidence.toFixed(1)}%
                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">
                        Findings
                    </div>

                    <div className="mt-1 text-2xl font-bold">
                        {domain.findings?.length ?? 0}
                    </div>

                </div>

            </div>

            <div className="mt-5">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Highest Severity

                </div>

                <div className="mt-2">

                    <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${severityColor(
                            highestSeverity,
                        )}`}
                    >

                        {highestSeverity}

                    </span>

                </div>

            </div>

            {findings.length > 0 && (

            <div className="mt-6">

                <div className="mb-3 text-xs uppercase tracking-wide text-slate-500">

                    Investigation Findings

                </div>

                <div className="space-y-3">

                    {findings.slice(0,3).map((finding)=> (

                        <div
                            key={finding.id}
                            className="rounded-lg border bg-slate-50 p-3"
                        >

                            <div className="font-medium">

                                {finding.title}

                            </div>

                            <div className="mt-1 text-sm text-slate-600">

                                {finding.description}

                            </div>

                        </div>

                    ))}

                </div>

            </div>

            )}

            {metadataEntries.length > 0 && (

                <div className="mt-5 border-t border-slate-100 pt-4">

                    <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Metadata
                    </div>

                    <div className="space-y-1 text-sm">

                        {metadataEntries.slice(0,6).map(
                            ([key, value]) => (

                                <div
                                    key={key}
                                    className="flex justify-between"
                                >
                                    <span className="text-slate-500">
                                        {key}
                                    </span>

                                    <span className="font-medium text-slate-700">
                                        {String(value)}
                                    </span>

                                </div>

                            ),
                        )}

                    </div>

                </div>

            )}

            <div className="mt-6 border-t border-slate-100 pt-4">

                <div className="grid grid-cols-2 gap-4">

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Metadata Fields

                        </div>

                        <div className="mt-1 text-xl font-bold">

                            {metadataCount}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Findings Available

                        </div>

                        <div className="mt-1 text-xl font-bold">

                            {findingCount}

                        </div>

                    </div>

                </div>

            </div>

            <div className="mt-6 rounded-lg bg-slate-50 p-4">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Institutional Interpretation

                </div>

                <div className="mt-2 text-sm leading-6 text-slate-700">

                    This investigation domain contributes to the final
                    allocator decision through its confidence score,
                    findings and supporting metadata. Each domain is
                    generated independently from the canonical
                    Investigation Context before institutional reasoning
                    combines all domain outputs.

                </div>

            </div>

        </div>
    );
}