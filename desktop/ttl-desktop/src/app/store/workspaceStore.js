import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useWorkspaceStore = create(
  persist(
    (set) => ({
      activeWorkspace: "dashboard",

      openWorkspaces: ["dashboard"],

      setActiveWorkspace: (workspace) =>
        set((state) => {
          const alreadyOpen =
            state.openWorkspaces.includes(workspace);

          return {
            activeWorkspace: workspace,
            openWorkspaces: alreadyOpen
              ? state.openWorkspaces
              : [...state.openWorkspaces, workspace],
          };
        }),

      closeWorkspaceTab: (workspace) =>
        set((state) => ({
          openWorkspaces:
            state.openWorkspaces.filter(
              (item) => item !== workspace
            ),
        })),

      resetWorkspaceState: () =>
        set({
          activeWorkspace: "dashboard",
          openWorkspaces: ["dashboard"],
        }),
    }),
    {
      name: "ttl-workspace-storage",
    }
  )
);