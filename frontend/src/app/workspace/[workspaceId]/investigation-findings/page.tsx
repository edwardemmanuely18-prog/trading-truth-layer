"use client";

import { useEffect, useState } from "react";

import {
    InvestigationReport,
    getWorkspaceInvestigation,
} from "@/lib/api";

import { useParams } from "next/navigation";

import Navbar
from "@/components/Navbar";

import InvestigationStatusBanner
from "@/components/investigations/header/InvestigationStatusBanner";

import InvestigationMetadataPanel
from "@/components/investigations/header/InvestigationMetadataPanel";

import FindingsTable
from "@/components/investigations/findings/FindingsTable";

import CriticalFindingsPanel
from "@/components/investigations/findings/CriticalFindingsPanel";

import FindingSeverityMatrix
from "@/components/investigations/findings/FindingSeverityMatrix";

import FindingImpactAnalysis
from "@/components/investigations/findings/FindingImpactAnalysis";

import FindingCorrelationMatrix
from "@/components/investigations/findings/FindingCorrelationMatrix";

import FindingRemediationRoadmap
from "@/components/investigations/findings/FindingRemediationRoadmap";

import RecommendationCountCard
from "@/components/investigations/cards/RecommendationCountCard";

import FindingCountCard
from "@/components/investigations/cards/FindingCountCard";


export default function InvestigationFindingsPage() {

    const params = useParams();

    const workspaceId = Number(
        params.workspaceId,
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

    useEffect(() => {

        async function load() {

            const data =
                await getWorkspaceInvestigation(
                    workspaceId,
                );

            setReport(
                data,
            );

            setLoading(
                false,
            );

        }

        void load();

    }, [

        workspaceId,

    ]);

    if (

        loading ||

        !report

    ) {

        return (

            <div className="min-h-screen bg-slate-50">

                <Navbar />

                <div className="mx-auto max-w-7xl px-6 py-10">

                    Loading Investigation Findings...

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

                        Institutional Investigation Findings

                    </h1>

                    <p className="mt-3 max-w-5xl leading-7 text-slate-600">

                        Findings represent the institutional conclusions
                        produced by the Investigation System after
                        evaluating execution, evidence, governance,
                        synchronization, verification and behavioral
                        intelligence.

                    </p>

                </div>

                <InvestigationStatusBanner
                    report={report}
                />

                <InvestigationMetadataPanel
                    report={report}
                />

                <div className="grid gap-6 lg:grid-cols-2">

                    <FindingCountCard
                        findings={report.findings.length}
                    />

                    <RecommendationCountCard
                        recommendations={
                            report.recommendations.length
                        }
                    />

                </div>

                <FindingsTable
                    findings={report.findings}
                />

                <CriticalFindingsPanel
                    findings={report.findings}
                />

                <FindingSeverityMatrix
                    findings={report.findings}
                />

                <FindingImpactAnalysis
                    summary={report.summary}
                />

                <FindingCorrelationMatrix
                    findings={report.findings}
                />

                <FindingRemediationRoadmap
                    findings={report.findings}
                />

            </div>

        </div>

    );

}