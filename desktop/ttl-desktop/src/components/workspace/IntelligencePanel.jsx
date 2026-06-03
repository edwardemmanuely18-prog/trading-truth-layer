function IntelligenceCard({
  label,
  value,
  description,
  valueClassName = "text-white",
}) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-800
        bg-[#0b1327]
        p-4
        flex
        flex-col
        gap-3
        shrink-0
      "
    >
      <p
        className="
          text-[11px]
          uppercase
          tracking-[0.25em]
          text-slate-500
        "
      >
        {label}
      </p>

      <h3
        className={`
          text-2xl xl:text-3xl
          font-black
          leading-none
          tracking-normal break-words
          ${valueClassName}
        `}
      >
        {value}
      </h3>

      <p
        className="
          text-sm
          leading-relaxed
          text-slate-400
        "
      >
        {description}
      </p>
    </div>
  );
}

export default function IntelligencePanel() {
  return (
    <div className="h-full p-4">
      <div
        className="
          flex
          h-full
          flex-col
          overflow-hidden
          rounded-2xl
          border
          border-slate-800
          bg-[#081028]
        "
      >
        {/* HEADER */}
        <div
          className="
            shrink-0
            border-b
            border-slate-800
            p-5
          "
        >
          <h2 className="text-2xl font-bold text-white">
            AI Intelligence
          </h2>

          <p
            className="
              mt-2
              text-sm
              leading-relaxed
              text-slate-400
            "
          >
            Institutional monitoring, runtime telemetry,
            market regime analysis, and AI orchestration.
          </p>
        </div>

        {/* SCROLLABLE CONTENT */}
        <div
          className="
            flex-1
            overflow-y-auto
            p-5
          "
        >
          <div className="flex flex-col gap-4">
            <IntelligenceCard
              label="Market Regime"
              value="HIGH
VOLATILITY"
              valueClassName="text-yellow-400"
              description="
Elevated cross-asset movement detected
across institutional liquidity zones.
              "
            />

            <IntelligenceCard
              label="AI Runtime"
              value="8 MODELS"
              valueClassName="text-emerald-400"
              description="
Ensemble inference engines synchronized
successfully across runtime clusters.
              "
            />

            <IntelligenceCard
              label="Risk Status"
              value="MODERATE"
              valueClassName="text-yellow-300"
              description="
Portfolio volatility remains within
institutional tolerance thresholds.
              "
            />

            <IntelligenceCard
              label="Liquidity"
              value="STABLE"
              valueClassName="text-cyan-400"
              description="
Cross-market liquidity conditions remain
operationally healthy.
              "
            />
          </div>
        </div>
      </div>
    </div>
  );
}