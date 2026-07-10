import type { ReactNode } from "react";

type Props = {

    children: ReactNode;

};

export default function InvitationLedger({

    children,

}: Props) {

    return (

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <div className="max-w-5xl">

                <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                    Identity Governance

                </div>

                <h2 className="mt-2 text-3xl font-bold">

                    Invitation Ledger

                </h2>

                <p className="mt-4 text-slate-600">

                    Every invitation represents a governed identity issuance
                    event. The invitation ledger preserves issuance,
                    acceptance, expiration, revocation and lifecycle
                    chronology so workspace membership remains completely
                    auditable.

                </p>

            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-4">

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Issued

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Identity invitation created.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Pending

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Awaiting recipient acceptance.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Accepted

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Identity joined workspace.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 p-5">

                    <div className="text-xs uppercase text-slate-500">

                        Revoked

                    </div>

                    <p className="mt-3 text-sm text-slate-600">

                        Invitation permanently invalidated.

                    </p>

                </div>

            </div>

            <div className="mt-8 rounded-2xl border border-indigo-200 bg-indigo-50 p-6">

                <h3 className="font-semibold text-indigo-900">

                    Governance Controls

                </h3>

                <div className="mt-4 grid gap-3 md:grid-cols-2">

                    <div>✓ Invitation provenance</div>

                    <div>✓ Authority assignment</div>

                    <div>✓ Acceptance chronology</div>

                    <div>✓ Revocation history</div>

                    <div>✓ Identity audit trail</div>

                    <div>✓ Immutable lifecycle events</div>

                </div>

            </div>

            <div className="mt-10">

                {children}

            </div>

        </section>

    );

}