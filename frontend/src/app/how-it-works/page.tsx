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
            Trading Truth Layer transforms raw trading activity into governed evidence, canonical verification, institutional reports, and independently verifiable public trust.

            Every published output is derived from the Trading Verification System (TVS), ensuring every metric, report, certificate, and public record originates from a single canonical evidence model rather than disconnected calculations.
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
                Trading Verification System (TVS)
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                Once a claim scope has been defined, the Trading Verification System becomes the canonical computation engine.

                TVS computes every metric, verification score, evidence artifact, report input, public record, and governance signal from a single immutable evidence snapshot.
              </p>
              <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
                <div className="text-sm font-medium text-slate-900">System effect</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Every downstream surface—including Claim Reports, Allocator Reports, Verification Certificates, Evidence Graphs and Public Verification Records—consumes the exact same canonical TVS output.

                  Nothing recomputes metrics independently.
                </p>
              </div>
              <div className="mt-4 text-sm text-slate-500">
                → TVS becomes the single source of truth for the entire platform.
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

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Step 5
                </div>

                <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                    Institutional Investigation System (IIS)
                </h3>

                <p className="mt-4 text-sm leading-7 text-slate-600">
                    After a claim has been verified and locked, Trading Truth Layer performs
                    an institutional investigation using the Institutional Investigation
                    System (IIS).

                    IIS consumes the canonical Trading Verification System outputs and
                    performs institutional reasoning across multiple investigation domains
                    including execution integrity, evidence quality, governance posture,
                    broker provenance, synchronization health, review coverage, behavioral
                    analysis, and allocator readiness.
                </p>

                <div className="mt-5 rounded-xl border border-slate-200 bg-white p-4">
                    <div className="text-sm font-medium text-slate-900">
                        System effect
                    </div>

                    <p className="mt-2 text-sm leading-6 text-slate-600">
                        The investigation produces institutional findings, allocator
                        recommendations, confidence scores, risk assessments and a final
                        allocator decision generated from a canonical investigation context.
                    </p>
                </div>

                <div className="mt-4 text-sm text-slate-500">
                    → IIS transforms verified trading records into institutional investment
                    intelligence suitable for allocators and professional reviewers.
                </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-6 lg:col-span-2">
              <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
                Step 6
              </div>
              <h3 className="mt-3 text-2xl font-semibold text-slate-950">
                Publish institutional trust
              </h3>
              <p className="mt-4 text-sm leading-7 text-slate-600">
                After verification, TTL separates presentation from verification.

                The public page is only one consumer of the canonical verification record.

                Institutional reports, allocators, auditors and external reviewers all consume the same governed evidence.
              </p>

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <div className="text-sm font-medium text-slate-500">
                    Public record
                  </div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">
                    Public Verification Record
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    Public-facing verification page exposing governed performance without exposing private operational evidence.
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-5">
                  <div className="text-sm font-medium text-slate-500">
                    Verification route
                  </div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">
                    Verification Certificate
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    Institutional verification certificate containing trust metrics, governance posture, verification score and canonical identifiers generated by the Verification Engine.
                  </p>
                </div>
              </div>

              <div className="mt-4 text-sm text-slate-500">
                → Every trust surface is generated from the same immutable verification record produced by TVS.
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
              Verification Certificate
            </h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Institutional certificate containing trust metrics,
              verification posture,
              governance score,
              integrity score
              and canonical identifiers.
            </p>

            <div className="mt-8 grid gap-4">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Public Verification Record</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Immutable public verification page exposing governed claim information backed by TVS.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Claim Report</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Professional report generated directly from verified evidence and canonical TVS outputs.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Allocator Due-Diligence Report</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Institutional investment report summarizing governance,
                  performance,
                  risk,
                  verification,
                  and evidence quality.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <div className="text-lg font-semibold text-slate-950">
                      Institutional Investigation Report
                  </div>

                  <p className="mt-2 text-sm leading-6 text-slate-600">
                      Institutional investigation output containing allocator decisions,
                      investigation findings, recommendations, risk assessments and
                      institutional readiness metrics generated by IIS.
                  </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                  Evidence Graph
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Visual relationship graph connecting trades,
                  evidence,
                  claims,
                  reports,
                  verification
                  and audit history.
                </p>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">Evidence Bundle</div>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  Governed archive containing evidence,
                  verification artifacts,
                  review history
                  and canonical exports.
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

        {/* INSTITUTIONAL ARCHITECTURE */}

        <div className="mt-14 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">

          <div className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
            Institutional Architecture
          </div>

          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
            Canonical services powering every verification
          </h2>

          <p className="mt-4 max-w-4xl text-base leading-7 text-slate-600">
            Trading Truth Layer is composed of institutional services operating on a
            shared canonical evidence model. Every report, verification result,
            governance score, public record, and trust surface is generated from the
            same underlying Trading Verification System rather than independent
            calculations.
          </p>

          <div className="mt-10 grid gap-4 md:grid-cols-2 xl:grid-cols-3">

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Trading Verification System (TVS)
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Canonical computation engine responsible for every metric,
                verification result, report input, and public trust record.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Verification Engine
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Produces institutional verification certificates, trust metrics,
                governance scores, integrity posture, and verification bands.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-lg font-semibold text-slate-950">
                    Institutional Investigation System (IIS)
                </div>

                <p className="mt-3 text-sm leading-6 text-slate-600">
                    Performs institutional investigations across multiple reasoning
                    domains to produce allocator decisions, institutional findings,
                    recommendations, investigation confidence scores and investment
                    readiness assessments.
                </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Evidence Registry
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Stores normalized trading evidence that serves as the foundation for
                every downstream verification workflow.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Evidence Graph
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Maintains traceable relationships between evidence, claims,
                verification, reports, governance history, and public trust records.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Reporting Engine
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Generates institutional Claim Reports, Allocator Reports,
                Verification Certificates, and executive documentation directly
                from TVS outputs.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-950">
                Public Verification Layer
              </div>

              <p className="mt-3 text-sm leading-6 text-slate-600">
                Publishes governed public verification records while protecting
                internal operational evidence and maintaining full traceability.
              </p>
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