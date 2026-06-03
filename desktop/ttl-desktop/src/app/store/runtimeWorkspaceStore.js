import { create } from "zustand";

export const useRuntimeWorkspaceStore = create((set) => ({
  activeWorkspace: "dashboard",

  openedTabs: [
    {
      id: "dashboard",
      label: "Dashboard",
      route: "/",
    },

    {
      id: "markets",
      label: "Markets",
      route: "/markets",
    },

    {
      id: "ai-research",
      label: "AI Research",
      route: "/ai-research",
    },
  ],

  setActiveWorkspace: (workspace) =>
    set({
      activeWorkspace: workspace,
    }),

  openWorkspace: (workspace) =>
    set((state) => {
      const exists = state.openedTabs.find(
        (tab) => tab.id === workspace.id
      );

      if (exists) {
        return {
          activeWorkspace: workspace.id,
        };
      }

      return {
        openedTabs: [...state.openedTabs, workspace],
        activeWorkspace: workspace.id,
      };
    }),

  closeWorkspace: (workspaceId) =>
    set((state) => {
      const filtered = state.openedTabs.filter(
        (tab) => tab.id !== workspaceId
      );

      return {
        openedTabs: filtered,
        activeWorkspace:
          filtered[0]?.id || null,
      };
    }),
}));