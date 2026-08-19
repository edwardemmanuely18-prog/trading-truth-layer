"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
    api,
    type V2EvidencePackage,
} from "../../../../lib/api";



function formatDate(
    value: string | null,
) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

function displayValue(
    value: unknown,
) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    return String(value);
}

export default function EvidencePackagesPage() {
    const params = useParams<{
        workspaceId: string;
    }>();

    const workspaceId = Number(
        params.workspaceId,
    );

    const [
        packages,
        setPackages,
    ] = useState<V2EvidencePackage[]>(
        [],
    );

    const [
        page,
        setPage,
    ] = useState(1);

    const [
        pagination,
        setPagination,
    ] = useState<{
        page: number;
        page_size: number;
        total_packages: number;
        total_pages: number;
        has_previous: boolean;
        has_next: boolean;
    } | null>(null);

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

    async function loadPackages(
        requestedPage = page,
    ) {
        try {
            setLoading(true);
            setError(null);

            const response =
                await api.getV2EvidencePackagesPage(
                    workspaceId,
                    requestedPage,
                    25,
                );

            setPackages(
                response.packages,
            );

            setPagination(
                response.pagination,
            );
        } catch (err) {
            console.error(err);

            setError(
                err instanceof Error
                    ? err.message
                    : "Unable to load evidence packages.",
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (!Number.isFinite(workspaceId)) {
            setError(
                "Invalid workspace ID.",
            );

            setLoading(false);
            return;
        }

        void loadPackages(1);
    }, [workspaceId]);

    return (
        <div className="min-h-screen bg-slate-50">
            <Navbar
                workspaceId={
                    workspaceId
                }
            />

            <main className="mx-auto max-w-7xl px-6 py-10">

                <div className="mb-8">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                        Evidence Registry
                    </div>

                    <div className="mt-2 flex items-center justify-between gap-6">
                        <div>
                            <h1 className="text-4xl font-bold text-slate-950">
                                Synchronization Packages
                            </h1>

                            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
                                Institutional synchronization-backed evidence
                                packages grouped by canonical synchronization
                                batch for controlled inspection, audit, and
                                downstream verification workflows.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={() =>
                                void loadPackages(
                                    page,
                                )
                            }
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm disabled:opacity-50"
                        >
                            <RefreshCw
                                className={
                                    loading
                                        ? "h-4 w-4 animate-spin"
                                        : "h-4 w-4"
                                }
                            />

                            Refresh
                        </button>
                    </div>
                </div>

                {error && (
                    <section className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-5 py-4">
                        <div className="text-sm font-semibold text-red-800">
                            Evidence Package Registry unavailable
                        </div>

                        <div className="mt-1 text-sm text-red-700">
                            {error}
                        </div>
                    </section>
                )}

                <section className="overflow-hidden rounded-2xl border border-slate-300 bg-white shadow-sm">

                    <div className="px-6 py-6">

                        <div className="mb-5">
                            <div className="text-sm font-semibold text-slate-950">
                                Synchronization Packages
                            </div>

                            <div className="mt-1 text-xs text-slate-500">
                                {pagination?.total_packages ??
                                    0}{" "}
                                package
                                {pagination?.total_packages === 1
                                    ? ""
                                    : "s"}
                            </div>
                        </div>

                        <div className="mb-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
                            Each package below represents a canonical
                            synchronization batch containing evidence
                            registered during the same acquisition cycle.
                            Package governance classifications such as
                            verification, investigation, or reporting are
                            not yet assigned by the V2 registry.
                        </div>

                        {loading ? (
                            <div className="py-16 text-center text-sm text-slate-500">
                                Loading evidence packages...
                            </div>
                        ) : packages.length === 0 ? (
                            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-16 text-center">
                                <div className="text-sm font-semibold text-slate-900">
                                    No synchronization packages found
                                </div>

                                <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">
                                    No synchronization batch with registered
                                    canonical evidence has been found for this
                                    workspace.
                                </p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto rounded-xl border border-slate-200">
                                <table className="min-w-full">
                                    <thead className="bg-slate-50">
                                        <tr className="border-b border-slate-200">
                                            <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Synchronization Batch
                                            </th>

                                            <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Provider
                                            </th>

                                            <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Account
                                            </th>

                                            <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Evidence
                                            </th>

                                            <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Session
                                            </th>

                                            <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                                                Latest Registered
                                            </th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {packages.map(
                                            (
                                                item,
                                            ) => (
                                                <tr
                                                    key={
                                                        item.synchronization_batch
                                                    }
                                                    className="border-b border-slate-100 last:border-b-0 hover:bg-slate-50"
                                                >
                                                    <td className="px-5 py-4">
                                                        <div className="font-mono text-xs font-semibold text-slate-900">
                                                            {
                                                                item.synchronization_batch
                                                            }
                                                        </div>
                                                    </td>

                                                    <td className="px-5 py-4">
                                                        <div className="text-sm font-semibold text-slate-900">
                                                            {displayValue(
                                                                item.provider_name,
                                                            )}
                                                        </div>

                                                        <div className="mt-1 text-xs text-slate-500">
                                                            {displayValue(
                                                                item.provider_platform,
                                                            )}
                                                        </div>
                                                    </td>

                                                    <td className="px-5 py-4 font-mono text-xs text-slate-700">
                                                        {displayValue(
                                                            item.broker_account_id,
                                                        )}
                                                    </td>

                                                    <td className="px-5 py-4">
                                                        <span className="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-700">
                                                            {
                                                                item.record_count
                                                            }{" "}
                                                            records
                                                        </span>
                                                    </td>

                                                    <td className="px-5 py-4 font-mono text-[11px] text-slate-600">
                                                        {displayValue(
                                                            item.synchronization_session,
                                                        )}
                                                    </td>

                                                    <td className="px-5 py-4 whitespace-nowrap text-xs text-slate-600">
                                                        {formatDate(
                                                            item.last_registered_at,
                                                        )}
                                                    </td>
                                                </tr>
                                            ),
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        )}

                    </div>
                </section>

                {pagination &&
                    pagination.total_pages >
                        0 && (
                        <div className="mt-5 flex items-center justify-between border-t border-slate-200 pt-4">
                            <div className="text-xs text-slate-500">
                                Page{" "}
                                {pagination.page}{" "}
                                of{" "}
                                {
                                    pagination.total_pages
                                }{" "}
                                ·{" "}
                                {
                                    pagination.total_packages
                                }{" "}
                                packages
                            </div>

                            <div className="flex gap-2">
                                <button
                                    type="button"
                                    disabled={
                                        loading ||
                                        !pagination.has_previous
                                    }
                                    onClick={() => {
                                        const nextPage =
                                            pagination.page -
                                            1;

                                        setPage(
                                            nextPage,
                                        );

                                        void loadPackages(
                                            nextPage,
                                        );
                                    }}
                                    className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-40"
                                >
                                    Previous
                                </button>

                                <button
                                    type="button"
                                    disabled={
                                        loading ||
                                        !pagination.has_next
                                    }
                                    onClick={() => {
                                        const nextPage =
                                            pagination.page +
                                            1;

                                        setPage(
                                            nextPage,
                                        );

                                        void loadPackages(
                                            nextPage,
                                        );
                                    }}
                                    className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-40"
                                >
                                    Next
                                </button>
                            </div>
                        </div>
                    )}

            </main>
        </div>
    );
}