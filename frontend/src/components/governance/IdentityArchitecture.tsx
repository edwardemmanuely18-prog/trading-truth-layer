export default function IdentityArchitecture() {

    const roles = [

        {
            title: "Owner",
            responsibility:
                "Responsible for workspace governance, billing, identity administration, policy management, and final approval of institutional operations.",

            permissions: [
                "Full workspace administration",
                "Manage members",
                "Approve governance changes",
                "Billing & subscription",
                "Workspace settings",
            ],
        },

        {
            title: "Operator",
            responsibility:
                "Responsible for operational execution including evidence ingestion, claim preparation, and verification workflows.",

            permissions: [
                "Import evidence",
                "Create claims",
                "Generate reports",
                "Verification workflow",
                "Cannot manage billing",
            ],
        },

        {
            title: "Auditor",
            responsibility:
                "Independent reviewer responsible for governance oversight and verification quality.",

            permissions: [
                "Review evidence",
                "Review verification",
                "Review reports",
                "Cannot modify evidence",
                "Cannot change governance",
            ],
        },

        {
            title: "Member",
            responsibility:
                "Standard workspace participant with limited operational permissions.",

            permissions: [
                "View assigned resources",
                "Participate in workflows",
                "No governance authority",
            ],
        },

    ];

    return (

        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">

            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Identity Architecture
            </div>

            <h2 className="mt-3 text-2xl font-semibold">
                Operational responsibilities
            </h2>

            <div className="mt-8 grid gap-6 md:grid-cols-2">

                {roles.map((role) => (

                    <div
                        key={role.title}
                        className="rounded-2xl border border-slate-200 p-6"
                    >

                        <div className="text-xl font-semibold">

                            {role.title}

                        </div>

                        <p className="mt-4 text-sm leading-7 text-slate-600">

                            {role.responsibility}

                        </p>

                        <ul className="mt-6 space-y-2">

                            {role.permissions.map((permission) => (

                                <li
                                    key={permission}
                                    className="text-sm text-slate-700"
                                >
                                    • {permission}
                                </li>

                            ))}

                        </ul>

                    </div>

                ))}

            </div>

        </div>

    );

}