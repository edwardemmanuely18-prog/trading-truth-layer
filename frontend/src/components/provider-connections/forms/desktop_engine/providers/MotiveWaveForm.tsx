import type {
    ProviderFormDefinition,
} from "../../types";

export const motiveWaveFormDefinition: ProviderFormDefinition = {
    provider: "MotiveWave",
    engine: "desktop_engine",

    title: "MotiveWave Desktop Bridge",

    description:
        "Connect TTL to MotiveWave through the native Desktop Trading Engine bridge. TTL automatically selects the appropriate bridge endpoint and discovers the connected terminal, broker and account context.",

    fields: [
        {
            name: "connection_mode",

            label: "Connection Mode",

            type: "select",

            defaultValue: "local",

            options: [
                {
                    label: "Local Desktop Bridge — Development",
                    value: "local",
                },
                {
                    label: "TTL Cloud Rendezvous — Production",
                    value: "remote",
                },
            ],

            required: true,

            description:
                "Use Local when MotiveWave is running with the TTL bridge on this machine. Use TTL Cloud Rendezvous for a client installation that connects outward to the TTL production infrastructure.",
        },

        {
            name: "pairing_token",

            label: "Rendezvous Pairing Token",

            type: "password",

            placeholder:
                "Only required when provided by TTL",

            required: false,

            description:
                "Required only when TTL has issued a pairing token for authenticated cloud rendezvous. Leave blank for normal local development.",
        },
    ],
};

export default motiveWaveFormDefinition;