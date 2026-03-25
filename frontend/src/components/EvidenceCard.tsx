"use client";

import { useMemo, useState } from "react";

type Props = {
  title: string;
  value: string;
  subtitle?: string;
};

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!value) return;
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  }

  return (
    <button
      type="button"
      onClick={() => void handleCopy()}
      disabled={!value}
      className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

export default function EvidenceCard({ title, value, subtitle }: Props) {
  const [expanded, setExpanded] = useState(false);

  const safeValue = value || "";
  const lines = useMemo(() => safeValue.split("\n"), [safeValue]);
  const lineCount = safeValue ? lines.length : 0;
  const charCount = safeValue.length;

  const shouldCollapse = lineCount > 18;
  const displayValue =
    shouldCollapse && !expanded ? lines.slice(0, 18).join("\n") : safeValue;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
            {lineCount} line{lineCount === 1 ? "" : "s"} · {charCount} char
          </div>
          <CopyButton value={safeValue} />
        </div>
      </div>

      <pre className="mt-4 overflow-x-auto whitespace-pre-wrap break-words rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
        {displayValue || "—"}
      </pre>

      {shouldCollapse ? (
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-500">
            Showing {expanded ? "full content" : "first 18 lines"}.
          </div>

          <button
            type="button"
            onClick={() => setExpanded((prev) => !prev)}
            className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            {expanded ? "Collapse" : "Expand"}
          </button>
        </div>
      ) : null}
    </section>
  );
}