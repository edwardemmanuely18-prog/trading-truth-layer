import type { GovernanceSummary } from "./types";

interface Props {

    summary: GovernanceSummary;

    snapshot?: any;

    configuredPlan: string;

    effectivePlan: string;

    configuredLimit: number | null;

    effectiveLimit: number | null;

    billingActivationRecommended: boolean;

    planMismatch: boolean;

}

export default function CapacityOverview({

    summary,

    snapshot,

    configuredPlan,

    effectivePlan,

    configuredLimit,

    effectiveLimit,

    billingActivationRecommended,

    planMismatch,

}: Props) {

    const limit = snapshot?.capacity?.member_limit
                      ??
                  effectiveLimit ?? 0;

    const utilization =

        snapshot?.capacity?.utilization

        ??

        (

            effectiveLimit

            ?

            Math.round(

                summary.memberCount /

                effectiveLimit *

                100

            )

            :

            0

        );

    const remaining =
        Math.max(limit - summary.memberCount, 0);

    return (
        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <div className="text-xs uppercase tracking-[0.25em] text-slate-500">
                        Capacity Governance
                    </div>

                    <h2 className="mt-2 text-3xl font-bold">
                        Workspace Capacity
                    </h2>

                    <p className="mt-2 max-w-3xl text-slate-600">
                        Capacity is governed by the effective commercial
                        plan currently enforcing workspace identity limits.
                    </p>

                </div>

                <div className="rounded-xl border bg-slate-50 px-6 py-4">

                    <div className="text-xs uppercase text-slate-500">
                        Utilization
                    </div>

                    <div className="mt-2 text-3xl font-bold">
                        {utilization}%
                    </div>

                </div>

            </div>

            <div className="mt-8 grid gap-6 md:grid-cols-4">

                <div className="rounded-xl border p-5">

                    <div className="text-sm text-slate-500">
                        Members
                    </div>

                    <div className="mt-2 text-3xl font-bold">
                        {summary.memberCount}
                    </div>

                </div>

                <div className="rounded-xl border p-5">

                    <div className="text-sm text-slate-500">
                        Remaining Capacity
                    </div>

                    <div className="mt-2 text-3xl font-bold">
                        {remaining}
                    </div>

                </div>

                <div className="rounded-xl border p-5">

                    <div className="text-sm text-slate-500">
                        Effective Plan
                    </div>

                    <div className="mt-2 text-xl font-semibold">
                        {effectivePlan}
                    </div>

                </div>

                <div className="rounded-xl border p-5">

                    <div className="text-sm text-slate-500">
                        Configured Plan
                    </div>

                    <div className="mt-2 text-xl font-semibold">
                        {configuredPlan}
                    </div>

                </div>

            </div>

            {planMismatch && (
                <div className="mt-8 rounded-2xl border border-amber-300 bg-amber-50 p-5">

                    <div className="font-semibold text-amber-900">
                        Commercial Plan Mismatch
                    </div>

                    <p className="mt-2 text-sm text-amber-800">
                        Billing has not yet activated the configured
                        commercial plan. Workspace enforcement is currently
                        using the effective plan.
                    </p>

                </div>
            )}

            {billingActivationRecommended && (
                <div className="mt-5 rounded-2xl border border-blue-300 bg-blue-50 p-5">

                    <div className="font-semibold text-blue-900">
                        Billing Activation Recommended
                    </div>

                    <p className="mt-2 text-sm text-blue-800">
                        Activating billing will align commercial
                        entitlements with workspace governance capacity.
                    </p>

                </div>
            )}

        </section>
    );
}