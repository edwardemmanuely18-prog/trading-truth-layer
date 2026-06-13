import { API_BASE_URL } from "./api";

const API_URL = API_BASE_URL;

function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem(
    "ttl_access_token"
  );
}

async function aurumFetch(
  endpoint: string
) {
  const token = getAccessToken();

  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      headers: {
        "Content-Type":
          "application/json",

        ...(token
          ? {
              Authorization:
                `Bearer ${token}`,
            }
          : {}),
      },

      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(
      `Aurum API error ${response.status}`
    );
  }

  return response.json();
}

export const aurumApi = {
  overview: () =>
    aurumFetch("/aurum/overview"),

  users: () =>
    aurumFetch("/aurum/users"),

  workspaces: () =>
    aurumFetch("/aurum/workspaces"),

  claims: () =>
    aurumFetch("/aurum/claims"),
};