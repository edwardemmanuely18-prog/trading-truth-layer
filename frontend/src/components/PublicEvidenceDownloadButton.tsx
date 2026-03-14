"use client";

type Props = {
  claimSchemaId: number;
  payload: unknown;
};

export default function PublicEvidenceDownloadButton({ claimSchemaId, payload }: Props) {
  function handleDownload() {
    const json = JSON.stringify(payload, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `public_evidence_claim_${claimSchemaId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
  }

  return (
    <button
      type="button"
      onClick={handleDownload}
      className="rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800"
    >
      Download Public Evidence JSON
    </button>
  );
}