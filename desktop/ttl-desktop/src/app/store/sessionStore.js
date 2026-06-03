import { create } from "zustand";

export const useSessionStore = create(
  (set) => ({
    authenticated: false,

    user: null,

    sessionLoaded: false,

    setAuthenticated: (value) =>
      set({
        authenticated: value,
      }),

    setUser: (user) =>
      set({
        user,
      }),

    setSessionLoaded: (value) =>
      set({
        sessionLoaded: value,
      }),
  })
);