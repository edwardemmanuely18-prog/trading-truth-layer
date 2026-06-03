import { X } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useRuntimeWorkspaceStore } from "../../app/store/runtimeWorkspaceStore";

export default function WorkspaceTabs() {
  const navigate = useNavigate();

  const {
    openedTabs,
    activeWorkspace,
    setActiveWorkspace,
    closeWorkspace,
  } = useRuntimeWorkspaceStore();

  function handleOpen(tab) {
    setActiveWorkspace(tab.id);

    navigate(tab.route);
  }

  function handleClose(e, tab) {
    e.stopPropagation();

    closeWorkspace(tab.id);

    navigate("/");
  }

  return (
    <div className="flex items-center gap-3 overflow-x-auto">
      {openedTabs.map((tab) => {
        const active =
          activeWorkspace === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => handleOpen(tab)}
            className={`
              flex items-center gap-4
              min-w-[180px]
              px-5 py-4
              rounded-2xl border
              transition-all
              ${
                active
                  ? "bg-slate-800 border-slate-700 text-white"
                  : "bg-[#081028] border-slate-800 text-slate-400"
              }
            `}
          >
            <span className="font-medium">
              {tab.label}
            </span>

            <X
              size={16}
              onClick={(e) =>
                handleClose(e, tab)
              }
              className="opacity-60 hover:opacity-100"
            />
          </button>
        );
      })}
    </div>
  );
}