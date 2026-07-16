"use client";

import {
    InvestigationDomain,
    InvestigationFinding,
} from "@/lib/api";

interface DomainDetailsPanelProps {
    title: string;
    domain?: InvestigationDomain | null;
}

function severityClasses(severity: string) {

    switch (severity.toUpperCase()) {

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

function domainHealth(confidence: number): string {

    if (confidence >= 95) return "Healthy";

    if (confidence >= 85) return "Stable";

    if (confidence >= 70) return "Review";

    return "Attention";

}

function FindingCard({
    finding,
}: {
    finding: InvestigationFinding;
}) {

    return (

        <div className="rounded-lg border border-slate-200 bg-white p-5">

            <div className="flex items-center justify-between">

                <h4 className="font-semibold text-slate-900">

                    {finding.title}

                </h4>

                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${severityClasses(
                        finding.severity,
                    )}`}
                >

                    {finding.severity}

                </span>

            </div>

            <p className="mt-3 text-sm text-slate-600">

                {finding.description}

            </p>

            {finding.evidence &&
            finding.evidence.length > 0 && (

            <div className="mt-4 rounded-lg bg-slate-50 p-4">

                <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">

                    Supporting Evidence

                </div>

                <div className="space-y-2">

                    {finding.evidence.map((item, index) => (

                        <div
                            key={index}
                            className="rounded border bg-white px-3 py-2 text-sm"
                        >

                            {item}

                        </div>

                    ))}

                </div>

            </div>

            )}

            <div className="mt-4 grid gap-4 md:grid-cols-2">

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Confidence

                    </div>

                    <div className="mt-1 font-semibold">

                        {finding.confidence.toFixed(1)}%

                    </div>

                </div>

                <div>

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Recommendation

                    </div>

                    <div className="mt-1 text-sm">

                        {finding.recommendation || "No recommendation"}

                    </div>

                </div>

            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-5">

                <div className="rounded bg-slate-50 p-3">

                    <div className="text-xs uppercase">

                        Claims

                    </div>

                    <div className="mt-1 font-semibold">

                        {finding.affected_claims?.length ?? 0}

                    </div>

                </div>

                <div className="rounded bg-slate-50 p-3">

                    <div className="text-xs uppercase">

                        Trades

                    </div>

                    <div className="mt-1 font-semibold">

                        {finding.affected_trades?.length ?? 0}

                    </div>

                </div>

                <div className="rounded bg-slate-50 p-3">

                    <div className="text-xs uppercase">

                        Members

                    </div>

                    <div className="mt-1 font-semibold">

                        {finding.affected_members?.length ?? 0}

                    </div>

                </div>

                <div className="rounded bg-slate-50 p-3">

                    <div className="text-xs uppercase">

                        Accounts

                    </div>

                    <div className="mt-1 font-semibold">

                        {finding.affected_accounts?.length ?? 0}

                    </div>

                </div>

                <div className="rounded bg-slate-50 p-3">

                    <div className="text-xs uppercase">

                        Sync Jobs

                    </div>

                    <div className="mt-1 font-semibold">

                        {finding.affected_sync_jobs?.length ?? 0}

                    </div>

                </div>

            </div>

        </div>

    );

}

export default function DomainDetailsPanel({

    title,

    domain,

}: DomainDetailsPanelProps) {

    if (!domain) {

        return (

            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">

                <h2 className="text-2xl font-semibold">

                    {title}

                </h2>

                <p className="mt-4 text-slate-500">

                    Investigation domain unavailable.

                </p>

            </section>

        );

    }

    const metadataEntries = Object.entries(
        domain.metadata ?? {},
    );

    const criticalCount =
        domain.findings.filter(
            f => f.severity.toUpperCase() === "CRITICAL",
        ).length;

    const highCount =
        domain.findings.filter(
            f => f.severity.toUpperCase() === "HIGH",
        ).length;

    const mediumCount =
        domain.findings.filter(
            f => f.severity.toUpperCase() === "MEDIUM",
        ).length;

    const lowCount =
        domain.findings.filter(
            f => f.severity.toUpperCase() === "LOW",
        ).length;

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="flex items-center justify-between">

                    <div>

                        <h2 className="text-2xl font-semibold">

                            {title}

                        </h2>

                        <p className="mt-1 text-sm text-slate-500">

                            Detailed institutional investigation
                            results for this domain.

                        </p>

                    </div>

                    <div className="text-right">

                        <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold">

                            {domainHealth(domain.confidence)}

                        </div>

                        <div className="mt-4 text-xs uppercase tracking-wide text-slate-500">

                            Confidence

                        </div>

                        <div className="mt-1 text-3xl font-bold">

                            {domain.confidence.toFixed(1)}%

                        </div>

                    </div>

                </div>

                <div className="grid gap-4 border-b border-slate-100 px-6 py-5 md:grid-cols-5">

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Findings

                        </div>

                        <div className="mt-2 text-3xl font-bold">

                            {domain.findings.length}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Critical

                        </div>

                        <div className="mt-2 text-3xl font-bold text-red-600">

                            {criticalCount}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            High

                        </div>

                        <div className="mt-2 text-3xl font-bold text-orange-600">

                            {highCount}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Medium

                        </div>

                        <div className="mt-2 text-3xl font-bold text-amber-600">

                            {mediumCount}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Low

                        </div>

                        <div className="mt-2 text-3xl font-bold text-blue-600">

                            {lowCount}

                        </div>

                    </div>

                </div>

            </div>

            {metadataEntries.length > 0 && (

                <div className="border-b border-slate-100 px-6 py-5">

                    <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">

                        Metadata

                    </h3>

                    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">

                        {metadataEntries.map(([key, value]) => (

                            <div
                                key={key}
                                className="rounded-lg bg-slate-50 p-4"
                            >

                                <div className="text-xs uppercase tracking-wide text-slate-500">

                                    {key}

                                </div>

                                <div className="mt-1 font-medium text-slate-800">

                                    {Array.isArray(value)
                                        ? value.join(", ")
                                        : typeof value === "object" && value !== null
                                        ? JSON.stringify(value, null, 2)
                                        : String(value)}

                                </div>

                            </div>

                        ))}

                    </div>

                </div>

            )}

            <div className="px-6 py-6">

                <div className="mb-5 flex items-center justify-between">

                    <h3 className="text-lg font-semibold">

                        Investigation Findings

                    </h3>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium">

                        {domain.findings.length} Findings

                    </span>

                </div>

                {domain.findings.length === 0 ? (

                    <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-slate-500">

                        No findings reported.

                    </div>

                ) : (

                    <div className="space-y-4">

                        {domain.findings.map((finding) => (

                            <FindingCard
                                key={finding.id}
                                finding={finding}
                            />

                        ))}

                    </div>

                )}

            </div>

        </section>

    );

}