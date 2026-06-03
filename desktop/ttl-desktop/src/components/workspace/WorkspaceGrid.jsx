export default function WorkspaceGrid({
  main,
  side,
  bottom,
}) {
  return (
    <div
      className="
        h-full
        w-full
        overflow-hidden
        flex
        flex-col
        gap-3
      "
    >
      {/* =========================================
          TOP WORKSPACE SURFACE
      ========================================= */}
      <div
        className="
          grid
          grid-cols-12
          gap-3
          h-[68%]
        	min-h-[520px]
          flex-shrink-0
        "
      >
        {/* MAIN WORKSPACE */}
        <div
          className="
            col-span-9
            overflow-hidden
            rounded-2xl
            border
            border-slate-800
            bg-[#081028]
          "
        >
          {main}
        </div>

        {/* AI / INTELLIGENCE PANEL */}
        <div
          className="
            col-span-3
            overflow-hidden
            rounded-2xl
            border
            border-slate-800
            bg-[#081028]
          "
        >
          {side}
        </div>
      </div>

      {/* =========================================
          BOTTOM ACTIVITY CONSOLE
      ========================================= */}
      <div
        className="
          flex-1
          min-h-[180px]
					max-h-[240px]
          overflow-hidden
          rounded-2xl
          border
          border-slate-800
          bg-[#081028]
        "
      >
        {bottom}
      </div>
    </div>
  );
}