import type { ProviderFormDefinition } from "../../types";

export const quantowerFormDefinition: ProviderFormDefinition = {
    provider: "Quantower",
    engine: "desktop_engine",
    title: "Quantower Desktop Connection",
    description:
        "Configure the provider-specific Quantower bridge/session used by the adapter.",
    fields: [
        {
            name: "bridge_endpoint",
            label: "Bridge Endpoint",
            placeholder: "Provider-specific endpoint",
        },
        {
            name: "account_id",
            label: "Account ID",
            placeholder: "Optional / auto-discovered",
        },
    ],
};

export default quantowerFormDefinition;
