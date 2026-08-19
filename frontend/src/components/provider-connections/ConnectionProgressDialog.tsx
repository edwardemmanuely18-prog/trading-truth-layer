"use client";

type ProgressStep = {

    title: string;

    status: "pending" | "running" | "completed" | "failed";

};

type Props = {

    open: boolean;

    title: string;

    message: string;

    steps: ProgressStep[];

    onClose: () => void;

};

export default function ConnectionProgressDialog({

    open,

    title,

    message,

    steps,

    onClose,

}: Props) {

    if (!open) {

        return null;

    }

    return (

        <div className="fixed inset-0 z-[9999] overflow-y-auto bg-black/50 p-10">

            <div
                className="
                    mx-auto
                    my-8
                    w-full
                    max-w-6xl
                    rounded-2xl
                    bg-white
                    shadow-2xl
                    max-h-[90vh]
                    overflow-y-auto
                "
            >

                <div className="border-b px-8 py-6">

                    <div className="text-2xl font-bold">

                        {title}

                    </div>

                    <div className="mt-2 text-slate-500">

                        {message}

                    </div>

                </div>

                <div className="p-8 overflow-y-auto">

                    <div className="space-y-5 pb-8">

                        <div className="rounded-xl bg-slate-900 p-5 text-sm text-green-400 font-mono">
                            <div>Desktop Trading Engine Runtime</div>
                            <div className="mt-3">
                                Waiting for backend response...
                            </div>
                        </div>

                        {steps.map((step) => (

                            <div
                                key={step.title}
                                className="flex items-center justify-between rounded-xl border p-5"
                            >

                                <div className="font-medium">

                                    {step.title}

                                </div>

                                <ProgressBadge
                                    status={step.status}
                                />

                            </div>

                        ))}

                    </div>

                </div>

                <div className="sticky bottom-0 flex justify-end border-t bg-white px-8 py-5">

                    <button
                        onClick={onClose}
                        className="rounded-lg border px-5 py-2 hover:bg-slate-100"
                    >

                        Close

                    </button>

                </div>

            </div>

        </div>

    );

}

function ProgressBadge({
    status,
}: {
    status: ProgressStep["status"];
}) {

    if (status === "completed") {

        return (

            <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-semibold text-green-700">

                Completed

            </span>

        );

    }

    if (status === "running") {

        return (

            <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-700">

                Running

            </span>

        );

    }

    if (status === "failed") {

        return (

            <span className="rounded-full bg-red-100 px-3 py-1 text-sm font-semibold text-red-700">

                Failed

            </span>

        );

    }

    return (

        <span className="rounded-full bg-slate-200 px-3 py-1 text-sm font-semibold text-slate-700">

            Pending

        </span>

    );

}