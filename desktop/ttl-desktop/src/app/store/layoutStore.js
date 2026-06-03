import { create } from "zustand";

export const useLayoutStore = create(
  (set) => ({
    layoutMode: "institutional",

    panels: {},

    setLayoutMode: (mode) =>
      set({
        layoutMode: mode,
      }),

    updatePanel: (id, config) =>
      set((state) => ({
        panels: {
          ...state.panels,
          [id]: config,
        },
      })),
  })
);