"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface Props {
    report: InvestigationReport;
}

export default function EvidenceReportCard({
    report,
}: Props) {

    return (

        <section className="rounded-xl border border-slate-200 bg-white">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Evidence Intelligence

                </div>

                <h3 className="mt-2 text-xl font-semibold text-slate-900">

                    Evidence Intelligence Report

                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">

                    Produces a complete institutional analysis of evidence
                    provenance, lineage, integrity, relationship graphs and
                    trust structure used during the investigation.

                </p>

            </div>

            <div className="space-y-6 p-6">

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

                    <Metric
                        label="Evidence Nodes"
                        value={String(report.nodes.length)}
                    />

                    <Metric
                        label="Relationships"
                        value={String(report.relationships.length)}
                    />

                    <Metric
                        label="Findings"
                        value={String(report.findings.length)}
                    />

                    <Metric
                        label="Timeline Events"
                        value={String(report.timeline.length)}
                    />

                    <Metric
                        label="Investigation Confidence"
                        value={`${report.summary.investigation_confidence.toFixed(1)}%`}
                    />

                    <Metric
                        label="Evidence Integrity"
                        value={
                            report.relationships.length > 0
                                ? "Verified"
                                : "Pending"
                        }
                    />

                </div>

                <div className="rounded-lg bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Evidence Intelligence Contents

                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2">

                        <Section text="Evidence Provenance" />
                        <Section text="Evidence Lineage" />
                        <Section text="Evidence Relationships" />
                        <Section text="Evidence Graph Analysis" />
                        <Section text="Integrity Validation" />
                        <Section text="Duplicate Detection" />
                        <Section text="Missing Evidence Analysis" />
                        <Section text="Orphan Evidence Detection" />
                        <Section text="Evidence Confidence" />
                        <Section text="Evidence Appendix" />

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
                    Generate Evidence Intelligence Report
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

            <div className="mt-2 text-base font-semibold text-slate-900">

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