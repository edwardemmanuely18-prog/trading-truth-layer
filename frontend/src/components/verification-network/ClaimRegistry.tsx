"use client";

import { VerificationAnalytics } from "@/lib/api";

interface Props {

    data: VerificationAnalytics;

}

export default function ClaimRegistry({

    data,

}: Props) {

    return (

        <div className="rounded-2xl border bg-white shadow-sm">

            <div className="border-b px-8 py-6">

                <div className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">

                    Institutional Registry

                </div>

                <h2 className="mt-2 text-2xl font-bold">

                    Verified Claim Registry

                </h2>

                <p className="mt-2 text-slate-600">

                    Every verified claim within this workspace together
                    with its governance state, visibility and public
                    verification routes.

                </p>

            </div>

            <div className="max-h-[700px] overflow-auto">

                <table className="min-w-full border-separate border-spacing-0">

                    <thead className="sticky top-0 z-10 bg-slate-100">

                        <tr className="text-left text-xs uppercase tracking-wider text-slate-500">

                            <th className="px-6 py-4">

                                Claim

                            </th>

                            <th className="px-6 py-4">

                                Status

                            </th>

                            <th className="px-6 py-4">

                                Visibility

                            </th>

                            <th className="px-6 py-4">

                                Network

                            </th>

                            <th className="px-6 py-4">

                                Hash

                            </th>

                            <th className="px-6 py-4">

                                Actions

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {data.claims.map((claim) => (

                            <tr

                                key={claim.id}

                                className="border-t hover:bg-slate-50"

                            >

                                <td className="px-6 py-5">

                                    <div className="font-semibold">

                                        {claim.name}

                                    </div>

                                    <div className="mt-1 text-xs text-slate-500">

                                        ID #{claim.id}

                                    </div>

                                </td>

                                <td className="px-6 py-5">

                                    <StatusBadge

                                        value={claim.status}

                                    />

                                </td>

                                <td className="px-6 py-5">

                                    <VisibilityBadge

                                        value={claim.visibility}

                                    />

                                </td>

                                <td className="px-6 py-5">

                                    <NetworkBadge

                                        value={claim.network_state}

                                    />

                                </td>

                                <td className="px-6 py-5">

                                    <div className="max-w-[220px] truncate font-mono text-xs">

                                        {claim.claim_hash ?? "Unavailable"}

                                    </div>

                                </td>

                                <td className="px-6 py-5">

                                    <div className="flex gap-2">

                                        <a

                                            href={`/verify/${claim.claim_hash}`}

                                            className="rounded-lg border px-3 py-2 text-sm hover:bg-slate-100"

                                        >

                                            Verify

                                        </a>

                                        <a

                                            href={`/claim/${claim.id}/public`}

                                            className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white"

                                        >

                                            Public

                                        </a>

                                    </div>

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>

    );

}

function StatusBadge({

    value,

}: {

    value: string;

}) {

    const v = value?.toLowerCase();

    const cls =

        v === "locked"

            ? "bg-green-50 text-green-700 border-green-200"

            : v === "published"

            ? "bg-blue-50 text-blue-700 border-blue-200"

            : v === "verified"

            ? "bg-amber-50 text-amber-700 border-amber-200"

            : "bg-slate-50 text-slate-700 border-slate-200";

    return (

        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${cls}`}>

            {value}

        </span>

    );

}

function VisibilityBadge({

    value,

}: {

    value: string;

}) {

    const cls =

        value?.toLowerCase() === "public"

            ? "bg-green-50 text-green-700 border-green-200"

            : value?.toLowerCase() === "unlisted"

            ? "bg-blue-50 text-blue-700 border-blue-200"

            : "bg-slate-50 text-slate-700 border-slate-200";

    return (

        <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${cls}`}>

            {value}

        </span>

    );

}

function NetworkBadge({

    value,

}: {

    value: string;

}) {

    const active =

        value === "Allocator Ready";

    return (

        <span

            className={`rounded-full border px-3 py-1 text-xs font-semibold ${

                active

                    ? "border-green-200 bg-green-50 text-green-700"

                    : "border-slate-200 bg-slate-50 text-slate-700"

            }`}

        >

            {value}

        </span>

    );

}