"use client";

import { useState } from "react";

import {
    InvestigationReport,
    downloadInstitutionalInvestigationReport,
} from "@/lib/api";

interface Props {
    workspaceId: number;
    report: InvestigationReport;
}

export default function InstitutionalInvestigationCard({
    workspaceId,
    report,
}: Props) {

    const [downloading, setDownloading] =
        useState(false);

    const handleDownload = async () => {

        try {

            setDownloading(true);

            await downloadInstitutionalInvestigationReport(
                workspaceId,
            );

        } catch (error) {

            console.error(error);

            alert(
                "Failed to generate the Institutional Investigation Report.",
            );

        } finally {

            setDownloading(false);

        }

    };

    return (

        <section className="rounded-xl border border-slate-200 bg-white">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Canonical Investigation Report

                </div>

                <h3 className="mt-2 text-xl font-semibold text-slate-900">

                    Institutional Investigation Report (IIR)

                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">

                    The complete institutional forensic report generated
                    from the canonical Investigation Context. This report
                    reconstructs every investigation domain, evidence
                    relationship, timeline event, finding and allocator
                    decision into a single institutional document suitable
                    for due diligence, compliance and independent review.

                </p>

            </div>

            <div className="space-y-6 p-6">

                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

                    <Stat
                        label="Investigation Domains"
                        value="8"
                    />

                    <Stat
                        label="Timeline Events"
                        value={String(report.timeline.length)}
                    />

                    <Stat
                        label="Evidence Nodes"
                        value={String(report.nodes.length)}
                    />

                    <Stat
                        label="Relationships"
                        value={String(report.relationships.length)}
                    />

                    <Stat
                        label="Findings"
                        value={String(report.findings.length)}
                    />

                    <Stat
                        label="Recommendations"
                        value={String(report.recommendations.length)}
                    />

                </div>

                <div className="rounded-lg bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Report Contents

                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2">

                        <ContentItem text="Institutional Cover Page" />
                        <ContentItem text="Investigation Provenance" />
                        <ContentItem text="Executive Summary" />
                        <ContentItem text="Timeline Reconstruction" />
                        <ContentItem text="Evidence Intelligence" />
                        <ContentItem text="Relationship Graph" />
                        <ContentItem text="Eight Investigation Domains" />
                        <ContentItem text="Critical Investigation Path" />
                        <ContentItem text="Institutional Findings" />
                        <ContentItem text="Recommendations" />
                        <ContentItem text="Allocator Decision" />
                        <ContentItem text="Technical Appendix" />

                    </div>

                </div>

                <button
                    type="button"
                    onClick={handleDownload}
                    disabled={downloading}
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
                        disabled:cursor-not-allowed
                        disabled:opacity-60
                    "
                >

                    {downloading
                        ? "Generating Report..."
                        : "Generate Institutional Investigation Report"}

                </button>

            </div>

        </section>

    );

}

function Stat({
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

function ContentItem({
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