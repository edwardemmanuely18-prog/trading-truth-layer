import type {
    ProviderFormDefinition,
    ProviderFormProps,
} from "../types";
import motiveWaveFormDefinition from "./providers/MotiveWaveForm";
import metaTrader5FormDefinition from "./providers/MetaTrader5Form";
import metaTrader4FormDefinition from "./providers/MetaTrader4Form";
import interactiveBrokersFormDefinition from "./providers/InteractiveBrokersForm";
import cTraderFormDefinition from "./providers/CTraderForm";
import ninjaTraderFormDefinition from "./providers/NinjaTraderForm";
import tradeStationFormDefinition from "./providers/TradeStationForm";
import sierraChartFormDefinition from "./providers/SierraChartForm";
import quantowerFormDefinition from "./providers/QuantowerForm";
import multiChartsFormDefinition from "./providers/MultiChartsForm";
import tradingTechnologiesFormDefinition from "./providers/TradingTechnologiesForm";
import ProviderConnectionForm from "../ProviderConnectionForm";

const DEFINITIONS: ProviderFormDefinition[] = [
    metaTrader5FormDefinition,
    metaTrader4FormDefinition,
    interactiveBrokersFormDefinition,
    cTraderFormDefinition,
    ninjaTraderFormDefinition,
    tradeStationFormDefinition,
    sierraChartFormDefinition,
    quantowerFormDefinition,
    multiChartsFormDefinition,
    motiveWaveFormDefinition,
    tradingTechnologiesFormDefinition,
];

export function getDesktopProviderFormDefinition(
    provider: string,
): ProviderFormDefinition {
    const key = provider.trim().toLowerCase();

    return (
        DEFINITIONS.find(
            (definition) =>
                definition.provider.toLowerCase() === key,
        ) ??
        {
            provider,
            engine: "desktop_engine",
            title: `${provider} Connection`,
            description:
                "This desktop provider is registered in the Desktop Trading Engine, but its provider-specific credential contract has not yet been explicitly defined in the frontend form registry.",
            fields: [],
            emptyState: (
                <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-sm leading-6 text-amber-800">
                    Provider-specific configuration is pending for this adapter.
                    The shared connection workflow remains available without
                    introducing provider logic into the shared page.
                </div>
            ),
        }
    );
}

export function DesktopEngineProviderForm(
    props: ProviderFormProps,
) {
    const definition =
        getDesktopProviderFormDefinition(
            props.provider,
        );

    return (
        <ProviderConnectionForm
            {...props}
            definition={definition}
        />
    );
}

export default DesktopEngineProviderForm;
