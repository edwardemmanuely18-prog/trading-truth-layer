export default function HowItWorksPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-5xl px-6 py-16">

        {/* HEADER */}
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold tracking-tight">
            How Trading Truth Layer Works
          </h1>

          <p className="mt-4 text-lg text-slate-600">
            A step-by-step guide to turning raw trading activity into
            verifiable claims, canonical records, and public proof.
          </p>
        </div>

        {/* FLOW */}
        <div className="mt-12 space-y-12">

          {/* STEP 1 */}
          <div>
            <div className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
              Step 1
            </div>
            <h2 className="mt-2 text-2xl font-semibold">
              Import trading data
            </h2>

            <p className="mt-3 text-slate-600">
              Upload or stream your trading activity into the platform using:
              CSV files, MT5 exports, IBKR data, or webhooks.
            </p>

            <div className="mt-3 text-sm text-slate-500">
              → This creates your canonical trade ledger.
            </div>
          </div>

          {/* STEP 2 */}
          <div>
            <div className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
              Step 2
            </div>
            <h2 className="mt-2 text-2xl font-semibold">
              Define a claim
            </h2>

            <p className="mt-3 text-slate-600">
              Select what the claim includes:
              time window, members, symbols, and methodology.
            </p>

            <div className="mt-3 text-sm text-slate-500">
              → This defines the scope of what is being verified.
            </div>
          </div>

          {/* STEP 3 */}
          <div>
            <div className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
              Step 3
            </div>
            <h2 className="mt-2 text-2xl font-semibold">
              Generate evidence & metrics
            </h2>

            <p className="mt-3 text-slate-600">
              The system computes:
              equity curve, net PnL, win rate, drawdown,
              and full trade-level evidence.
            </p>

            <div className="mt-3 text-sm text-slate-500">
              → Everything becomes reproducible and auditable.
            </div>
          </div>

          {/* STEP 4 */}
          <div>
            <div className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
              Step 4
            </div>
            <h2 className="mt-2 text-2xl font-semibold">
              Verify and lock the claim
            </h2>

            <p className="mt-3 text-slate-600">
              Once finalized, the claim is cryptographically locked.
              A claim hash and trade-set fingerprint are generated.
            </p>

            <div className="mt-3 text-sm text-slate-500">
              → This ensures integrity and prevents tampering.
            </div>
          </div>

          {/* STEP 5 */}
          <div>
            <div className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
              Step 5
            </div>
            <h2 className="mt-2 text-2xl font-semibold">
              Publish public proof
            </h2>

            <p className="mt-3 text-slate-600">
              Each claim produces two surfaces:
            </p>

            <ul className="mt-3 space-y-2 text-slate-600">
              <li>• Public record (presentation layer)</li>
              <li>• Verification route (canonical proof layer)</li>
            </ul>

            <div className="mt-3 text-sm text-slate-500">
              → Anyone can independently verify the claim.
            </div>
          </div>

        </div>

        {/* SUMMARY */}
        <div className="mt-16 rounded-2xl border border-slate-200 bg-white p-6">
          <h3 className="text-lg font-semibold">What you get</h3>

          <div className="mt-4 space-y-2 text-slate-600 text-sm">
            <div>• Verifiable trading claims</div>
            <div>• Canonical trade ledger</div>
            <div>• Cryptographic integrity proofs</div>
            <div>• Public verification surfaces</div>
            <div>• Dispute-ready evidence</div>
          </div>
        </div>

      </div>
    </main>
  );
}