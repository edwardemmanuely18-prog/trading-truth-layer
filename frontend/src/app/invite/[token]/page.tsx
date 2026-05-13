"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { api } from "../../../lib/api";

export default function InviteAcceptancePage() {
  const params = useParams();
  const router = useRouter();

  const rawToken = Array.isArray(params?.token)
    ? params.token[0]
    : params?.token;

  const token = decodeURIComponent(String(rawToken || ""))
    .trim()
    .replace(/\s+/g, "");

  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setError("Invite token missing");
      setLoading(false);
      return;
    }

    const acceptInvite = async () => {
      try {
        console.log("FINAL TOKEN:", token);

        const response = await api.acceptWorkspaceInvite(
          encodeURIComponent(token)
        );

        console.log("INVITE ACCEPT RESPONSE:", response);

        setSuccess(true);

        setTimeout(() => {
          router.push("/");
        }, 1500);
      } catch (err: any) {
        console.error(err);

        setError(
          err?.message ||
            "This invite link is invalid, already used, or no longer available."
        );
      } finally {
        setLoading(false);
      }
    };

    acceptInvite();
  }, [token, router]);

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="max-w-xl w-full border rounded-3xl p-10">
        <p className="text-sm text-slate-500 mb-4">
          Trading Truth Layer
        </p>

        <h1 className="text-5xl font-bold mb-6">
          Workspace Invite Acceptance
        </h1>

        <p className="text-slate-600 mb-8">
          Review and activate access for the workspace invite token.
        </p>

        {loading && (
          <div className="border rounded-2xl p-6 bg-slate-50">
            Processing workspace invite...
          </div>
        )}

        {!loading && success && (
          <div className="border border-green-300 bg-green-50 rounded-2xl p-6">
            <h2 className="font-semibold text-green-700 mb-2">
              Invite accepted successfully
            </h2>

            <p className="text-green-700">
              Redirecting to workspace...
            </p>
          </div>
        )}

        {!loading && error && (
          <div className="border border-red-300 bg-red-50 rounded-2xl p-6">
            <h2 className="font-semibold text-red-700 mb-2">
              Invite could not be accepted
            </h2>

            <p className="text-red-700">
              {error}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}