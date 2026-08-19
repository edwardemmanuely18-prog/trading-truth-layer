import type {
    ProviderEngine,
    ProviderFormDefinition,
    ProviderFormProps,
} from "./types";
import { getDesktopProviderFormDefinition } from "./desktop_engine/DesktopEngineProviderForm";

export function normalizeProviderKey(
    provider: string,
): string {
    return provider
        .trim()
        .toLowerCase();
}

export function getProviderEngine(
    provider: string,
): ProviderEngine {
    const key = normalizeProviderKey(provider);

    // Current active provider catalogue places the registered providers
    // below under the Desktop Trading Engine.
    const desktopProviders = new Set([
        "metatrader 5",
        "mt5",
        "metatrader 4",
        "mt4",
        "interactive brokers",
        "ibkr",
        "ctrader",
        "ninjatrader",
        "tradestation",
        "sierra chart",
        "quantower",
        "multicharts",
        "motivewave",
        "trading technologies",
        "tt",
    ]);

    if (desktopProviders.has(key)) {
        return "desktop_engine";
    }

    // No Gateway or Financial providers are currently registered.
    return "desktop_engine";
}

export function getProviderFormDefinition(
    provider: string,
    engine: ProviderEngine = getProviderEngine(provider),
): ProviderFormDefinition {
    switch (engine) {
        case "desktop_engine":
            return getDesktopProviderFormDefinition(provider);

        case "gateway":
            return {
                provider,
                engine,
                title: `${provider} Gateway Configuration`,
                description:
                    "No provider-specific Gateway form is registered yet.",
                fields: [],
            };

        case "financial":
            return {
                provider,
                engine,
                title: `${provider} Financial Configuration`,
                description:
                    "No provider-specific Financial form is registered yet.",
                fields: [],
            };
    }
}

export function getInitialProviderFormValues(
    provider: string,
    engine: ProviderEngine = getProviderEngine(provider),
): Record<string, string> {
    const definition =
        getProviderFormDefinition(
            provider,
            engine,
        );

    return Object.fromEntries(
        definition.fields.map(
            (field) => [
                field.name,
                field.defaultValue ?? "",
            ],
        ),
    );
}

export function validateProviderConfiguration(
    provider: string,
    values: Record<string, string>,
    engine: ProviderEngine = getProviderEngine(provider),
): string | null {
    const definition =
        getProviderFormDefinition(
            provider,
            engine,
        );

    for (const field of definition.fields) {
        if (
            field.required &&
            !(values[field.name] ?? "").trim()
        ) {
            return `${field.label} is required.`;
        }
    }

    if (
        normalizeProviderKey(provider) ===
        normalizeProviderKey("MotiveWave")
    ) {
        const connectionMode =
            (values["connection_mode"] ?? "")
                .trim()
                .toLowerCase();

        if (
            connectionMode === "local" &&
            !(values["bridge_endpoint"] ?? "").trim()
        ) {
            return "Bridge Endpoint is required for Local Desktop Bridge mode.";
        }
    }

    return null;
}

// Keep ProviderFormProps imported in this module so future registrars can
// extend this contract without changing the shared page.
export type { ProviderFormProps };
