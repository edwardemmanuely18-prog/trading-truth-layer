"use client";

import type { ProviderFormProps } from "../types";

export default function FinancialProviderForm({
    provider,
}: ProviderFormProps) {
    return (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6">
            <div className="text-lg font-semibold text-slate-900">
                {provider || "Financial"} Provider Configuration
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
                No Financial Engine provider is currently registered in the
                active provider catalogue. This engine namespace is ready for
                provider-specific forms when a Financial adapter is introduced.
            </p>
        </div>
    );
}
