"use client";

import { InvestigationReport } from "@/lib/api";

interface Props {
    report: InvestigationReport;
}

function CoverageCard({
    title,
    value,
    subtitle,
}:{
    title:string;
    value:string;
    subtitle:string;
}){

    return(

        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {title}

            </div>

            <div className="mt-2 text-3xl font-bold">

                {value}

            </div>

            <div className="mt-2 text-sm text-slate-500">

                {subtitle}

            </div>

        </div>

    );

}

export default function InvestigationCoveragePanel({

    report,

}:Props){

    const evidenceNodes =
        report.nodes.length;

    const relationships =
        report.relationships.length;

    const findings =
        report.findings.length;

    const recommendations =
        report.recommendations.length;

    const timeline =
        report.timeline.length;

    return(

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                    Investigation Coverage

                </div>

                <h2 className="mt-2 text-2xl font-semibold">

                    Institutional Coverage Metrics

                </h2>

                <p className="mt-2 max-w-4xl text-sm leading-7 text-slate-600">

                    Canonical investigation coverage produced from the
                    Investigation Context.

                </p>

            </div>

            <div className="grid gap-4 p-6 md:grid-cols-3 xl:grid-cols-5">

                <CoverageCard

                    title="Evidence Nodes"

                    value={String(evidenceNodes)}

                    subtitle="Evidence analysed"

                />

                <CoverageCard

                    title="Relationships"

                    value={String(relationships)}

                    subtitle="Relationships reconstructed"

                />

                <CoverageCard

                    title="Timeline"

                    value={String(timeline)}

                    subtitle="Events reconstructed"

                />

                <CoverageCard

                    title="Findings"

                    value={String(findings)}

                    subtitle="Institutional findings"

                />

                <CoverageCard

                    title="Recommendations"

                    value={String(recommendations)}

                    subtitle="Allocator recommendations"

                />

            </div>

        </section>

    );

}