"use client";

import { useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Navbar from "../../../../../../components/Navbar";

import ConnectionProgressDialog
from "../../../../../../components/provider-connections/ConnectionProgressDialog";

import { ProviderConnectionForm,
    getInitialProviderFormValues,
    getProviderFormDefinition,
    validateProviderConfiguration,
    type ProviderFormValues,
} from "../../../../../../components/provider-connections/forms";
import {
    testDesktopConnection,
    createDesktopConnection,
} from "../../../../../../lib/api";

type Environment = "demo" | "live";

type SynchronizationMode =
    | "manual"
    | "automatic"
    | "scheduled";

type InitialSynchronization =
    | "historical"
    | "historical_only"
    | "live_only";

type SynchronizationFrequency =
    | "5"
    | "15"
    | "30"
    | "60"
    | "daily";

type SynchronizationProfile =
    | "complete_verification"
    | "performance_analytics"
    | "risk_monitoring"
    | "custom";

type EvidenceCategory =
    | "trades"
    | "orders"
    | "deals"
    | "positions"
    | "account"
    | "balance"
    | "equity"
    | "margin"
    | "buying_power"
    | "broker"
    | "server"
    | "terminal"
    | "user"
    | "symbols"
    | "prices"
    | "activity"
    | "history";


export default function DesktopProviderConnectionPage() {

    const searchParams = useSearchParams();

    const router = useRouter();

    const params = useParams();

    const workspaceId = Number(params.workspaceId);

    const provider =
        searchParams.get("provider")?.trim() ?? "";

    // ============================================================
    // Desktop Connection Configuration
    // ============================================================

    type VerificationConfiguration = {
        validateProviderCredentials: boolean;
        verifyProviderIdentity: boolean;
        verifyTradingAccount: boolean;
        validateServerIdentity: boolean;
        verifyEvidenceTranslation: boolean;
    };

    type SecurityConfiguration = {
        encryptedCredentialStorage: boolean;
        secureConnectorSession: boolean;
        enableRuntimeHealthMonitoring: boolean;
        publishVerificationEvents: boolean;
        requireSuccessfulVerification: boolean;
    };

    type SynchronizationConfiguration = {
        mode: SynchronizationMode;
        frequency: SynchronizationFrequency;
        initialSynchronization: InitialSynchronization;
        incrementalSynchronization: boolean;
        automaticRetry: boolean;
        healthMonitoring: boolean;
        publishEvidenceAutomatically: boolean;
        notifyVerificationRuntime: boolean;
    };

    type DesktopConnectionConfiguration = {
        connectionName: string;
        description: string;
        environment: Environment;

        synchronizationProfile: SynchronizationProfile;

        evidenceCategories: EvidenceCategory[];

        synchronization: SynchronizationConfiguration;

        verification: VerificationConfiguration;

        security: SecurityConfiguration;
    };

    const DEFAULT_CONNECTION_CONFIGURATION: DesktopConnectionConfiguration = {
        connectionName: "",
        description: "",
        environment: "demo",

        synchronizationProfile: "complete_verification",

        evidenceCategories: [
            "trades",
            "orders",
            "deals",
            "positions",
            "account",
            "balance",
            "equity",
            "margin",
            "buying_power",
            "broker",
            "server",
            "terminal",
            "user",
            "symbols",
            "prices",
            "activity",
            "history",
        ],

        synchronization: {
            mode: "manual",
            frequency: "15",
            initialSynchronization: "historical",
            incrementalSynchronization: true,
            automaticRetry: true,
            healthMonitoring: true,
            publishEvidenceAutomatically: true,
            notifyVerificationRuntime: true,
        },

        verification: {
            validateProviderCredentials: true,
            verifyProviderIdentity: true,
            verifyTradingAccount: true,
            validateServerIdentity: true,
            verifyEvidenceTranslation: true,
        },

        security: {
            encryptedCredentialStorage: true,
            secureConnectorSession: true,
            enableRuntimeHealthMonitoring: true,
            publishVerificationEvents: true,
            requireSuccessfulVerification: true,
        },
    };

    const [configuration, setConfiguration] =
        useState<DesktopConnectionConfiguration>(
            DEFAULT_CONNECTION_CONFIGURATION,
        );

    // ============================================================
    // Provider Credentials
    // ============================================================

    const DEFAULT_CREDENTIALS: ProviderFormValues =
        getInitialProviderFormValues(provider);

    const [credentials, setCredentials] =
        useState<ProviderFormValues>(DEFAULT_CREDENTIALS);

    // ============================================================
    // Runtime UI State
    // ============================================================

    type ConnectionWorkflowState =
        | "idle"
        | "testing"
        | "test_success"
        | "test_failed"
        | "creating"
        | "created"
        | "create_failed";

    const [progressOpen, setProgressOpen] = useState(false);

    const [creating, setCreating] = useState(false);

    const [submitting, setSubmitting] = useState(false);

    const [workflowState, setWorkflowState] =
        useState<ConnectionWorkflowState>("idle");

    const [testResponse, setTestResponse] =
        useState<
            Awaited<ReturnType<typeof testDesktopConnection>> | null
        >(null);

    // ============================================================
    // UI Action Feedback
    // ============================================================

    type ActionFeedbackState = "idle" | "working" | "success" | "error";

    const [actionFeedback, setActionFeedback] = useState<{
        state: ActionFeedbackState;
        message: string;
    }>({
        state: "idle",
        message: "",
    });

    function showActionFeedback(
        state: ActionFeedbackState,
        message: string,
    ) {
        setActionFeedback({
            state,
            message,
        });
    }

    function validateSelectedProvider(): boolean {
        if (!provider) {
            showActionFeedback(
                "error",
                "No desktop provider was selected. Return to Provider Connections and select a supported provider.",
            );

            return false;
        }

        return true;
    }


    function toggleEvidenceCategory(
        category: EvidenceCategory,
    ) {
        setConfiguration((previous) => {
            const exists =
                previous.evidenceCategories.includes(category);

            return {
                ...previous,
                evidenceCategories: exists
                    ? previous.evidenceCategories.filter(
                        (item) => item !== category,
                    )
                    : [
                        ...previous.evidenceCategories,
                        category,
                    ],
            };
        });

        showActionFeedback(
            "success",
            `${category.replaceAll("_", " ")} evidence ${
                configuration.evidenceCategories.includes(category)
                    ? "disabled"
                    : "enabled"
            }.`,
        );
    }

    function handleSelectAllEvidence() {
        const allSelected =
            configuration.evidenceCategories.length ===
            ALL_EVIDENCE_CATEGORIES.length;

        updateConfiguration({
            evidenceCategories: allSelected
                ? []
                : [...ALL_EVIDENCE_CATEGORIES],
        });

        showActionFeedback(
            "success",
            allSelected
                ? "All evidence categories cleared."
                : "All evidence categories selected.",
        );
    }

    // ============================================================
    // Configuration Helpers
    // ============================================================

    function updateConfiguration(
        updates: Partial<DesktopConnectionConfiguration>,
    ) {
        setConfiguration((previous) => ({
            ...previous,
            ...updates,
        }));
    }

    function updateSynchronization(
        updates: Partial<SynchronizationConfiguration>,
    ) {
        setConfiguration((previous) => ({
            ...previous,
            synchronization: {
                ...previous.synchronization,
                ...updates,
            },
        }));
    }

    function updateVerification(
        updates: Partial<VerificationConfiguration>,
    ) {
        setConfiguration((previous) => ({
            ...previous,
            verification: {
                ...previous.verification,
                ...updates,
            },
        }));
    }

    function updateSecurity(
        updates: Partial<SecurityConfiguration>,
    ) {
        setConfiguration((previous) => ({
            ...previous,
            security: {
                ...previous.security,
                ...updates,
            },
        }));
    }

    const ALL_EVIDENCE_CATEGORIES: EvidenceCategory[] = [
        "trades",
        "orders",
        "deals",
        "positions",

        "account",
        "balance",
        "equity",
        "margin",
        "buying_power",

        "broker",
        "server",
        "terminal",
        "user",

        "symbols",
        "prices",
        "activity",
        "history",
    ];

    function formatSynchronizationMode(
        mode: SynchronizationMode,
    ): string {
        switch (mode) {
            case "manual":
                return "Manual";

            case "automatic":
                return "Automatic";

            case "scheduled":
                return "Scheduled";

            default:
                return mode;
        }
    }

    function formatEnvironment(
        environment: Environment,
    ): string {
        switch (environment) {
            case "demo":
                return "Demo";

            case "live":
                return "Live";

            default:
                return environment;
        }
    }

    function formatInitialSynchronization(
        mode: InitialSynchronization,
    ): string {
        switch (mode) {
            case "historical":
                return "Historical + Live";

            case "historical_only":
                return "Historical Only";

            case "live_only":
                return "Live Only";

            default:
                return mode;
        }
    }

    function formatBoolean(
        value: boolean,
    ): string {
        return value ? "Enabled" : "Disabled";
    }

    function formatProfile(
        profile: SynchronizationProfile,
    ): string {
        switch (profile) {
            case "complete_verification":
                return "Complete Verification";

            case "performance_analytics":
                return "Performance Analytics";

            case "risk_monitoring":
                return "Risk Monitoring";

            case "custom":
                return "Custom Profile";

            default:
                return profile;
        }
    }

    const EVIDENCE_GROUPS = [
        {
            title: "Trading Evidence",
            items: [
                { label: "Trades", value: "trades" },
                { label: "Orders", value: "orders" },
                { label: "Deals", value: "deals" },
                { label: "Positions", value: "positions" },
            ],
        },
        {
            title: "Account Evidence",
            items: [
                { label: "Account", value: "account" },
                { label: "Balance", value: "balance" },
                { label: "Equity", value: "equity" },
                { label: "Margin", value: "margin" },
                { label: "Buying Power", value: "buying_power" },
            ],
        },
        {
            title: "Infrastructure",
            items: [
                { label: "Broker", value: "broker" },
                { label: "Server", value: "server" },
                { label: "Terminal", value: "terminal" },
                { label: "User", value: "user" },
            ],
        },
        {
            title: "Market Evidence",
            items: [
                { label: "Symbols", value: "symbols" },
                { label: "Prices", value: "prices" },
                { label: "Activity", value: "activity" },
                { label: "History", value: "history" },
            ],
        },
    ] satisfies {
        title: string;
        items: {
            label: string;
            value: EvidenceCategory;
        }[];
    }[];

    const SYNCHRONIZATION_PROFILES = [
        {
            value: "complete_verification" as const,
            title: "Complete Verification",
            description:
                "Acquire every canonical evidence category required for institutional verification and due diligence.",
            recommended: true,
        },
        {
            value: "performance_analytics" as const,
            title: "Performance Analytics",
            description:
                "Synchronize only trading performance, executions and portfolio analytics.",
            recommended: false,
        },
        {
            value: "risk_monitoring" as const,
            title: "Risk Monitoring",
            description:
                "Synchronize balances, equity, margin, buying power and exposure metrics.",
            recommended: false,
        },
        {
            value: "custom" as const,
            title: "Custom Profile",
            description:
                "Use the manually selected evidence categories from the previous section.",
            recommended: false,
        },
    ];

    function formatDiscoveryValue(
        value: string | null | undefined,
    ): string {
        if (value === null || value === undefined || value.trim() === "") {
            return "Not reported";
        }

        return value;
    }

    function resetForm() {
        setConfiguration({
            ...DEFAULT_CONNECTION_CONFIGURATION,
            synchronization: {
                ...DEFAULT_CONNECTION_CONFIGURATION.synchronization,
            },
            verification: {
                ...DEFAULT_CONNECTION_CONFIGURATION.verification,
            },
            security: {
                ...DEFAULT_CONNECTION_CONFIGURATION.security,
            },
            evidenceCategories: [
                ...DEFAULT_CONNECTION_CONFIGURATION.evidenceCategories,
            ],
        });

        setCredentials({
            ...DEFAULT_CREDENTIALS,
        });

        setProgressOpen(false);
        setCreating(false);
        setSubmitting(false);
        setWorkflowState("idle");
        setTestResponse(null);

        setActionFeedback({
            state: "idle",
            message: "",
        });
    }

    function getEnvironmentLabel(
        environment: Environment,
    ): string {
        return environment === "demo"
            ? "Demo"
            : "Live";
    }

    function getSynchronizationModeLabel(
        mode: SynchronizationMode,
    ): string {
        switch (mode) {
            case "automatic":
                return "Automatic";

            case "scheduled":
                return "Scheduled";

            case "manual":
            default:
                return "Manual";
        }
    }

    function getConnectionStatusLabel(): string {
        switch (workflowState) {
            case "testing":
                return "Testing";

            case "test_success":
                return "Test Successful";

            case "test_failed":
                return "Test Failed";

            case "creating":
                return "Creating";

            case "created":
                return "Created";

            case "create_failed":
                return "Creation Failed";

            case "idle":
            default:
                return "Not Tested";
        }
    }

    const progressSteps: {
        title: string;
        status: "pending" | "running" | "completed" | "failed";
    }[] = [
        {
            title: "Submit Connection Request",
            status:
                workflowState === "creating"
                    ? "running"
                    : workflowState === "created"
                        ? "completed"
                        : workflowState === "create_failed"
                            ? "failed"
                            : "pending",
        },
        {
            title: "Backend Processing",
            status:
                workflowState === "creating"
                    ? "pending"
                    : workflowState === "created"
                        ? "pending"
                        : workflowState === "create_failed"
                            ? "pending"
                            : "pending",
        },
        {
            title: "Receive Backend Response",
            status:
                workflowState === "created"
                    ? "completed"
                    : workflowState === "create_failed"
                        ? "failed"
                        : "pending",
        },
    ];

    async function handleTestConnection() {
        try {
            if (!validateSelectedProvider()) {
                return;
            }

            if (!configuration.connectionName.trim()) {
                showActionFeedback(
                    "error",
                    "Connection name is required before testing the provider connection.",
                );
                return;
            }

            const providerValidationError =
                validateProviderConfiguration(
                    provider,
                    credentials,
                );

            if (providerValidationError) {
                showActionFeedback(
                    "error",
                    providerValidationError,
                );
                return;
            }

            setTestResponse(null);

            setSubmitting(true);
            setWorkflowState("testing");

            showActionFeedback(
                "working",
                "Testing provider connection...",
            );

            const response = await testDesktopConnection(
                workspaceId,
                {
                    provider,
                    connection_name:
                        configuration.connectionName,
                    environment:
                        configuration.environment,
                    synchronization_profile:
                        configuration.synchronizationProfile,
                    evidence_categories:
                        configuration.evidenceCategories,
                    credentials,
                },
            );

            console.log(
                "Desktop provider connection test response:",
                response,
            );

            if (!response.success) {
                setTestResponse(response);               
                setWorkflowState("test_failed");

                showActionFeedback(
                    "error",
                    response.message ||
                        "Provider connection test failed.",
                );

                return;
            }

            setTestResponse(response);
            setWorkflowState("test_success");

            const accountSummary = response.discovery.account_number
                ? ` Account ${response.discovery.account_number} authenticated successfully.`
                : "";

            showActionFeedback(
                "success",
                `Provider connection test completed successfully.${accountSummary}`,
            );
        } catch (error) {
            console.error(
                "Desktop provider connection test failed:",
                error,
            );

            showActionFeedback(
                "error",
                error instanceof Error
                    ? error.message
                    : "Unable to test provider connection.",
            );
        } finally {
            setSubmitting(false);
        }
    }

    async function handleCreateConnection() {
        try {
            if (!validateSelectedProvider()) {
                return;
            }

            if (!configuration.connectionName.trim()) {
                showActionFeedback(
                    "error",
                    "Connection name is required before creating the provider connection.",
                );
                return;
            }

            const providerValidationError =
                validateProviderConfiguration(
                    provider,
                    credentials,
                );

            if (providerValidationError) {
                showActionFeedback(
                    "error",
                    providerValidationError,
                );
                return;
            }

            setSubmitting(true);
            setCreating(true);
            setProgressOpen(true);
            setWorkflowState("creating");

            showActionFeedback(
                "working",
                "Creating provider connection...",
            );

            const response = await createDesktopConnection(
                workspaceId,
                {
                    provider,
                    connection_name:
                        configuration.connectionName,
                    environment:
                        configuration.environment,
                    synchronization_profile:
                        configuration.synchronizationProfile,
                    evidence_categories:
                        configuration.evidenceCategories,
                    credentials,
                },
            );

            console.log(
                "Provider connection created:",
                response,
            );

            if (!response?.id) {
                setWorkflowState("create_failed");

                showActionFeedback(
                    "error",
                    "Provider connection creation returned an invalid response.",
                );

                return;
            }

            setWorkflowState("created");

            showActionFeedback(
                "success",
                `Provider connection "${response.connection_name}" created successfully.`,
            );

            setCreating(false);
            setProgressOpen(false);

            router.push(
                `/workspace/${workspaceId}/provider-connections`,
            );

        } catch (error) {
            console.error(
                "Provider connection creation failed:",
                error,
            );

            showActionFeedback(
                "error",
                error instanceof Error
                    ? error.message
                    : "Unable to create provider connection.",
            );
        } finally {
            setSubmitting(false);
            setCreating(false);
        }
    }

    function handleSaveDraft() {
        try {
            const draft = {
                provider,
                workspaceId,
                configuration,
                credentials,
            };

            localStorage.setItem(
                `ttl:provider-connection-draft:${workspaceId}:${provider}`,
                JSON.stringify(draft),
            );

            showActionFeedback(
                "success",
                "Provider connection draft saved locally.",
            );
        } catch (error) {
            console.error(error);

            showActionFeedback(
                "error",
                "Unable to save provider connection draft.",
            );
        }
    }

    return (

        <div className="min-h-screen bg-slate-50">

            <Navbar />

            <div className="mx-auto max-w-7xl px-6 py-10">

                {/* ====================================================== */}
                {/* Hero */}
                {/* ====================================================== */}

                <div className="flex flex-col gap-8 xl:flex-row xl:items-start xl:justify-between">

                    <div className="max-w-5xl">

                        <div className="text-xs uppercase tracking-[0.22em] text-slate-500">

                            DESKTOP TRADING ENGINE

                        </div>

                        <h1 className="mt-3 text-5xl font-bold tracking-tight">

                            Desktop Provider Connection

                        </h1>

                        <p className="mt-6 text-lg leading-8 text-slate-600">

                            Establish an authenticated provider connection
                            between the Trading Truth Layer Desktop Trading
                            Engine and a supported desktop trading platform.
                            The Desktop Trading Engine will authenticate the
                            selected provider, validate the connection,
                            synchronize the selected canonical evidence
                            categories and publish standardized evidence into
                            the institutional Evidence Acquisition Runtime.

                        </p>

                    </div>

                    <div className="w-full max-w-sm rounded-2xl border bg-white p-8 shadow-sm">

                        <div className="text-sm uppercase tracking-wider text-slate-500">

                            Selected Provider

                        </div>

                        <div className="mt-4 text-3xl font-bold">

                            {provider}

                        </div>

                        <div className="mt-8 space-y-4">

                            <StatusRow
                                label="Engine"
                                value="Desktop Trading Engine"
                            />

                            <StatusRow
                                label="Connection Status"
                                value={getConnectionStatusLabel()}
                            />

                            <StatusRow
                                label="Workspace"
                                value={`Workspace #${workspaceId}`}
                            />

                            <StatusRow
                                label="Runtime"
                                value={
                                    actionFeedback.state === "working"
                                        ? "Processing"
                                        : "Ready"
                                }
                            />

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Provider Summary */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Provider Summary

                            </h2>

                            <p className="mt-2 max-w-4xl text-slate-600 leading-7">

                                Institutional overview of the selected desktop trading
                                provider before creating an authenticated provider
                                connection. The Desktop Trading Engine uses this metadata
                                to construct the canonical acquisition pipeline.

                            </p>

                        </div>

                        <div className="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700">

                            SUPPORTED

                        </div>

                    </div>

                    <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">

                        <SummaryCard
                            title="Provider"
                            value={provider}
                            subtitle="Selected desktop platform"
                        />

                        <SummaryCard
                            title="Engine"
                            value="Desktop Trading Engine"
                            subtitle="Canonical acquisition engine"
                        />

                        <SummaryCard
                            title="Adapter"
                            value={`${provider} Adapter`}
                            subtitle="Universal Evidence Adapter"
                        />

                        <SummaryCard
                            title="Version"
                            value="1.0.0"
                            subtitle="Adapter release"
                        />

                        <SummaryCard
                            title="Authentication"
                            value="Supported"
                            subtitle="Credential validation"
                        />

                        <SummaryCard
                            title="Evidence Model"
                            value="Canonical"
                            subtitle="UEA Translation"
                        />

                        <SummaryCard
                            title="Synchronization"
                            value="Available"
                            subtitle="Evidence acquisition"
                        />

                        <SummaryCard
                            title="Verification"
                            value="Enabled"
                            subtitle="Institutional verification"
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Connection Details */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div>

                        <h2 className="text-3xl font-semibold">

                            Connection Details

                        </h2>

                        <p className="mt-2 max-w-4xl text-slate-600 leading-7">

                            Configure the institutional identity of this provider
                            connection. These settings identify the connection inside
                            the Trading Truth Layer Evidence Acquisition Runtime and are
                            stored independently from provider credentials.

                        </p>

                    </div>

                    <div className="mt-10 grid gap-8 lg:grid-cols-2">

                        {/* -------------------------------------------------- */}
                        {/* Left */}
                        {/* -------------------------------------------------- */}

                        <div className="space-y-6">

                            <div>

                                <label className="mb-2 block text-sm font-semibold">

                                    Connection Name

                                </label>

                                <input
                                    type="text"
                                    placeholder="Example: MT5 Primary Demo"
                                    value={configuration.connectionName}
                                    onChange={(event) =>
                                        updateConfiguration({
                                            connectionName: event.target.value,
                                        })
                                    }
                                    className="w-full rounded-xl border px-4 py-3 outline-none focus:border-slate-900"
                                />

                            </div>

                            <div>

                                <label className="mb-2 block text-sm font-semibold">

                                    Description

                                </label>

                                <textarea
                                    rows={4}
                                    placeholder="Optional description for this provider connection."
                                    value={configuration.description}
                                    onChange={(event) =>
                                        updateConfiguration({
                                            description: event.target.value,
                                        })
                                    }
                                    className="w-full rounded-xl border px-4 py-3 outline-none focus:border-slate-900"
                                />

                            </div>

                            <div>

                                <label className="mb-2 block text-sm font-semibold">

                                    Workspace

                                </label>

                                <input
                                    type="text"
                                    value={`Workspace #${workspaceId}`}
                                    readOnly
                                    className="w-full rounded-xl border bg-slate-100 px-4 py-3"
                                />

                            </div>

                        </div>

                        {/* -------------------------------------------------- */}
                        {/* Right */}
                        {/* -------------------------------------------------- */}

                        <div className="space-y-8">

                            <div>

                                <label className="mb-4 block text-sm font-semibold">

                                    Trading Environment

                                </label>

                                <div className="grid grid-cols-2 gap-4">

                                    <label className="cursor-pointer rounded-xl border p-5 hover:border-slate-900">
                                        <input
                                            type="radio"
                                            name="environment"
                                            value="demo"
                                            checked={configuration.environment === "demo"}
                                            onChange={() =>
                                                updateConfiguration({
                                                    environment: "demo",
                                                })
                                            }
                                            className="mr-3"
                                        />

                                        <span className="font-semibold">
                                            Demo
                                        </span>

                                        <div className="mt-2 text-sm text-slate-500">
                                            Connect to a simulated trading account.
                                        </div>
                                    </label>

                                    <label className="cursor-pointer rounded-xl border p-5 hover:border-slate-900">
                                        <input
                                            type="radio"
                                            name="environment"
                                            value="live"
                                            checked={configuration.environment === "live"}
                                            onChange={() =>
                                                updateConfiguration({
                                                    environment: "live",
                                                })
                                            }
                                            className="mr-3"
                                        />

                                        <span className="font-semibold">
                                            Live
                                        </span>

                                        <div className="mt-2 text-sm text-slate-500">
                                            Connect to a production trading account.
                                        </div>
                                    </label>

                                </div>

                            </div>

                            <div>

                                <label className="mb-4 block text-sm font-semibold">

                                    Synchronization Mode

                                </label>

                                <select
                                    value={configuration.synchronization.mode}
                                    onChange={(event) =>
                                        updateSynchronization({
                                            mode: event.target.value as SynchronizationMode,
                                        })
                                    }
                                    className="w-full rounded-xl border px-4 py-3"
                                >
                                    <option value="manual">
                                        Manual
                                    </option>

                                    <option value="automatic">
                                        Automatic
                                    </option>

                                    <option value="scheduled">
                                        Scheduled
                                    </option>
                                </select>

                            </div>

                            <div className="rounded-xl border bg-slate-50 p-5">

                                <div className="text-lg font-semibold">

                                    Connection Preview

                                </div>

                                <div className="mt-4 space-y-3 text-sm">

                                    <PreviewRow
                                        label="Provider"
                                        value={provider}
                                    />

                                    <PreviewRow
                                        label="Engine"
                                        value="Desktop Trading Engine"
                                    />

                                    <PreviewRow
                                        label="Environment"
                                        value={getEnvironmentLabel(
                                            configuration.environment,
                                        )}
                                    />

                                    <PreviewRow
                                        label="Synchronization"
                                        value={getSynchronizationModeLabel(
                                            configuration.synchronization.mode,
                                        )}
                                    />

                                    <PreviewRow
                                        label="Status"
                                        value={getConnectionStatusLabel()}
                                    />

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Provider Credentials */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Provider Credentials

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Enter only the credentials required to authenticate with the
                                selected trading platform.

                                After successful authentication the Desktop Trading Engine
                                automatically discovers the installed trading terminal,
                                broker identity, server, account information, platform
                                capabilities and runtime metadata.

                                No manual platform configuration is required.

                            </p>

                        </div>

                        <div className="rounded-full bg-amber-100 px-4 py-2 text-sm font-semibold text-amber-700">

                            {provider}

                        </div>

                    </div>

                    <div className="mt-10">

                        <ProviderConnectionForm
                            provider={provider}
                            values={credentials}
                            onChange={setCredentials}
                            definition={{
                                ...getProviderFormDefinition(provider),
                            }}
                        />

                    </div>

                    <div className="mt-10 rounded-2xl border bg-slate-50 p-8">

                        <div className="flex items-center justify-between">

                            <div>

                                <h3 className="text-2xl font-semibold">
                                    Automatic Provider Discovery
                                </h3>

                                <p className="mt-2 text-slate-600 leading-7">

                                    During Test Connection the Desktop Trading Engine will
                                    automatically discover terminal metadata, broker
                                    metadata and account information. These values become
                                    the canonical provider identity stored by Trading Truth
                                    Layer.

                                </p>

                            </div>

                            <div className="rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-700">

                                Auto Discovery

                            </div>

                        </div>

                        <div className="mt-8 grid gap-6 lg:grid-cols-2 xl:grid-cols-3">

                            <DiscoveryRow
                                label="Provider"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.provider,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Provider Registration"
                                value={
                                    testResponse
                                        ? testResponse.discovery.provider_registered
                                            ? "Registered"
                                            : "Not Registered"
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Engine Version"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.engine_version,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Terminal Company"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.terminal_company,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Terminal Version"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.terminal_version,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Terminal Build"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.terminal_build,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Terminal Architecture"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.terminal_architecture,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Terminal Path"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.terminal_path,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Broker Company"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.broker_name,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Broker Server"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.server,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Trading Account"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.discovery.account_number,
                                        )
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Evidence Capabilities"
                                value={
                                    testResponse
                                        ? testResponse.discovery.supported_evidence.length > 0
                                            ? testResponse.discovery.supported_evidence.join(", ")
                                            : "None reported"
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Engine Status"
                                value={
                                    testResponse
                                        ? testResponse.discovery.engine_running
                                            ? "Running"
                                            : "Stopped"
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Engine Health"
                                value={
                                    testResponse
                                        ? testResponse.discovery.healthy
                                            ? "Healthy"
                                            : "Unhealthy"
                                        : "Awaiting Test Connection"
                                }
                            />

                            <DiscoveryRow
                                label="Connection Status"
                                value={
                                    testResponse
                                        ? formatDiscoveryValue(
                                            testResponse.connection.connection_status,
                                        )
                                        : getConnectionStatusLabel()
                                }
                            />

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Evidence Selection */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Evidence Selection

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Select which canonical evidence categories should be
                                synchronized from this provider. Every selected category
                                will be translated into the Trading Truth Layer
                                institutional evidence model before entering the Evidence
                                Acquisition Runtime.

                            </p>

                        </div>

                        <button
                            type="button"
                            onClick={handleSelectAllEvidence}
                            className="rounded-lg border px-5 py-2 text-sm font-medium hover:bg-slate-100"
                        >
                            {configuration.evidenceCategories.length ===
                            ALL_EVIDENCE_CATEGORIES.length
                                ? "Clear All"
                                : "Select All"}
                        </button>

                    </div>

                    <div className="mt-10 grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
                        {EVIDENCE_GROUPS.map((group) => (
                            <EvidenceGroup
                                key={group.title}
                                title={group.title}
                                items={group.items}
                                selectedCategories={
                                    configuration.evidenceCategories
                                }
                                onToggle={toggleEvidenceCategory}
                            />
                        ))}
                    </div>

                </div>

                {/* ====================================================== */}
                {/* Synchronization Profile */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Synchronization Profile

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Synchronization profiles define which canonical evidence
                                categories will be acquired and how the Desktop Trading
                                Engine should construct the synchronization pipeline for
                                this provider connection.

                            </p>

                        </div>

                    </div>

                    <div className="mt-10 grid gap-6 lg:grid-cols-2">
                        {SYNCHRONIZATION_PROFILES.map((profile) => (
                            <ProfileCard
                                key={profile.value}
                                title={profile.title}
                                description={profile.description}
                                recommended={profile.recommended}
                                selected={
                                    configuration.synchronizationProfile ===
                                    profile.value
                                }
                                onSelect={() => {
                                    updateConfiguration({
                                        synchronizationProfile:
                                            profile.value,
                                    });

                                    showActionFeedback(
                                        "success",
                                        `${profile.title} profile selected.`,
                                    );
                                }}
                            />
                        ))}
                    </div>

                </div>

                {/* ====================================================== */}
                {/* Synchronization Configuration */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Synchronization Configuration

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Configure how the Desktop Trading Engine should execute
                                evidence acquisition for this provider connection.
                                These settings control synchronization scheduling,
                                acquisition strategy and recovery behavior.

                            </p>

                        </div>

                    </div>

                    <div className="mt-10 grid gap-10 lg:grid-cols-2">

                        {/* ------------------------------------------------ */}
                        {/* Left Column                                     */}
                        {/* ------------------------------------------------ */}

                        <div className="space-y-8">

                            <div>

                                <label className="mb-3 block text-sm font-semibold">

                                    Synchronization Mode

                                </label>

                                <select
                                    value={configuration.synchronization.mode}
                                    onChange={(event) =>
                                        updateSynchronization({
                                            mode: event.target.value as SynchronizationMode,
                                        })
                                    }
                                    className="w-full rounded-xl border px-4 py-3"
                                >

                                    <option value="manual">

                                        Manual

                                    </option>

                                    <option value="automatic">

                                        Automatic

                                    </option>

                                    <option value="scheduled">

                                        Scheduled

                                    </option>

                                </select>

                            </div>

                            <div>

                                <label className="mb-3 block text-sm font-semibold">

                                    Synchronization Frequency

                                </label>

                                <select
                                    value={configuration.synchronization.frequency}
                                    onChange={(event) =>
                                        updateSynchronization({
                                            frequency:
                                                event.target.value as SynchronizationFrequency,
                                        })
                                    }
                                    className="w-full rounded-xl border px-4 py-3"
                                >
                                    <option value="5">
                                        Every 5 Minutes
                                    </option>

                                    <option value="15">
                                        Every 15 Minutes
                                    </option>

                                    <option value="30">
                                        Every 30 Minutes
                                    </option>

                                    <option value="60">
                                        Every Hour
                                    </option>

                                    <option value="daily">
                                        Daily
                                    </option>
                                </select>

                            </div>

                            <div>

                                <label className="mb-3 block text-sm font-semibold">

                                    Initial Synchronization

                                </label>

                                <select
                                    value={
                                        configuration.synchronization.initialSynchronization
                                    }
                                    onChange={(event) =>
                                        updateSynchronization({
                                            initialSynchronization:
                                                event.target.value as InitialSynchronization,
                                        })
                                    }
                                    className="w-full rounded-xl border px-4 py-3"
                                >
                                    <option value="historical">
                                        Historical + Live
                                    </option>

                                    <option value="historical_only">
                                        Historical Only
                                    </option>

                                    <option value="live_only">
                                        Live Only
                                    </option>
                                </select>

                            </div>

                        </div>

                        {/* ------------------------------------------------ */}
                        {/* Right Column                                    */}
                        {/* ------------------------------------------------ */}

                        <div className="space-y-6">

                            <ToggleRow
                                title="Incremental Synchronization"
                                description="Synchronize only newly available evidence after the initial acquisition."
                                enabled={
                                    configuration.synchronization
                                        .incrementalSynchronization
                                }
                                onChange={(enabled) =>
                                    updateSynchronization({
                                        incrementalSynchronization: enabled,
                                    })
                                }
                            />

                            <ToggleRow
                                title="Automatic Retry"
                                description="Retry failed synchronization jobs automatically."
                                enabled={
                                    configuration.synchronization.automaticRetry
                                }
                                onChange={(enabled) =>
                                    updateSynchronization({
                                        automaticRetry: enabled,
                                    })
                                }
                            />

                            <ToggleRow
                                title="Health Monitoring"
                                description="Continuously monitor provider connectivity."
                                enabled={
                                    configuration.synchronization.healthMonitoring
                                }
                                onChange={(enabled) =>
                                    updateSynchronization({
                                        healthMonitoring: enabled,
                                    })
                                }
                            />

                            <ToggleRow
                                title="Publish Evidence Automatically"
                                description="Publish validated evidence packages immediately after synchronization."
                                enabled={
                                    configuration.synchronization
                                        .publishEvidenceAutomatically
                                }
                                onChange={(enabled) =>
                                    updateSynchronization({
                                        publishEvidenceAutomatically: enabled,
                                    })
                                }
                            />

                            <ToggleRow
                                title="Notify Verification Runtime"
                                description="Automatically notify TVS after successful synchronization."
                                enabled={
                                    configuration.synchronization
                                        .notifyVerificationRuntime
                                }
                                onChange={(enabled) =>
                                    updateSynchronization({
                                        notifyVerificationRuntime: enabled,
                                    })
                                }
                            />

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Verification & Security */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Verification & Security

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Configure the institutional verification and security
                                controls that will be executed before this provider
                                connection is admitted into the Evidence Acquisition
                                Runtime. Every successful connection undergoes
                                authentication, identity validation and integrity
                                verification before synchronization begins.

                            </p>

                        </div>

                        <div className="rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-700">

                            Institutional Verification

                        </div>

                    </div>

                    <div className="mt-10 grid gap-8 lg:grid-cols-2">

                        {/* ================================================= */}
                        {/* Verification Controls                            */}
                        {/* ================================================= */}

                        <div className="space-y-5">

                            <VerificationOption
                                title="Validate Provider Credentials"
                                description="Verify that the supplied credentials are accepted by the provider."
                                enabled={
                                    configuration.verification
                                        .validateProviderCredentials
                                }
                                onChange={(enabled) =>
                                    updateVerification({
                                        validateProviderCredentials: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Verify Provider Identity"
                                description="Confirm the provider identity and supported platform."
                                enabled={
                                    configuration.verification
                                        .verifyProviderIdentity
                                }
                                onChange={(enabled) =>
                                    updateVerification({
                                        verifyProviderIdentity: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Verify Trading Account"
                                description="Confirm ownership and accessibility of the selected trading account."
                                enabled={
                                    configuration.verification
                                        .verifyTradingAccount
                                }
                                onChange={(enabled) =>
                                    updateVerification({
                                        verifyTradingAccount: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Validate Server Identity"
                                description="Verify that the connection targets the expected trading server."
                                enabled={
                                    configuration.verification
                                        .validateServerIdentity
                                }
                                onChange={(enabled) =>
                                    updateVerification({
                                        validateServerIdentity: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Verify Evidence Translation"
                                description="Execute a translation validation before evidence acquisition."
                                enabled={
                                    configuration.verification
                                        .verifyEvidenceTranslation
                                }
                                onChange={(enabled) =>
                                    updateVerification({
                                        verifyEvidenceTranslation: enabled,
                                    })
                                }
                            />

                        </div>

                        {/* ================================================= */}
                        {/* Security Controls                                */}
                        {/* ================================================= */}

                        <div className="space-y-5">

                            <VerificationOption
                                title="Encrypted Credential Storage"
                                description="Store provider credentials using institutional encryption."
                                enabled={
                                    configuration.security.encryptedCredentialStorage
                                }
                                onChange={(enabled) =>
                                    updateSecurity({
                                        encryptedCredentialStorage: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Secure Connector Session"
                                description="Require authenticated connector sessions."
                                enabled={
                                    configuration.security.secureConnectorSession
                                }
                                onChange={(enabled) =>
                                    updateSecurity({
                                        secureConnectorSession: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Enable Runtime Health Monitoring"
                                description="Continuously monitor connection integrity."
                                enabled={
                                    configuration.security
                                        .enableRuntimeHealthMonitoring
                                }
                                onChange={(enabled) =>
                                    updateSecurity({
                                        enableRuntimeHealthMonitoring: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Publish Verification Events"
                                description="Record verification events in the runtime activity log."
                                enabled={
                                    configuration.security.publishVerificationEvents
                                }
                                onChange={(enabled) =>
                                    updateSecurity({
                                        publishVerificationEvents: enabled,
                                    })
                                }
                            />

                            <VerificationOption
                                title="Require Successful Verification"
                                description="Block synchronization until every verification stage succeeds."
                                enabled={
                                    configuration.security.requireSuccessfulVerification
                                }
                                onChange={(enabled) =>
                                    updateSecurity({
                                        requireSuccessfulVerification: enabled,
                                    })
                                }
                            />

                        </div>

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Connection Review */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Connection Review

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Review the complete provider connection configuration
                                before creating the connection. This summary represents
                                the configuration that will be submitted to the Desktop
                                Trading Engine for authentication, registration,
                                synchronization and evidence acquisition.

                            </p>

                        </div>

                        <div className="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700">

                            CONFIGURATION REVIEW

                        </div>

                    </div>

                    <div className="mt-10 grid gap-6 lg:grid-cols-2 xl:grid-cols-3">

                        <ReviewCard
                            title="Provider"
                            rows={[
                                ["Provider", provider],
                                ["Engine", "Desktop Trading Engine"],
                                ["Adapter", `${provider} Adapter`],
                                ["Version", "1.0.0"],
                            ]}
                        />

                        <ReviewCard
                            title="Connection"
                            rows={[
                                [
                                    "Environment",
                                    getEnvironmentLabel(
                                        configuration.environment,
                                    ),
                                ],
                                [
                                    "Synchronization",
                                    getSynchronizationModeLabel(
                                        configuration.synchronization.mode,
                                    ),
                                ],
                                [
                                    "Workspace",
                                    `Workspace #${workspaceId}`,
                                ],
                                [
                                    "Status",
                                    getConnectionStatusLabel(),
                                ],
                            ]}
                        />

                        <ReviewCard
                            title="Evidence"
                            rows={[
                                [
                                    "Trading",
                                    formatBoolean(
                                        configuration.evidenceCategories.some(
                                            (category) =>
                                                [
                                                    "trades",
                                                    "orders",
                                                    "deals",
                                                    "positions",
                                                ].includes(category),
                                        ),
                                    ),
                                ],
                                [
                                    "Account",
                                    formatBoolean(
                                        configuration.evidenceCategories.some(
                                            (category) =>
                                                [
                                                    "account",
                                                    "balance",
                                                    "equity",
                                                    "margin",
                                                    "buying_power",
                                                ].includes(category),
                                        ),
                                    ),
                                ],
                                [
                                    "Infrastructure",
                                    formatBoolean(
                                        configuration.evidenceCategories.some(
                                            (category) =>
                                                [
                                                    "broker",
                                                    "server",
                                                    "terminal",
                                                    "user",
                                                ].includes(category),
                                        ),
                                    ),
                                ],
                                [
                                    "Market",
                                    formatBoolean(
                                        configuration.evidenceCategories.some(
                                            (category) =>
                                                [
                                                    "symbols",
                                                    "prices",
                                                    "activity",
                                                    "history",
                                                ].includes(category),
                                        ),
                                    ),
                                ],
                            ]}
                        />

                        <ReviewCard
                            title="Synchronization"
                            rows={[
                                [
                                    "Profile",
                                    formatProfile(
                                        configuration.synchronizationProfile,
                                    ),
                                ],
                                [
                                    "Initial Sync",
                                    formatInitialSynchronization(
                                        configuration.synchronization
                                            .initialSynchronization,
                                    ),
                                ],
                                [
                                    "Incremental",
                                    formatBoolean(
                                        configuration.synchronization
                                            .incrementalSynchronization,
                                    ),
                                ],
                                [
                                    "Health Monitoring",
                                    formatBoolean(
                                        configuration.synchronization
                                            .healthMonitoring,
                                    ),
                                ],
                            ]}
                        />

                        <ReviewCard
                            title="Verification"
                            rows={[
                                [
                                    "Credential Validation",
                                    formatBoolean(
                                        configuration.verification
                                            .validateProviderCredentials,
                                    ),
                                ],
                                [
                                    "Provider Identity",
                                    formatBoolean(
                                        configuration.verification
                                            .verifyProviderIdentity,
                                    ),
                                ],
                                [
                                    "Account Verification",
                                    formatBoolean(
                                        configuration.verification
                                            .verifyTradingAccount,
                                    ),
                                ],
                                [
                                    "Translation Validation",
                                    formatBoolean(
                                        configuration.verification
                                            .verifyEvidenceTranslation,
                                    ),
                                ],
                            ]}
                        />

                        <ReviewCard
                            title="Security"
                            rows={[
                                [
                                    "Credential Encryption",
                                    formatBoolean(
                                        configuration.security
                                            .encryptedCredentialStorage,
                                    ),
                                ],
                                [
                                    "Secure Connector",
                                    formatBoolean(
                                        configuration.security
                                            .secureConnectorSession,
                                    ),
                                ],
                                [
                                    "Runtime Monitoring",
                                    formatBoolean(
                                        configuration.security
                                            .enableRuntimeHealthMonitoring,
                                    ),
                                ],
                                [
                                    "Verification Required",
                                    configuration.security
                                        .requireSuccessfulVerification
                                        ? "Yes"
                                        : "No",
                                ],
                            ]}
                        />

                    </div>

                </div>

                {/* ====================================================== */}
                {/* Connection Actions */}
                {/* ====================================================== */}

                <div className="mt-10 rounded-2xl border bg-white p-8">

                    <div className="flex items-center justify-between">

                        <div>

                            <h2 className="text-3xl font-semibold">

                                Connection Actions

                            </h2>

                            <p className="mt-2 max-w-5xl text-slate-600 leading-7">

                                Execute the Desktop Trading Engine connection workflow.
                                Test provider connectivity, validate credentials and
                                create an authenticated provider connection capable of
                                synchronizing canonical evidence into the Trading Truth
                                Layer Evidence Acquisition Runtime.

                            </p>

                        </div>

                    </div>

                    {/* ====================================================== */}
                    {/* Workflow Preview */}
                    {/* ====================================================== */}

                    <div className="mt-10 rounded-xl border bg-slate-50 p-6">

                        <div className="text-lg font-semibold">

                            Connection Workflow

                        </div>

                        <div className="mt-6 grid gap-4 md:grid-cols-3 xl:grid-cols-7">

                            <WorkflowStep label="Credentials" />

                            <WorkflowStep label="Authentication" />

                            <WorkflowStep label="Verification" />

                            <WorkflowStep label="Connector" />

                            <WorkflowStep label="Synchronization" />

                            <WorkflowStep label="Evidence Runtime" />

                            <WorkflowStep label="Completed" />

                        </div>

                    </div>

                    {/* ====================================================== */}
                    {/* Runtime Status */}
                    {/* ====================================================== */}

                    <div className="mt-8 rounded-xl border border-dashed p-6">

                        <div className="text-lg font-semibold">

                            Runtime Status

                        </div>

                        <div className="mt-4 text-slate-500 leading-7">
                            {actionFeedback.message ||
                                "Ready for provider connection configuration."}
                        </div>

                    </div>

                    {/* ====================================================== */}
                    {/* Actions */}
                    {/* ====================================================== */}

                    {actionFeedback.state !== "idle" && (
                        <div
                            className={`mb-6 rounded-xl border p-5 ${
                                actionFeedback.state === "working"
                                    ? "border-blue-200 bg-blue-50 text-blue-800"
                                    : actionFeedback.state === "success"
                                    ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                                    : "border-red-200 bg-red-50 text-red-800"
                            }`}
                        >
                            <div className="flex items-center gap-3">
                                {actionFeedback.state === "working" && (
                                    <span className="h-3 w-3 animate-pulse rounded-full bg-blue-600" />
                                )}

                                {actionFeedback.state === "success" && (
                                    <span className="font-bold">✓</span>
                                )}

                                {actionFeedback.state === "error" && (
                                    <span className="font-bold">!</span>
                                )}

                                <span className="font-medium">
                                    {actionFeedback.message}
                                </span>
                            </div>
                        </div>
                    )}

                    <div className="mt-10 flex flex-wrap gap-4">

                        <button
                            type="button"
                            onClick={handleSaveDraft}
                            disabled={submitting}
                            className="rounded-xl border px-6 py-3 font-medium hover:bg-slate-100 disabled:opacity-50"
                        >
                            Save Draft
                        </button>

                        <button

                            onClick={handleTestConnection}

                            className="rounded-xl border px-6 py-3 font-medium hover:bg-slate-100 disabled:opacity-50"

                            disabled={submitting}

                        >

                            Test Connection

                        </button>

                        <button

                            onClick={handleCreateConnection}

                            className="rounded-xl bg-slate-900 px-8 py-3 font-medium text-white hover:bg-slate-800 disabled:opacity-50"

                            disabled={submitting}

                        >

                            Create Provider Connection

                        </button>

                        <button
                            type="button"
                            onClick={() => {
                                resetForm();

                                showActionFeedback(
                                    "success",
                                    "Connection form has been reset to its default configuration.",
                                );
                            }}
                            disabled={submitting}
                            className="rounded-xl border border-red-300 px-6 py-3 font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                        >
                            Reset Form
                        </button>

                    </div>

                    {/* ====================================================== */}
                    {/* Expected Runtime Messages */}
                    {/* ====================================================== */}

                    <div className="mt-10 rounded-xl border bg-slate-50 p-6">

                        <div className="text-lg font-semibold">

                            Expected Runtime Messages

                        </div>

                        <div className="mt-5 space-y-2 text-sm text-slate-600">

                            <div>• Authenticating provider...</div>

                            <div>• Validating supplied credentials...</div>

                            <div>• Discovering installed trading terminal...</div>

                            <div>• Reading terminal executable...</div>

                            <div>• Reading terminal version...</div>

                            <div>• Reading terminal build...</div>

                            <div>• Detecting terminal architecture...</div>

                            <div>• Discovering broker identity...</div>

                            <div>• Discovering trading server...</div>

                            <div>• Reading trading account information...</div>

                            <div>• Reading account balances and equity...</div>

                            <div>• Detecting supported evidence capabilities...</div>

                            <div>• Validating Desktop Trading Engine compatibility...</div>

                            <div>• Building Canonical Desktop Evidence Package...</div>

                            <div>• Registering Desktop Connector...</div>

                            <div>• Creating Synchronization Session...</div>

                            <div>• Publishing Provider Connection...</div>

                        </div>

                    </div>

                </div>



            </div>

            <ConnectionProgressDialog

                open={
                    progressOpen &&
                    creating
                }

                title="Creating Provider Connection"

                message="Desktop Trading Engine is executing the institutional provider connection workflow."

                onClose={() => setProgressOpen(false)}

                steps={progressSteps}

            />

        </div>

    );

}

function StatusRow({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div className="flex items-center justify-between border-b pb-3 last:border-none">

            <span className="text-sm text-slate-500">

                {label}

            </span>

            <span className="font-semibold">

                {value}

            </span>

        </div>

    );

}

function SummaryCard({
    title,
    value,
    subtitle,
}: {
    title: string;
    value: string;
    subtitle: string;
}) {

    return (

        <div className="rounded-xl border bg-slate-50 p-6">

            <div className="text-sm text-slate-500">

                {title}

            </div>

            <div className="mt-3 text-2xl font-bold">

                {value}

            </div>

            <div className="mt-2 text-sm text-slate-500">

                {subtitle}

            </div>

        </div>

    );

}

function PreviewRow({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div className="flex items-center justify-between border-b pb-2 last:border-none">

            <span className="text-slate-500">

                {label}

            </span>

            <span className="font-semibold">

                {value}

            </span>

        </div>

    );

}

function DiscoveryRow({
    label,
    value,
}: {
    label: string;
    value: string;
}) {

    return (

        <div className="rounded-xl border bg-white p-5">

            <div className="text-sm text-slate-500">

                {label}

            </div>

            <div className="mt-3 font-semibold text-slate-800">

                {value}

            </div>

        </div>

    );

}

function EvidenceGroup({
    title,
    items,
    selectedCategories,
    onToggle,
}: {
    title: string;
    items: {
        label: string;
        value: EvidenceCategory;
    }[];
    selectedCategories: EvidenceCategory[];
    onToggle: (category: EvidenceCategory) => void;
}) {
    return (
        <div className="rounded-xl border bg-slate-50 p-6">
            <div className="text-xl font-semibold">
                {title}
            </div>

            <div className="mt-6 space-y-4">
                {items.map((item) => (
                    <label
                        key={item.value}
                        className="flex cursor-pointer items-center justify-between"
                    >
                        <span>
                            {item.label}
                        </span>

                        <input
                            type="checkbox"
                            checked={selectedCategories.includes(
                                item.value,
                            )}
                            onChange={() =>
                                onToggle(item.value)
                            }
                            className="h-4 w-4"
                        />
                    </label>
                ))}
            </div>
        </div>
    );
}

function ProfileCard({
    title,
    description,
    recommended = false,
    selected = false,
    onSelect,
}: {
    title: string;
    description: string;
    recommended?: boolean;
    selected?: boolean;
    onSelect: () => void;
}) {
    return (
        <div
            className={`rounded-xl border p-6 ${
                selected
                    ? "border-slate-900 bg-slate-100"
                    : "bg-slate-50"
            }`}
        >
            <div className="flex items-center justify-between">
                <div className="text-xl font-semibold">
                    {title}
                </div>

                {recommended && (
                    <div className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
                        RECOMMENDED
                    </div>
                )}
            </div>

            <div className="mt-4 text-sm leading-7 text-slate-600">
                {description}
            </div>

            <button
                type="button"
                onClick={onSelect}
                className="mt-8 rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-800"
            >
                {selected ? "Selected" : "Select Profile"}
            </button>
        </div>
    );
}

function ToggleRow({
    title,
    description,
    enabled = false,
    onChange,
}: {
    title: string;
    description: string;
    enabled?: boolean;
    onChange: (enabled: boolean) => void;
}) {
    return (
        <div className="rounded-xl border bg-slate-50 p-5">
            <div className="flex items-center justify-between">
                <div>
                    <div className="font-semibold">
                        {title}
                    </div>

                    <div className="mt-2 text-sm leading-6 text-slate-500">
                        {description}
                    </div>
                </div>

                <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(event) =>
                        onChange(event.target.checked)
                    }
                    className="h-5 w-5"
                />
            </div>
        </div>
    );
}

function VerificationOption({
    title,
    description,
    enabled = false,
    onChange,
}: {
    title: string;
    description: string;
    enabled?: boolean;
    onChange: (enabled: boolean) => void;
}) {
    return (
        <div className="rounded-xl border bg-slate-50 p-5">
            <div className="flex items-start justify-between gap-6">
                <div>
                    <div className="text-lg font-semibold">
                        {title}
                    </div>

                    <div className="mt-2 text-sm leading-6 text-slate-500">
                        {description}
                    </div>
                </div>

                <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(event) =>
                        onChange(event.target.checked)
                    }
                    className="mt-1 h-5 w-5"
                />
            </div>
        </div>
    );
}

function ReviewCard({
    title,
    rows,
}: {
    title: string;
    rows: [string, string][];
}) {

    return (

        <div className="rounded-xl border bg-slate-50 p-6">

            <div className="text-xl font-semibold">

                {title}

            </div>

            <div className="mt-6 space-y-3">

                {rows.map(([label, value]) => (

                    <div
                        key={label}
                        className="flex items-center justify-between border-b pb-2 last:border-none"
                    >

                        <span className="text-sm text-slate-500">

                            {label}

                        </span>

                        <span className="font-semibold">

                            {value}

                        </span>

                    </div>

                ))}

            </div>

        </div>

    );

}

function WorkflowStep({
    label,
}: {
    label: string;
}) {

    return (

        <div className="rounded-lg border bg-white p-4 text-center">

            <div className="mx-auto mb-3 h-3 w-3 rounded-full bg-slate-300" />

            <div className="text-sm font-medium">

                {label}

            </div>

        </div>

    );

}