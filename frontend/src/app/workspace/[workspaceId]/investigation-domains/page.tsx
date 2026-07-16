"use client";

import { useEffect, useState } from "react";

import {
    getWorkspaceInvestigation,
    InvestigationReport,
} from "@/lib/api";

import { useParams } from "next/navigation";

import Navbar from "@/components/Navbar";

import InvestigationStatusBanner
from "@/components/investigations/header/InvestigationStatusBanner";

import InvestigationMetadataPanel
from "@/components/investigations/header/InvestigationMetadataPanel";

import DomainGrid
from "@/components/investigations/domains/DomainGrid";

import InvestigationDomainTabs
from "@/components/investigations/domains/InvestigationDomainTabs";

import AllocatorPanel
from "@/components/investigations/domains/AllocatorPanel";

import DomainConfidenceMatrix
from "@/components/investigations/domains/DomainConfidenceMatrix";

import DomainDependencyGraph
from "@/components/investigations/domains/DomainDependencyGraph";

import CrossDomainConsensus
from "@/components/investigations/domains/CrossDomainConsensus";

import DomainCoverageMatrix
from "@/components/investigations/domains/DomainCoverageMatrix";

export default function InvestigationDomainsPage() {

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

                    Loading Investigation Domains...

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

                        Institutional Investigation Domains

                    </h1>

                    <p className="mt-3 max-w-5xl leading-7 text-slate-600">

                        Every Institutional Investigation is decomposed into
                        specialized reasoning engines. Each engine evaluates
                        one dimension of institutional trust before contributing
                        to the final allocator decision.

                    </p>

                </div>

                <InvestigationStatusBanner
                    report={report}
                />

                <InvestigationMetadataPanel
                    report={report}
                />

                <DomainGrid
                    report={report}
                />

                <InvestigationDomainTabs
                    report={report}
                />

                <AllocatorPanel
                    allocator={report.allocator}
                />

                <DomainConfidenceMatrix
                    report={report}
                />

                <DomainDependencyGraph />

                <CrossDomainConsensus
                    report={report}
                />

                <DomainCoverageMatrix
                    report={report}
                />

            </div>

        </div>

    );

}