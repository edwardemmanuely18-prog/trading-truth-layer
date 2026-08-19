import type { ProviderFormDefinition } from "../../types";

export const tradingTechnologiesFormDefinition: ProviderFormDefinition = {
    provider: "Trading Technologies",
    engine: "desktop_engine",
    title: "Trading Technologies Connection",
    description:
        "Configure the provider-specific Trading Technologies authentication and account context required by the adapter.",
    fields: [
        {
            name: "api_key",
            label: "API Key",
            type: "password",
            placeholder: "Provider API key",
        },
        {
            name: "api_secret",
            label: "API Secret",
            type: "password",
            placeholder: "â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢",
        },
        {
            name: "account_id",
            label: "Account ID",
            placeholder: "Optional / auto-discovered",
        },
    ],
};

export default tradingTechnologiesFormDefinition;
