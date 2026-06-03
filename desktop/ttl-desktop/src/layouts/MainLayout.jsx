import {
  NavLink,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { useEffect } from "react";
import {
  PanelLeft,
  Bell,
  Search,
} from "lucide-react";

import { useWorkspaceStore } from "../app/store/workspaceStore";
import { useUIStore } from "../app/store/uiStore";

import CommandPalette from "../components/system/CommandPalette";

import WorkspaceTabs from "../components/system/WorkspaceTabs";

import { Outlet } from "react-router-dom";

import NotificationStack from "../components/system/NotificationStack";

import { navigation } from "../config/navigation";

import { useRuntimeWorkspaceStore } from "../app/store/runtimeWorkspaceStore";

import {
  pushNotification,
} from "../services/runtime/notificationRuntime";

export default function MainLayout() {
  const location = useLocation();

  const navigate = useNavigate();

  const setActiveWorkspace =
    useWorkspaceStore((state) => state.setActiveWorkspace);

  const sidebarCollapsed =
    useUIStore((state) => state.sidebarCollapsed);

  const toggleSidebar =
    useUIStore((state) => state.toggleSidebar);

  useEffect(() => {
    const currentWorkspace =
      navigation.find(
        (item) => item.route === location.pathname
      );

    if (currentWorkspace) {
      setActiveWorkspace(currentWorkspace.id);
    }
  }, [location.pathname, setActiveWorkspace]);

  return (
    <>
      <CommandPalette />

      <div className="h-screen w-screen bg-[#020817] text-white flex overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`
            border-r border-slate-800 bg-[#081028]
            flex flex-col transition-all duration-300
            ${
              sidebarCollapsed
                ? "w-20"
                : "w-64"
            }
          `}
        >
          {/* Logo */}
          <div className="h-24 px-5 flex items-center border-b border-slate-800">
            <div
              className={`
                transition-all duration-300
                ${sidebarCollapsed ? "hidden" : "block"}
              `}
            >
              <h1 className="text-2xl font-bold tracking-tight leading-tight">
                Trading Truth
                <br />
                Layer
              </h1>

              <p className="text-xs text-slate-400 mt-2">
                Institutional Trading OS
              </p>
            </div>

            {sidebarCollapsed && (
              <div className="w-full flex justify-center">
                <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center font-bold text-lg">
                  TTL
                </div>
              </div>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-auto">
            {navigation.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.id}
                  onClick={() => {
                    navigate(item.route);
                  }}
                  className={`
                    w-full
                    flex
                    items-center
                    ${
                      sidebarCollapsed
                        ? "justify-center px-0"
                        : "gap-3 px-4"
                    }
                    py-3
                    rounded-xl
                    transition-all
                    ${
                      location.pathname === item.route
                        ? "bg-slate-800 text-white"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                    }
                  `}
                >
                  <Icon size={20} />

                  {!sidebarCollapsed && (
                    <span>{item.label}</span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Bottom Status */}
          <div className="p-4 border-t border-slate-800">
            <div className="rounded-xl bg-slate-900 p-4">
              {!sidebarCollapsed && (
                <>
                  <p className="text-xs text-slate-400">
                    System Status
                  </p>

                  <div className="flex items-center gap-2 mt-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>

                    <span className="text-sm text-emerald-300">
                      Core Engines Active
                    </span>
                  </div>
                </>
              )}

              {sidebarCollapsed && (
                <div className="flex justify-center">
                  <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></div>
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* Main Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Top Bar */}
          <header className="h-20 border-b border-slate-800 bg-[#081028]/80 backdrop-blur-xl px-6 flex items-center justify-between">
            {/* Left Side */}
            <div className="flex items-center gap-4">
              <button
                onClick={toggleSidebar}
                className="w-11 h-11 rounded-xl border border-slate-700 bg-slate-900 hover:bg-slate-800 transition-all flex items-center justify-center"
              >
                <PanelLeft size={18} />
              </button>

              <div>
                <h2 className="text-xl font-semibold">
                  Institutional Workspace
                </h2>

                <p className="text-sm text-slate-500">
                  Trading Truth Layer Desktop Runtime
                </p>
              </div>
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-3">
              {/* Command Launcher */}
              <button
                onClick={() =>
                  useUIStore.setState({
                    commandPaletteOpen: true,
                  })
                }
                className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-900 hover:bg-slate-800 transition-all flex items-center gap-3 text-slate-400"
              >
                <Search size={16} />

                <span className="text-sm">
                  Search commands...
                </span>

                <div className="px-2 py-1 rounded-md bg-slate-800 text-xs">
                  CTRL + K
                </div>
              </button>

              {/* Notifications */}
              <button
                onClick={() => {
                  pushNotification({
                    title: "System Notification",
                    message: "TTL notification center operational.",
                    type: "info",
                  });
                }}
                className="w-11 h-11 rounded-xl border border-slate-700 bg-slate-900 hover:bg-slate-800 transition-all flex items-center justify-center relative"
              >
                <Bell size={18} />

                <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-emerald-400"></div>
              </button>

              {/* AI Status */}
              <div className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-900 flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>

                <span className="text-sm text-slate-300">
                  AI Models Online
                </span>
              </div>
            </div>
          </header>

          <WorkspaceTabs />

          <NotificationStack />

          {/* Workspace Area */}
          <section className="flex-1 overflow-auto bg-[#020817] p-6">
            <Outlet />
          </section>
        </main>
      </div>
    </>
  );
}