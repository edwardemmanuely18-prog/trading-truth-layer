"use client";

import SectionCard
from "../common/SectionCard";

export default function DomainDependencyGraph() {

    const rows = [

        {
            domain: "Execution",
            consumes: "Execution Replay",
            produces: "Execution Assessment",
        },

        {
            domain: "Evidence",
            consumes: "Execution",
            produces: "Evidence Integrity",
        },

        {
            domain: "Verification",
            consumes: "Evidence",
            produces: "Verification Result",
        },

        {
            domain: "Governance",
            consumes: "Verification",
            produces: "Governance Assessment",
        },

        {
            domain: "Synchronization",
            consumes: "Broker State",
            produces: "Synchronization Health",
        },

        {
            domain: "Broker",
            consumes: "Broker Connections",
            produces: "Broker Reliability",
        },

        {
            domain: "Review",
            consumes: "Investigation Findings",
            produces: "Institutional Review",
        },

        {
            domain: "Behavior",
            consumes: "Historical Activity",
            produces: "Behavior Profile",
        },

        {
            domain: "Allocator",
            consumes: "All Domains",
            produces: "Institutional Decision",
        },

    ];

    return (

        <SectionCard

            title="Domain Dependency Graph"

            subtitle="Institutional reasoning flow across IIS."

        >

            <div className="overflow-x-auto">

                <table className="min-w-full">

                    <thead>

                        <tr className="border-b">

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Domain

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Consumes

                            </th>

                            <th className="px-4 py-3 text-left text-xs uppercase tracking-wide text-slate-500">

                                Produces

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {rows.map(row => (

                            <tr
                                key={row.domain}
                                className="border-b last:border-0"
                            >

                                <td className="px-4 py-4 font-semibold">

                                    {row.domain}

                                </td>

                                <td className="px-4 py-4">

                                    {row.consumes}

                                </td>

                                <td className="px-4 py-4">

                                    {row.produces}

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

        </SectionCard>

    );

}