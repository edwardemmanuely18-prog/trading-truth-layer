"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "@/components/Navbar";

import {
    getWorkspaceInvestigation,
    InvestigationReport,
} from "@/lib/api";

import RelationshipGraph
from "@/components/investigations/graph/RelationshipGraph";

export default function InvestigationEvidencePage() {

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

                        : "Unable to load investigation evidence.",

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

                    Loading Evidence Explorer...

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

                        Investigation Evidence Explorer

                    </h1>

                    <p className="mt-3 max-w-4xl leading-7 text-slate-600">

                        Explore the canonical evidence graph produced by the
                        Institutional Investigation System. Every investigation
                        entity, relationship and evidence object is reconstructed
                        from the Investigation Context to provide complete
                        forensic traceability.

                    </p>

                </div>

                <RelationshipGraph

                    nodes={
                        report.nodes
                    }

                    relationships={
                        report.relationships
                    }

                />

            </div>

        </div>

    );

}