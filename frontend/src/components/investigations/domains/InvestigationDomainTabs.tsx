"use client";

import { useMemo, useState } from "react";

import {
    InvestigationReport,
} from "@/lib/api";

import DomainDetailsPanel from "./DomainDetailsPanel";

interface InvestigationDomainTabsProps {
    report: InvestigationReport;
}

import type {
    InvestigationDecision,
    InvestigationDomain,
} from "@/lib/api";

interface DomainTab {

    id: string;

    title: string;

    domain?: InvestigationDomain | InvestigationDecision | null;

}

export default function InvestigationDomainTabs({

    report,

}: InvestigationDomainTabsProps) {

    const tabs = useMemo<DomainTab[]>(() => [

        {
            id: "execution",
            title: "Execution",
            domain: report.execution,
        },

        {
            id: "evidence",
            title: "Evidence",
            domain: report.evidence,
        },

        {
            id: "verification",
            title: "Verification",
            domain: report.verification,
        },

        {
            id: "governance",
            title: "Governance",
            domain: report.governance,
        },

        {
            id: "broker",
            title: "Broker",
            domain: report.broker,
        },

        {
            id: "synchronization",
            title: "Synchronization",
            domain: report.synchronization,
        },

        {
            id: "review",
            title: "Review",
            domain: report.review,
        },

        {
            id: "behavior",
            title: "Behavior",
            domain: report.behavior,
        },

        {
            id: "allocator",
            title: "Allocator",
            domain: report.allocator,
        },

    ], [report]);

    const [activeTab, setActiveTab] = useState(
        tabs[0]?.id ?? "",
    );

    const active = tabs.find(
        (tab) => tab.id === activeTab,
    );

    const completedDomains = tabs.filter(

        (tab) =>

            tab.id !== "allocator" &&

            tab.domain,

    );

    const averageConfidence =

        completedDomains.length > 0

            ? completedDomains.reduce(

                (sum, tab) =>

                    sum +

                    ((tab.domain as InvestigationDomain)

                        ?.confidence ?? 0),

                0,

            ) /

            completedDomains.length

            : 0;

    return (

        <section className="space-y-6">

            <div>

                <h2 className="text-2xl font-semibold">

                    Investigation Domains

                </h2>

                <p className="mt-1 text-slate-500">

                    Explore each institutional investigation
                    domain independently.

                </p>

                <div className="mt-6 grid gap-4 md:grid-cols-3">

                    <div className="rounded-lg border bg-white p-4">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Domains

                        </div>

                        <div className="mt-2 text-3xl font-bold">

                            {completedDomains.length}

                        </div>

                    </div>

                    <div className="rounded-lg border bg-white p-4">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Average Confidence

                        </div>

                        <div className="mt-2 text-3xl font-bold">

                            {averageConfidence.toFixed(1)}%

                        </div>

                    </div>

                    <div className="rounded-lg border bg-white p-4">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Active Domain

                        </div>

                        <div className="mt-2 text-xl font-semibold">

                            {active?.title}

                        </div>

                    </div>

                </div>

            </div>

            <div className="flex flex-wrap gap-2">

                {tabs.map((tab) => (

                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`rounded-lg border px-4 py-2 text-sm font-medium transition ${
                            activeTab === tab.id
                                ? `
                                    border-blue-700
                                    bg-blue-700
                                    text-white
                                    shadow-md
                                    ring-2
                                    ring-blue-200
                                `
                                : "border-slate-300 bg-white text-slate-700 hover:bg-slate-100 hover:border-slate-400"
                        }`}
                    >

                        <div className="flex items-center gap-2">

                            <span>

                                {tab.title}

                            </span>

                            {tab.id !== "allocator" && tab.domain && (

                                <span
                                    className={`rounded-full px-2 py-0.5 text-[10px] font-semibold transition-all duration-200 ${
                                        activeTab === tab.id
                                            ? "bg-white text-blue-700"
                                            : "bg-slate-100 text-slate-700"
                                    }`}
                                >

                                    {(tab.domain as InvestigationDomain)
                                        .confidence.toFixed(0)}%

                                </span>

                            )}

                        </div>

                    </button>

                ))}

            </div>

            <div className="rounded-lg border bg-slate-50 p-4">

                <div className="text-sm text-slate-600">

                    Select a domain to inspect its findings,
                    confidence, metadata and institutional
                    interpretation independently from the
                    allocator decision.

                </div>

            </div>

            {active && active.id !== "allocator" && (

                <DomainDetailsPanel
                    title={active.title}
                    domain={active.domain as InvestigationDomain}
                />

            )}

            {active && active.id === "allocator" && (

                <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">

                    <h3 className="text-xl font-semibold">
                        Allocator Decision
                    </h3>

                    <p className="mt-3 max-w-3xl leading-7 text-slate-600">

                        The Allocator is the final institutional reasoning
                        engine. It consumes the outputs of every completed
                        investigation domain and produces the canonical
                        institutional decision, confidence score, residual
                        risk assessment and required remediation actions.
                        The full allocator output is presented in the
                        dedicated Allocator section above.

                    </p>

                </div>

            )}

        </section>

    );

}