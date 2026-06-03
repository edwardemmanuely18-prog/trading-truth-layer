import { create } from "zustand";

export const useRuntimeStore = create((set, get) => ({
  /*
  |--------------------------------------------------------------------------
  | WORKSPACE
  |--------------------------------------------------------------------------
  */

  activeWorkspace: "primary",

  setActiveWorkspace: (workspaceId) =>
    set({
      activeWorkspace: workspaceId,
    }),

  /*
  |--------------------------------------------------------------------------
  | RUNTIME TABS
  |--------------------------------------------------------------------------
  */

  tabs: [
    {
      id: "dashboard",
      label: "Dashboard",
      route: "/",
      closable: false,
    },

    {
      id: "markets",
      label: "Markets",
      route: "/markets",
      closable: true,
    },

    {
      id: "ai-research",
      label: "AI Research",
      route: "/ai-research",
      closable: true,
    },
  ],

  activeTab: "dashboard",

  setActiveTab: (tabId) =>
    set({
      activeTab: tabId,
    }),

  addTab: (tab) => {
    const exists = get().tabs.find((t) => t.id === tab.id);

    if (exists) {
      set({
        activeTab: tab.id,
      });

      return;
    }

    set({
      tabs: [...get().tabs, tab],
      activeTab: tab.id,
    });
  },

  closeTab: (tabId) => {
    const tabs = get().tabs;

    const target = tabs.find((t) => t.id === tabId);

    if (!target || !target.closable) {
      return;
    }

    const filtered = tabs.filter((t) => t.id !== tabId);

    set({
      tabs: filtered,
      activeTab: filtered[0]?.id || null,
    });
  },

  /*
  |--------------------------------------------------------------------------
  | NOTIFICATIONS
  |--------------------------------------------------------------------------
  */

  notifications: [],

  pushNotification: (notification) => {
    const item = {
      id: crypto.randomUUID(),
      title: notification.title || "System Notification",
      message: notification.message || "",
      type: notification.type || "info",
      createdAt: Date.now(),
    };

    set({
      notifications: [item, ...get().notifications],
    });

    setTimeout(() => {
      get().removeNotification(item.id);
    }, 5000);
  },

  removeNotification: (id) =>
    set({
      notifications: get().notifications.filter(
        (n) => n.id !== id
      ),
    }),

  clearNotifications: () =>
    set({
      notifications: [],
    }),

  /*
  |--------------------------------------------------------------------------
  | LAYOUT
  |--------------------------------------------------------------------------
  */

  layout: {
    leftSidebarCollapsed: false,
    rightPanelCollapsed: false,
    bottomPanelCollapsed: false,
  },

  updateLayout: (payload) =>
    set({
      layout: {
        ...get().layout,
        ...payload,
      },
    }),
}));