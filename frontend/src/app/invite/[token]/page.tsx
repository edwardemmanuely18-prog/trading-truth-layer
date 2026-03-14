"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../../../lib/api";

type PageProps = {
  params: Promise<{
    token: string;
  }>;
};

type AcceptResult = {
  message?: string;
  invite?: {
    id: number;
    workspace_id: number;
    email: string;
    role: string;
    status: string;
    accepted_at?: string | null;
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

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export default function InviteAcceptPage({ params }: PageProps) {
  const [token, setToken] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AcceptResult | null>(null);

  useEffect(() => {
    async function acceptInvite() {
      setLoading(true);
      setError(null);

      try {
        const resolved = await params;
        const inviteToken = resolved.token;
        setToken(inviteToken);

        const response = (await api.acceptWorkspaceInvite(inviteToken)) as AcceptResult;
        setResult(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to accept invite");
      } finally {
        setLoading(false);
      }
    }

    void acceptInvite();
  }, [params]);

  return (
    <div className="min-h-screen bg-slate-50 px-6 py-12 text-slate-900">
      <div className="mx-auto max-w-2xl">
        <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="mb-6">
            <Link href="/" className="text-sm text-slate-500 hover:underline">
              Trading Truth Layer
            </Link>
            <h1 className="mt-3 text-3xl font-bold">Workspace Invitation</h1>
            <p className="mt-2 text-slate-600">
              Accept your invitation to join a verified trading workspace.
            </p>
          </div>

          {loading ? (
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
              Accepting invite...
            </div>
          ) : error ? (
            <div className="space-y-4">
              <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700">
                <div className="font-semibold">Invite acceptance failed</div>
                <div className="mt-2 text-sm break-words">{error}</div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                <div className="text-sm text-slate-500">Token</div>
                <div className="mt-2 break-all rounded-xl bg-white p-3 font-mono text-xs text-slate-700 border border-slate-200">
                  {token || "—"}
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link
                  href="/dashboard"
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                >
                  Go to Dashboard
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 text-emerald-800">
                <div className="font-semibold">Invite accepted</div>
                <div className="mt-2 text-sm">
                  You are now a member of the workspace.
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <div className="text-sm text-slate-500">Invited Email</div>
                  <div className="mt-2 text-lg font-semibold">
                    {result?.invite?.email || "—"}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <div className="text-sm text-slate-500">Workspace Role</div>
                  <div className="mt-2 text-lg font-semibold">
                    {result?.membership?.role || result?.invite?.role || "—"}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <div className="text-sm text-slate-500">User Name</div>
                  <div className="mt-2 text-lg font-semibold">
                    {result?.user?.name || "—"}
                  </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <div className="text-sm text-slate-500">Accepted At</div>
                  <div className="mt-2 text-lg font-semibold">
                    {formatDateTime(result?.invite?.accepted_at)}
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <div className="text-sm text-slate-500">Invite Token</div>
                <div className="mt-2 break-all rounded-xl bg-slate-50 p-3 font-mono text-xs text-slate-700">
                  {token || "—"}
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <Link
                  href="/dashboard"
                  className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
                >
                  Go to Dashboard
                </Link>

                <Link
                  href="/claims"
                  className="rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-50"
                >
                  View Claims
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}