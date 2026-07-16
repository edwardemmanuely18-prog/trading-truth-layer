"use client";

interface Props {
    score?: number;
}

export default function InvestigationScoreCard({
    score = 0,
}: Props) {

    const normalizedScore = Number.isFinite(score)
        ? score
        : 0;

    const band =
        normalizedScore >= 95
            ? "Institutional"
            : normalizedScore >= 85
            ? "Strong"
            : normalizedScore >= 70
            ? "Needs Review"
            : "High Risk";

    const bandClasses =
        normalizedScore >= 95
            ? "bg-emerald-100 text-emerald-700"
            : normalizedScore >= 85
            ? "bg-blue-100 text-blue-700"
            : normalizedScore >= 70
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
                Investigation Score
            </div>

            <div
                className="
                    mt-3
                    text-5xl
                    font-bold
                "
            >
                {normalizedScore.toFixed(1)}
            </div>

            <div className="mt-4">

                <div className="flex items-center justify-between text-sm">

                    <span className="text-slate-500">

                        Investigation Rating

                    </span>

                    <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${bandClasses}`}
                    >

                        {band}

                    </span>

                </div>

                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">

                    <div
                        className="h-full rounded-full bg-emerald-600 transition-all"
                        style={{
                            width: `${Math.min(
                                100,
                                Math.max(
                                    0,
                                    normalizedScore,
                                ),
                            )}%`,
                        }}
                    />

                </div>

            </div>

            <div className="mt-5 rounded-lg bg-slate-50 p-4">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Interpretation

                </div>

                <div className="mt-2 text-sm leading-6 text-slate-700">

                    {normalizedScore >= 95 &&

                        "Investigation confidence is at institutional level. Current evidence strongly supports the investigation outcome."}

                    {normalizedScore >= 85 &&
                        normalizedScore < 95 &&

                        "Investigation is well supported. Minor observations should be reviewed before institutional reliance."}

                    {normalizedScore >= 70 &&
                        normalizedScore < 85 &&

                        "Investigation requires additional review before relying on allocator decisions."}

                    {normalizedScore < 70 &&

                        "Investigation confidence is insufficient. Critical findings should be resolved before institutional acceptance."}

                </div>

            </div>
        </div>
    );
}