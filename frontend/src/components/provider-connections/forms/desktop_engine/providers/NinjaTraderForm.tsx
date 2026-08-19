import type { ProviderFormDefinition } from "../../types";

export const ninjaTraderFormDefinition: ProviderFormDefinition = {
    provider: "NinjaTrader",
    engine: "desktop_engine",
    title: "NinjaTrader Desktop Connection",
    description:
        "Configure the provider-specific desktop bridge/session required by the NinjaTrader adapter.",
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

export default ninjaTraderFormDefinition;
