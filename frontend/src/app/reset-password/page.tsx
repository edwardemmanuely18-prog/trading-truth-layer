"use client";

export const dynamic = "force-dynamic";

import {
  FormEvent,
  useState,
  useEffect,
} from "react";

import { api } from "../../lib/api";



export default function ResetPasswordPage() {

  const [token, setToken] = useState("");

  useEffect(() => {
  const params = new URLSearchParams(
      window.location.search
  );

  setToken(
      params.get("token") || ""
  );
  }, []);

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [success, setSuccess] =
    useState(false);

  const [error, setError] =
    useState("");

  async function onSubmit(
    e: FormEvent
  ) {
    e.preventDefault();

    try {
      setLoading(true);
      setError("");

      await api.resetPassword({
        token,
        password,
      });

      setSuccess(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Reset failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-6">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">

        <h1 className="text-3xl font-bold">
          Reset Password
        </h1>

        {success ? (
          <>
            <div className="mt-6 rounded-xl border border-green-200 bg-green-50 p-4 text-green-700">
              Password updated successfully.
            </div>

            <a
              href="/login"
              className="mt-6 inline-block rounded-xl bg-slate-900 px-5 py-3 text-white"
            >
              Login
            </a>
          </>
        ) : (
          <form
            onSubmit={onSubmit}
            className="mt-6 space-y-4"
          >
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="New Password"
              className="w-full rounded-xl border px-4 py-3"
            />

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-slate-900 px-5 py-3 text-white"
            >
              {loading
                ? "Updating..."
                : "Update Password"}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}