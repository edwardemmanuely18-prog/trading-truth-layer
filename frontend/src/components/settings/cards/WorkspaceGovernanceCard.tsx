"use client";

type Props = {

    governance?: {

        workspaceId: number;

        role: string;

        configuredPlan: string;

        effectivePlan: string;

        billingStatus: string;

        createdAt: string;

        updatedAt: string;

    };

};

function Row({

    label,

    value,

}:{

    label:string;

    value:string|number;

}){

    return(

        <div className="flex items-center justify-between border-b py-3 last:border-0">

            <div className="text-sm text-slate-500">

                {label}

            </div>

            <div className="font-semibold">

                {value}

            </div>

        </div>

    );

}

export default function WorkspaceGovernanceCard({

    governance,

}: Props) {

    return(

        <div className="rounded-3xl border bg-white p-6 shadow-sm">

            <h2 className="text-2xl font-semibold">

                Workspace Governance

            </h2>

            <p className="mt-2 text-sm text-slate-500">

                Governance identity and commercial
                configuration of the workspace.

            </p>

            <div className="mt-6">

                <Row

                    label="Workspace ID"

                    value={governance?.workspaceId ?? "—"}

                />

                <Row

                    label="Current Plan"

                    value={governance?.configuredPlan ?? "—"}

                />

                <Row

                    label="Workspace Role"

                    value={governance?.role ?? "—"}

                />

                <Row

                    label="Billing Status"

                    value={governance?.billingStatus ?? "Inactive"}

                />

                <Row

                    label="Created"

                    value={governance?.createdAt ?? "—"}

                />

                <Row

                    label="Last Updated"

                    value={governance?.updatedAt ?? "—"}

                />

            </div>

        </div>

    );

}