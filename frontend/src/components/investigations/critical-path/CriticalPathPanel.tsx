"use client";

import type {
    InvestigationCriticalPath,
} from "@/lib/api";

import SectionCard from "../common/SectionCard";

interface Props {
    criticalPath?: InvestigationCriticalPath | null;
}

export default function CriticalPathPanel({
    criticalPath,
}: Props) {

    if (!criticalPath) {
        return null;
    }

    const score = criticalPath.score ?? 0;
    const rootCause =
        criticalPath.root_cause ??
        "No root cause identified.";

    const steps = criticalPath.steps ?? [];

    return (
        <SectionCard
            title="Critical Investigation Path"
            subtitle="Institutional Root Cause Reconstruction"
        >
            <div
                className="
                    max-h-[900px]
                    overflow-y-auto
                    pr-2
                "
            >
                <div className="space-y-8">

                <div>
                    <div className="text-xs uppercase tracking-widest text-gray-500">
                        Investigation Confidence
                    </div>

                    <div className="mt-2 text-5xl font-bold">
                        {score.toFixed(2)}
                    </div>
                </div>

                <div>
                    <div className="text-xs uppercase tracking-widest text-gray-500">
                        Root Cause
                    </div>

                    <div className="mt-3 leading-7 text-gray-700 dark:text-gray-300">
                        {rootCause}
                    </div>
                </div>

                <div>

                    <div className="text-xs uppercase tracking-widest text-gray-500 mb-4">
                        Investigation Sequence
                    </div>

                    <div className="space-y-4">

                        {steps.length === 0 ? (

                            <div className="text-sm text-gray-500">
                                No investigation sequence available.
                            </div>

                        ) : (

                            steps.map((step, index) => (

                                <div
                                    key={step.order}
                                    className="flex gap-4"
                                >

                                    <div className="flex flex-col items-center shrink-0">

                                        <div
                                            className="
                                                flex
                                                h-10
                                                w-10
                                                items-center
                                                justify-center
                                                rounded-full
                                                border
                                                font-bold
                                            "
                                        >
                                            {step.order}
                                        </div>

                                        {index !== steps.length - 1 && (

                                            <div className="mt-2 w-px flex-1 bg-slate-300" />

                                        )}

                                    </div>

                                    <div
                                        className="
                                            flex-1
                                            rounded-lg
                                            border
                                            p-4
                                        "
                                    >

                                        <div className="font-semibold">
                                            {step.title}
                                        </div>

                                        <div className="mt-3 flex flex-wrap items-center gap-2">

                                            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium">

                                                {step.category}

                                            </span>

                                            <span
                                                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                                    step.severity.toUpperCase() === "CRITICAL"
                                                        ? "bg-red-100 text-red-700"
                                                        : step.severity.toUpperCase() === "HIGH"
                                                        ? "bg-orange-100 text-orange-700"
                                                        : step.severity.toUpperCase() === "MEDIUM"
                                                        ? "bg-amber-100 text-amber-700"
                                                        : step.severity.toUpperCase() === "LOW"
                                                        ? "bg-blue-100 text-blue-700"
                                                        : "bg-emerald-100 text-emerald-700"
                                                }`}
                                            >

                                                {step.severity}

                                            </span>

                                        </div>

                                        <div className="mt-3 leading-7 text-slate-700">

                                            {step.description}

                                        </div>

                                        {"confidence" in step && step.confidence !== undefined && (

                                            <div className="mt-4">

                                                <div className="text-xs uppercase tracking-wide text-slate-500">

                                                    Confidence

                                                </div>

                                                <div className="mt-1 font-semibold">

                                                    {Number(step.confidence).toFixed(1)}%

                                                </div>

                                            </div>

                                        )}

                                        {"metadata" in step &&
                                        step.metadata &&
                                        Object.keys(step.metadata).length > 0 && (

                                        <div className="mt-5 rounded-lg bg-slate-50 p-4">

                                            <div className="mb-3 text-xs uppercase tracking-wide text-slate-500">

                                                Metadata

                                            </div>

                                            <div className="grid gap-3 md:grid-cols-2">

                                                {Object.entries(step.metadata).map(([key,value])=>(

                                                    <div
                                                        key={key}
                                                        className="rounded-md bg-white p-3"
                                                    >

                                                        <div className="text-xs uppercase tracking-wide text-slate-500">

                                                            {key}

                                                        </div>

                                                        <div className="mt-1 font-medium">

                                                            {String(value)}

                                                        </div>

                                                    </div>

                                                ))}

                                            </div>

                                        </div>

                                        )}

                                    </div>

                                </div>

                            ))

                        )}

                    </div>

                </div>

                </div>

            </div>

        </SectionCard>
    );

}