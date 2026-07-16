"use client";

interface Props {

    recommendations: number;

}

export default function RecommendationCountCard({

    recommendations,

}: Props) {

    const status =
        recommendations === 0
            ? "Complete"
            : recommendations <= 3
            ? "Minor Actions"
            : recommendations <= 8
            ? "Action Plan"
            : "Major Remediation";

    const badgeClass =
        recommendations === 0
            ? "bg-emerald-100 text-emerald-700"
            : recommendations <= 3
            ? "bg-blue-100 text-blue-700"
            : recommendations <= 8
            ? "bg-amber-100 text-amber-700"
            : "bg-red-100 text-red-700";

    return (

        <div
            className="
                rounded-xl
                border
                bg-white
                dark:bg-neutral-900
                shadow-sm
                p-6
            "
        >

            <div
                className="
                    text-xs
                    uppercase
                    tracking-wider
                    text-gray-500
                "
            >
                Recommendations
            </div>

            <div className="mt-4 flex items-end justify-between">

                <div className="text-5xl font-bold">

                    {recommendations}

                </div>

                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${badgeClass}`}
                >

                    {status}

                </span>

            </div>

            <div className="mt-5 rounded-lg bg-slate-50 p-4">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Recommended Actions

                </div>

                <div className="mt-2 text-sm leading-6 text-slate-700">

                    {recommendations === 0 &&

                        "The investigation concluded without requiring additional remediation actions."}

                    {recommendations > 0 &&
                        recommendations <= 3 &&

                        "A limited number of remediation actions are recommended before institutional approval."}

                    {recommendations > 3 &&
                        recommendations <= 8 &&

                        "Several remediation actions have been identified. Recommendations should be prioritized according to investigation findings."}

                    {recommendations > 8 &&

                        "The investigation identified extensive remediation requirements. A structured implementation plan is recommended before institutional reliance."}

                </div>

            </div>

            <div className="mt-6 border-t pt-4">

                <div className="flex items-center justify-between text-sm">

                    <span className="text-slate-500">

                        Remediation Status

                    </span>

                    <span className="font-semibold">

                        {recommendations === 0
                            ? "Completed"
                            : "Pending"}

                    </span>

                </div>

            </div>

        </div>

    );

}