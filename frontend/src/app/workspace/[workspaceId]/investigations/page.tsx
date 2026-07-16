"use client";

import { useEffect, useState } from "react";

import {
    getInvestigationOverview,
    getWorkspaceInvestigation,
    InvestigationOverview,
    InvestigationReport,
} from "@/lib/api";

import Navbar from "@/components/Navbar";

import ExecutiveSummary
from "@/components/investigations/summary/ExecutiveSummary";

import DomainGrid
from "@/components/investigations/domains/DomainGrid";

import AllocatorPanel
from "@/components/investigations/domains/AllocatorPanel";

import InvestigationDomainTabs
from "@/components/investigations/domains/InvestigationDomainTabs";

import InvestigationScoreCard
from "@/components/investigations/cards/InvestigationScoreCard";

import InvestigationHealthCard
from "@/components/investigations/cards/InvestigationHealthCard";

import FindingCountCard
from "@/components/investigations/cards/FindingCountCard";

import RecommendationCountCard
from "@/components/investigations/cards/RecommendationCountCard";

import CriticalPathPanel
from "@/components/investigations/critical-path/CriticalPathPanel";

import TimelinePanel
from "@/components/investigations/timeline/TimelinePanel";

import FindingsTable
from "@/components/investigations/findings/FindingsTable";

import RecommendationsTable
from "@/components/investigations/recommendations/RecommendationsTable";

import RelationshipGraph
from "@/components/investigations/graph/RelationshipGraph";

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

import { useParams } from "next/navigation";

export default function InvestigationPage() {

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

                    Loading Institutional Investigation...

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

                        Institutional Investigation System

                    </h1>

                    <p className="mt-3 max-w-4xl leading-7 text-slate-600">

                        The Institutional Investigation System (IIS) performs
                        independent forensic analysis across execution,
                        evidence, governance, synchronization, broker activity,
                        review history and institutional verification before
                        producing an allocator decision. Every investigation is
                        reconstructed from the canonical Investigation Context,
                        allowing institutional users to understand not only
                        what was detected, but why the system reached its
                        conclusion.

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

                <DomainGrid
                    report={report}
                />

                <AllocatorPanel
                    allocator={report.allocator}
                />

                <InvestigationDomainTabs
                    report={report}
                />

                {report.critical_path && (

                    <CriticalPathPanel
                        criticalPath={report.critical_path}
                    />

                )}

                <TimelinePanel
                    events={report.timeline}
                />

                <RelationshipGraph

                    nodes={report.nodes}

                    relationships={report.relationships}

                />

                <FindingsTable

                    findings={report.findings}

                />

                <RecommendationsTable

                    recommendations={report.recommendations}

                />

            </div>

        </div>
        

    );

}