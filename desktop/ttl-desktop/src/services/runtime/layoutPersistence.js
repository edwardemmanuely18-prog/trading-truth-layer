import { storageEngine } from "./storageEngine";

const LAYOUT_KEY = "workspace-layout";

export function saveLayout(layout) {
  storageEngine.set(LAYOUT_KEY, layout);
}

export function loadLayout() {
  return storageEngine.get(LAYOUT_KEY, {
    sidebarCollapsed: false,
    activeTabs: ["dashboard"],
  });
}