import type { ProviderFormDefinition } from "../../types";

export const metaTrader5FormDefinition: ProviderFormDefinition = {
    provider: "MetaTrader 5",
    engine: "desktop_engine",
    title: "MetaTrader 5 Connection",
    description:
        "Provide the credentials required by the MetaTrader 5 desktop integration. Terminal discovery remains part of the shared Desktop Trading Engine workflow.",
    fields: [
        {
            name: "account",
            label: "Account / Login ID",
            placeholder: "Example: 108357802",
            required: true,
        },
        {
            name: "password",
            label: "Password",
            type: "password",
            placeholder: "â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢",
            required: true,
        },
        {
            name: "server",
            label: "Trading Server",
            placeholder: "MetaQuotes-Demo",
            required: true,
        },
        {
            name: "terminal_path",
            label: "Terminal Executable",
            placeholder:
                "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            description:
                "Optional when automatic terminal discovery is available.",
        },
    ],
};

export default metaTrader5FormDefinition;
