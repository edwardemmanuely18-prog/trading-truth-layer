"use client";

import type {
    InvestigationSummary,
} from "@/lib/api";

import SectionCard from "../common/SectionCard";

interface Props {

    summary: InvestigationSummary;

}

function Metric({

    label,

    value,

}: {

    label: string;

    value: number | string;

}) {

    return (

        <div
            className="
                rounded-lg
                border
                bg-slate-50
                dark:bg-neutral-800
                p-4
            "
        >

            <div
                className="
                    text-xs
                    uppercase
                    tracking-wider
                    text-slate-500
                "
            >

                {label}

            </div>

            <div
                className="
                    mt-2
                    text-3xl
                    font-bold
                "
            >

                {value}

            </div>

        </div>

    );

}

function riskBadge(risk: string) {

    switch (risk.toUpperCase()) {

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

export default function ExecutiveSummary({

    summary,

}: Props) {

    return (

        <SectionCard

            title="Executive Investigation Brief"

            subtitle="Institutional Investigation System (IIS)"

        >

            <div className="space-y-10">

                {/* ====================================================== */}
                {/* Executive Status */}
                {/* ====================================================== */}

                <div className="grid gap-8 lg:grid-cols-2">

                    <div>

                        <div className="text-xs uppercase tracking-widest text-slate-500">

                            Investigation Confidence

                        </div>

                        <div className="mt-3 text-6xl font-bold">

                            {summary.investigation_confidence.toFixed(2)}

                        </div>

                    </div>

                    <div>

                        <div className="text-xs uppercase tracking-widest text-slate-500">

                            Overall Risk

                        </div>

                        <div className="mt-3">

                            <span
                                className={`rounded-full px-4 py-2 text-lg font-semibold ${riskBadge(
                                    summary.overall_risk,
                                )}`}
                            >

                                {summary.overall_risk}

                            </span>

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Findings */}
                {/* ====================================================== */}

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Investigation Findings

                    </div>

                    <div className="grid gap-4 md:grid-cols-5">

                        <Metric

                            label="Critical"

                            value={summary.critical_findings}

                        />

                        <Metric

                            label="High"

                            value={summary.high_findings}

                        />

                        <Metric

                            label="Medium"

                            value={summary.medium_findings}

                        />

                        <Metric

                            label="Low"

                            value={summary.low_findings}

                        />

                        <Metric

                            label="Information"

                            value={summary.informational_findings}

                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Investigation Statistics */}
                {/* ====================================================== */}

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Investigation Statistics

                    </div>

                    <div className="grid gap-4 md:grid-cols-4">

                        <Metric

                            label="Total Findings"

                            value={summary.total_findings}

                        />

                        <Metric

                            label="Evidence Nodes"

                            value={summary.evidence_nodes}

                        />

                        <Metric

                            label="Relationships"

                            value={summary.relationships}

                        />

                        <Metric

                            label="Timeline Events"

                            value={summary.timeline_events}

                        />

                    </div>

                </div>

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Investigation Coverage

                    </div>

                    <div className="grid gap-4 md:grid-cols-4">

                        <Metric

                            label="Confidence"

                            value={`${summary.investigation_confidence.toFixed(1)}%`}

                        />

                        <Metric

                            label="Entities"

                            value={summary.evidence_nodes}

                        />

                        <Metric

                            label="Relationships"

                            value={summary.relationships}

                        />

                        <Metric

                            label="Timeline"

                            value={summary.timeline_events}

                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Affected Objects */}
                {/* ====================================================== */}

                <div>

                    <div className="mb-4 text-xs uppercase tracking-widest text-slate-500">

                        Investigation Scope Impact

                    </div>

                    <div className="grid gap-4 md:grid-cols-4">

                        <Metric

                            label="Claims"

                            value={summary.affected_claims}

                        />

                        <Metric

                            label="Members"

                            value={summary.affected_members}

                        />

                        <Metric

                            label="Accounts"

                            value={summary.affected_accounts}

                        />

                        <Metric

                            label="Sync Jobs"

                            value={summary.affected_sync_jobs}

                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Executive Narrative */}
                {/* ====================================================== */}

                <div className="space-y-4">

                    {summary.critical_findings > 0 && (

                        <div className="rounded-lg border border-red-200 bg-red-50 p-4">

                            <div className="font-semibold text-red-700">

                                Immediate Attention Required

                            </div>

                            <div className="mt-2 text-sm text-red-700">

                                This investigation contains

                                {" "}

                                <strong>

                                    {summary.critical_findings}

                                </strong>

                                {" "}

                                critical finding(s).

                            </div>

                        </div>

                    )}

                    <div>

                        {summary.executive_summary}

                    </div>

                </div>

            </div>

        </SectionCard>

    );

}