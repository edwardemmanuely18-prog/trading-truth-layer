import { Command } from "cmdk";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

import { workspaceRegistry } from "../../workspaces/registry";
import { useUIStore } from "../../app/store/uiStore";

export default function CommandPalette() {
  const navigate = useNavigate();

  const commandPaletteOpen =
    useUIStore((state) => state.commandPaletteOpen);

  const closeCommandPalette =
    useUIStore((state) => state.closeCommandPalette);

  useEffect(() => {
    const down = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();

        useUIStore.setState({
          commandPaletteOpen: true,
        });
      }

      if (event.key === "Escape") {
        useUIStore.setState({
          commandPaletteOpen: false,
        });
      }
    };

    document.addEventListener("keydown", down);

    return () => document.removeEventListener("keydown", down);
  }, []);

  if (!commandPaletteOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-start justify-center pt-32">
      <Command className="w-[700px] rounded-2xl border border-slate-800 bg-[#081028] overflow-hidden shadow-2xl">
        <div className="border-b border-slate-800">
          <Command.Input
            autoFocus
            placeholder="Search workspaces, commands, AI systems..."
            className="w-full bg-transparent px-6 py-5 text-white outline-none text-lg"
          />
        </div>

        <Command.List className="max-h-[500px] overflow-auto p-3">
          <Command.Empty className="p-6 text-slate-400">
            No results found.
          </Command.Empty>

          <Command.Group heading="Workspaces">
            {workspaceRegistry.map((workspace) => (
              <Command.Item
                key={workspace.id}
                onSelect={() => {
                  navigate(workspace.route);
                  closeCommandPalette();
                }}
                className="px-4 py-3 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-white cursor-pointer transition-all"
              >
                {workspace.title}
              </Command.Item>
            ))}
          </Command.Group>
        </Command.List>
      </Command>
    </div>
  );
}