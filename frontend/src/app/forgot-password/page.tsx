"use client";

import { FormEvent, useState } from "react";
import { api } from "../../lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();

    try {
      setLoading(true);
      setError("");

      await api.forgotPassword({
        email: email.trim(),
      });

      setSent(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to process request"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-6">
      <div className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm">

        <h1 className="text-3xl font-bold">
          Forgot Password
        </h1>

        <p className="mt-2 text-slate-600">
          Enter your email address and we'll send a password reset link.
        </p>

        {sent ? (
          <div className="mt-6 rounded-xl border border-green-200 bg-green-50 p-4 text-green-700">
            If an account exists for that email,
            a reset link has been sent.
          </div>
        ) : (
          <form
            onSubmit={onSubmit}
            className="mt-6 space-y-4"
          >
            <input
              type="email"
              required
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              placeholder="Email"
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
                ? "Sending..."
                : "Send Reset Link"}
            </button>
          </form>
        )}
      </div>
    </main>
  );
}