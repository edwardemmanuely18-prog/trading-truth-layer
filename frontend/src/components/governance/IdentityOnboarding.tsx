import type { ReactNode } from "react";

type Props = {

    children: ReactNode;

};

export default function IdentityOnboarding({

    children,

}: Props) {

    return (

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <div className="max-w-4xl">

                <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                    Identity Governance

                </div>

                <h2 className="mt-2 text-3xl font-bold">

                    Identity Onboarding

                </h2>

                <p className="mt-4 text-slate-600">

                    Every identity enters the workspace through a governed
                    onboarding workflow. Invitations establish authority,
                    accountability, audit ownership, lifecycle controls and
                    long-term governance posture.

                </p>

            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-2">

                <div className="rounded-2xl border bg-slate-50 p-6">

                    <h3 className="text-lg font-semibold">

                        Governance Principles

                    </h3>

                    <div className="mt-5 space-y-3 text-sm">

                        <div>✓ Identity must be attributable</div>

                        <div>✓ Authority must be explicitly granted</div>

                        <div>✓ Every invitation is permanently audited</div>

                        <div>✓ Workspace roles follow least privilege</div>

                        <div>✓ Invitation history cannot be silently altered</div>

                    </div>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-6">

                    <h3 className="text-lg font-semibold">

                        Recommended Role Usage

                    </h3>

                    <div className="mt-5 space-y-4 text-sm">

                        <div>

                            <strong>Owner</strong>

                            <div className="text-slate-600">

                                Governance, billing and identity authority.

                            </div>

                        </div>

                        <div>

                            <strong>Operator</strong>

                            <div className="text-slate-600">

                                Daily trading operations and claim management.

                            </div>

                        </div>

                        <div>

                            <strong>Auditor</strong>

                            <div className="text-slate-600">

                                Independent review with read-only evidence access.

                            </div>

                        </div>

                        <div>

                            <strong>Member</strong>

                            <div className="text-slate-600">

                                Standard operational participant.

                            </div>

                        </div>

                    </div>

                </div>

            </div>

            <div className="mt-8 rounded-2xl border border-emerald-200 bg-emerald-50 p-6">

                <h3 className="font-semibold text-emerald-900">

                    Pre-Onboarding Governance Checks

                </h3>

                <div className="mt-4 grid gap-3 md:grid-cols-2">

                    <div>✓ Workspace active</div>

                    <div>✓ Identity governance enabled</div>

                    <div>✓ Invitation lifecycle enabled</div>

                    <div>✓ Commercial plan evaluated</div>

                    <div>✓ Workspace audit enabled</div>

                    <div>✓ Capacity validated before issuance</div>

                </div>

            </div>

            <div className="mt-10">

                {children}

            </div>

        </section>

    );

}