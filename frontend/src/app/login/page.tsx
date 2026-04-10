"use client";

import { FormEvent, Suspense, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "../../lib/api";
import { useAuth } from "../../components/AuthProvider";

const ACTIVE_WORKSPACE_KEY = "ttl_active_workspace_id";

function LoginPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh, user, workspaces, loading: authLoading, isAuthenticated } = useAuth();

  const inviteToken = useMemo(
    () => searchParams.get("token") || searchParams.get("invite_token"),
    [searchParams]
  );

  const redirect = useMemo(() => searchParams.get("redirect") || null, [searchParams]);

  const prefilledEmail = useMemo(() => searchParams.get("email") || "", [searchParams]);

  const [email, setEmail] = useState(prefilledEmail);
  const [password, setPassword] = useState("");

  const inviteRedirect = useMemo(() => {
    if (!inviteToken) return null;
    return `/invite/${encodeURIComponent(inviteToken)}`;
  }, [inviteToken]);

  const finalRedirect = useMemo(() => {
    if (redirect) return redirect;
    if (inviteRedirect) return inviteRedirect;
    return null;
  }, [redirect, inviteRedirect]);

  const registerHref = useMemo(() => {
    const params = new URLSearchParams();

    if (inviteToken) {
      params.set("token", inviteToken);
    }

    if (finalRedirect) {
      params.set("redirect", finalRedirect);
    }

    if (email.trim()) {
      params.set("email", email.trim());
    } else if (prefilledEmail.trim()) {
      params.set("email", prefilledEmail.trim());
    }

    const query = params.toString();
    return query ? `/register?${query}` : "/register";
  }, [inviteToken, finalRedirect, email, prefilledEmail]);

  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (prefilledEmail) {
      setEmail(prefilledEmail);
    }
  }, [prefilledEmail]);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated || !user) return;

    if (finalRedirect) {
      router.replace(finalRedirect);
      return;
    }

    const firstWorkspace = workspaces?.[0];
    if (firstWorkspace) {
      if (typeof window !== "undefined") {
        window.localStorage.setItem(
          ACTIVE_WORKSPACE_KEY,
          String(firstWorkspace.workspace_id)
        );
      }

      router.replace(`/workspace/${firstWorkspace.workspace_id}/dashboard`);
      return;
    }

    router.replace("/");
  }, [authLoading, isAuthenticated, user, finalRedirect, workspaces, router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();

    try {
      setLoading(true);
      setError(null);

      const result = await api.login({
        email: email.trim(),
        password,
      });

      await refresh();

      const firstWorkspace = result.workspaces?.[0];

      if (typeof window !== "undefined") {
        window.localStorage.removeItem(ACTIVE_WORKSPACE_KEY);

        if (firstWorkspace) {
          window.localStorage.setItem(
            ACTIVE_WORKSPACE_KEY,
            String(firstWorkspace.workspace_id)
          );
        }
      }

      if (finalRedirect) {
        router.push(finalRedirect);
        return;
      }

      if (firstWorkspace) {
        router.push(`/workspace/${firstWorkspace.workspace_id}/dashboard`);
      } else {
        router.push("/");
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed. Please check your details and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  if (authLoading) {
    return (
      <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
        <div className="mx-auto max-w-md rounded-2xl border bg-white p-8 shadow-sm">
          Loading session...
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
      <div className="mx-auto max-w-md rounded-2xl border bg-white p-8 shadow-sm">
        <div className="mb-6">
          <div className="text-sm text-slate-500">Trading Truth Layer</div>
          <h1 className="mt-2 text-3xl font-bold">Login</h1>
          <p className="mt-2 text-sm text-slate-600">
            Sign in to access your workspace operations surface.
          </p>
        </div>

        {inviteToken ? (
          <div className="mb-4 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
            Sign in with the invited email to continue to workspace invite acceptance.
          </div>
        ) : null}

        {redirect && !inviteToken ? (
          <div className="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            Sign in to continue to your requested page.
          </div>
        ) : null}

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="mb-2 block text-sm font-medium">Email</label>
            <input
              type="email"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">Password</label>
            <input
              type="password"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-slate-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error ? (
            <div className="break-words rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="mt-6 border-t pt-4 text-sm text-slate-600">
          Need an account?{" "}
          <Link href={registerHref} className="font-medium text-slate-900 hover:underline">
            Create one
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-slate-50 px-6 py-16 text-slate-900">
          <div className="mx-auto max-w-md rounded-2xl border bg-white p-8 shadow-sm">
            Loading login page...
          </div>
        </main>
      }
    >
      <LoginPageInner />
    </Suspense>
  );
}