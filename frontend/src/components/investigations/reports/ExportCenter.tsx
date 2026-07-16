"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface Props {
    report: InvestigationReport;
}

export default function ExportCenter({
    report,
}: Props) {

    const exports = [

        {
            title: "Canonical Investigation Report",
            format: "JSON",
            description:
                "Canonical IIS investigation snapshot for downstream systems.",
        },

        {
            title: "Investigation Timeline",
            format: "CSV",
            description:
                "Chronological investigation events.",
        },

        {
            title: "Investigation Findings",
            format: "CSV",
            description:
                "Complete institutional finding register.",
        },

        {
            title: "Recommendations",
            format: "CSV",
            description:
                "Institutional remediation recommendations.",
        },

    ];

    return (

        <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Export Center

                </div>

                <h2 className="mt-2 text-2xl font-semibold text-slate-900">

                    Structured Investigation Exports

                </h2>

                <p className="mt-2 max-w-4xl text-sm leading-7 text-slate-600">

                    Export structured datasets generated from the canonical
                    Institutional Investigation System. These exports are
                    intended for downstream analytics, automation,
                    integration and archival.

                </p>

            </div>

            <div className="grid gap-5 p-6 lg:grid-cols-2">

                {exports.map(item => (

                    <div
                        key={`${item.title}-${item.format}`}
                        className="rounded-xl border border-slate-200 bg-slate-50 p-5"
                    >

                        <div className="flex items-center justify-between">

                            <h3 className="text-lg font-semibold text-slate-900">

                                {item.title}

                            </h3>

                            <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">

                                {item.format}

                            </span>

                        </div>

                        <p className="mt-3 text-sm leading-6 text-slate-600">

                            {item.description}

                        </p>

                        <div className="mt-5 flex gap-3">

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

                                Generate

                            </button>

                            <button
                                type="button"
                                className="
                                    rounded-lg
                                    border
                                    border-slate-300
                                    bg-white
                                    px-4
                                    py-2
                                    text-sm
                                    font-semibold
                                    text-slate-700
                                    transition
                                    hover:bg-slate-100
                                "
                            >

                                Queue

                            </button>

                        </div>

                    </div>

                ))}

            </div>

            <div className="border-t border-slate-200 bg-slate-50 px-6 py-5">

                <div className="grid gap-4 md:grid-cols-4">

                    <Metric
                        label="Structured Exports"
                        value="4"
                    />

                    <Metric
                        label="Export Formats"
                        value="JSON + CSV"
                    />

                    <Metric
                        label="Investigation Findings"
                        value={String(report.findings.length)}
                    />

                    <Metric
                        label="Timeline Events"
                        value={String(report.timeline.length)}
                    />

                </div>

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

        <div className="rounded-lg border border-slate-200 bg-white p-4">

            <div className="text-xs uppercase tracking-wide text-slate-500">

                {label}

            </div>

            <div className="mt-2 text-lg font-semibold text-slate-900">

                {value}

            </div>

        </div>

    );

}