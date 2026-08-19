"use client";

import type {
    ProviderFieldDefinition,
    ProviderFormDefinition,
    ProviderFormProps,
} from "./types";

function Field({
    definition,
    value,
    onChange,
}: {
    definition: ProviderFieldDefinition;
    value: string;
    onChange: (value: string) => void;
}) {
    const commonClass =
        "w-full rounded-xl border px-4 py-3 outline-none focus:border-slate-900";

    return (
        <div>
            <label className="mb-2 block text-sm font-semibold">
                {definition.label}
                {definition.required ? (
                    <span className="ml-1 text-red-600">*</span>
                ) : null}
            </label>

            {definition.type === "select" ? (
                <select
                    value={value}
                    onChange={(event) => onChange(event.target.value)}
                    className={commonClass}
                >
                    {(definition.options ?? []).map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            ) : (
                <input
                    type={definition.type ?? "text"}
                    value={value}
                    placeholder={definition.placeholder}
                    onChange={(event) => onChange(event.target.value)}
                    className={commonClass}
                />
            )}

            {definition.description ? (
                <p className="mt-2 text-sm leading-6 text-slate-500">
                    {definition.description}
                </p>
            ) : null}
        </div>
    );
}

export default function ProviderConnectionForm({
    definition,
    values,
    onChange,
}: ProviderFormProps & {
    definition: ProviderFormDefinition;
}) {
    return (
        <div className="space-y-8">
            <div className="rounded-2xl border border-blue-200 bg-blue-50 p-6">
                <div className="text-lg font-semibold text-slate-900">
                    {definition.title}
                </div>

                <p className="mt-2 max-w-4xl leading-7 text-slate-600">
                    {definition.description}
                </p>
            </div>

            {definition.fields.length > 0 ? (
                <div className="grid gap-6 lg:grid-cols-2">
                    {definition.fields.map((field) => (
                        <Field
                            key={field.name}
                            definition={field}
                            value={values[field.name] ?? ""}
                            onChange={(value) =>
                                onChange({
                                    ...values,
                                    [field.name]: value,
                                })
                            }
                        />
                    ))}
                </div>
            ) : (
                definition.emptyState ?? null
            )}
        </div>
    );
}
