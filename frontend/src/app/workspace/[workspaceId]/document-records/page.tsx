"use client";

import {
    useEffect,
    useState,
} from "react";

import { RefreshCw } from "lucide-react";

import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
    api,
    type V2EvidenceRegistrySummary,
} from "../../../../lib/api";

type DocumentTab =
    | "STATEMENTS"
    | "TRADE_REPORTS"
    | "CONFIRMATIONS"
    | "CONTRACTS"
    | "IMAGES"
    | "OCR";

const TABS: Array<{
    key: DocumentTab;
    label: string;
}> = [
    {
        key: "STATEMENTS",
        label: "Statements",
    },
    {
        key: "TRADE_REPORTS",
        label: "Trade Reports",
    },
    {
        key: "CONFIRMATIONS",
        label: "Confirmations",
    },
    {
        key: "CONTRACTS",
        label: "Contracts",
    },
    {
        key: "IMAGES",
        label: "Images",
    },
    {
        key: "OCR",
        label: "OCR",
    },
];

export default function DocumentRecordsPage() {
    const params = useParams<{
        workspaceId: string;
    }>();

    const workspaceId = Number(
        params.workspaceId
    );

    const [
        activeTab,
        setActiveTab,
    ] = useState<DocumentTab>(
        "STATEMENTS"
    );

    const [
        summary,
        setSummary,
    ] = useState<V2EvidenceRegistrySummary | null>(
        null
    );

    const [
        loading,
        setLoading,
    ] = useState(true);

    const [
        error,
        setError,
    ] = useState<string | null>(
        null
    );

    async function loadSummary() {
        try {
            setLoading(true);
            setError(null);

            const response =
                await api.getV2EvidenceRegistrySummary(
                    workspaceId
                );

            setSummary(response);
        } catch (err) {
            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Unable to load document registry state."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!Number.isFinite(workspaceId)) {
            setError(
                "Invalid workspace ID."
            );

            setLoading(false);
            return;
        }

        void loadSummary();
    }, [workspaceId]);

    return (
        <div className="min-h-screen bg-slate-50">
            <Navbar
                workspaceId={workspaceId}
            />

            <main className="mx-auto max-w-7xl px-6 py-10">

                <div className="mb-8">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Evidence Registry
                    </div>

                    <div className="mt-2 flex items-center justify-between gap-6">
                        <div>
                            <h1 className="text-4xl font-bold text-slate-950">
                                Document Records
                            </h1>

                            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                                Canonical document evidence including
                                statements, reports, confirmations,
                                contracts, images, and OCR artifacts.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                void loadSummary()
                            }
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <RefreshCw
                                className={`h-4 w-4 ${
                                    loading
                                        ? "animate-spin"
                                        : ""
                                }`}
                            />

                            Refresh
                        </button>
                    </div>
                </div>

                {error && (
                    <section className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
                        <div className="text-sm font-semibold text-red-800">
                            Document Registry unavailable
                        </div>

                        <div className="mt-1 text-sm text-red-700">
                            {error}
                        </div>
                    </section>
                )}

                <section className="overflow-hidden rounded-2xl border border-slate-300 bg-white shadow-sm">

                    <div className="border-b border-slate-200 px-6 pt-5">
                        <div className="flex flex-wrap gap-2">
                            {TABS.map(
                                (tab) => {
                                    const active =
                                        activeTab ===
                                        tab.key;

                                    return (
                                        <button
                                            key={
                                                tab.key
                                            }
                                            type="button"
                                            onClick={() =>
                                                setActiveTab(
                                                    tab.key
                                                )
                                            }
                                            className={[
                                                "rounded-lg px-4 py-2 text-sm font-semibold transition",
                                                active
                                                    ? "bg-slate-950 text-white"
                                                    : "border border-slate-200 text-slate-600 hover:bg-slate-50",
                                            ].join(
                                                " "
                                            )}
                                        >
                                            {
                                                tab.label
                                            }

                                            <span
                                                className={[
                                                    "ml-2 rounded-full px-2 py-0.5 text-[10px]",
                                                    active
                                                        ? "bg-white/15 text-white"
                                                        : "bg-slate-100 text-slate-500",
                                                ].join(
                                                    " "
                                                )}
                                            >
                                                0
                                            </span>
                                        </button>
                                    );
                                }
                            )}
                        </div>
                    </div>

                    <div className="px-6 py-8">

                        <div className="mb-6">
                            <div className="text-sm font-semibold text-slate-950">
                                {
                                    TABS.find(
                                        (tab) =>
                                            tab.key ===
                                            activeTab
                                    )?.label
                                }
                            </div>

                            <div className="mt-1 text-xs text-slate-500">
                                0 records
                            </div>
                        </div>

                        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">

                            <div className="text-sm font-semibold text-slate-900">
                                Document evidence is not yet
                                represented in the V2 registry taxonomy.
                            </div>

                            <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-500">
                                The current canonical evidence contract
                                exposes trading, account, financial,
                                market, history, and custom evidence.
                                Dedicated document classifications such
                                as statements, confirmations, contracts,
                                images, and OCR are not yet defined.
                            </p>

                            <div className="mx-auto mt-5 max-w-xl rounded-lg border border-slate-200 bg-white px-5 py-4 text-left">
                                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                    Current registry evidence types
                                </div>

                                <div className="mt-3 flex flex-wrap gap-2">
                                    {summary
                                        ? Object.keys(
                                            summary.evidence_type_counts
                                        ).sort().map(
                                            (type) => (
                                                <span
                                                    key={
                                                        type
                                                    }
                                                    className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600"
                                                >
                                                    {
                                                        type
                                                    }
                                                </span>
                                            )
                                        )
                                        : (
                                            <span className="text-xs text-slate-400">
                                                Loading...
                                            </span>
                                        )}
                                </div>
                            </div>

                        </div>
                    </div>

                </section>

                <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="text-sm font-semibold text-slate-900">
                        Document Evidence Pipeline
                    </div>

                    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                        This surface is reserved for the future
                        document-ingestion and document-evidence layer.
                        Once that layer emits canonical document evidence,
                        these categories can be connected to the same
                        server-side V2 pagination and Evidence Detail
                        contract used by Trading Records and Account Records.
                    </p>
                </section>

            </main>
        </div>
    );
}