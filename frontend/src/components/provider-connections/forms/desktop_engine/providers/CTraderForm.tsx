import type { ProviderFormDefinition } from "../../types";

export const cTraderFormDefinition: ProviderFormDefinition = {
    provider: "cTrader",
    engine: "desktop_engine",

    title: "cTrader Connection",

    description:
        "Authorize a cTrader demo or live trading account for Trading Truth Layer evidence acquisition. TTL manages the cTrader application credentials and uses your authorization token to access the account.",

    fields: [
        {
            name: "access_token",
            label: "Access Token",
            type: "password",
            placeholder: "Paste your cTrader access token",
            required: true,
            description:
                "Enter the cTrader access token issued for the Trading Truth Layer integration.",
        },

        {
            name: "account_id",
            label: "Account ID",
            placeholder: "Optional / auto-discovered",
            description:
                "Leave blank to automatically discover the authorized cTrader trading account.",
        },
    ],
};

export default cTraderFormDefinition;