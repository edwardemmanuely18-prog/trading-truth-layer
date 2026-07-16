"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface Props {
    report: InvestigationReport;
}

export default function CriticalPathReportCard({
    report,
}: Props) {

    const criticalPath =
        report.critical_path;

    return (

        <section className="rounded-xl border border-slate-200 bg-white">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Root Cause Analysis

                </div>

                <h3 className="mt-2 text-xl font-semibold text-slate-900">

                    Critical Path Investigation Report

                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">

                    Produces the institutional causal reconstruction of the
                    investigation by identifying the root cause, tracing
                    evidence dependencies, ranking investigation findings
                    and documenting the remediation roadmap.

                </p>

            </div>

            <div className="space-y-6 p-6">

                <div className="grid gap-4 md:grid-cols-2">

                    <Metric
                        label="Critical Path Score"
                        value={`${criticalPath?.score ?? 0}`}
                    />

                    <Metric
                        label="Root Cause"
                        value={
                            criticalPath?.root_cause ??
                            "Not Determined"
                        }
                    />

                    <Metric
                        label="Critical Steps"
                        value={
                            String(
                                criticalPath?.steps?.length ?? 0,
                            )
                        }
                    />

                    <Metric
                        label="Recommendations"
                        value={
                            String(
                                criticalPath?.recommendations?.length ?? 0,
                            )
                        }
                    />

                </div>

                <div className="rounded-lg bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Report Contents

                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2">

                        <Section text="Root Cause Identification" />

                        <Section text="Critical Investigation Path" />

                        <Section text="Finding Prioritization" />

                        <Section text="Evidence Dependency Chain" />

                        <Section text="Risk Escalation Analysis" />

                        <Section text="Decision Rationale" />

                        <Section text="Remediation Roadmap" />

                        <Section text="Residual Risk Assessment" />

                        <Section text="Institutional Recommendations" />

                        <Section text="Appendix" />

                    </div>

                </div>

                <button
                    type="button"
                    className="
                        rounded-lg
                        bg-slate-900
                        px-4
                        py-2
                        text-sm
                        font-semibold
                        text-white
                        transition
                        hover:bg-slate-800
                    "
                >

                    Generate Critical Path Report

                </button>

            </div>

        </section>

    );

}

function Metric({

    label,

    value,

}: {

    label: string;

    value: string;

}) {

    return (

        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {label}

            </div>

            <div className="mt-2 text-lg font-semibold text-slate-900">

                {value}

            </div>

        </div>

    );

}

function Section({

    text,

}: {

    text: string;

}) {

    return (

        <div className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">

            {text}

        </div>

    );

}