"use client";

import { FormEvent, Suspense, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "../../../lib/api";
import { useAuth } from "../../../components/AuthProvider";

type AcceptResult = {
  message?: string;
  invite?: {
    workspace_id?: number;
    email?: string;
    role?: string;
    status?: string;
  };
  membership?: {
    workspace_id?: number;
    user_id?: number;
    role?: string;
  };
  user?: {
    id?: number;
    email?: string;
    name?: string;
    role?: string;
  };
};

function extractErrorMessage(err: unknown): string {
  if (!(err instanceof Error)) {
    return "Failed to accept workspace invite.";
  }

  const raw = err.message || "Failed to accept workspace invite.";

  try {
    const parsed = JSON.parse(raw);
    if (typeof parsed?.detail === "string") {
      return parsed.detail;
    }
  } catch {
    // keep raw
  }

  return raw;
}

function AcceptInvitePageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isAuthenticated, refresh, workspaces, loading: authLoading } = useAuth();

  const tokenFromQuery = useMemo(
    () => searchParams.get("token") || searchParams.get("invite_token") || "",
    [searchParams]
  );

  const [token, setToken] = useState(tokenFromQuery);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AcceptResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const hasAutoAttemptedRef = useRef(false);

  useEffect(() => {
    setToken(tokenFromQuery);
  }, [tokenFromQuery]);

  async function acceptInvite(currentToken: string) {
    const accepted = (await api.acceptWorkspaceInvite(currentToken.trim())) as AcceptResult;
    await refresh();
    setResult(accepted);
    return accepted;
  }

  async function handleAccept(event?: FormEvent<HTMLFormElement>) {
    if (event) {
      event.preventDefault();
    }

    if (!isAuthenticated) {
      setError("You need to sign in before accepting an invite.");
      return;
    }

    if (!token.trim()) {
      setError("Invite token is required.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResult(null);
      await acceptInvite(token.trim());
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) return;
    if (!tokenFromQuery.trim()) return;
    if (result) return;
    if (loading) return;
    if (hasAutoAttemptedRef.current) return;

    hasAutoAttemptedRef.current = true;

    void (async () => {
      try {
        setLoading(true);
        setError(null);
        await acceptInvite(tokenFromQuery.trim());
      } catch (err) {
        setError(extractErrorMessage(err));
      } finally {
        setLoading(false);
      }
    })();
  }, [authLoading, isAuthenticated, tokenFromQuery, result, loading]);

  const acceptedWorkspaceId =
    result?.membership?.workspace_id || result?.invite?.workspace_id || null;

  const workspaceNowAvailable = acceptedWorkspaceId
    ? workspaces.some((w) => w.workspace_id === acceptedWorkspaceId)
    : false;

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
      <div className="mx-auto max-w-2xl rounded-2xl border bg-white p-8 shadow-sm">
        <div className="mb-6">
          <div className="text-sm text-slate-500">Trading Truth Layer</div>
          <h1 className="mt-2 text-3xl font-bold">Accept Workspace Invite</h1>
          <p className="mt-2 text-sm text-slate-600">
            Confirm and attach your account to a workspace using a valid invite token.
          </p>
        </div>

        {authLoading ? (
          <div className="mb-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            Checking session...
          </div>
        ) : !isAuthenticated ? (
          <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
            You need to sign in or create an account before accepting an invite.
            <div className="mt-3 flex flex-wrap gap-3">
              <Link
                href={token ? `/login?token=${encodeURIComponent(token)}` : "/login"}
                className="rounded-lg border border-amber-300 bg-white px-4 py-2 font-medium hover:bg-amber-100"
              >
                Sign In
              </Link>
              <Link
                href={token ? `/register?token=${encodeURIComponent(token)}` : "/register"}
                className="rounded-lg border border-amber-300 bg-white px-4 py-2 font-medium hover:bg-amber-100"
              >
                Create Account
              </Link>
            </div>
          </div>
        ) : (
          <div className="mb-6 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            Signed in as <span className="font-semibold">{user?.email || "unknown user"}</span>
          </div>
        )}

        {result ? (
          <div className="mb-6 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-800">
            <div className="font-semibold">
              {result.message || "Invite accepted successfully."}
            </div>
            <div className="mt-2">
              Workspace ID: <span className="font-medium">{acceptedWorkspaceId ?? "—"}</span>
            </div>
            <div className="mt-1">
              Role granted:{" "}
              <span className="font-medium">
                {result.membership?.role || result.invite?.role || "—"}
              </span>
            </div>

            {acceptedWorkspaceId ? (
              <div className="mt-4">
                <button
                  type="button"
                  onClick={() => router.push(`/workspace/${acceptedWorkspaceId}/dashboard`)}
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                >
                  {workspaceNowAvailable ? "Open Workspace Dashboard" : "Go to Workspace Dashboard"}
                </button>
              </div>
            ) : null}
          </div>
        ) : null}

        {error ? (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 break-words">
            {error}
          </div>
        ) : null}

        <form onSubmit={handleAccept} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">Invite Token</label>
            <textarea
              value={token}
              onChange={(e) => setToken(e.target.value)}
              rows={4}
              className="w-full rounded-xl border border-slate-300 px-4 py-3 font-mono text-sm outline-none focus:border-slate-500"
              placeholder="Paste workspace invite token here"
            />
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={loading || !isAuthenticated}
              className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {loading ? "Accepting Invite..." : "Accept Invite"}
            </button>

            <Link
              href="/login"
              className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold hover:bg-slate-50"
            >
              Go to Login
            </Link>
          </div>
        </form>
      </div>
    </main>
  );
}

export default function AcceptInvitePage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
          <div className="mx-auto max-w-2xl rounded-2xl border bg-white p-8 shadow-sm">
            Loading invite acceptance page...
          </div>
        </main>
      }
    >
      <AcceptInvitePageInner />
    </Suspense>
  );
}