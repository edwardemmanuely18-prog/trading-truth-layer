import type { ReactNode } from "react";

export type ProviderEngine =
    | "desktop_engine"
    | "gateway"
    | "financial";

export type ProviderFormValues = Record<string, string>;

export type ProviderFieldType =
    | "text"
    | "password"
    | "number"
    | "url"
    | "select";

export type ProviderFieldOption = {
    label: string;
    value: string;
};

export type ProviderFieldDefinition = {
    name: string;
    label: string;
    type?: ProviderFieldType;
    placeholder?: string;
    description?: string;
    required?: boolean;
    defaultValue?: string;
    options?: ProviderFieldOption[];
};

export type ProviderFormDefinition = {
    provider: string;
    engine: ProviderEngine;
    title: string;
    description: string;
    fields: ProviderFieldDefinition[];
    emptyState?: ReactNode;
};

export type ProviderFormProps = {
    provider: string;
    values: ProviderFormValues;
    onChange: (values: ProviderFormValues) => void;
};
