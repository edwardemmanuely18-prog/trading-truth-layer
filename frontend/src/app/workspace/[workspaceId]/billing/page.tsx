"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import Navbar from "../../../../components/Navbar";

import * as api from "../../../../lib/api";

import type {

  WorkspaceBillingFoundation,

  WorkspaceUsageSummary,

  WorkspaceGovernance,

  WorkspacePlanDetail,

  WorkspaceSettings,

  BillingDiagnostics,

  BillingCheckoutResponse,

  BillingPortalResponse,

  BillingInvoiceResponse,

} from "../../../../lib/api";

import { useParams } from "next/navigation";

function MetricCard({

  title,

  value,

  subtitle,

}: {

  title: string;

  value: React.ReactNode;

  subtitle?: string;

}) {

  return (

    <div className="rounded-3xl border bg-white p-6 shadow-sm">

      <div className="text-sm text-slate-500">

        {title}

      </div>

      <div className="mt-3 text-3xl font-bold text-slate-900">

        {value}

      </div>

      {subtitle ? (

        <div className="mt-2 text-sm text-slate-500">

          {subtitle}

        </div>

      ) : null}

    </div>

  );

}

function MetricRow({
    label,
    value,
}: {
    label: string;
    value: React.ReactNode;
}) {

    return (

        <div className="border-b border-slate-100 last:border-b-0">

            <div className="flex items-center justify-between px-8 py-6">

                <span className="font-medium text-slate-600">

                    {label}

                </span>

                <span className="font-semibold text-slate-900">

                    {value}

                </span>

            </div>

        </div>

    );

}

function StatusBadge({

  value,

}: {

  value: string;

}) {

  const normalized = value.toLowerCase();

  const cls =

    normalized === "active"

      ? "bg-emerald-100 text-emerald-700"

      : normalized === "trialing"

      ? "bg-blue-100 text-blue-700"

      : normalized === "past_due"

      ? "bg-amber-100 text-amber-700"

      : normalized === "cancelled"

      ? "bg-red-100 text-red-700"

      : "bg-slate-100 text-slate-700";

  return (

    <span

      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${cls}`}

    >

      {value}

    </span>

  );

}

export default function BillingPage() {

  const params = useParams();

  const workspaceId = Number(params.workspaceId);

  const [loading, setLoading] = useState(true);

  const [checkoutLoading, setCheckoutLoading] = useState(false);

  const [selectedPlan,setSelectedPlan] =
  useState("sandbox");

  const [billingCycle,setBillingCycle] = useState<"monthly"|"annual">("monthly");

  const [error, setError] = useState<string | null>(null);

  const [billingFoundation, setBillingFoundation] =

    useState<WorkspaceBillingFoundation | null>(null);

  const [usage, setUsage] =

    useState<WorkspaceUsageSummary | null>(null);

  const [governance, setGovernance] =

    useState<WorkspaceGovernance | null>(null);

  const [settings, setSettings] =

    useState<WorkspaceSettings | null>(null);

  const [diagnostics, setDiagnostics] =

    useState<BillingDiagnostics | null>(null);

  const load = useCallback(async () => {

    try {

      setLoading(true);

      setError(null);

      const [

        billing,

        usageSummary,

        governanceSummary,

        workspaceSettings,

        diagnosticSummary,

      ] = await Promise.all([

        api.getWorkspaceBillingFoundation(workspaceId),

        api.getWorkspaceUsage(workspaceId),

        api.getWorkspaceGovernance(workspaceId),

        api.getWorkspaceSettings(workspaceId),

        api.getBillingDiagnostics(workspaceId),

      ]);

      setBillingFoundation(billing);

      setUsage(usageSummary);

      setGovernance(governanceSummary);

      setSettings(workspaceSettings);

      setDiagnostics(diagnosticSummary);

    } catch (err: any) {

      setError(

        err?.message ||

          "Failed to load billing workspace."

      );

    } finally {

      setLoading(false);

    }

  }, [workspaceId]);

  const handleCheckout = async (
      planCode: string,
      billingCycle: "monthly" | "annual",
  ) => {

      try {

          setCheckoutLoading(true);

          const response =
              await api.createBillingCheckout(
                  workspaceId,
                  {
                      plan_code: planCode,
                      billing_cycle: billingCycle,
                  },
              );

          if (response.checkout_url) {

              window.location.assign(
                  response.checkout_url
              );

              return;

          }

          alert(

              response.message ??

              "Unable to create checkout."

          );

      } catch (err: any) {

          alert(
              err?.message ??
              "Unable to create checkout."
          );

      } finally {

          setCheckoutLoading(false);

      }

  };

  useEffect(() => {

    load();

  }, [load]);

    const configuredPlan =
        billingFoundation?.plan_code ??
        "sandbox";

    const provider =
        billingFoundation?.billing_provider_label ??
        "Manual";

    const environment =
        billingFoundation?.provider_environment ??
        "Unknown";

    const billingStatus =
        billingFoundation?.billing_status ??
        "inactive";

    const effectivePlan =
        billingFoundation?.effective_plan_code ??
        configuredPlan;

    const renewal =

        billingFoundation?.subscription_current_period_end ??

        "—";

    const plans = useMemo(() => {

        const rawPlans = billingFoundation?.public_plans;

        if (
            !rawPlans ||
            Object.keys(rawPlans).length === 0
        ) {
            return [];
        }

        return Object.entries(rawPlans).map(
            ([code, plan]: any) => ({

                code,

                name:
                    plan.name ??
                    code.charAt(0).toUpperCase() +
                    code.slice(1),

                description:
                    plan.description ??
                    "Commercial workspace subscription.",

                pricing: {

                    monthly:
                        plan.pricing?.monthly ??
                        plan.monthly_price_usd ??
                        0,

                    annual:
                        plan.pricing?.annual ??
                        plan.annual_price_usd ??
                        0,

                },

                claims:
                    plan.claims ?? 0,

                trades:
                    plan.trades ?? 0,

                members:
                    plan.members ?? 0,

                storage_mb:
                    plan.storage_mb ?? 0,

                commercial_services:
                    plan.commercial_services ?? [],

                workflow_outcomes:
                    plan.workflow_outcomes ?? [],

                features:
                    plan.infrastructure ?? [],

                capacity_summary:
                    plan.capacity_summary ?? {},

            })
        );

    }, [billingFoundation]);

    const orderedPlans = [...(plans ?? [])].sort((a, b) => {

        const order = [
            "sandbox",
            "starter",
            "pro",
            "growth",
            "business",
        ];

        return (
            order.indexOf(a.code.toLowerCase()) -
            order.indexOf(b.code.toLowerCase())
        );

    });

    const selectedPlanResolved =
        useMemo(() => {

            return (
                orderedPlans.find(
                    p =>
                        p.code === selectedPlan
                ) ??
                orderedPlans[0]
            );

        }, [
            orderedPlans,
            selectedPlan,
        ]);

    useEffect(() => {

        if (!selectedPlan && orderedPlans.length > 0) {

            setSelectedPlan(configuredPlan);

        }

    }, [
        configuredPlan,
        orderedPlans,
        selectedPlan,
    ]);


    if (loading) {

    return (

      <div className="min-h-screen bg-slate-50">

        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-20">

          <div className="rounded-3xl border bg-white p-10 shadow">

            Loading Billing Console...

          </div>

        </div>

      </div>

    );

  }

  const handleInvoice = async () => {

      try {

          const result: BillingInvoiceResponse =
              await api.downloadLatestInvoice(
                  workspaceId
              );

          if (result.invoice_url) {

              window.open(

                  result.invoice_url,

                  "_blank"

              );

              return;

          }

          alert(

              result.message ??

              "No invoice available."

          );

      }

      catch(err:any){

          alert(

              err?.message ??

              "Unable to retrieve invoice."

          );

      }

  };

  if (error) {

    return (

      <div className="min-h-screen bg-slate-50">

        <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-20">

          <div className="rounded-3xl border border-red-200 bg-red-50 p-10">

            {error}

          </div>

        </div>

      </div>

    );

  }

  return (

    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <main className="mx-auto max-w-7xl space-y-8 px-6 py-8">

        {/* =======================================================
            HERO
        ======================================================= */}

        <section className="rounded-3xl border bg-white p-10 shadow-sm">

            <div className="flex flex-col gap-10 xl:flex-row xl:items-start xl:justify-between">

                <div className="max-w-4xl">

                    <div className="text-sm uppercase tracking-[0.35em] text-slate-500">

                        Workspace Commercial Center

                    </div>

                    <h1 className="mt-4 text-5xl font-bold tracking-tight">

                        Billing & Subscription

                    </h1>

                    <p className="mt-6 text-lg leading-8 text-slate-600">

                        Institutional commercial management console for workspace
                        subscriptions, entitlement enforcement, provider diagnostics,
                        billing lifecycle, commercial infrastructure, invoices,
                        governance and operational capacity.

                    </p>

                </div>

                <div className="rounded-2xl border bg-slate-50 px-8 py-6">

                    <div className="text-sm text-slate-500">

                        Commercial Status

                    </div>

                    <div className="mt-4">

                        <StatusBadge value={billingStatus} />

                    </div>

                    <div className="mt-6 text-sm text-slate-500">

                        Billing Provider

                    </div>

                    <div className="mt-2 text-2xl font-bold">

                        {provider}

                    </div>

                </div>

            </div>

        </section>

        {/* =======================================================
            SUMMARY METRICS
        ======================================================= */}

        <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-5">

            <MetricCard
                title="Configured Plan"
                value={configuredPlan.toUpperCase()}
            />

            <MetricCard
                title="Effective Plan"
                value={effectivePlan.toUpperCase()}
            />

            <MetricCard
                title="Billing Status"
                value={<StatusBadge value={billingStatus} />}
            />

            <MetricCard
                title="Provider"
                value={provider}
            />

            <MetricCard
                title="Environment"
                value={
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold">
                        {environment}
                    </span>
                }
            />

        </section>

        {/* =======================================================
            CURRENT SUBSCRIPTION
        ======================================================= */}

        <section className="rounded-3xl border bg-white p-10 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <h2 className="text-4xl font-bold">

                        Current Subscription

                    </h2>

                    <p className="mt-3 text-slate-600">

                        Active commercial subscription currently governing this
                        workspace.

                    </p>

                </div>

                <StatusBadge value={billingStatus} />

            </div>

            <div className="mt-10 rounded-2xl border bg-slate-50 p-8">

                <div className="grid gap-x-14 gap-y-8 lg:grid-cols-2">

                    <MetricRow
                        label="Workspace"
                        value={
                            settings?.name ??
                            `Workspace #${workspaceId}`
                        }
                    />

                    <MetricRow
                        label="Provider"
                        value={provider}
                    />

                    <MetricRow
                        label="Configured Plan"
                        value={configuredPlan}
                    />

                    <MetricRow
                        label="Effective Plan"
                        value={effectivePlan}
                    />

                    <MetricRow
                        label="Environment"
                        value={
                            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold">
                                {environment}
                            </span>
                        }
                    />

                    <MetricRow
                        label="Billing Status"
                        value={
                            <StatusBadge
                                value={billingStatus}
                            />
                        }
                    />

                </div>

            </div>

        </section>

        {/* =======================================================
            COMMERCIAL PLANS
        ======================================================= */}

        <section className="rounded-3xl border bg-white p-10 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <h2 className="text-4xl font-bold">

                        Commercial Plans

                    </h2>

                    <p className="mt-3 text-slate-600">

                        Compare every institutional subscription tier. Each tier
                        expands governance capacity, verification infrastructure,
                        operational scale and commercial services.

                    </p>

                </div>

            </div>

            <div className="mt-10 grid gap-8 lg:grid-cols-2 2xl:grid-cols-3">

                {orderedPlans.map((plan) => {

                    const current =
                        configuredPlan.toLowerCase() ===
                        plan.code.toLowerCase();

                    const selected =
                        selectedPlan === plan.code;

                    return (

                        <div
                            key={plan.code}
                            className={`rounded-3xl border p-8 transition-all ${
                                current
                                    ? "border-blue-600 ring-2 ring-blue-100"
                                    : selected
                                    ? "border-emerald-500 ring-2 ring-emerald-100"
                                    : "border-slate-200"
                            }`}
                        >

                            <div className="flex items-start justify-between">

                                <div>

                                    <h3 className="text-3xl font-bold">

                                        {plan.name}

                                    </h3>

                                    <p className="mt-3 text-slate-600">

                                        {plan.description}

                                    </p>

                                </div>

                                {current ? (

                                    <span className="rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-700">

                                        CURRENT

                                    </span>

                                ) : selected ? (

                                    <span className="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700">

                                        SELECTED

                                    </span>

                                ) : null}

                            </div>

                            <div className="mt-8 grid gap-4 md:grid-cols-2">

                                <MetricCard
                                    title="Monthly"
                                    value={`$${plan.pricing.monthly}`}
                                />

                                <MetricCard
                                    title="Annual"
                                    value={`$${plan.pricing.annual}`}
                                />

                            </div>

                            <div className="mt-8 rounded-2xl border bg-slate-50 p-6">

                                <div className="mb-4 font-semibold uppercase tracking-wide text-slate-500">

                                    Capacity

                                </div>

                                <MetricRow
                                    label="Claims"
                                    value={plan.capacity_summary?.claims ?? plan.claims}
                                />

                                <MetricRow
                                    label="Trades"
                                    value={plan.capacity_summary?.trades ?? plan.trades}
                                />

                                <MetricRow
                                    label="Members"
                                    value={plan.capacity_summary?.members ?? plan.members}
                                />

                                <MetricRow
                                    label="Storage"
                                    value={
                                        plan.capacity_summary?.storage ??
                                        `${plan.storage_mb} MB`
                                    }
                                />

                            </div>

                            <button
                                onClick={() => setSelectedPlan(plan.code)}
                                className={`mt-8 w-full rounded-xl px-6 py-4 font-semibold transition ${
                                    selected
                                        ? "bg-emerald-600 text-white"
                                        : "bg-slate-900 text-white hover:bg-slate-800"
                                }`}
                            >
                                {selected ? "Selected Plan" : "Select Plan"}
                            </button>

                            <div className="mt-8 space-y-6">

                                <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">

                                    <div className="font-semibold uppercase tracking-wide text-emerald-700">

                                        Platform Infrastructure

                                    </div>

                                    <div className="mt-4 space-y-3">

                                        {(plan.features ?? []).length === 0 ? (

                                            <div className="text-sm text-slate-500">

                                                Standard infrastructure

                                            </div>

                                        ) : (

                                            plan.features.map((feature: string) => (

                                                <div
                                                    key={feature}
                                                    className="flex gap-3"
                                                >

                                                    <span className="font-bold text-emerald-600">

                                                        ✓

                                                    </span>

                                                    <span>

                                                        {feature}

                                                    </span>

                                                </div>

                                            ))

                                        )}

                                    </div>

                                </div>

                                <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5">

                                    <div className="font-semibold uppercase tracking-wide text-blue-700">

                                        Commercial Services

                                    </div>

                                    <div className="mt-4 space-y-3">

                                        {(plan.commercial_services ?? []).length === 0 ? (

                                            <div className="text-sm text-slate-500">

                                                Standard commercial services

                                            </div>

                                        ) : (

                                            plan.commercial_services.map((service: string) => (

                                                <div
                                                    key={service}
                                                    className="flex gap-3"
                                                >

                                                    <span className="font-bold text-blue-700">

                                                        ✓

                                                    </span>

                                                    <span>

                                                        {service}

                                                    </span>

                                                </div>

                                            ))

                                        )}

                                    </div>

                                </div>

                            </div>

                        </div>

                    );

                })}

            </div>

        </section>

        {/* =======================================================
            CHECKOUT CONSOLE
        ======================================================= */}

        <section className="rounded-3xl border bg-white p-10 shadow-sm">

            <div className="flex items-center justify-between">

                <div>

                    <h2 className="text-4xl font-bold">

                        Subscription Activation

                    </h2>

                    <p className="mt-3 text-slate-600">

                        Review subscription tiers, compare operational workflows, evaluate commercial capacity, and activate the subscription that best matches your verification operations.

                    </p>

                </div>

                <StatusBadge value={billingStatus} />

            </div>

            <div className="mt-10 grid gap-10 xl:grid-cols-[1.2fr_0.8fr]">

                {/* LEFT PANEL */}

                <div>

                    <div className="grid gap-6 lg:grid-cols-2">

                        <div>

                            <label className="text-sm font-semibold uppercase tracking-wide text-slate-500">

                                Commercial Plan

                            </label>

                            <select

                                value={selectedPlan}

                                onChange={(e)=>

                                    setSelectedPlan(e.target.value)

                                }

                                className="mt-3 w-full rounded-xl border p-4"

                            >

                                {orderedPlans.map(plan=>(

                                    <option

                                        key={plan.code}

                                        value={plan.code}

                                    >

                                        {plan.name}

                                    </option>

                                ))}

                            </select>

                        </div>

                        <div>

                            <label className="text-sm font-semibold uppercase tracking-wide text-slate-500">

                                Billing Cycle

                            </label>

                            <select

                                value={billingCycle}

                                onChange={(e)=>

                                    setBillingCycle(

                                        e.target.value as

                                        "monthly" |

                                        "annual"

                                    )

                                }

                                className="mt-3 w-full rounded-xl border p-4"

                            >

                                <option value="monthly">

                                    Monthly

                                </option>

                                <option value="annual">

                                    Annual

                                </option>

                            </select>

                        </div>

                    </div>

                    <div className="mt-10 rounded-2xl border bg-slate-50 p-8">

                        <h3 className="text-3xl font-bold">

                            {selectedPlanResolved.name}

                        </h3>

                        <p className="mt-4 text-slate-600">

                            {selectedPlanResolved.description}

                        </p>

                        <div className="mt-8 grid gap-4 md:grid-cols-2">

                            <MetricCard

                                title="Monthly"

                                value={`$${selectedPlanResolved.pricing.monthly}`}

                            />

                            <MetricCard

                                title="Annual"

                                value={`$${selectedPlanResolved.pricing.annual}`}

                            />

                        </div>

                        <div className="mt-8 rounded-xl border bg-white p-6">

                            <div className="font-semibold uppercase tracking-wide text-slate-500">

                                Capacity Included

                            </div>

                            <MetricRow

                                label="Claims"

                                value={selectedPlanResolved.claims}

                            />

                            <MetricRow

                                label="Trades"

                                value={selectedPlanResolved.trades}

                            />

                            <MetricRow

                                label="Members"

                                value={selectedPlanResolved.members}

                            />

                            <MetricRow

                                label="Storage"

                                value={`${selectedPlanResolved.storage_mb} MB`}

                            />

                        </div>

                        <div className="mt-8 rounded-xl border bg-white p-6">

                            <div className="text-lg font-semibold">

                                Selected Subscription

                            </div>

                            <div className="mt-6 grid gap-3">

                                <MetricRow

                                    label="Commercial Plan"

                                    value={selectedPlanResolved.name}

                                />

                                <MetricRow

                                    label="Billing Cycle"

                                    value={billingCycle}

                                />

                                <MetricRow

                                    label="Monthly"

                                    value={`$${selectedPlanResolved.pricing.monthly}`}

                                />

                                <MetricRow

                                    label="Annual"

                                    value={`$${selectedPlanResolved.pricing.annual}`}

                                />

                            </div>

                        </div>

                    </div>

                    <div className="mt-8 space-y-6">

                    <div className="rounded-2xl border border-blue-200 bg-blue-50 p-6">

                    <div className="font-semibold uppercase tracking-wide text-blue-700">

                    Commercial Services

                    </div>

                    <div className="mt-4 space-y-3">

                    {

                    selectedPlanResolved.commercial_services.length===0

                    ?

                    <div className="text-slate-500">

                    Standard Commercial Workflows

                    </div>

                    :

                    selectedPlanResolved.commercial_services.map((service: string) => (

                    <div

                    key={service}

                    className="flex gap-3"

                    >

                    <div className="font-bold text-blue-700">

                    ✓

                    </div>

                    <div>

                    {service}

                    </div>

                    </div>

                    ))

                    }

                    </div>

                    </div>

                    <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">

                    <div className="font-semibold uppercase tracking-wide text-emerald-700">

                    Infrastructure

                    </div>

                    <div className="mt-4 space-y-3">

                    {

                    selectedPlanResolved.features.length===0

                    ?

                    <div className="text-slate-500">

                    Standard Infrastructure

                    </div>

                    :

                    selectedPlanResolved.features.map((feature: string) => (

                    <div

                    key={feature}

                    className="flex gap-3"

                    >

                    <div className="font-bold text-emerald-700">

                    ✓

                    </div>

                    <div>

                    {feature}

                    </div>

                    </div>

                    ))

                    }

                    </div>

                    </div>

                    </div>

                </div>

                {/* RIGHT PANEL */}

                <div className="space-y-6">

                    <button

                        onClick={()=>

                            handleCheckout(

                                selectedPlan,

                                billingCycle

                            )

                        }

                        disabled={checkoutLoading}

                        className="w-full rounded-xl bg-slate-900 px-6 py-5 text-lg font-semibold text-white"

                    >

                        {checkoutLoading

                            ? "Creating Checkout..."

                            : "Proceed To Checkout"}

                    </button>
                    
                    <button

                        onClick={load}

                        className="w-full rounded-xl border px-6 py-4 font-semibold"

                    >

                        Refresh Billing

                    </button>

                    <button

                        onClick={handleInvoice}

                        className="w-full rounded-xl border px-6 py-4 font-semibold"

                    >

                        Download Latest Invoice

                    </button>

                    <button

                        onClick={() => {

                            const subject = encodeURIComponent(

                                `Billing Support - Workspace ${workspaceId}`

                            );

                            window.location.href =

                                `mailto:support@tradingtruthlayer.com?subject=${subject}`;

                        }}

                        className="w-full rounded-xl border px-6 py-4 font-semibold"

                    >

                        Contact Billing Support

                    </button>

                </div>

            </div>

        </section>

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <h2 className="text-3xl font-bold">

                Workspace Usage

            </h2>

            <p className="mt-2 text-slate-500">

                Current entitlement consumption for this workspace.

            </p>

            <div className="mt-8 space-y-8">

                {[
                    {
                        label: "Claims",
                        used: usage?.usage?.claims ?? 0,
                        limit: usage?.limits?.claims ?? 0,
                    },
                    {
                        label: "Trades",
                        used: usage?.usage?.trades ?? 0,
                        limit: usage?.limits?.trades ?? 0,
                    },
                    {
                        label: "Members",
                        used: usage?.usage?.members ?? 0,
                        limit: usage?.limits?.members ?? 0,
                    },
                    {
                        label: "Storage (MB)",
                        used: usage?.usage?.storage_mb ?? 0,
                        limit: usage?.limits?.storage_mb ?? 0,
                    },
                ].map((item) => {

                    const percent =
                        item.limit > 0
                            ? Math.min(
                                  (item.used / item.limit) * 100,
                                  100,
                              )
                            : 0;

                    return (

                        <div key={item.label}>

                            <div className="mb-2 flex justify-between">

                                <span className="font-semibold">

                                    {item.label}

                                </span>

                                <span>

                                    {item.used} / {item.limit}

                                </span>

                            </div>

                            <div className="h-3 rounded-full bg-slate-200">

                                <div
                                    className="h-3 rounded-full bg-emerald-600"
                                    style={{
                                        width: `${percent}%`,
                                    }}
                                />

                            </div>

                        </div>

                    );

                })}

            </div>

        </section>

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <h2 className="text-4xl font-bold">

            Platform & Billing Health

            </h2>

            <p className="mt-3 text-slate-600">

            Real-time operational readiness of the commercial infrastructure, provider connectivity and billing lifecycle.

            </p>

            <div className="mt-8 grid gap-6 md:grid-cols-2">

                {[
                    [
                        "Provider Ready",
                        diagnostics?.provider_ready,
                    ],
                    [
                        "Checkout",
                        diagnostics?.checkout_ready,
                    ],
                    [
                        "Portal",
                        diagnostics?.portal_ready,
                    ],
                    [
                        "Webhook",
                        diagnostics?.webhookConfigured,
                    ],
                ].map(([title, state]) => (

                    <div
                        key={String(title)}
                        className="flex items-center justify-between rounded-2xl border p-5"
                    >

                        <div className="font-semibold">

                            {title}

                        </div>

                        <div
                            className={`font-bold ${
                                state
                                    ? "text-emerald-600"
                                    : "text-red-600"
                            }`}
                        >

                            {state ? "✓ Ready" : "Not Enabled"}

                        </div>

                    </div>

                ))}

            </div>

        </section>

        <section className="rounded-3xl border bg-white p-8 shadow-sm">

            <h2 className="text-3xl font-bold">

                Subscription Summary

            </h2>

            <div className="mt-8 rounded-2xl border">

                <MetricRow
                    label="Commercial Status"
                    value={<StatusBadge value={billingStatus} />}
                />

                <MetricRow
                    label="Current Plan"
                    value={configuredPlan}
                />

                <MetricRow
                    label="Effective Plan"
                    value={effectivePlan}
                />

                <MetricRow
                    label="Provider"
                    value={provider}
                />

                <MetricRow
                    label="Next Renewal"
                    value={renewal}
                />

                <MetricRow
                    label="Workspace"
                    value={settings?.name ?? `Workspace #${workspaceId}`}
                />

            </div>

        </section>
           
      </main>

    </div>

  );

}