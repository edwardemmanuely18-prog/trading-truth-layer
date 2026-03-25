"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../components/AuthProvider";

declare global {
  interface Window {
    Paddle?: {
      Environment?: {
        set?: (value: string) => void;
      };
      Initialize?: (config: Record<string, unknown>) => void;
    };
  }
}

const PADDLE_SCRIPT_SRC = "https://cdn.paddle.com/paddle/v2/paddle.js";
const PADDLE_CLIENT_TOKEN = process.env.NEXT_PUBLIC_PADDLE_CLIENT_TOKEN || "";
const PADDLE_ENV = (process.env.NEXT_PUBLIC_PADDLE_ENV || "").trim().toLowerCase();

function SurfaceCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-semibold tracking-tight text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
    </div>
  );
}

export default function HomePage() {
  const { user, workspaces, loading, logout } = useAuth();

  const [checkoutBanner, setCheckoutBanner] = useState<string | null>(null);
  const [checkoutBannerTone, setCheckoutBannerTone] = useState<"info" | "success" | "error">("info");
  const [debugLines, setDebugLines] = useState<string[]>([]);

  const firstWorkspace = workspaces[0] ?? null;

  const primaryWorkspaceHref = useMemo(() => {
    if (!firstWorkspace) return null;
    return `/workspace/${firstWorkspace.workspace_id}/dashboard`;
  }, [firstWorkspace]);

  const checkoutHandledRef = useRef<string | null>(null);
  const paddleInitializedRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const debug: string[] = [];
    const url = new URL(window.location.href);
    const rawPtxn = url.searchParams.get("_ptxn");
    const rawLegacyPtxn = url.searchParams.get("ptxn");
    const transactionId = rawPtxn?.startsWith("txn_")
      ? rawPtxn
      : rawLegacyPtxn?.startsWith("txn_")
        ? rawLegacyPtxn
        : null;

    debug.push(`build=homepage-paddle-debug`);
    debug.push(`href=${window.location.href}`);
    debug.push(`raw__ptxn=${rawPtxn || "null"}`);
    debug.push(`raw_ptxn=${rawLegacyPtxn || "null"}`);
    debug.push(`transaction_id=${transactionId || "null"}`);
    debug.push(`token_present=${PADDLE_CLIENT_TOKEN ? "yes" : "no"}`);
    debug.push(`token_prefix=${PADDLE_CLIENT_TOKEN ? PADDLE_CLIENT_TOKEN.slice(0, 12) : "none"}`);
    debug.push(`env=${PADDLE_ENV || "unset"}`);

    setDebugLines(debug);

    if (!transactionId) {
      setCheckoutBannerTone("info");
      setCheckoutBanner("No Paddle transaction handoff detected on this page.");
      return;
    }

    if (checkoutHandledRef.current === transactionId) return;
    checkoutHandledRef.current = transactionId;

    if (!PADDLE_CLIENT_TOKEN) {
      setCheckoutBannerTone("error");
      setCheckoutBanner(
        "Paddle checkout handoff detected, but NEXT_PUBLIC_PADDLE_CLIENT_TOKEN is missing."
      );
      return;
    }

    const handlePaddleReady = () => {
      if (!window.Paddle?.Initialize) {
        setCheckoutBannerTone("error");
        setCheckoutBanner("Paddle.js loaded, but Paddle.Initialize is unavailable.");
        return;
      }

      if (paddleInitializedRef.current) {
        setCheckoutBannerTone("info");
        setCheckoutBanner("Paddle is already initialized.");
        return;
      }

      try {
        const tokenLooksSandbox = PADDLE_CLIENT_TOKEN.startsWith("test_");
        if ((PADDLE_ENV === "sandbox" || tokenLooksSandbox) && window.Paddle?.Environment?.set) {
          window.Paddle.Environment.set("sandbox");
        }

        window.Paddle.Initialize({
          token: PADDLE_CLIENT_TOKEN,
          eventCallback: (event: any) => {
            const eventName = String(event?.name || "").toLowerCase();

            setDebugLines((prev) => [...prev, `event=${eventName || "unknown"}`]);

            if (eventName === "checkout.loaded" || eventName === "checkout.opened") {
              setCheckoutBannerTone("info");
              setCheckoutBanner("Secure Paddle checkout opened.");
            }

            if (eventName === "checkout.closed") {
              setCheckoutBannerTone("info");
              setCheckoutBanner("Checkout was closed.");
            }

            if (eventName === "checkout.completed") {
              setCheckoutBannerTone("success");
              setCheckoutBanner("Checkout completed successfully.");
            }

            if (eventName === "checkout.error" || eventName === "checkout.failed") {
              setCheckoutBannerTone("error");
              setCheckoutBanner("Paddle checkout reported an error.");
            }
          },
          checkout: {
            settings: {
              displayMode: "overlay",
              theme: "light",
              locale: "en",
            },
          },
        });

        paddleInitializedRef.current = true;
        setCheckoutBannerTone("info");
        setCheckoutBanner("Paddle initialized. Waiting for checkout overlay...");
      } catch (error) {
        setCheckoutBannerTone("error");
        setCheckoutBanner(
          error instanceof Error
            ? `Failed to initialize Paddle.js: ${error.message}`
            : "Failed to initialize Paddle.js."
        );
      }
    };

    const existingScript = document.querySelector<HTMLScriptElement>(
      `script[src="${PADDLE_SCRIPT_SRC}"]`
    );

    if (existingScript) {
      setDebugLines((prev) => [...prev, "script=existing"]);
      if (window.Paddle?.Initialize) {
        handlePaddleReady();
      } else {
        existingScript.addEventListener("load", handlePaddleReady, { once: true });
        existingScript.addEventListener(
          "error",
          () => {
            setCheckoutBannerTone("error");
            setCheckoutBanner("Failed to load Paddle.js from CDN.");
          },
          { once: true }
        );
      }
      return;
    }

    setDebugLines((prev) => [...prev, "script=injecting"]);

    const script = document.createElement("script");
    script.src = PADDLE_SCRIPT_SRC;
    script.async = true;
    script.onload = () => {
      setDebugLines((prev) => [...prev, "script=loaded"]);
      handlePaddleReady();
    };
    script.onerror = () => {
      setDebugLines((prev) => [...prev, "script=error"]);
      setCheckoutBannerTone("error");
      setCheckoutBanner("Failed to load Paddle.js from CDN.");
    };
    document.head.appendChild(script);
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div>
            <div className="text-lg font-bold tracking-tight">Trading Truth Layer</div>
            <div className="text-sm text-slate-500">Verified Trading Claims OS</div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {loading ? (
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-500">
                Loading session...
              </div>
            ) : user ? (
              <>
                {primaryWorkspaceHref ? (
                  <Link
                    href={primaryWorkspaceHref}
                    className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
                  >
                    Open Workspace
                  </Link>
                ) : null}

                <button
                  onClick={logout}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-50"
                >
                  Sign Out
                </button>
              </>
            ) : null}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pt-6">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700 shadow-sm">
          PADDLE HANDOFF BUILD ACTIVE
        </div>
      </section>

      {checkoutBanner ? (
        <section className="mx-auto max-w-7xl px-6 pt-4">
          <div
            className={`rounded-2xl border p-4 text-sm shadow-sm ${
              checkoutBannerTone === "success"
                ? "border-green-200 bg-green-50 text-green-800"
                : checkoutBannerTone === "error"
                  ? "border-red-200 bg-red-50 text-red-700"
                  : "border-blue-200 bg-blue-50 text-blue-800"
            }`}
          >
            {checkoutBanner}
          </div>
        </section>
      ) : null}

      <section className="mx-auto max-w-7xl px-6 pt-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 text-xs text-slate-700 shadow-sm">
          <div className="font-semibold text-slate-900">Paddle debug</div>
          <div className="mt-2 space-y-1">
            {debugLines.map((line, index) => (
              <div key={`${line}-${index}`} className="break-all font-mono">
                {line}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-12">
        <h1 className="text-5xl font-bold tracking-tight">Verified Trading Claims OS</h1>
        <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-600">
          Broker-neutral verification infrastructure for trading communities, operators, and
          performance claims. Convert raw trading activity into canonical ledgers, standardized
          claims, verified leaderboards, and dispute-ready evidence packs.
        </p>

        <div className="mt-10 grid gap-4 md:grid-cols-3">
          <SurfaceCard
            title="Canonical Trade Ledger"
            description="Normalize imported trading activity into a durable, queryable source of truth."
          />
          <SurfaceCard
            title="Claims Schema Engine"
            description="Define exactly what is included in a performance claim, with clear methodology and exclusions."
          />
          <SurfaceCard
            title="Evidence Pack Generator"
            description="Export signed, dispute-ready claim artifacts with trade-set hashes and reproducible metrics."
          />
        </div>
      </section>
    </main>
  );
}