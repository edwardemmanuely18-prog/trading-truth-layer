"use client";

type Props={

    feature:string;

};

export default function UpgradeRequired({

    feature,

}:Props){

    return(

        <div className="rounded-3xl border bg-white p-10">

            <div className="text-4xl">

                🔒

            </div>

            <h1 className="mt-5 text-3xl font-bold">

                Upgrade Required

            </h1>

            <p className="mt-4 text-slate-500">

                Your current workspace plan
                does not include

                <strong>

                    {" "}
                    {feature}

                </strong>

                .

            </p>

            <button

                className="mt-8 rounded-xl bg-slate-900 px-6 py-3 text-white"

            >

                Upgrade Workspace

            </button>

        </div>

    );

}