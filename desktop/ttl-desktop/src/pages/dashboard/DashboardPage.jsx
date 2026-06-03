import WorkspaceGrid from "../../components/workspace/WorkspaceGrid";
import IntelligencePanel from "../../components/workspace/IntelligencePanel";
import ActivityConsole from "../../components/workspace/ActivityConsole";

function MetricCard({
  title,
  primary,
  secondary,
}) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-800
        bg-[#081028]
        p-6
        shadow-xl
        flex
        flex-col
        justify-between
        min-h-[230px]
      "
    >
      <div>
        <p className="text-sm uppercase tracking-[0.18em] text-slate-500">
          {title}
        </p>

        <div className="mt-6">
          <h3
            className="
              text-3xl
              xl:text-4xl
              font-bold
              leading-tight
              tracking-tight
              text-white
            "
          >
            {primary}
          </h3>

          <p
            className="
              mt-3
              text-lg
              font-medium
              tracking-[0.18em]
              uppercase
              text-slate-400
            "
          >
            {secondary}
          </p>
        </div>
      </div>
    </div>
  );
}

function WorkspaceRuntimePanel() {
  return (
    <div
      className="
        h-full
        rounded-2xl
        border
        border-dashed
        border-slate-700
        bg-[#050b1a]
        flex
        items-center
        justify-center
        text-slate-500
        text-lg
        tracking-[0.14em]
        uppercase
      "
    >
      Institutional Multi-Workspace Engine
    </div>
  );
}

function MainWorkspace() {
  return (
    <div className="flex h-full flex-col">
      {/* TOP METRICS */}
      <div className="grid grid-cols-3 gap-6 p-6">
        <MetricCard
          title="Market Intelligence"
          primary="24"
          secondary="Active Feeds"
        />

        <MetricCard
          title="AI Models"
          primary="8"
          secondary="Models Running"
        />

        <MetricCard
          title="Portfolio Exposure"
          primary="$2.4M"
          secondary="Simulated Exposure"
        />
      </div>

      {/* MAIN RUNTIME SURFACE */}
      <div className="flex-1 p-6 pt-0">
        <WorkspaceRuntimePanel />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <WorkspaceGrid
      main={<MainWorkspace />}
      side={<IntelligencePanel />}
      bottom={<ActivityConsole />}
    />
  );
}