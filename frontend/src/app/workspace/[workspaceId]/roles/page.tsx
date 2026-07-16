"use client";

import Navbar from "../../../../components/Navbar";

import { useParams } from "next/navigation";

function Metric({
    title,
    value,
}: {
    title: string;
    value: string | number;
}) {
    return (
        <div className="rounded-2xl border bg-slate-50 p-5">
            <div className="text-xs uppercase tracking-wide text-slate-500">
                {title}
            </div>

            <div className="mt-3 text-3xl font-bold">
                {value}
            </div>
        </div>
    );
}

function RoleCard({
    title,
    responsibilities,
}: {
    title: string;
    responsibilities: string[];
}) {
    return (
        <div className="rounded-3xl border bg-white p-6 shadow-sm">
            <h3 className="text-xl font-semibold">
                {title}
            </h3>

            <ul className="mt-5 space-y-3 text-sm text-slate-600">
                {responsibilities.map((item) => (
                    <li key={item}>
                        • {item}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default function RolesPage() {

    const params = useParams();

    const workspaceId =
        Number(params.workspaceId);

    const permissions = [

              {
                  capability: "Workspace Governance",
                  owner: "✓",
                  operator: "",
                  auditor: "",
                  member: "",
              },

              {
                  capability: "Claims",
                  owner: "✓",
                  operator: "✓",
                  auditor: "✓",
                  member: "✓",
              },

              {
                  capability: "Evidence",
                  owner: "✓",
                  operator: "✓",
                  auditor: "✓",
                  member: "✓",
              },

              {
                  capability: "Verification",
                  owner: "✓",
                  operator: "✓",
                  auditor: "✓",
                  member: "",
              },

              {
                  capability: "Reports",
                  owner: "✓",
                  operator: "✓",
                  auditor: "",
                  member: "",
              },

              {
                  capability: "Investigations",
                  owner: "✓",
                  operator: "✓",
                  auditor: "✓",
                  member: "",
              },

              {
                  capability: "Members",
                  owner: "✓",
                  operator: "",
                  auditor: "",
                  member: "",
              },

              {
                  capability: "Billing",
                  owner: "✓",
                  operator: "",
                  auditor: "",
                  member: "",
              },

              {
                  capability: "Settings",
                  owner: "✓",
                  operator: "",
                  auditor: "",
                  member: "",
              },

              {
                  capability: "Public Trust Layer",
                  owner: "✓",
                  operator: "✓",
                  auditor: "✓",
                  member: "✓",
              },

          ];

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar workspaceId={workspaceId} />

            <main className="mx-auto max-w-7xl px-6 py-10 space-y-8">

                {/* Hero */}

                <div className="rounded-3xl border bg-white p-8 shadow-sm">

                    <div className="text-xs uppercase tracking-[0.25em] text-slate-500">

                        Institutional Governance System

                    </div>

                    <h1 className="mt-3 text-4xl font-bold">

                        Workspace Roles & Authority Matrix

                    </h1>

                    <p className="mt-4 max-w-4xl text-slate-600">

                        Trading Truth Layer uses a canonical institutional
                        governance model based upon delegated operational
                        authority, commercial entitlements, verification
                        independence, and governance readiness. Workspace
                        roles are institutional identities and are not
                        user-configurable.

                    </p>

                </div>

                {/* Overview */}

                <div className="grid gap-4 md:grid-cols-4">

                    <Metric
                        title="Canonical Roles"
                        value={4}
                    />

                    <Metric
                        title="Authority Levels"
                        value={4}
                    />

                    <Metric
                        title="Governance Model"
                        value="TTL"
                    />

                    <Metric
                        title="Role Architecture"
                        value="Canonical"
                    />

                </div>

                {/* Authority Hierarchy */}

                <div className="rounded-3xl border bg-white p-8 shadow-sm">

                    <h2 className="text-2xl font-semibold">

                        Authority Hierarchy

                    </h2>

                    <p className="mt-2 text-slate-600">

                        Workspace authority flows downward through
                        delegated institutional responsibilities.

                    </p>

                    <div className="mt-8 space-y-4">

                        <HierarchyCard title="OWNER" />
                        <HierarchyCard title="OPERATOR" />
                        <HierarchyCard title="AUDITOR" />
                        <HierarchyCard title="MEMBER" />

                    </div>

                </div>

                {/* Role Cards */}

                <div>

                    <h2 className="mb-6 text-2xl font-semibold">

                        Institutional Role Architecture

                    </h2>

                    <div className="grid gap-6 lg:grid-cols-2">

                        <RoleCard
                            title="Owner"
                            responsibilities={[
                                "Workspace Governance",
                                "Commercial Authority",
                                "Identity Management",
                                "Billing Management",
                                "Workspace Settings",
                                "Member Administration",
                                "Institutional Oversight",
                            ]}
                        />

                        <RoleCard
                            title="Operator"
                            responsibilities={[
                                "Claim Operations",
                                "Evidence Operations",
                                "Verification Operations",
                                "Reporting Operations",
                                "Trading Operations",
                                "Workflow Execution",
                                "Operational Management",
                            ]}
                        />

                        <RoleCard
                            title="Auditor"
                            responsibilities={[
                                "Independent Reviews",
                                "Evidence Audits",
                                "Compliance Reviews",
                                "Verification Reviews",
                                "Governance Observation",
                                "Institutional Assurance",
                            ]}
                        />

                        <RoleCard
                            title="Member"
                            responsibilities={[
                                "Claim Participation",
                                "Evidence Submission",
                                "Workspace Collaboration",
                                "Limited Operational Access",
                            ]}
                        />

                    </div>

                </div>

                {/* Permission Matrix */}

                <div className="rounded-3xl border bg-white shadow-sm overflow-hidden">

                    <div className="border-b p-8">

                        <h2 className="text-2xl font-semibold">

                            Permission Matrix

                        </h2>

                        <p className="mt-2 text-slate-600">

                            Canonical operational responsibilities for
                            each institutional role.

                        </p>

                    </div>

                    <div className="overflow-x-auto">

                        <table className="min-w-full">

                            <thead className="sticky top-0 bg-slate-100">

                                <tr>

                                    <th className="px-6 py-4 text-left">
                                        Capability
                                    </th>

                                    <th className="px-6 py-4">
                                        Owner
                                    </th>

                                    <th className="px-6 py-4">
                                        Operator
                                    </th>

                                    <th className="px-6 py-4">
                                        Auditor
                                    </th>

                                    <th className="px-6 py-4">
                                        Member
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                              {permissions.map((permission) => (

                                  <tr
                                      key={permission.capability}
                                      className="border-t"
                                  >

                                      <td className="px-6 py-4 text-left font-medium">
                                          {permission.capability}
                                      </td>

                                      <td className="px-6 py-4 text-center">
                                          {permission.owner}
                                      </td>

                                      <td className="px-6 py-4 text-center">
                                          {permission.operator}
                                      </td>

                                      <td className="px-6 py-4 text-center">
                                          {permission.auditor}
                                      </td>

                                      <td className="px-6 py-4 text-center">
                                          {permission.member}
                                      </td>

                                  </tr>

                              ))}

                          </tbody>

                        </table>

                    </div>

                </div>

                {/* Delegation Rules */}

                <div className="rounded-3xl border bg-white p-8 shadow-sm">

                    <h2 className="text-2xl font-semibold">

                        Delegation Rules

                    </h2>

                    <ul className="mt-6 space-y-3 text-slate-600">

                        <li>
                            • Only Owners may manage workspace governance.
                        </li>

                        <li>
                            • Only Owners may invite or remove members.
                        </li>

                        <li>
                            • Operators manage institutional workflows.
                        </li>

                        <li>
                            • Auditors operate independently from operational workflows.
                        </li>

                        <li>
                            • Members participate within delegated permissions.
                        </li>

                        <li>
                            • Commercial and plan entitlements supersede role authority.
                        </li>

                    </ul>

                </div>

                {/* Governance Principles */}

                <div className="rounded-3xl border bg-white p-8 shadow-sm">

                    <h2 className="text-2xl font-semibold">

                        Institutional Governance Principles

                    </h2>

                    <div className="mt-6 grid gap-4 md:grid-cols-2">

                        <Principle text="Separation of Authority" />
                        <Principle text="Verification Independence" />
                        <Principle text="Institutional Accountability" />
                        <Principle text="Least Privilege Access" />
                        <Principle text="Commercial Entitlement Enforcement" />
                        <Principle text="Governance Readiness" />

                    </div>

                </div>

            </main>

        </div>

    );

}

function HierarchyCard({
    title,
}:{
    title:string;
}){

    return(

        <div className="rounded-2xl border bg-slate-50 px-6 py-4 font-semibold">

            {title}

        </div>

    );

}

function Principle({
    text,
}:{
    text:string;
}){

    return(

        <div className="rounded-xl border bg-slate-50 p-4">

            {text}

        </div>

    );

}