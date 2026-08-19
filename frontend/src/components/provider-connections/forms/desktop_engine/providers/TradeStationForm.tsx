import type { ProviderFormDefinition } from "../../types";

export const tradeStationFormDefinition: ProviderFormDefinition = {
    provider: "TradeStation",
    engine: "desktop_engine",
    title: "TradeStation Connection",
    description:
        "Configure the provider-specific TradeStation authentication and account context required by the active adapter.",
    fields: [
        {
            name: "client_id",
            label: "Client ID",
            placeholder: "Application client ID",
            required: true,
        },
        {
            name: "client_secret",
            label: "Client Secret",
            type: "password",
            placeholder: "â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢",
        },
        {
            name: "access_token",
            label: "Access Token",
            type: "password",
            placeholder: "Optional / integration managed",
        },
        {
            name: "account_id",
            label: "Account ID",
            placeholder: "Optional / auto-discovered",
        },
    ],
};

export default tradeStationFormDefinition;
