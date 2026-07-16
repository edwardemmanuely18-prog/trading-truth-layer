"use client";

import {
    InvestigationReport,
} from "@/lib/api";

interface Props {
    report: InvestigationReport;
}

export default function DomainReportCard({
    report,
}: Props) {

    const domains = [

        {
            name: "Execution",
            confidence: report.execution?.confidence,
        },

        {
            name: "Evidence",
            confidence: report.evidence?.confidence,
        },

        {
            name: "Verification",
            confidence: report.verification?.confidence,
        },

        {
            name: "Governance",
            confidence: report.governance?.confidence,
        },

        {
            name: "Broker",
            confidence: report.broker?.confidence,
        },

        {
            name: "Synchronization",
            confidence: report.synchronization?.confidence,
        },

        {
            name: "Review",
            confidence: report.review?.confidence,
        },

        {
            name: "Behaviour",
            confidence: report.behavior?.confidence,
        },

    ];

    const completed = domains.filter(
        d => d.confidence !== undefined,
    ).length;

    return (

        <section className="rounded-xl border border-slate-200 bg-white">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Investigation Domains

                </div>

                <h3 className="mt-2 text-xl font-semibold text-slate-900">

                    Domain Investigation Report

                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">

                    Documents the analytical output produced by each
                    Institutional Investigation System engine. Each domain
                    receives its own chapter with findings, confidence,
                    supporting evidence and institutional conclusions.

                </p>

            </div>

            <div className="space-y-6 p-6">

                <div className="grid gap-4 md:grid-cols-2">

                    <Metric
                        label="Investigation Domains"
                        value={`${completed}/8`}
                    />

                    <Metric
                        label="Overall Confidence"
                        value={`${report.summary.investigation_confidence.toFixed(1)}%`}
                    />

                </div>

                <div className="rounded-lg bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Report Chapters

                    </div>

                    <div className="mt-4 space-y-3">

                        {domains.map(domain => (

                            <div
                                key={domain.name}
                                className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3"
                            >

                                <div className="font-medium text-slate-800">

                                    {domain.name}

                                </div>

                                <div className="text-sm text-slate-600">

                                    {domain.confidence !== undefined
                                        ? `${domain.confidence.toFixed(1)}%`
                                        : "Pending"}

                                </div>

                            </div>

                        ))}

                    </div>

                </div>

                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Included Analysis

                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-2">

                        <Section text="Execution Investigation" />

                        <Section text="Evidence Investigation" />

                        <Section text="Verification Investigation" />

                        <Section text="Governance Investigation" />

                        <Section text="Broker Investigation" />

                        <Section text="Synchronization Investigation" />

                        <Section text="Review Investigation" />

                        <Section text="Behaviour Investigation" />

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

                    Generate Domain Investigation Report

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