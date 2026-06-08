"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "../../lib/api";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");

    if (!token) {
      setError("Missing verification token");
      setLoading(false);
      return;
    }

    api
      .verifyEmail(token)
      .then((result) => {
        setStatus(result.status);
      })
      .catch((err) => {
        setError(
          err instanceof Error
            ? err.message
            : "Verification failed"
        );
      })
      .finally(() => {
        setLoading(false);
      });
  }, [searchParams]);

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-6">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">

        {loading && (
          <div>
            Verifying email...
          </div>
        )}

        {!loading && status === "verified" && (
          <>
            <h1 className="text-2xl font-bold">
              Email Verified
            </h1>

            <p className="mt-4">
              Your account has been verified successfully.
            </p>

            <a
              href="/login"
              className="mt-6 inline-block rounded-xl bg-slate-900 px-5 py-3 text-white"
            >
              Continue to Login
            </a>
          </>
        )}

        {!loading && status === "already_verified" && (
          <>
            <h1 className="text-2xl font-bold">
              Already Verified
            </h1>

            <a
              href="/login"
              className="mt-6 inline-block rounded-xl bg-slate-900 px-5 py-3 text-white"
            >
              Continue to Login
            </a>
          </>
        )}

        {!loading && error && (
          <>
            <h1 className="text-2xl font-bold text-red-600">
              Verification Failed
            </h1>

            <p className="mt-4">
              {error}
            </p>
          </>
        )}

      </div>
    </main>
  );
}