"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface InvestigationMetadataPanelProps {
    report: InvestigationReport;
}

function formatTimestamp(value?: string | null) {

    if (!value) {
        return "Unavailable";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function MetadataItem({
    label,
    value,
}: {
    label: string;
    value: React.ReactNode;
}) {
    return (

        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {label}

            </div>

            <div className="mt-2 text-sm font-semibold break-all">

                {value}

            </div>

        </div>

    );
}

export default function InvestigationMetadataPanel({
    report,
}: InvestigationMetadataPanelProps) {

    const allocatorMetadata =
        report.allocator?.metadata ?? {};

    const reportMetadata =
        report.metadata ?? {};

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Investigation Metadata

                </div>

                <h2 className="mt-2 text-2xl font-semibold">

                    Investigation Provenance

                </h2>

                <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-500">

                    Canonical metadata describing how this investigation
                    was generated and which institutional reasoning engines
                    contributed to the final allocator decision.

                </p>

            </div>

            <div className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-4">

                <MetadataItem
                    label="Decision Engine"
                    value="Institutional Investigation System"
                />

                <MetadataItem
                    label="Allocator Engine"
                    value="Allocator V1"
                />

                <MetadataItem
                    label="Investigation Domains"
                    value={`${allocatorMetadata.completed_domains ?? 0}/8`}
                />

                <MetadataItem
                    label="Investigation Confidence"
                    value={`${report.summary.investigation_confidence.toFixed(1)}%`}
                />

                <MetadataItem
                    label="Decision"
                    value={report.allocator?.decision ?? "Unknown"}
                />

                <MetadataItem
                    label="Residual Risk"
                    value={report.allocator?.residual_risk ?? "Unknown"}
                />

                <MetadataItem
                    label="Evidence Nodes"
                    value={report.nodes.length}
                />

                <MetadataItem
                    label="Relationships"
                    value={report.relationships.length}
                />

                <MetadataItem
                    label="Findings"
                    value={report.findings.length}
                />

                <MetadataItem
                    label="Recommendations"
                    value={report.recommendations.length}
                />

                <MetadataItem
                    label="Timeline Events"
                    value={report.timeline.length}
                />

                <MetadataItem
                    label="Generated"
                    value={
                        formatTimestamp(
                            report.generated_at ??
                            (
                                reportMetadata as Record<string, unknown>
                            ).generated_at as string | undefined,
                        )
                    }
                />

            </div>

        </section>

    );

}