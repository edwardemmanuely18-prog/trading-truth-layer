export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#020817] text-white">
      <section className="max-w-7xl mx-auto px-8 py-32">
        <div className="max-w-4xl">
          <p className="text-cyan-400 font-semibold tracking-widest uppercase">
            Institutional Trading Infrastructure
          </p>

          <h1 className="text-7xl font-black leading-tight mt-6">
            Trading Truth Layer
          </h1>

          <p className="text-2xl text-slate-400 mt-8 leading-relaxed">
            AI-powered institutional-grade trading operating system
            designed for research orchestration, execution intelligence,
            portfolio monitoring, and market infrastructure analysis.
          </p>

          <div className="flex gap-6 mt-12">
            <a
              href="/download"
              className="px-8 py-4 rounded-2xl bg-cyan-500 text-black font-bold hover:bg-cyan-400 transition-all"
            >
              Download Desktop App
            </a>

            <a
              href="/pricing"
              className="px-8 py-4 rounded-2xl border border-slate-700 hover:border-cyan-400 transition-all"
            >
              View Pricing
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}