import { loadLayout } from "./layoutPersistence";
import { loadSession } from "./sessionPersistence";

import { useUIStore } from "../../app/store/uiStore";
import { useWorkspaceStore } from "../../app/store/workspaceStore";

export function bootstrapRuntime() {
  const layout = loadLayout();

  const session = loadSession();

  useUIStore.setState({
    sidebarCollapsed:
      layout.sidebarCollapsed,
  });

  useWorkspaceStore.setState({
    activeWorkspace:
      session.lastWorkspace,
  });

  console.log(
    "TTL Runtime Bootstrapped"
  );
}