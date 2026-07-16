"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";

import WorkspaceIdentityCard from "../../../../components/settings/cards/WorkspaceIdentityCard";
import WorkspaceProfileCard from "../../../../components/settings/cards/WorkspaceProfileCard";
import WorkspaceUsageCard from "../../../../components/settings/cards/WorkspaceUsageCard";
import PlatformReadinessCard from "../../../../components/settings/cards/PlatformReadinessCard";
import WorkspaceGovernanceCard from "../../../../components/settings/cards/WorkspaceGovernanceCard";
import WorkspacePreferencesCard from "../../../../components/settings/cards/WorkspacePreferencesCard";
import VerificationPreferencesCard from "../../../../components/settings/cards/VerificationPreferencesCard";
import BrandingCard from "../../../../components/settings/cards/BrandingCard";
import InternalPlanSimulationCard
from "../../../../components/settings/cards/InternalPlanSimulationCard";
import WorkspaceDangerZoneCard from "../../../../components/settings/cards/WorkspaceDangerZoneCard";

import { useAuth } from "../../../../components/AuthProvider";
import {
  api,
  type WorkspaceSettings,
  type WorkspaceUsageSummary,
  type PlatformReadiness,
} from "../../../../lib/api";

const PLAN_ORDER = ["sandbox", "starter", "pro", "growth", "business"] as const;

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatPercent(value?: number | null) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatUsd(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `$${Number(value).toLocaleString()}`;
}

function isOverLimit(used?: number, limit?: number) {
  if (used === undefined || limit === undefined) return false;
  if (limit <= 0) return false;
  return used > limit;
}

function isAtOrOverLimit(used?: number, limit?: number) {
  if (used === undefined || limit === undefined) return false;
  if (limit <= 0) return false;
  return used >= limit;
}

function normalizeText(value?: string | null) {
  return String(value || "").toLowerCase().trim();
}

function formatDimensionLabel(value: string) {
  switch (value) {
    case "storage_mb":
      return "Storage";
    case "claims":
      return "Claims";
    case "trades":
      return "Trades";
    case "members":
      return "Members";
    default:
      return value;
  }
}

function formatPlanCodeLabel(value?: string | null) {
  const normalized = normalizeText(value);
  if (!normalized) return "Starter";
  if (normalized === "sandbox") return "Sandbox";
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}

function formatBooleanLabel(value?: boolean) {
  return value ? "yes" : "no";
}

function formatCheckoutModeLabel(mode?: string | null) {
  const normalized = normalizeText(mode);

  if (normalized === "paddle_checkout_ready")
    return "Paddle checkout ready";

  if (
    normalized === "lemon_checkout_ready" ||
    normalized === "lemonsqueezy_checkout_ready"
  ) {
    return "Lemon Squeezy checkout ready";
  }

  if (normalized === "stripe_checkout_ready")
    return "Stripe checkout ready";
  if (normalized === "manual_billing_ready") return "Manual billing ready";
  if (normalized === "placeholder_until_checkout") return "Checkout not configured";
  if (normalized === "sandbox_activation") return "Sandbox activation";
  return mode || "Unknown";
}

function formatProviderEnvironmentLabel(value?: string | null) {
  const normalized = normalizeText(value);
  if (!normalized) return "live";
  if (normalized === "sandbox") return "sandbox";
  return normalized;
}

function formatCapabilityStatus(params: {
  enabled?: boolean;
  fallbackWhenDisabled: string;
  foundationLabel?: string;
}) {
  const { enabled, fallbackWhenDisabled, foundationLabel } = params;
  if (enabled) return "enabled";
  return foundationLabel || fallbackWhenDisabled;
}

function formatReadinessSourceLabel(provider?: string | null) {
  const normalized = normalizeText(provider);
  if (!normalized) return "internal";
  if (normalized === "mt5") return "MT5";
  if (normalized === "ibkr") return "IBKR";
  if (normalized === "csv") return "CSV";
  if (normalized === "webhook") return "Webhook";
  return provider || "internal";
}

function getUsageRatio(used?: number, limit?: number): number | null {
  if (used === undefined || limit === undefined || limit <= 0) return null;
  return used / limit;
}

function UsageCard({
  label,
  used,
  limit,
  ratio,
  atOrOver,
  hint,
}: {
  label: string;
  used?: number;
  limit?: number;
  ratio?: number | null;
  atOrOver: boolean;
  hint?: string;
}) {
  const safeUsed = used ?? 0;
  const safeLimit = limit ?? 0;
  const numericRatio =
    typeof ratio === "number" && Number.isFinite(ratio)
      ? Math.max(0, Math.min(1, ratio))
      : safeLimit > 0
        ? Math.max(0, Math.min(1, safeUsed / safeLimit))
        : 0;

  return (
    <div
      className={`rounded-2xl border p-4 ${
        atOrOver ? "border-amber-200 bg-amber-50" : "border-slate-200 bg-slate-50"
      }`}
    >
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-2 text-xl font-semibold">
        {safeUsed} / {safeLimit}
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-white">
        <div
          className={`h-full rounded-full ${atOrOver ? "bg-amber-400" : "bg-slate-900"}`}
          style={{ width: `${numericRatio * 100}%` }}
        />
      </div>
      <div className="mt-2 text-sm text-slate-500">Utilization: {formatPercent(ratio)}</div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  const textValue = String(value);

  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div
        className={`mt-2 break-words font-semibold text-slate-900 ${
          textValue.length > 24 ? "text-lg leading-7" : "text-2xl"
        }`}
      >
        {textValue}
      </div>
      {hint ? <div className="mt-2 text-xs text-slate-500">{hint}</div> : null}
    </div>
  );
}

export default function WorkspaceSettingsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  useEffect(() => {
    const upgrade = searchParams.get("upgrade");

    if (upgrade === "true") {
      (async () => {
        try {
          const workspaceId = Number(params?.workspaceId);

          const res = await api.createBillingCheckoutSession(workspaceId, {
            plan_code: "pro",
            billing_cycle: "monthly",
          });

          if (res.checkout_url) {
            window.location.href = res.checkout_url;
          }
        } catch (err) {
          console.error("Auto checkout failed:", err);
        }
      })();
    }
  }, []);
  const { user, workspaces, loading: authLoading, getWorkspaceRole } = useAuth();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const workspaceRole = workspaceId ? getWorkspaceRole(workspaceId) : null;
  const canEdit = workspaceRole === "owner";
  const canSeeUpgrade = workspaceRole === "owner";

  const activeTab = searchParams.get("tab");

  const [settings, setSettings] = useState<WorkspaceSettings | null>(null);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [platformReadiness, setPlatformReadiness] = useState<PlatformReadiness | null>(null);

  const [simulation,setSimulation]=useState<any>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const [timezone, setTimezone] = useState("UTC");

  const [language, setLanguage] = useState("English");

  const [currency, setCurrency] = useState("USD");

  const SUPPORTED_CURRENCIES = [

      "USD",
      "EUR",
      "GBP",
      "JPY",
      "CHF",
      "CAD",
      "AUD",
      "NZD",
      "SGD",
      "HKD",
      "SEK",
      "NOK",
      "DKK",

      // Africa

      "ZAR",
      "TZS",
      "KES",
      "UGX",
      "NGN",
      "EGP",

      // Middle East

      "AED",
      "SAR",
      "QAR",

      // Asia

      "CNY",
      "INR",
      "KRW",
      "THB",
      "MYR",
      "IDR",

  ];

  const [dateFormat, setDateFormat] = useState("YYYY-MM-DD");

  const [autoRefresh, setAutoRefresh] = useState(true);

  const [autoSave, setAutoSave] = useState(true);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function loadPage(targetWorkspaceId: number) {
    try {
      setLoading(true);
      setError(null);

      const [

          settingsRes,

          usageRes,

          platformReadinessRes,

      ] = await Promise.all([

          api.getWorkspaceSettings(targetWorkspaceId),

          api.getWorkspaceUsage(targetWorkspaceId),

          api.getWorkspacePlatformReadiness(targetWorkspaceId),

      ]);

      let simulationRes = null;

      if (settingsRes.is_internal) {

          simulationRes =
              await api.getWorkspacePlanSimulation(
                  targetWorkspaceId
              );

      }

      setSettings(settingsRes);
      setUsage(usageRes);
      setPlatformReadiness(platformReadinessRes);

      setSettings(settingsRes);
      setUsage(usageRes);

      setPlatformReadiness(platformReadinessRes);

      setSimulation(
          simulationRes
      );

      setName(settingsRes.name || "");
      setDescription(settingsRes.description || "");
      setTimezone(
          settingsRes.preferences?.timezone ??
          "UTC"
      );

      setLanguage(
          settingsRes.preferences?.language ??
          "English"
      );

      setCurrency(
          settingsRes.preferences?.currency ??
          "USD"
      );

      setDateFormat(
          settingsRes.preferences?.date_format ??
          "YYYY-MM-DD"
      );

      setAutoRefresh(
          settingsRes.preferences?.auto_refresh ??
          true
      );

      setAutoSave(
          settingsRes.preferences?.auto_save ??
          true
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workspace settings.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!workspaceId) return;
    if (!workspaceMembership) return;
    void loadPage(workspaceId);
  }, [workspaceId, workspaceMembership]);

  async function handleSave() {

    if (!workspaceId || !canEdit) return;

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const updated = await api.updateWorkspaceSettings(workspaceId, {

          name,

          description,

          timezone,

          language,

          currency,

          date_format: dateFormat,

          auto_refresh: autoRefresh,

          auto_save: autoSave,

      });

      setSettings(updated);
      setSuccess("Workspace settings updated successfully.");

      const refreshedUsage =
          await api.getWorkspaceUsage(workspaceId);

      setUsage(refreshedUsage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update workspace settings.");
    } finally {
      setSaving(false);
    }
  }

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading workspace settings...</div>
        </main>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace settings page.
          </div>
        </main>
      </div>
    );
  }

  const governanceUsage = {
    members: Number(usage?.usage?.members ?? 0),
    trades: Number(usage?.usage?.trades ?? 0),
    claims: Number(usage?.usage?.claims ?? 0),
    storage_mb: Number(usage?.usage?.storage_mb ?? 0),
  };

  const governanceLimits = {
    members: Number(usage?.limits?.members ?? 0),
    trades: Number(usage?.limits?.trades ?? 0),
    claims: Number(usage?.limits?.claims ?? 0),
    storage_mb: Number(usage?.limits?.storage_mb ?? 0),
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">Trading Truth Layer · Workspace Settings</div>
            <h1 className="mt-2 text-4xl font-bold tracking-tight">Workspace Settings</h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Configure workspace identity, operational governance,
              verification behaviour, branding and platform preferences.
            </p>
            {activeTab === "billing" ? (
              <div className="mt-4 inline-flex rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-800">
                billing focus
              </div>
            ) : null}
          </div>

          <div className="rounded-2xl border bg-white px-5 py-4 shadow-sm">
            <div className="text-sm text-slate-500">Workspace Role</div>
            <div className="mt-2 text-xl font-semibold">{workspaceRole || "unknown"}</div>
          </div>
        </div>

        {loading ? (
          <div className="rounded-2xl border bg-white p-6 shadow-sm">Loading workspace settings...</div>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">{error}</div>
        ) : (
          <>

              <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
                <div className="space-y-6">
                  <WorkspaceUsageCard
                      usage={governanceUsage}
                      limits={governanceLimits}
                  />

                  <WorkspaceGovernanceCard
                      governance={{
                          workspaceId: settings?.workspace_id ?? workspaceId,
                          role: workspaceRole ?? "",
                          configuredPlan: settings?.plan_code ?? "",
                          effectivePlan: settings?.effective_plan_code ?? "",
                          createdAt: settings?.created_at ?? "",
                          updatedAt: settings?.updated_at ?? "",
                      }}
                  />

                  <WorkspaceProfileCard

                      canEdit={canEdit}

                      saving={saving}

                      name={name}

                      description={description}

                      currency={currency}

                      setCurrency={setCurrency}

                      setName={setName}

                      setDescription={setDescription}

                      onSubmit={() => {

                          void handleSave();

                      }}

                  />

                  <WorkspaceDangerZoneCard

                      onExport={() => {}}

                      onArchive={() => {}}

                      onTransfer={() => {}}

                      onDelete={() => {}}

                  />

                  <div className="rounded-3xl border bg-white p-6 shadow-sm">
                    <h2 className="text-2xl font-semibold">Workspace Record</h2>
                    <div className="mt-4 space-y-3 text-sm text-slate-600">
                      <div>
                        <span className="font-medium text-slate-900">Workspace ID:</span>{" "}
                        {settings?.workspace_id || workspaceId}
                      </div>
                      <div>
                        <span className="font-medium text-slate-900">Created:</span>{" "}
                        {formatDateTime(settings?.created_at)}
                      </div>
                      <div>
                        <span className="font-medium text-slate-900">Updated:</span>{" "}
                        {formatDateTime(settings?.updated_at)}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-6">
                  <PlatformReadinessCard
                      verificationExposure="Public"
                      externalVerification="Enabled"
                      apiAccess="Foundation Ready"
                      brokerConnections="Supported"
                      webhooks="Supported"
                      trustNetwork="Enabled"
                  />

                  <WorkspacePreferencesCard
                      timezone={timezone}
                      currency={currency}
                      language={language}
                      dateFormat={dateFormat}
                      autoRefresh={autoRefresh}
                      autoSave={autoSave}
                      readOnly
                  />

                  <VerificationPreferencesCard
                      publicVerification={true}
                      verificationRoutes={true}
                      trustScore={true}
                      qrCodes={true}
                      jsonEvidence={true}
                      pdfEvidence={true}
                      zipEvidence={true}
                      autoLock={true}
                      autoPublish={false}
                      onPublicVerification={() => {}}
                      onVerificationRoutes={() => {}}
                      onTrustScore={() => {}}
                      onQrCodes={() => {}}
                      onJsonEvidence={() => {}}
                      onPdfEvidence={() => {}}
                      onZipEvidence={() => {}}
                      onAutoLock={() => {}}
                      onAutoPublish={() => {}}
                  />

                  <BrandingCard
                      organization={name}

                      website="https://tradingtruthlayer.com"

                      logo="/ttl-logo.png"

                      primaryColor="#0f172a"

                      accentColor="#2563eb"

                      reportFooter={
                          "Trading Truth Layer"
                      }

                      disclaimer={
                          "Generated by the Trading Truth Layer Verification System."
                      }

                      readOnly
                  />

                  {settings?.is_internal && (

                      <InternalPlanSimulationCard

                          workspaceId={workspaceId}

                          simulation={simulation}

                          onChanged={async () => {

                              const snapshot =
                                  await api.getWorkspacePlanSimulation(
                                      workspaceId
                                  );

                              setSimulation(snapshot);

                              await loadPage(workspaceId);

                          }}

                      />

                  )}

                  {!canEdit ? (
                    <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6 text-amber-800 shadow-sm">
                      Your current role is <span className="font-semibold">{workspaceRole}</span>.
                      Only workspace owners can update settings, billing contact details, and upgrade
                      workspace plans.
                    </div>
                  ) : null}
                </div>
              </div>
          </>
        )}
      </main>
    </div>
  );
}