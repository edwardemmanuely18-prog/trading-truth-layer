"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "@/components/Navbar";

import {
    getInvestigationOverview,
    getWorkspaceInvestigation,
    InvestigationOverview,
    InvestigationReport,
} from "@/lib/api";

import InvestigationStatusBanner
from "@/components/investigations/header/InvestigationStatusBanner";

import InvestigationMetadataPanel
from "@/components/investigations/header/InvestigationMetadataPanel";

import InvestigationProgressPanel
from "@/components/investigations/header/InvestigationProgressPanel";

import InvestigationReadinessPanel
from "@/components/investigations/header/InvestigationReadinessPanel";

import InvestigationCoveragePanel
from "@/components/investigations/header/InvestigationCoveragePanel";

import InvestigationScoreCard
from "@/components/investigations/cards/InvestigationScoreCard";

import InvestigationHealthCard
from "@/components/investigations/cards/InvestigationHealthCard";

import FindingCountCard
from "@/components/investigations/cards/FindingCountCard";

import RecommendationCountCard
from "@/components/investigations/cards/RecommendationCountCard";

import ExecutiveSummary
from "@/components/investigations/summary/ExecutiveSummary";

import AllocatorPanel
from "@/components/investigations/domains/AllocatorPanel";

export default function InvestigationOverviewPage() {

    const params = useParams();

    const workspaceId = Number(
        params.workspaceId,
    );

    const [

        overview,

        setOverview,

    ] = useState<InvestigationOverview | null>(
        null,
    );

    const [

        report,

        setReport,

    ] = useState<InvestigationReport | null>(
        null,
    );

    const [

        loading,

        setLoading,

    ] = useState(true);

    const [

        error,

        setError,

    ] = useState<string | null>(
        null,
    );

    useEffect(() => {

        async function load() {

            try {

                setLoading(true);

                const [

                    overviewData,

                    reportData,

                ] = await Promise.all([

                    getInvestigationOverview(
                        workspaceId,
                    ),

                    getWorkspaceInvestigation(
                        workspaceId,
                    ),

                ]);

                setOverview(
                    overviewData,
                );

                setReport(
                    reportData,
                );

            } catch (err) {

                setError(

                    err instanceof Error
                        ? err.message
                        : "Failed to load investigation.",

                );

            } finally {

                setLoading(false);

            }

        }

        void load();

    }, [

        workspaceId,

    ]);

    if (loading) {

        return (

            <div className="min-h-screen bg-slate-50">

                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">

                    Loading Investigation Overview...

                </div>

            </div>

        );

    }

    if (error || !report) {

        return (

            <div className="min-h-screen bg-slate-50">

                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10 text-red-600">

                    {error}

                </div>

            </div>

        );

    }

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar />

            <div className="mx-auto max-w-7xl px-6 py-10 space-y-8">

                <div>

                    <h1 className="text-4xl font-bold">

                        Investigation Overview

                    </h1>

                    <p className="mt-3 max-w-4xl leading-7 text-slate-600">

                        Executive overview of the institutional investigation,
                        allocator decision, readiness, coverage, confidence,
                        and investigation health.

                    </p>

                </div>

                <InvestigationStatusBanner
                    report={report}
                />

                <InvestigationMetadataPanel
                    report={report}
                />

                <InvestigationProgressPanel
                    report={report}
                />

                <InvestigationReadinessPanel
                    report={report}
                />

                <InvestigationCoveragePanel
                    report={report}
                />

                <div className="grid gap-6 lg:grid-cols-4">

                    <InvestigationScoreCard
                        score={report.summary.investigation_confidence}
                    />

                    <InvestigationHealthCard
                        health={report.summary.overall_risk}
                    />

                    <FindingCountCard
                        findings={report.summary.total_findings}
                    />

                    <RecommendationCountCard
                        recommendations={report.recommendations.length}
                    />

                </div>

                <ExecutiveSummary
                    summary={report.summary}
                />

                <AllocatorPanel
                    allocator={report.allocator}
                />

            </div>

        </div>

    );

}