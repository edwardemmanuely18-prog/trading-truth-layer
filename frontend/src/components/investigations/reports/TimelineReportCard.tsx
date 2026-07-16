"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface Props {
    report: InvestigationReport;
}

export default function TimelineReportCard({
    report,
}: Props) {

    const timelineCount =
        report.timeline.length;

    return (

        <section className="rounded-xl border border-slate-200 bg-white">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Timeline Reconstruction

                </div>

                <h3 className="mt-2 text-xl font-semibold text-slate-900">

                    Investigation Timeline Report

                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">

                    Produces a chronological reconstruction of the
                    investigation from the earliest institutional event
                    through the final allocator decision. This report is
                    intended for forensic replay, regulatory review and
                    post-incident analysis.

                </p>

            </div>

            <div className="space-y-6 p-6">

                <div className="grid gap-4 md:grid-cols-2">

                    <Metric
                        label="Timeline Events"
                        value={String(
                            timelineCount,
                        )}
                    />

                    <Metric
                        label="Coverage"
                        value={
                            timelineCount > 0
                                ? "Chronological Reconstruction Available"
                                : "No Timeline Available"
                        }
                    />

                    <Metric
                        label="Investigation Status"
                        value={report.status}
                    />

                    <Metric
                        label="Evidence Correlation"
                        value={
                            report.relationships.length > 0
                                ? "Linked"
                                : "Unavailable"
                        }
                    />

                </div>

                <div className="rounded-lg bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Included Sections

                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2">

                        <Item text="Investigation Start" />
                        <Item text="Execution Replay" />
                        <Item text="Synchronization Events" />
                        <Item text="Audit History" />
                        <Item text="Review Timeline" />
                        <Item text="Evidence Discovery" />
                        <Item text="Critical Investigation Events" />
                        <Item text="Allocator Decision" />

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
                    Generate Timeline Report
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

function Item({

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