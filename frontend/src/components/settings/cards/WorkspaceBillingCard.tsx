"use client";

type Props = {
  configuredPlan: string;
  effectivePlan: string;

  billingStatus?: string;
  provider: string;

  monthlyPrice?: number | null;
  annualPrice?: number |null;

  selectedPlan: string;
  billingCycle: string;

  plans: {
    code: string;
    name: string;
  }[];

  checkoutLoading: boolean;
  portalLoading: boolean;

  canUpgrade: boolean;

  onSelectPlan: (plan: string) => void;

  onBillingCycle: (cycle: string) => void;

  onCheckout: () => void;

  onPortal: () => void;
};

export default function WorkspaceBillingCard({

    configuredPlan,

    effectivePlan,

    billingStatus,

    provider,

    monthlyPrice,

    annualPrice,

    selectedPlan,

    billingCycle,

    plans,

    checkoutLoading,

    portalLoading,

    canUpgrade,

    onSelectPlan,

    onBillingCycle,

    onCheckout,

    onPortal,

}: Props) {

  return (

    <div className="rounded-3xl border bg-white p-6 shadow-sm">

      <h2 className="text-2xl font-semibold">

        Workspace Billing

      </h2>

      <p className="mt-1 text-sm text-slate-500">

        Commercial plan,
        subscription status,
        billing provider
        and upgrade actions.

      </p>

      <div className="mt-6 grid gap-4 md:grid-cols-2">

        <Info
          title="Current Plan"
          value={configuredPlan}
        />

        <Info
          title="Billing Status"
          value={billingStatus ?? "Inactive"}
        />

        <Info
          title="Billing Provider"
          value={provider}
        />

        <Info
          title="Monthly Price"
          value={monthlyPrice == null ? "—" : `$${monthlyPrice}`}
        />

        <Info
          title="Annual Price"
          value={annualPrice == null ? "—" : `$${annualPrice}`}
        />

        <Info
          title="Effective Plan"
          value={effectivePlan}
        />

      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">

          <div>

              <div className="mb-2 text-sm font-medium">

                  Selected Plan

              </div>

              <select
                  value={selectedPlan}
                  onChange={(e)=>onSelectPlan(e.target.value)}
                  className="w-full rounded-xl border px-4 py-3"
              >

                  {plans.map(plan=>(
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

              <div className="mb-2 text-sm font-medium">

                  Billing Cycle

              </div>

              <select
                  value={billingCycle}
                  onChange={(e)=>onBillingCycle(e.target.value)}
                  className="w-full rounded-xl border px-4 py-3"
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

      <div className="mt-6 flex flex-wrap gap-3">

        <button

          onClick={onCheckout}

          disabled={
            !canUpgrade ||
            checkoutLoading
          }

          className="rounded-xl bg-slate-900 px-5 py-3 text-white disabled:bg-slate-400"

        >

          {checkoutLoading
            ? "Preparing..."
            : "Upgrade Plan"}

        </button>

        <button

          onClick={onPortal}

          disabled={
            !canUpgrade ||
            portalLoading
          }

          className="rounded-xl border px-5 py-3"

        >

          {portalLoading
            ? "Opening..."
            : "Billing Portal"}

        </button>

      </div>

    </div>

  );

}

function Info({

  title,

  value,

}: {

  title: string;

  value: string;

}) {

  return (

    <div className="rounded-xl border bg-slate-50 p-4">

      <div className="text-sm text-slate-500">

        {title}

      </div>

      <div className="mt-1 text-lg font-semibold">

        {value}

      </div>

    </div>

  );

}