"use client";

import { API_BASE_URL } from "../lib/api";

type Props = {
  claimSchemaId: number;
  claimHash?: string | null;
  payload?: unknown;
};

async function downloadFromResponse(response: Response, fallbackFilename: string) {
  if (!response.ok) {
    throw new Error("Download failed");
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition");
  const match = disposition?.match(/filename="(.+)"/);
  const filename = match?.[1] || fallbackFilename;

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function DownloadEvidenceButton({ claimSchemaId, claimHash, payload }: Props) {
  async function handleDownloadJson() {
    if (payload) {
      const json = JSON.stringify(payload, null, 2);
      const blob = new Blob([json], { type: "application/json" });
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `evidence_pack_claim_${claimSchemaId}${claimHash ? `_${claimHash.slice(0, 12)}` : ""}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      URL.revokeObjectURL(url);
      return;
    }

    const response = await fetch(
      `${API_BASE_URL}/claim-schemas/${claimSchemaId}/evidence-pack/download`
    );

    await downloadFromResponse(
      response,
      `evidence_pack_claim_${claimSchemaId}${claimHash ? `_${claimHash.slice(0, 12)}` : ""}.json`
    );
  }

  async function handleDownloadZip() {
    const response = await fetch(
      `${API_BASE_URL}/claim-schemas/${claimSchemaId}/evidence-bundle/download`
    );

    await downloadFromResponse(
      response,
      `evidence_bundle_claim_${claimSchemaId}${claimHash ? `_${claimHash.slice(0, 12)}` : ""}.zip`
    );
  }

  async function handleDownloadPdf() {
    const response = await fetch(
      `${API_BASE_URL}/public/claim-schemas/${claimSchemaId}/claim-report/download`
    );

    await downloadFromResponse(
      response,
      `claim_report_${claimSchemaId}${claimHash ? `_${claimHash.slice(0, 12)}` : ""}.pdf`
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={() => void handleDownloadJson()}
        className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
      >
        Download Evidence JSON
      </button>

      <button
        type="button"
        onClick={() => void handleDownloadZip()}
        className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-50"
      >
        Download Evidence ZIP
      </button>

      <button
        type="button"
        onClick={() => void handleDownloadPdf()}
        className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-50"
      >
        Download Claim Report PDF
      </button>
    </div>
  );
}
