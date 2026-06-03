const events = [
  {
    id: 1,
    type: "AI",
    message:
      "Institutional inference engine synchronized.",
  },
  {
    id: 2,
    type: "MARKET",
    message:
      "24 market feeds connected successfully.",
  },
  {
    id: 3,
    type: "RISK",
    message:
      "Portfolio volatility monitoring initialized.",
  },
  {
    id: 4,
    type: "SYSTEM",
    message:
      "Workspace orchestration runtime operational.",
  },
];

export default function ActivityConsole() {
  return (
    <div className="h-full flex flex-col">
      <div className="px-5 py-4 border-b border-slate-800">
        <h2 className="text-lg font-semibold text-white">
          Activity Console
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          System events, execution logs, AI activity
        </p>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        {events.map((event) => (
          <div
            key={event.id}
            className="rounded-xl border border-slate-800 bg-slate-900 p-4"
          >
            <div className="flex items-center gap-3">
              <div className="px-2 py-1 rounded-md bg-slate-800 text-xs text-cyan-300">
                {event.type}
              </div>

              <p className="text-sm text-slate-300">
                {event.message}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}