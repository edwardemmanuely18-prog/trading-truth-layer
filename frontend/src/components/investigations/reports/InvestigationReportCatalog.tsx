"use client";

import {
    InvestigationReport,
} from "@/lib/api";

import ExecutiveInvestigationCard from "./ExecutiveInvestigationCard";
import InstitutionalInvestigationCard from "./InstitutionalInvestigationCard";


interface Props {
    workspaceId: number;
    report: InvestigationReport;
}

export default function InvestigationReportCatalog({
    workspaceId,
    report,
}: Props) {

    return (

        <div className="space-y-8">

            <section className="rounded-xl border border-slate-200 bg-white shadow-sm">

                <div className="border-b border-slate-200 px-6 py-5">

                    <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                        Investigation Reports

                    </div>

                    <h2 className="mt-2 text-3xl font-semibold text-slate-900">

                        Institutional Investigation Report Center

                    </h2>

                    <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-600">

                        Generate institutional reports from the canonical
                        Investigation Context. The Institutional
                        Investigation Report (IIR) serves as the
                        authoritative investigation document, while
                        specialized reports provide deeper forensic
                        analysis for specific investigation domains.

                    </p>

                </div>

                <div className="space-y-10 p-6">

                    {/* =======================================================
                        PRIMARY INSTITUTIONAL REPORTS
                    ======================================================== */}

                    <section className="space-y-5">

                        <div>

                            <div className="text-xs uppercase tracking-[0.2em] text-slate-500">

                                Primary Reports

                            </div>

                            <h3 className="mt-2 text-2xl font-semibold text-slate-900">

                                Institutional Decision Reports

                            </h3>

                            <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600">

                                These are the primary institutional documents produced by
                                the Investigation Intelligence System. They are intended
                                for allocators, regulators, investment committees and
                                executive decision makers.

                            </p>

                        </div>

                        <InstitutionalInvestigationCard
                            workspaceId={workspaceId}
                            report={report}
                        />

                        <ExecutiveInvestigationCard
                            workspaceId={workspaceId}
                            report={report}
                        />

                    </section>

                </div>

            </section>

        </div>

    );

}