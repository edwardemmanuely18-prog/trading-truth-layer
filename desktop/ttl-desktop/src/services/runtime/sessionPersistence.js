import { storageEngine } from "./storageEngine";

const SESSION_KEY = "runtime-session";

export function saveSession(session) {
  storageEngine.set(SESSION_KEY, session);
}

export function loadSession() {
  return storageEngine.get(SESSION_KEY, {
    authenticated: false,
    workspaces: [],
    lastWorkspace: "dashboard",
  });
}