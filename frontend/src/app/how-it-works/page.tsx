export default function HowItWorksPage() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="max-w-4xl">
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
            Trust Infrastructure Overview
          </div>

          <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
            How Trading Truth Layer Works
          </h1>

          <p className="mt-5 max-w-4xl text-lg leading-8 text-slate-600">
            Trading Truth Layer converts raw trading activity into governed claims,
            reproducible evidence, canonical integrity records, and public verification
            surfaces. The system is designed for serious operators, trading businesses,
            communities, allocators, institutional reviewers, and dispute-sensitive
            environments where correctness, auditability, and trust posture matter.
          </p>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-sm font-medium text-slate-500">Core posture</div>
            <div className="mt-2 text-xl font-semibold text-slate-950">
              Governance-first verification
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Claims are not treated as screenshots or informal summaries. They are
              structured records with scope, evidence, lifecycle controls, and integrity
              anchors.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-sm font-medium text-slate-500">System output</div>
            <div className="mt-2 text-xl font-semibold text-slate-950">
              Evidence-bearing records
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Each governed claim produces machine-readable evidence, human-readable
              reports, verification routes, audit history, and public trust surfaces.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-sm font-medium text-slate-500">Operational fit</div>
            <div className="mt-2 text-xl font-semibold text-slate-950">
              Built for real review workflows
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              The platform supports internal review, external credibility checks,
              public distribution, and dispute-ready evidence packaging without breaking
              traceability.
            </p>
          </div>
        </div>

        <div className="mt-14 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="max-w-3xl">
            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
              End-to-end lifecycle
            </div>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              From raw trade activity to public proof
            </h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              The platform follows a controlled lifecycle so every public output can be
              traced back to a defined scope, underlying evidence, and a locked integrity
              state.
            </p>
          </div>

          <div className="mt-10 grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Step 1
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Import trading data
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                Upload or stream trading activity into the platform using CSV imports,
                MT5 exports, IBKR-connected ingestion, manual entries, or webhook-based
                submission flows.
              </p>
              <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
                <div className="text-sm font-medium text-slate-900">System effect</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Imported activity is normalized into a canonical trade ledger so all
                  downstream claim computation starts from a consistent evidence base.
                </p>
              </div>
              <div className="mt-4 text-sm text-slate-500">
                → This creates the governed trade substrate used by claims, evidence packs,
                and audit review.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Step 2
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Define a claim
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                Create a structured claim by defining reporting period, included members,
                included symbols, exclusions, methodology notes, and exposure posture.
              </p>
              <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
                <div className="text-sm font-medium text-slate-900">System effect</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  The platform produces a deterministic scope definition so the claim can
                  be reviewed, recomputed, challenged, versioned, and later verified under
                  the same rules.
                </p>
              </div>
              <div className="mt-4 text-sm text-slate-500">
                → This defines exactly what is being asserted and what evidence belongs
                inside the claim boundary.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Step 3
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Generate evidence and metrics
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                Once the scope is defined, the system computes evidence-bearing claim
                outputs such as equity path, net PnL, win rate, profit factor, drawdown,
                trade-level inclusion or exclusion, and member-level leaderboard context.
              </p>
              <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
                <div className="text-sm font-medium text-slate-900">System effect</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Every visible number is tied back to the claim scope and underlying
                  ledger rows, making the record reproducible, explainable, and suitable
                  for internal or external review.
                </p>
              </div>
              <div className="mt-4 text-sm text-slate-500">
                → This transforms raw activity into inspectable evidence rather than a
                loose performance summary.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Step 4
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Verify and lock the claim
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                After review, the claim progresses through governed lifecycle transitions.
                Verification confirms the evidence snapshot, and locking finalizes the
                trade-set fingerprint and canonical claim hash.
              </p>
              <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
                <div className="text-sm font-medium text-slate-900">System effect</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  A locked claim becomes tamper-evident. Integrity checks can later confirm
                  that the published record still matches the stored evidence-bearing state.
                </p>
              </div>
              <div className="mt-4 text-sm text-slate-500">
                → This is the point where trust moves from internal review into durable
                verification posture.
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 lg:col-span-2">
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Step 5
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Publish public proof
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                A publishable claim can move into external trust surfaces. The platform
                separates presentation from proof so audiences can consume the record
                appropriately.
              </p>

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <div className="text-sm font-medium text-slate-500">
                    Public record
                  </div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">
                    Presentation layer
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    A clean public surface for distributing claim results, scope summary,
                    leaderboard highlights, and trust-facing outputs.
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <div className="text-sm font-medium text-slate-500">
                    Verification route
                  </div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">
                    Canonical proof layer
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    A direct integrity-oriented verification surface where third parties can
                    inspect canonical identifiers, fingerprints, and evidence posture.
                  </p>
                </div>
              </div>

              <div className="mt-4 text-sm text-slate-500">
                → External users can review the presentation layer while serious reviewers
                can move one step deeper into the proof layer.
              </div>
            </div>
          </div>
        </div>

        <div className="mt-14 grid gap-6 xl:grid-cols-2">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
              What the platform produces
            </div>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Governed outputs, not just charts
            </h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Each governed claim can produce multiple artifacts and trust surfaces. These
              outputs are designed for machine consumption, human review, archival storage,
              public distribution, and dispute resolution.
            </p>

            <div className="mt-8 grid gap-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Evidence JSON</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Portable machine-readable evidence payload containing structured claim
                  scope, evidence rows, metrics, hashes, and related metadata for systems,
                  automation, and downstream inspection.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Evidence ZIP bundle</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Packaged export for archival handoff, internal review, dispute handling,
                  or external delivery. Bundles can include evidence payloads, audit events,
                  manifests, and related claim artifacts.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Claim report PDF</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Presentation-grade document for committees, allocators, institutional
                  reviewers, clients, community operators, or formal review workflows that
                  require a stable human-readable report.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Hashes and integrity anchors
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Canonical claim hash and locked trade-set fingerprint establish
                  tamper-evident integrity posture and allow later confirmation that the
                  published claim still matches the stored record.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Audit timeline</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Lifecycle transitions, edits, publication changes, and lock-state
                  progression remain visible through audit history so trust can be supported
                  by chronology, not only by final numbers.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
              Review and trust model
            </div>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Why this system is different
            </h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Trading Truth Layer is not only an analytics display. It is a trust
              infrastructure layer built around correctness, determinism, governance, and
              explainability.
            </p>

            <div className="mt-8 space-y-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Deterministic scope definition
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Claims are defined by explicit scope rules, not by informal narrative.
                  That makes recomputation and independent review possible.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Evidence-first verification
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Metrics, equity paths, and rankings are generated from underlying evidence
                  rows, not detached from them. Every visible result should be explainable.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Lifecycle-governed publication
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Draft, verified, published, and locked states exist to preserve review
                  discipline and prevent silent mutation of public-facing records.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Public trust with internal traceability
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Public outputs are supported by internal evidence, audit records, and
                  integrity checks so external credibility does not rely on screenshots or
                  unverifiable summaries.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Dispute-ready posture
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Evidence packs, canonical exports, and reviewable histories support
                  challenge handling, investigation, and institutional review without losing
                  continuity.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-14 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
            What you get
          </div>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
            Institutional-grade outputs from a governed workflow
          </h2>

          <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Verifiable trading claims
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Structured records with scope, evidence, lifecycle, and integrity posture.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Canonical trade ledger
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                A normalized operational base for claims, evidence review, and downstream
                trust computation.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Reproducible evidence packs
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                JSON, ZIP, and supporting review artifacts for storage, transmission, and
                challenge handling.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Cryptographic integrity proofs
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Claim hashes and locked trade-set fingerprints to support tamper-evident
                trust posture.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Public verification surfaces
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Presentation and proof layers that separate public readability from deeper
                verification.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Governance and audit traceability
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Lifecycle history and evidence chronology for operators, institutions, and
                serious external reviewers.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}