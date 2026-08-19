import type { ProviderFormDefinition } from "../../types";

export const sierraChartFormDefinition: ProviderFormDefinition = {
    provider: "Sierra Chart",
    engine: "desktop_engine",
    title: "Sierra Chart Desktop Connection",
    description:
        "Configure the provider-specific Sierra Chart bridge/session used by the adapter.",
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

export default sierraChartFormDefinition;
