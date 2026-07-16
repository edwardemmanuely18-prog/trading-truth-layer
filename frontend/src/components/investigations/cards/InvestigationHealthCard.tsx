"use client";

interface Props {

    health: string;

}

export default function InvestigationHealthCard({

    health,

}: Props) {

    const normalizedHealth = health.toUpperCase();

    const badgeClass =
        normalizedHealth === "CRITICAL"
            ? "bg-red-100 text-red-700"
            : normalizedHealth === "HIGH"
            ? "bg-orange-100 text-orange-700"
            : normalizedHealth === "MEDIUM"
            ? "bg-amber-100 text-amber-700"
            : normalizedHealth === "LOW"
            ? "bg-blue-100 text-blue-700"
            : "bg-emerald-100 text-emerald-700";

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
                Overall Health
            </div>

            <div className="mt-5">

                <span
                    className={`rounded-full px-4 py-2 text-lg font-semibold ${badgeClass}`}
                >

                    {health}

                </span>

            </div>

            <div className="mt-5 rounded-lg bg-slate-50 p-4">

                <div className="text-xs uppercase tracking-wide text-slate-500">

                    Health Assessment

                </div>

                <div className="mt-2 text-sm leading-6 text-slate-700">

                    {normalizedHealth === "CRITICAL" &&

                        "The investigation identified critical institutional risks requiring immediate remediation."}

                    {normalizedHealth === "HIGH" &&

                        "High-risk observations were identified. Institutional review is recommended before relying on investigation outcomes."}

                    {normalizedHealth === "MEDIUM" &&

                        "The investigation is generally healthy but contains findings that should be reviewed."}

                    {normalizedHealth === "LOW" &&

                        "Only low-risk observations were detected. Overall investigation health remains strong."}

                    {normalizedHealth === "INFORMATION" &&

                        "No material institutional risks were identified during the investigation."}

                </div>

            </div>

            <div className="mt-6 border-t pt-4">

                <div className="flex items-center justify-between text-sm">

                    <span className="text-slate-500">

                        Institutional Assessment

                    </span>

                    <span className="font-semibold">

                        {normalizedHealth === "CRITICAL"
                            ? "Immediate Action"
                            : normalizedHealth === "HIGH"
                            ? "Review Required"
                            : normalizedHealth === "MEDIUM"
                            ? "Monitor"
                            : "Healthy"}

                    </span>

                </div>

            </div>

        </div>

    );

}