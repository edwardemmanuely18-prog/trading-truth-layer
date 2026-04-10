"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { api } from "../../../lib/api";
import { useAuth } from "../../../components/AuthProvider";

type AcceptResult = {
  message: string;
  invite?: {
    id: number;
    workspace_id: number;
    email: string;
    role: string;
    token: string;
    status: string;
    accepted_at?: string | null;
    expires_at?: string | null;
  };
  user?: {
    id: number;
    email: string;
    name: string;
    role: string;
  };
  membership?: {
    workspace_id: number;
    user_id: number;
    role: string;
  };
};

function formatErrorMessage(raw: string) {
  const text = String(raw || "").trim();

  if (!text) return "Failed to accept invite.";

  if (text.includes("Invite has expired")) {
    return "This invite has expired.";
  }

  if (text.includes("already accepted")) {
    return "This invite has already been accepted.";
  }

  if (text.includes("Invite not found")) {
    return "This invite link is invalid, already used, or no longer available.";
  }

  if (text.includes("Authentication required")) {
    return "You need to sign in before accepting this invite.";
  }

  if (text.includes("Invite email does not match authenticated user")) {
    return "The invited email does not match the account currently signed in.";
  }

  try {
    const parsed = JSON.parse(text);
    const detail = parsed?.detail;

    if (typeof detail === "string") {
      return formatErrorMessage(detail);
    }
  } catch {
    // ignore json parse failure
  }

  return text;
}

function getErrorTone(message: string) {
  const lower = message.toLowerCase();

  if (lower.includes("already been accepted")) {
    return "amber";
  }

  if (lower.includes("expired") || lower.includes("invalid")) {
    return "red";
  }

  if (lower.includes("does not match")) {
    return "blue";
  }

  return "red";
}

export default function InviteAcceptPage() {
  const params = useParams();
  const router = useRouter();
  const { user, refresh, logout } = useAuth();

  const token = useMemo(() => {
    const raw = Array.isArray(params?.token) ? params.token[0] : params?.token;
    return raw ? String(raw) : "";
  }, [params]);

  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<AcceptResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function acceptInvite() {
      if (!token) {
        setError("Invalid invite token.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const accepted = (await api.acceptWorkspaceInvite(token)) as AcceptResult;
        setResult(accepted);
        await refresh();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to accept invite.";
        setError(formatErrorMessage(message));
      } finally {
        setLoading(false);
      }
    }

    void acceptInvite();
  }, [token, refresh]);

  const workspaceId = result?.membership?.workspace_id;
  const inviteEmail = result?.invite?.email || "";
  const currentUserEmail = user?.email || result?.user?.email || "";
  const errorTone = error ? getErrorTone(error) : "red";
  const isIdentityMismatch = Boolean(
    error && error.toLowerCase().includes("does not match")
  );

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
      <div className="mx-auto max-w-2xl rounded-2xl border bg-white p-8 shadow-sm">
        <div className="mb-6">
          <div className="text-sm text-slate-500">Trading Truth Layer</div>
          <h1 className="mt-2 text-3xl font-bold">Workspace Invite Acceptance</h1>
          <p className="mt-2 text-sm text-slate-600">
            Review and activate access for the workspace invite token.
          </p>
        </div>

        {loading ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            Accepting invite...
          </div>
        ) : error ? (
          <div className="space-y-6">
            <div
              className={`rounded-xl border p-5 text-sm ${
                errorTone === "amber"
                  ? "border-amber-200 bg-amber-50 text-amber-800"
                  : errorTone === "blue"
                  ? "border-blue-200 bg-blue-50 text-blue-800"
                  : "border-red-200 bg-red-50 text-red-700"
              }`}
            >
              <div className="mb-1 font-semibold">Invite could not be accepted</div>
              <div>{error}</div>
            </div>

            {isIdentityMismatch ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm">
                <div className="text-slate-500">Identity check</div>

                <div className="mt-3 space-y-2">
                  <div>
                    <span className="text-slate-500">Invited email:</span>{" "}
                    <span className="font-medium text-slate-900">
                      {inviteEmail || "Unknown"}
                    </span>
                  </div>

                  <div>
                    <span className="text-slate-500">Current signed-in account:</span>{" "}
                    <span className="font-medium text-slate-900">
                      {currentUserEmail || "No authenticated session detected"}
                    </span>
                  </div>
                </div>
              </div>
            ) : null}

            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
              {isIdentityMismatch
                ? "To accept this invite, sign in with the same email that received the invitation, or create that account first."
                : "Review the invite state, then continue with the correct authentication or workspace path."}
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => {
                  logout(`/login?redirect=/invite/${encodeURIComponent(token)}`);
                }}
                className="inline-flex rounded-xl bg-slate-900 px-5 py-2 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Sign out and sign in with invited account
              </button>

              <button
                type="button"
                onClick={() => {
                  const emailQuery = inviteEmail
                    ? `&email=${encodeURIComponent(inviteEmail)}`
                    : "";

                  logout(`/register?redirect=/invite/${encodeURIComponent(token)}${emailQuery}`);
                }}
                className="inline-flex rounded-xl border border-slate-300 px-5 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Sign out and create account with invited email
              </button>

              {user ? (
                <button
                  onClick={() => logout()}
                  className="inline-flex rounded-xl border border-slate-300 px-5 py-2 text-sm font-medium hover:bg-slate-50"
                >
                  Sign out current account
                </button>
              ) : null}

              <Link
                href="/"
                className="inline-flex rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Go to Home
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700">
              {result?.message || "Invite accepted successfully."}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-xl border bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Accepted Email</div>
                <div className="mt-2 font-medium">
                  {result?.user?.email || result?.invite?.email || "—"}
                </div>
              </div>

              <div className="rounded-xl border bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Workspace Role</div>
                <div className="mt-2 font-medium">{result?.membership?.role || "—"}</div>
              </div>

              <div className="rounded-xl border bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Workspace ID</div>
                <div className="mt-2 font-medium">
                  {result?.membership?.workspace_id || result?.invite?.workspace_id || "—"}
                </div>
              </div>

              <div className="rounded-xl border bg-slate-50 p-4">
                <div className="text-sm text-slate-500">Invite Status</div>
                <div className="mt-2 font-medium">{result?.invite?.status || "accepted"}</div>
              </div>
            </div>

            {workspaceId ? (
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => router.push(`/workspace/${workspaceId}/dashboard`)}
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                >
                  Open Workspace Dashboard
                </button>

                <button
                  onClick={() => router.push(`/workspace/${workspaceId}/members`)}
                  className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
                >
                  Open Members Page
                </button>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </main>
  );
}