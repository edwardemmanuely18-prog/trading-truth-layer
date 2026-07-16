"use client";

import {
    useEffect,
    useState,
} from "react";

import {

    InvestigationReport,

    downloadExecutiveReport,

} from "@/lib/api";

interface Props {

    workspaceId: number;

    report: InvestigationReport;

}

export default function ExecutiveInvestigationCard({

    workspaceId,

    report,

}: Props) {

    const [

        downloading,

        setDownloading,

    ] = useState(false);

    const [

        message,

        setMessage,

    ] = useState<string | null>(null);

    async function handleDownload() {

        try {

            setMessage(null);

            setDownloading(true);

            setMessage(
                "Generating Executive Report..."
            );

            await downloadExecutiveReport(
                workspaceId,
            );

            setMessage(
                "Executive Report downloaded successfully."
            );

        } catch (error) {

            console.error(error);

            setMessage(
                "Failed to generate Executive Report."
            );

        } finally {

            setDownloading(false);

        }

    }

    useEffect(() => {

        if (!message) {
            return;
        }

        const timer = window.setTimeout(() => {

            setMessage(null);

        }, 3000);

        return () => window.clearTimeout(timer);

    }, [message]);

    return (

        <section className="rounded-xl border border-slate-200 bg-white">

            <div className="border-b border-slate-200 px-6 py-5">

                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                    Executive Report

                </div>

                <h3 className="mt-2 text-xl font-semibold text-slate-900">

                    Executive Investigation Report

                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-600">

                    High-level institutional briefing intended for CIOs,
                    portfolio managers and investment committees. This
                    report summarizes the investigation outcome without
                    exposing the complete forensic reconstruction.

                </p>

            </div>

            <div className="space-y-5 p-6">

                <div className="grid gap-4 md:grid-cols-2">

                    <Metric
                        label="Decision"
                        value={
                            report.allocator?.decision ??
                            "Unavailable"
                        }
                    />

                    <Metric
                        label="Confidence"
                        value={`${report.summary.investigation_confidence.toFixed(2)}%`}
                    />

                    <Metric
                        label="Residual Risk"
                        value={
                            report.allocator?.residual_risk ??
                            "Unknown"
                        }
                    />

                    <Metric
                        label="Critical Findings"
                        value={
                            String(
                                report.summary.critical_findings
                            )
                        }
                    />

                </div>

                <div className="rounded-lg bg-slate-50 p-4">

                    <div className="text-xs uppercase tracking-wide text-slate-500">

                        Executive Summary

                    </div>

                    <p className="mt-2 text-sm leading-7 text-slate-700">

                        {report.summary.executive_summary}

                    </p>

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
                        ? "Generating..."
                        : "Download Executive Report"}

                </button>

                {message && (

                    <div
                        className={`
                            mt-3
                            rounded-lg
                            border
                            px-4
                            py-3
                            text-sm
                            ${
                                message.startsWith("Failed")
                                    ? "border-red-200 bg-red-50 text-red-700"
                                    : "border-emerald-200 bg-emerald-50 text-emerald-700"
                            }
                        `}
                    >

                        {message}

                    </div>

                )}

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