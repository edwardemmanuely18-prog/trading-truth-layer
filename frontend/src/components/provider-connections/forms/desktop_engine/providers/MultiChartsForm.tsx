import type { ProviderFormDefinition } from "../../types";

export const multiChartsFormDefinition: ProviderFormDefinition = {
    provider: "MultiCharts",
    engine: "desktop_engine",
    title: "MultiCharts Desktop Connection",
    description:
        "Configure the provider-specific MultiCharts bridge/session used by the adapter.",
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

export default multiChartsFormDefinition;
