import { create } from "zustand";

export const useAuthStore = create((set) => ({
  user: null,

  authenticated: false,

  token: null,

  login: ({ user, token }) =>
    set({
      user,
      token,
      authenticated: true,
    }),

  logout: () =>
    set({
      user: null,
      token: null,
      authenticated: false,
    }),
}));