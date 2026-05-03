"use client";

import { useMemo, useState } from "react";
import { API_BASE_URL, getStoredAccessToken } from "../lib/api";

type Props = {
  claimSchemaId: number;
  claimHash?: string | null;
  payload?: unknown;
};

type DownloadKind = "json" | "zip" | "pdf";

function tryParseJson(text: string) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function resolveDevUserId(): string | null {
  if (typeof window === "undefined") return null;

  const fromQuery = new URLSearchParams(window.location.search).get("user_id");
  if (fromQuery) return fromQuery;

  return "1";
}

function buildAuthenticatedUrl(path: string) {
  const token = getStoredAccessToken();

  // ✅ FORCE API PREFIX
  const normalizedPath = path.startsWith("/api") ? path : `/api${path}`;

  if (token) {
    return `${API_BASE_URL}${normalizedPath}`;
  }

  const userId = resolveDevUserId();
  if (!userId) {
    return `${API_BASE_URL}${normalizedPath}`;
  }

  const separator = normalizedPath.includes("?") ? "&" : "?";
  return `${API_BASE_URL}${normalizedPath}${separator}user_id=${encodeURIComponent(userId)}`;
}

function buildHeaders() {
  const headers = new Headers();
  const token = getStoredAccessToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return headers;
}

function safeHashPrefix(claimHash?: string | null) {
  return claimHash ? `_${claimHash.slice(0, 12)}` : "";
}

function triggerBlobDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function downloadFromResponse(response: Response, fallbackFilename: string) {
  if (!response.ok) {
    let detail = "Download failed";

    try {
      const contentType = response.headers.get("content-type") || "";

      if (contentType.includes("application/json")) {
        const data = await response.json();
        if (typeof data?.detail === "string") {
          detail = data.detail;
        } else {
          detail = JSON.stringify(data);
        }
      } else {
        const text = await response.text();
        const parsed = tryParseJson(text);

        if (typeof parsed?.detail === "string") {
          detail = parsed.detail;
        } else if (text) {
          detail = text;
        }
      }
    } catch {
      detail = "Download failed";
    }

    throw new Error(detail);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition");
  const match = disposition?.match(/filename="(.+)"/);
  const filename = match?.[1] || fallbackFilename;

  triggerBlobDownload(blob, filename);
}

function DownloadCard({
  title,
  description,
  buttonLabel,
  loading,
  disabled,
  onClick,
}: {
  title: string;
  description: string;
  buttonLabel: string;
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-sm font-semibold text-slate-900">{title}</div>
          <div className="mt-2 text-xs leading-5 text-slate-600">{description}</div>
        </div>

        <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] font-semibold text-slate-600">
          {loading ? "preparing..." : "available"}
        </span>
      </div>

      <button
        type="button"
        onClick={onClick}
        disabled={disabled}
        className="mt-4 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Downloading..." : buttonLabel}
      </button>
    </div>
  );
}

export default function DownloadEvidenceButton({ claimSchemaId, claimHash, payload }: Props) {
  const [loadingKind, setLoadingKind] = useState<DownloadKind | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileHints = useMemo(
    () => ({
      json: `evidence_pack_claim_${claimSchemaId}${safeHashPrefix(claimHash)}.json`,
      zip: `evidence_bundle_claim_${claimSchemaId}${safeHashPrefix(claimHash)}.zip`,
      pdf: `claim_report_${claimSchemaId}${safeHashPrefix(claimHash)}.pdf`,
    }),
    [claimSchemaId, claimHash]
  );

  async function runDownload(kind: DownloadKind, action: () => Promise<void>) {
    try {
      setLoadingKind(kind);
      setError(null);
      await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    } finally {
      setLoadingKind(null);
    }
  }

  async function handleDownloadJson() {
    await runDownload("json", async () => {
      if (payload) {
        const json = JSON.stringify(payload, null, 2);
        const blob = new Blob([json], { type: "application/json" });
        triggerBlobDownload(blob, fileHints.json);
        return;
      }

      const response = await fetch(
        buildAuthenticatedUrl(`/claim-schemas/${claimSchemaId}/evidence-pack/download`),
        {
          method: "GET",
          headers: buildHeaders(),
          credentials: "include",
        }
      );

      await downloadFromResponse(response, fileHints.json);
    });
  }

  async function handleDownloadZip() {
    await runDownload("zip", async () => {
      const response = await fetch(
        buildAuthenticatedUrl(`/api/claim-schemas/${claimSchemaId}/evidence-bundle/download`),
        {
          method: "GET",
          headers: buildHeaders(),
          credentials: "include",
        }
      );

      await downloadFromResponse(response, fileHints.zip);
    });
  }

  async function handleDownloadPdf() {
    await runDownload("pdf", async () => {
      const response = await fetch(
        buildAuthenticatedUrl(`/claim-schemas/${claimSchemaId}/claim-report/download`),
        {
          method: "GET",
          headers: buildHeaders(),
          credentials: "include",
        }
      );

      await downloadFromResponse(response, fileHints.pdf);
    });
  }

  const anyLoading = loadingKind !== null;

  return (
    <div className="space-y-3">
      <div className="grid gap-3 lg:grid-cols-3">
        <DownloadCard
          title="Evidence JSON"
          description="Portable structured export of the evidence pack payload for downstream review, storage, or inspection."
          buttonLabel="Download Evidence JSON"
          loading={loadingKind === "json"}
          disabled={anyLoading}
          onClick={() => void handleDownloadJson()}
        />

        <DownloadCard
          title="Evidence ZIP Bundle"
          description="Packaged export including evidence pack, audit events, and manifest for archival or dispute-ready handoff."
          buttonLabel="Download Evidence ZIP"
          loading={loadingKind === "zip"}
          disabled={anyLoading}
          onClick={() => void handleDownloadZip()}
        />

        <DownloadCard
          title="Claim Report PDF"
          description="Presentation-grade verification report for internal review, trust presentation, and external credibility workflows."
          buttonLabel="Download Claim Report PDF"
          loading={loadingKind === "pdf"}
          disabled={anyLoading}
          onClick={() => void handleDownloadPdf()}
        />
      </div>

      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-sm font-semibold text-slate-900">Export naming</div>
        <div className="mt-3 grid gap-2 text-xs text-slate-600 md:grid-cols-3">
          <div className="rounded-xl bg-white p-3">
            <div className="font-medium text-slate-700">JSON</div>
            <div className="mt-1 break-all">{fileHints.json}</div>
          </div>
          <div className="rounded-xl bg-white p-3">
            <div className="font-medium text-slate-700">ZIP</div>
            <div className="mt-1 break-all">{fileHints.zip}</div>
          </div>
          <div className="rounded-xl bg-white p-3">
            <div className="font-medium text-slate-700">PDF</div>
            <div className="mt-1 break-all">{fileHints.pdf}</div>
          </div>
        </div>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}
    </div>
  );
}