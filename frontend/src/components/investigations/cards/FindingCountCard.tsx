"use client";

interface Props {

    findings: number;

}

export default function FindingCountCard({

    findings,

}: Props) {


    const status =
        findings === 0
            ? "Clean"
            : findings <= 5
            ? "Minor"
            : findings <= 15
            ? "Moderate"
            : "Significant";

    const badgeClass =
        findings === 0
            ? "bg-emerald-100 text-emerald-700"
            : findings <= 5
            ? "bg-blue-100 text-blue-700"
            : findings <= 15
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
                Findings
            </div>

            <div className="mt-4 flex items-end justify-between">

                <div className="text-5xl font-bold">

                    {findings}

                </div>

                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${badgeClass}`}
                >

                    {status}

                </span>

            </div>

            <div className="mt-5 rounded-lg bg-slate-50 p-4">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Investigation Assessment

                </div>

                <div className="mt-2 text-sm leading-6 text-slate-700">

                    {findings === 0 &&

                        "No investigation findings were produced. The investigation completed without identifying material issues."}

                    {findings > 0 &&
                        findings <= 5 &&

                        "A small number of findings were identified. Review the observations before final institutional approval."}

                    {findings > 5 &&
                        findings <= 15 &&

                        "Multiple findings require attention. Prioritize remediation according to investigation recommendations."}

                    {findings > 15 &&

                        "The investigation detected a significant number of findings requiring comprehensive institutional review."}

                </div>

            </div>

            <div className="mt-6 border-t pt-4">

                <div className="flex items-center justify-between text-sm">

                    <span className="text-slate-500">

                        Investigation Status

                    </span>

                    <span className="font-semibold">

                        {status}

                    </span>

                </div>

            </div>

        </div>

    );

}