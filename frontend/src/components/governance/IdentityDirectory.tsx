import type { ReactNode } from "react";

type Props = {

    children: ReactNode;

    snapshot?: {

        authority_distribution?: {

            critical: number;

            high: number;

            medium: number;

            standard: number;

        };

    };

};

export default function IdentityDirectory({

    children,

    snapshot,

}: Props) {

    return (

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <div className="max-w-5xl">

                <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                    Identity Governance

                </div>

                <h2 className="mt-2 text-3xl font-bold">

                    Identity Directory

                </h2>

                <p className="mt-4 text-slate-600">

                    The identity directory is the canonical governance registry
                    for every individual that participates inside the workspace.
                    Every authority assignment, permission boundary and audit
                    relationship originates from this directory.

                </p>

            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-4">

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Owner

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Commercial authority,
                        governance,
                        billing,
                        workspace administration.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Operator

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Operational execution,
                        evidence ingestion,
                        claim management,
                        report generation.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Auditor

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Independent review,
                        evidence inspection,
                        lifecycle validation,
                        compliance oversight.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Member

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Daily operational
                        participant with
                        limited authority.

                    </p>

                </div>

            </div>

            <div className="mt-8 rounded-2xl border border-blue-200 bg-blue-50 p-6">

                <h3 className="font-semibold text-blue-900">

                    Governance Objectives

                </h3>

                <div className="mt-4 grid gap-3 md:grid-cols-2">

                    <div>✓ Least privilege principle</div>

                    <div>✓ Segregation of duties</div>

                    <div>✓ Owner accountability</div>

                    <div>✓ Independent audit capability</div>

                    <div>✓ Traceable authority assignments</div>

                    <div>✓ Lifecycle governance</div>

                </div>

            </div>

            <div className="mt-8">

                <h3 className="text-lg font-semibold">

                    Authority Distribution

                </h3>

                <p className="mt-2 text-sm text-slate-600">

                    Current authority concentration derived from the
                    canonical Governance Snapshot.

                </p>

                <div className="mt-6 grid gap-4 md:grid-cols-4">

                    <div className="rounded-2xl border bg-white p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Critical

                        </div>

                        <div className="mt-3 text-3xl font-bold">

                            {snapshot?.authority_distribution?.critical ?? 0}

                        </div>

                    </div>

                    <div className="rounded-2xl border bg-white p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            High

                        </div>

                        <div className="mt-3 text-3xl font-bold">

                            {snapshot?.authority_distribution?.high ?? 0}

                        </div>

                    </div>

                    <div className="rounded-2xl border bg-white p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Medium

                        </div>

                        <div className="mt-3 text-3xl font-bold">

                            {snapshot?.authority_distribution?.medium ?? 0}

                        </div>

                    </div>

                    <div className="rounded-2xl border bg-white p-5">

                        <div className="text-xs uppercase tracking-wide text-slate-500">

                            Standard

                        </div>

                        <div className="mt-3 text-3xl font-bold">

                            {snapshot?.authority_distribution?.standard ?? 0}

                        </div>

                    </div>

                </div>

            </div>

            <div className="mt-10">

                {children}

            </div>

        </section>

    );

}