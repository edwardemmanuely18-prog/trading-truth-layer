import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useUIStore = create(
  persist(
    (set) => ({
      sidebarCollapsed: false,

      commandPaletteOpen: false,

      notifications: [],

      toggleSidebar: () =>
        set((state) => ({
          sidebarCollapsed: !state.sidebarCollapsed,
        })),

      openCommandPalette: () =>
        set({
          commandPaletteOpen: true,
        }),

      closeCommandPalette: () =>
        set({
          commandPaletteOpen: false,
        }),

      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            notification,
            ...state.notifications,
          ],
        })),

      clearNotifications: () =>
        set({
          notifications: [],
        }),
    }),
    {
      name: "ttl-ui-storage",
    }
  )
);