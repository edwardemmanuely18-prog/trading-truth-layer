"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api, type AuthUser, type AuthWorkspace } from "../lib/api";

type AuthContextValue = {
  user: AuthUser | null;
  workspaces: AuthWorkspace[];
  loading: boolean;
  isAuthenticated: boolean;
  refresh: () => Promise<void>;
  logout: (redirectTo?: string) => void;
  getWorkspaceRole: (workspaceId: number) => string | null;
  hasWorkspaceRole: (workspaceId: number, roles: string[]) => boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [workspaces, setWorkspaces] = useState<AuthWorkspace[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const result = await api.getMe();
      setUser(result.user);
      setWorkspaces(Array.isArray(result.workspaces) ? result.workspaces : []);
    } catch {
      setUser(null);
      setWorkspaces([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback((redirectTo?: string) => {
    api.logout();
    setUser(null);
    setWorkspaces([]);

    if (typeof window !== "undefined") {
      window.location.href = redirectTo || "/login";
    }
  }, []);

  const getWorkspaceRole = useCallback(
    (workspaceId: number) => {
      const row = workspaces.find((w) => w.workspace_id === workspaceId);
      return row?.workspace_role || null;
    },
    [workspaces]
  );

  const hasWorkspaceRole = useCallback(
    (workspaceId: number, roles: string[]) => {
      const role = getWorkspaceRole(workspaceId);
      if (!role) return false;
      return roles.includes(role);
    },
    [getWorkspaceRole]
  );

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    function handleStorage(event: StorageEvent) {
      if (event.key === "ttl_access_token") {
        void refresh();
      }
    }

    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener("storage", handleStorage);
    };
  }, [refresh]);

  const value = useMemo(
    () => ({
      user,
      workspaces,
      loading,
      isAuthenticated: Boolean(user),
      refresh,
      logout,
      getWorkspaceRole,
      hasWorkspaceRole,
    }),
    [user, workspaces, loading, refresh, logout, getWorkspaceRole, hasWorkspaceRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}