"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "../../lib/api";
import { useAuth } from "../../components/AuthProvider";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh, user, workspaces, loading: authLoading, isAuthenticated } = useAuth();

  const inviteToken = useMemo(
    () => searchParams.get("token") || searchParams.get("invite_token"),
    [searchParams]
  );

  const redirect = useMemo(
    () => searchParams.get("redirect") || null,
    [searchParams]
  );

  const [email, setEmail] = useState("owner@tradingtruthlayer.com");
  const [password, setPassword] = useState("OwnerPass123!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated || !user) return;

    if (inviteToken) {
      router.replace(`/invites/accept?token=${encodeURIComponent(inviteToken)}`);
      return;
    }

    if (redirect) {
      router.replace(redirect);
      return;
    }

    const firstWorkspace = workspaces?.[0];
    if (firstWorkspace) {
      router.replace(`/workspace/${firstWorkspace.workspace_id}/dashboard`);
      return;
    }

    router.replace("/");
  }, [authLoading, isAuthenticated, user, inviteToken, redirect, workspaces, router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();

    try {
      setLoading(true);
      setError(null);

      const result = await api.login({ email, password });
      await refresh();

      if (inviteToken) {
        router.push(`/invites/accept?token=${encodeURIComponent(inviteToken)}`);
        return;
      }

      if (redirect) {
        router.push(redirect);
        return;
      }

      const firstWorkspace = result.workspaces?.[0];
      if (firstWorkspace) {
        router.push(`/workspace/${firstWorkspace.workspace_id}/dashboard`);
      } else {
        router.push("/");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
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
            Sign in to accept your workspace invite after authentication.
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
              required
            />
          </div>

          {error ? (
            <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 break-words">
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
          <Link
            href={
              inviteToken
                ? `/register?token=${encodeURIComponent(inviteToken)}`
                : "/register"
            }
            className="font-medium text-slate-900 hover:underline"
          >
            Create one
          </Link>
        </div>
      </div>
    </main>
  );
}