"use client";

import type {
    InvestigationFinding,
} from "@/lib/api";

import SectionCard from "../common/SectionCard";

interface Props {

    findings: InvestigationFinding[];

}

function severityClasses(
    severity: string,
): string {

    switch (
        severity.toUpperCase()
    ) {

        case "CRITICAL":
            return "bg-red-100 text-red-700 border-red-200";

        case "HIGH":
            return "bg-orange-100 text-orange-700 border-orange-200";

        case "MEDIUM":
            return "bg-amber-100 text-amber-700 border-amber-200";

        case "LOW":
            return "bg-blue-100 text-blue-700 border-blue-200";

        default:
            return "bg-emerald-100 text-emerald-700 border-emerald-200";

    }

}

function severityRank(
    severity: string,
): number {

    switch (severity.toUpperCase()) {

        case "CRITICAL":
            return 5;

        case "HIGH":
            return 4;

        case "MEDIUM":
            return 3;

        case "LOW":
            return 2;

        default:
            return 1;

    }

}

function Metric({

    label,

    value,

}: {

    label: string;

    value: number;

}) {

    return (

        <div className="rounded-lg bg-slate-50 p-3">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {label}

            </div>

            <div className="mt-1 text-lg font-semibold">

                {value}

            </div>

        </div>

    );

}

function FindingCard({

    finding,

}: {

    finding: InvestigationFinding;

}) {

    const evidence =

        finding.evidence ?? [];

    return (

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="flex items-start justify-between gap-4">

                    <div>

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Finding ID

                        </div>

                        <div className="mt-1 font-mono text-sm">

                            {finding.id}

                        </div>

                        <h3 className="mt-4 text-xl font-semibold">

                            {finding.title}

                        </h3>

                        {"category" in finding && (

                            <div className="mt-2">

                                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">

                                    {String((finding as any).category)}

                                </span>

                            </div>

                        )}

                    </div>

                    <div className="text-right">

                        <span
                            className={`rounded-full border px-3 py-1 text-xs font-semibold ${severityClasses(
                                finding.severity,
                            )}`}
                        >

                            {finding.severity}

                        </span>

                        <div className="mt-4">

                            <div className="text-xs uppercase tracking-wide text-slate-500">

                                Confidence

                            </div>

                            <div className="mt-1 text-2xl font-bold">

                                {finding.confidence.toFixed(
                                    1,
                                )}
                                %

                            </div>

                        </div>

                    </div>

                </div>

            </div>

            <div className="px-6 py-5">

                <p className="leading-7 text-slate-700">

                    {finding.description}

                </p>

                            <div className="mt-6 grid gap-4 md:grid-cols-5">

                    <Metric
                        label="Claims"
                        value={
                            finding.affected_claims
                                ?.length ?? 0
                        }
                    />

                    <Metric
                        label="Trades"
                        value={
                            finding.affected_trades
                                ?.length ?? 0
                        }
                    />

                    <Metric
                        label="Members"
                        value={
                            finding.affected_members
                                ?.length ?? 0
                        }
                    />

                    <Metric
                        label="Accounts"
                        value={
                            finding.affected_accounts
                                ?.length ?? 0
                        }
                    />

                    <Metric
                        label="Sync Jobs"
                        value={
                            finding.affected_sync_jobs
                                ?.length ?? 0
                        }
                    />

                </div>

                <div className="mt-8 grid gap-6 lg:grid-cols-2">

                    <div>

                        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">

                            Institutional Recommendation

                        </div>

                        <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-4">

                            {finding.recommendation ||

                                "No recommendation available."}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">

                            Supporting Evidence

                        </div>

                        <div className="mt-2 text-xs text-slate-500">

                            {evidence.length} evidence reference(s)

                        </div>

                        {evidence.length === 0 ? (

                            <div className="mt-3 rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">

                                No supporting evidence references
                                were supplied by this investigation.

                            </div>

                        ) : (

                            <div className="mt-3 space-y-2">

                                {evidence.map(

                                    (

                                        item,

                                        index,

                                    ) => (

                                        <div
                                            key={`${finding.id}-${index}`}
                                            className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3"
                                        >

                                            {item}

                                        </div>

                                    ),

                                )}

                            </div>

                        )}

                    </div>

                </div>

                {/* ========================= */}
                {/* Investigation Metadata */}
                {/* ========================= */}

                {"metadata" in finding &&
                (finding as any).metadata &&
                Object.keys((finding as any).metadata).length > 0 && (

                    <div className="mt-8">

                        <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">

                            Investigation Metadata

                        </div>

                        <div className="grid gap-3 md:grid-cols-2">

                            {Object.entries(
                                (finding as any).metadata,
                            ).map(([key, value]) => (

                                <div
                                    key={key}
                                    className="rounded-lg border border-slate-200 bg-slate-50 p-3"
                                >

                                    <div className="text-xs uppercase tracking-wide text-slate-500">

                                        {key}

                                    </div>

                                    <div className="mt-1 font-medium">

                                        {String(value)}

                                    </div>

                                </div>

                            ))}

                        </div>

                    </div>

                )}

            </div>

        </div>

    );

}

export default function FindingsTable({

    findings,

}: Props) {

    const orderedFindings = [...findings].sort(

        (a, b) =>

            severityRank(b.severity) -

            severityRank(a.severity),

    );

    return (

        <SectionCard

            title="Institutional Findings"

            subtitle="Risk findings generated by the Institutional Investigation System"

        >

            {findings.length === 0 ? (

                <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-500">

                    No investigation findings were generated.

                </div>

            ) : (

                <div
                    className="
                        max-h-[1000px]
                        overflow-y-auto
                        rounded-xl
                        border
                        border-slate-200
                    "
                >

                    <div
                        className="
                            sticky
                            top-0
                            z-10
                            border-b
                            border-slate-200
                            bg-white
                            p-6
                        "
                    >

                        <div className="grid gap-4 md:grid-cols-5">

                            <Metric
                                label="Critical"
                                value={
                                    orderedFindings.filter(
                                        f => f.severity === "CRITICAL",
                                    ).length
                                }
                            />

                            <Metric
                                label="High"
                                value={
                                    orderedFindings.filter(
                                        f => f.severity === "HIGH",
                                    ).length
                                }
                            />

                            <Metric
                                label="Medium"
                                value={
                                    orderedFindings.filter(
                                        f => f.severity === "MEDIUM",
                                    ).length
                                }
                            />

                            <Metric
                                label="Low"
                                value={
                                    orderedFindings.filter(
                                        f => f.severity === "LOW",
                                    ).length
                                }
                            />

                            <Metric
                                label="Total"
                                value={orderedFindings.length}
                            />

                        </div>

                    </div>

                    <div className="space-y-6 p-6">

                        {orderedFindings.map(

                            (finding) => (

                                <FindingCard
                                    key={finding.id}
                                    finding={finding}
                                />

                            ),

                        )}

                    </div>

                </div>

            )}

        </SectionCard>

    );

}