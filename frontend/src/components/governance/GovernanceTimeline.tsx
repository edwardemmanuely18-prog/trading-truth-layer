export default function GovernanceTimeline() {

    return (

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                Governance History

            </div>

            <h2 className="mt-2 text-3xl font-bold">

                Identity Governance Timeline

            </h2>

            <p className="mt-4 max-w-4xl text-slate-600">

                Identity governance follows a permanent chronology.
                Every authority assignment, invitation, role transition,
                acceptance, removal and audit event contributes to the
                institutional history of the workspace.

            </p>

            <div className="mt-10 space-y-6">

                <div className="rounded-xl border-l-4 border-blue-600 bg-slate-50 p-5">

                    <div className="font-semibold">

                        Workspace Created

                    </div>

                    <div className="mt-2 text-sm text-slate-600">

                        Initial owner established governance.

                    </div>

                </div>

                <div className="rounded-xl border-l-4 border-emerald-600 bg-slate-50 p-5">

                    <div className="font-semibold">

                        Identity Invitations

                    </div>

                    <div className="mt-2 text-sm text-slate-600">

                        Members entered through governed invitation
                        workflows.

                    </div>

                </div>

                <div className="rounded-xl border-l-4 border-amber-600 bg-slate-50 p-5">

                    <div className="font-semibold">

                        Authority Assignments

                    </div>

                    <div className="mt-2 text-sm text-slate-600">

                        Roles establish operational boundaries.

                    </div>

                </div>

                <div className="rounded-xl border-l-4 border-violet-600 bg-slate-50 p-5">

                    <div className="font-semibold">

                        Future Governance Events

                    </div>

                    <div className="mt-2 text-sm text-slate-600">

                        Billing activation, ownership transfers,
                        administrator changes,
                        auditor appointments,
                        compliance reviews,
                        policy updates,
                        revocations,
                        and lifecycle transitions
                        will appear here.

                    </div>

                </div>

            </div>

        </section>

    );

}