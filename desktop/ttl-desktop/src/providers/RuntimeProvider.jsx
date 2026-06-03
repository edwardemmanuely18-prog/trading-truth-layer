import {
  createContext,
  useContext,
  useMemo,
} from "react";

import {
  useRuntimeStore,
} from "../core/runtime/store/runtimeStore";

const RuntimeContext = createContext(null);

export function RuntimeProvider({ children }) {
  const runtime = useRuntimeStore();

  const api = useMemo(() => {
    return {
      runtime,

      /*
      |------------------------------------------------------------------
      | WORKSPACE
      |------------------------------------------------------------------
      */

      setActiveWorkspace:
        runtime.setActiveWorkspace,

      /*
      |------------------------------------------------------------------
      | TABS
      |------------------------------------------------------------------
      */

      openTab: runtime.addTab,

      closeTab: runtime.closeTab,

      setActiveTab:
        runtime.setActiveTab,

      /*
      |------------------------------------------------------------------
      | NOTIFICATIONS
      |------------------------------------------------------------------
      */

      pushNotification:
        runtime.pushNotification,

      clearNotifications:
        runtime.clearNotifications,

      /*
      |------------------------------------------------------------------
      | LAYOUT
      |------------------------------------------------------------------
      */

      updateLayout:
        runtime.updateLayout,
    };
  }, [runtime]);

  return (
    <RuntimeContext.Provider value={api}>
      {children}
    </RuntimeContext.Provider>
  );
}

export function useRuntimeContext() {
  const context = useContext(RuntimeContext);

  if (!context) {
    throw new Error(
      "useRuntimeContext must be used inside RuntimeProvider"
    );
  }

  return context;
}