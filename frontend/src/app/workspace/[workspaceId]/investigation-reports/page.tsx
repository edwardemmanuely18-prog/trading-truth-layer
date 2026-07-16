"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "@/components/Navbar";

import InvestigationReportCatalog
from "@/components/investigations/reports/InvestigationReportCatalog";

import {
    InvestigationReport,
    getWorkspaceInvestigation,
} from "@/lib/api";

export default function InvestigationReportsPage() {

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

                const reportData =
                    await getWorkspaceInvestigation(
                        workspaceId,
                    );

                setReport(
                    reportData,
                );

            } catch (err) {

                setError(

                    err instanceof Error
                        ? err.message
                        : "Failed to load investigation reports.",

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

                    Loading Investigation Reports...

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

            <div className="mx-auto max-w-7xl px-6 py-10">

                <InvestigationReportCatalog
                    workspaceId={workspaceId}
                    report={report}
                />

            </div>

        </div>

    );

}