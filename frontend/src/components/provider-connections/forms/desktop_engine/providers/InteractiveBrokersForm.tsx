import type { ProviderFormDefinition } from "../../types";

export const interactiveBrokersFormDefinition: ProviderFormDefinition = {
    provider: "Interactive Brokers",
    engine: "desktop_engine",
    title: "Interactive Brokers TWS / Gateway",
    description:
        "Configure the local TWS or IB Gateway connection used by the Desktop Trading Engine.",
    fields: [
        {
            name: "host",
            label: "Gateway Host",
            defaultValue: "127.0.0.1",
            required: true,
        },
        {
            name: "port",
            label: "Gateway Port",
            type: "number",
            defaultValue: "7497",
            required: true,
        },
        {
            name: "client_id",
            label: "Client ID",
            type: "number",
            defaultValue: "1",
            required: true,
        },
        {
            name: "account_id",
            label: "Account ID",
            placeholder: "Optional / auto-discovered",
        },
        {
            name: "gateway_mode",
            label: "Gateway Mode",
            type: "select",
            defaultValue: "paper",
            options: [
                { label: "Paper", value: "paper" },
                { label: "Live", value: "live" },
            ],
        },
        {
            name: "read_only",
            label: "Read Only",
            type: "select",
            defaultValue: "false",
            options: [
                { label: "Disabled", value: "false" },
                { label: "Enabled", value: "true" },
            ],
        },
    ],
};

export default interactiveBrokersFormDefinition;
