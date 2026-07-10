import {
    RoleCapability,
} from "./types";

const capabilities: RoleCapability[] = [

    {
        surface: "Dashboard",
        owner: true,
        operator: true,
        auditor: true,
        member: true,
    },

    {
        surface: "Evidence",
        owner: true,
        operator: true,
        auditor: true,
        member: false,
    },

    {
        surface: "Claims",
        owner: true,
        operator: true,
        auditor: true,
        member: false,
    },

    {
        surface: "Verification",
        owner: true,
        operator: true,
        auditor: true,
        member: false,
    },

    {
        surface: "Reports",
        owner: true,
        operator: true,
        auditor: true,
        member: false,
    },

    {
        surface: "Members",
        owner: true,
        operator: false,
        auditor: false,
        member: false,
    },

    {
        surface: "Billing",
        owner: true,
        operator: false,
        auditor: false,
        member: false,
    },

    {
        surface: "Workspace Settings",
        owner: true,
        operator: false,
        auditor: false,
        member: false,
    },

];

function Cell({

    value,

}: {

    value: boolean;

}) {

    return (

        <td className="border border-slate-200 px-4 py-3 text-center">

            {value ? "✓" : "—"}

        </td>

    );

}

export default function PermissionMatrix() {

    return (

        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Access Matrix
            </div>

            <h2 className="mt-3 text-2xl font-semibold">

                Institutional permissions

            </h2>

            <div className="mt-8 overflow-x-auto">

                <table className="min-w-full border-collapse">

                    <thead>

                        <tr className="bg-slate-100">

                            <th className="border border-slate-200 px-4 py-3 text-left">

                                Surface

                            </th>

                            <th className="border border-slate-200 px-4 py-3">

                                Owner

                            </th>

                            <th className="border border-slate-200 px-4 py-3">

                                Operator

                            </th>

                            <th className="border border-slate-200 px-4 py-3">

                                Auditor

                            </th>

                            <th className="border border-slate-200 px-4 py-3">

                                Member

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {capabilities.map((row) => (

                            <tr key={row.surface}>

                                <td className="border border-slate-200 px-4 py-3 font-medium">

                                    {row.surface}

                                </td>

                                <Cell value={row.owner} />

                                <Cell value={row.operator} />

                                <Cell value={row.auditor} />

                                <Cell value={row.member} />

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </div>

    );

}