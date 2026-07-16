"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "@/components/Navbar";

import {
    getWorkspaceInvestigation,
    InvestigationReport,
} from "@/lib/api";

import TimelinePanel
from "@/components/investigations/timeline/TimelinePanel";

import CriticalPathPanel
from "@/components/investigations/critical-path/CriticalPathPanel";

export default function InvestigationTimelinePage() {

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

                const data =
                    await getWorkspaceInvestigation(
                        workspaceId,
                    );

                setReport(
                    data,
                );

            } catch (err) {

                setError(

                    err instanceof Error

                        ? err.message

                        : "Unable to load investigation timeline.",

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

                    Loading Investigation Timeline...

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

                        Timeline Reconstruction

                    </h1>

                    <p className="mt-3 max-w-4xl leading-7 text-slate-600">

                        Canonical forensic replay generated from the Investigation
                        Context. The replay reconstructs execution activity,
                        synchronization, audit events, governance decisions,
                        institutional reviews and allocator reasoning in strict
                        chronological order.

                    </p>

                </div>

                <CriticalPathPanel

                    criticalPath={
                        report.critical_path
                    }

                />

                <TimelinePanel

                    events={
                        report.timeline
                    }

                />

            </div>

        </div>

    );

}