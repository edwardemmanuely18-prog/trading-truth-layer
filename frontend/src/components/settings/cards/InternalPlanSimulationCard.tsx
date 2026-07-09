"use client";

import { useState } from "react";

import {
    setWorkspacePlanSimulation,
    clearWorkspacePlanSimulation,
} from "../../../lib/api";

type SimulationSnapshot = {

    workspace_id: number;

    actual_plan: string;

    effective_plan: string;

    simulation_enabled: boolean;

    simulated_plan: string | null;

};

type Props = {

    workspaceId: number;

    simulation: SimulationSnapshot | null;

    onChanged: () => Promise<void>;

};

const PLANS = [

    "sandbox",

    "starter",

    "pro",

    "growth",

    "business",

    "enterprise",

];

function formatPlan(plan?: string | null) {

    if (!plan) {

        return "—";

    }

    return (

        plan.charAt(0).toUpperCase() +

        plan.slice(1)

    );

}

export default function InternalPlanSimulationCard({

    workspaceId,

    simulation,

    onChanged,

}: Props) {

    const [

        selectedPlan,

        setSelectedPlan,

    ] = useState(

        simulation?.effective_plan ??

        "sandbox"

    );

    const [

        loading,

        setLoading,

    ] = useState(false);

    async function applySimulation() {

        try {

            setLoading(true);

            await setWorkspacePlanSimulation(

                workspaceId,

                selectedPlan,

            );

            await onChanged();

        } finally {

            setLoading(false);

        }

    }

    async function clearSimulation() {

        try {

            setLoading(true);

            await clearWorkspacePlanSimulation(

                workspaceId,

            );

            await onChanged();

        } finally {

            setLoading(false);

        }

    }

    return (

        <div className="rounded-3xl border border-blue-200 bg-blue-50 p-6 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <h2 className="text-2xl font-semibold">

                        Internal Plan Simulation

                    </h2>

                    <p className="mt-2 text-sm text-slate-600">

                        Internal QA tool for validating
                        entitlement behaviour across all
                        commercial plans.

                    </p>

                </div>

                <div className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white">

                    INTERNAL

                </div>

            </div>

            {simulation?.simulation_enabled && (

                <div className="mt-6 rounded-2xl border border-amber-300 bg-amber-100 p-4">

                    <div className="font-semibold text-amber-900">

                        Simulation Active

                    </div>

                    <div className="mt-1 text-sm text-amber-800">

                        Workspace billing remains on{" "}
                        <strong>

                            {formatPlan(
                                simulation.actual_plan
                            )}

                        </strong>

                        {" "}while TTL is behaving as{" "}

                        <strong>

                            {formatPlan(
                                simulation.effective_plan
                            )}

                        </strong>

                        .

                    </div>

                </div>

            )}

            <div className="mt-8 grid gap-5 md:grid-cols-2">

                <InfoCard

                    label="Actual Billing Plan"

                    value={formatPlan(

                        simulation?.actual_plan

                    )}

                />

                <InfoCard

                    label="Effective Plan"

                    value={formatPlan(

                        simulation?.effective_plan

                    )}

                />

                <InfoCard

                    label="Simulation"

                    value={

                        simulation?.simulation_enabled

                            ? "Enabled"

                            : "Disabled"

                    }

                />

                <InfoCard

                    label="Current Override"

                    value={

                        formatPlan(

                            simulation?.simulated_plan

                        )

                    }

                />

            </div>

            <div className="mt-8">

                <label className="mb-2 block text-sm font-medium">

                    Simulate Plan

                </label>

                <select

                    className="w-full rounded-xl border bg-white px-4 py-3"

                    value={selectedPlan}

                    onChange={(e) =>

                        setSelectedPlan(

                            e.target.value

                        )

                    }

                >

                    {PLANS.map((plan) => (

                        <option

                            key={plan}

                            value={plan}

                        >

                            {formatPlan(plan)}

                        </option>

                    ))}

                </select>

            </div>

            <div className="mt-8 flex gap-3">

                <button

                    disabled={loading}

                    onClick={applySimulation}

                    className="rounded-xl bg-slate-900 px-5 py-3 font-semibold text-white disabled:opacity-50"

                >

                    Apply Simulation

                </button>

                <button

                    disabled={loading}

                    onClick={clearSimulation}

                    className="rounded-xl border bg-white px-5 py-3 font-semibold disabled:opacity-50"

                >

                    Clear Simulation

                </button>

            </div>

            <div className="mt-8 rounded-2xl border bg-white p-5">

                <div className="font-semibold">

                    Safety Guarantees

                </div>

                <ul className="mt-3 space-y-2 text-sm text-slate-600">

                    <li>

                        ✓ Workspace.plan_code is never modified

                    </li>

                    <li>

                        ✓ Paddle subscriptions are never modified

                    </li>

                    <li>

                        ✓ Stripe subscriptions are never modified

                    </li>

                    <li>

                        ✓ Billing state remains canonical

                    </li>

                    <li>

                        ✓ Only entitlement resolution changes

                    </li>

                </ul>

            </div>

        </div>

    );

}

function InfoCard({

    label,

    value,

}: {

    label: string;

    value: string;

}) {

    return (

        <div className="rounded-2xl border bg-white p-4">

            <div className="text-sm text-slate-500">

                {label}

            </div>

            <div className="mt-2 text-xl font-semibold">

                {value}

            </div>

        </div>

    );

}