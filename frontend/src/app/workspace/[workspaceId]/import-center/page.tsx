"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getBrokerAdapters,
  getImportBatches,
  createImportPreview,
  BrokerAdapter,
  ImportBatch,
  confirmImportPreview,
} from "../../../../lib/api";



type ImportPreviewData = {
  preview_session_id: number;
  status: string;

  preview: {
    workspace_id: number;
    source_type: string;

    rows_received: number;
    rows_accepted: number;
    rows_rejected: number;
    rows_duplicates: number;

    normalized_preview: any[];
    rejected_preview: any[];
    duplicate_preview: any[];
  };

  message: string;
};


function mapAdapterToSourceType(
  adapter: string
) {
  switch (adapter) {

    case "csv_import":
      return "csv";

    case "interactive_brokers":
      return "ibkr";

    case "metatrader_5":
      return "mt5";

    case "mt5":
      return "mt5";

    case "ibkr":
      return "ibkr";

    default:
      return "auto";
  }
}

export default function ImportCenterPage() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const [adapters, setAdapters] =
    useState<BrokerAdapter[]>([]);

  const [batches, setBatches] =
    useState<ImportBatch[]>([]);

  const [selectedAdapter,
    setSelectedAdapter] =
      useState("");

  const [error, setError] =
    useState("");

  const [selectedFile,
    setSelectedFile] =
      useState<File | null>(null);

  const [previewResult,
    setPreviewResult] =
      useState<ImportPreviewData | null>(null);

  const [confirming, setConfirming] =
    useState(false);

  const [successMessage, setSuccessMessage] =
    useState<string | null>(null);

  const [importResultBanner, setImportResultBanner] =
    useState<{
      type: "success" | "warning" | "error";
      message: string;
    } | null>(null);

  async function load() {
    try {
      setLoading(true);

      const [
        adapterData,
        batchData,
      ] = await Promise.all([
        getBrokerAdapters(workspaceId),
        getImportBatches(workspaceId),
      ]);

      const operationalAdapters =
        adapterData.filter(
          (adapter) =>
            [
              "csv_import",
              "interactive_brokers",
              "ibkr",
              "metatrader_5",
              "mt5",
            ].includes(
              adapter.provider.toLowerCase()
            )
        );

      setAdapters(operationalAdapters);
      setBatches(batchData as ImportBatch[]);

      if (
        adapterData.length &&
        !selectedAdapter
      ) {
        setSelectedAdapter(
          adapterData[0].provider
        );
      }
    } catch (err: any) {
      setError(
        err?.message ??
        "Failed loading import center"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (workspaceId) {
      load();
    }
  }, [workspaceId]);

  function handleFileSelect(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file =
      event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);
  }

  const preview =
    previewResult?.preview;

  const acceptanceRate =
    preview
      ? (
          (preview.rows_accepted /
            Math.max(
              preview.rows_received,
              1
            )) *
          100
        ).toFixed(1)
      : "0";

  const rejectionRate =
    preview
      ? (
          (preview.rows_rejected /
            Math.max(
              preview.rows_received,
              1
            )) *
          100
        ).toFixed(1)
      : "0";

  const duplicateRate =
    preview
      ? (
          (preview.rows_duplicates /
            Math.max(
              preview.rows_received,
              1
            )) *
          100
        ).toFixed(1)
      : "0";

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

        <div className="mx-auto max-w-7xl px-6 py-10 space-y-8">

        {importResultBanner && (

          <div
            className={`
              rounded-xl
              p-4
              border
              ${
                importResultBanner.type === "success"
                  ? "bg-green-50 border-green-200 text-green-700"
                  : importResultBanner.type === "warning"
                  ? "bg-amber-50 border-amber-200 text-amber-700"
                  : "bg-red-50 border-red-200 text-red-700"
              }
            `}
          >
            {importResultBanner.message}
          </div>

        )}

        <div className="rounded-2xl border bg-white p-8">
          <h1 className="text-4xl font-bold">
            Import Center
          </h1>

          <p className="mt-4 text-slate-600">
            Institutional-grade evidence
            ingestion pipeline for
            broker exports, CSV files,
            historical account data,
            and third-party trading
            records.
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        )}

        <div className="rounded-2xl border bg-white p-8">
          <h2 className="text-2xl font-semibold">
            Create Import Job
          </h2>

          <div className="mt-6 grid gap-6 md:grid-cols-2">

            <div>
              <label className="block text-sm font-medium">
                Adapter
              </label>

              <select
                className="mt-2 w-full rounded-lg border p-3"
                value={selectedAdapter}
                onChange={(e) =>
                  setSelectedAdapter(
                    e.target.value
                  )
                }
              >
                {adapters.map(
                  (adapter) => (
                    <option
                      key={
                        adapter.id
                      }
                      value={
                        adapter.provider
                      }
                    >
                      {
                        adapter.display_name
                      }
                    </option>
                  )
                )}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium">
                Evidence File
              </label>

              <label
                className="
                  mt-2
                  flex
                  h-40
                  cursor-pointer
                  items-center
                  justify-center
                  rounded-xl
                  border-2
                  border-dashed
                  border-slate-300
                  bg-slate-50
                "
              >
                <div className="text-center">

                  <p className="font-medium">
                    Upload Evidence File
                  </p>

                  <p className="mt-2 text-sm text-slate-500">
                    MT5 • IBKR • CSV
                  </p>

                  {selectedFile && (
                    <p className="mt-4 text-green-700">
                      {selectedFile.name}
                    </p>
                  )}

                </div>

                <input
                  type="file"
                  className="hidden"
                  onChange={
                    handleFileSelect
                  }
                />
              </label>
            </div>

          </div>

          <div className="md:col-span-2">

            <button
              disabled={
                !selectedFile ||
                uploading
              }
              className="
                rounded-lg
                bg-slate-900
                px-5
                py-3
                text-white
                disabled:opacity-50
              "
              onClick={async () => {
                if (!selectedFile)
                  return;

                try {
                  setUploading(true);

                  console.log("ADAPTER PROVIDER:", selectedAdapter);

                  const preview =
                    await createImportPreview(
                      workspaceId,
                      mapAdapterToSourceType(
                        selectedAdapter
                      ),
                      selectedFile
                    );

                  console.log(
                    "Selected Adapter:",
                    selectedAdapter
                  );

                  console.log(preview);

                  setPreviewResult(
                    preview as ImportPreviewData
                  );

                  await load();

                } catch (err: any) {

                  alert(
                    err?.message ??
                    "Preview failed"
                  );

                } finally {

                  setUploading(false);

                }
              }}
            >
              Generate Preview
            </button>

          </div>
        </div>

        {previewResult && preview && (

        <div className="space-y-6">

          <div className="rounded-2xl border bg-white p-8">

            <h2 className="text-2xl font-semibold">
              Import Preview
            </h2>

            <p className="mt-2 text-slate-500">
              Preview Session #
              {previewResult.preview_session_id}
            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-4">

              <div className="rounded-xl border p-4">
                <div className="text-sm text-slate-500">
                  Rows Received
                </div>

                <div className="mt-2 text-3xl font-bold">
                  {preview.rows_received}
                </div>
              </div>

              <div className="rounded-xl border p-4">
                <div className="text-sm text-slate-500">
                  Accepted
                </div>

                <div className="mt-2 text-3xl font-bold text-green-700">
                  {preview.rows_accepted}
                </div>
              </div>

              <div className="rounded-xl border p-4">
                <div className="text-sm text-slate-500">
                  Rejected
                </div>

                <div className="mt-2 text-3xl font-bold text-red-700">
                  {preview.rows_rejected}
                </div>
              </div>

              <div className="rounded-xl border p-4">
                <div className="text-sm text-slate-500">
                  Duplicates
                </div>

                <div className="mt-2 text-3xl font-bold text-amber-600">
                  {preview.rows_duplicates}
                </div>
              </div>

            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">

              <div className="rounded-xl bg-slate-50 p-4">
                <div className="text-sm text-slate-500">
                  Acceptance Rate
                </div>

                <div className="mt-2 text-2xl font-bold">
                  {acceptanceRate}%
                </div>
              </div>

              <div className="rounded-xl bg-slate-50 p-4">
                <div className="text-sm text-slate-500">
                  Rejection Rate
                </div>

                <div className="mt-2 text-2xl font-bold">
                  {rejectionRate}%
                </div>
              </div>

              <div className="rounded-xl bg-slate-50 p-4">
                <div className="text-sm text-slate-500">
                  Duplicate Rate
                </div>

                <div className="mt-2 text-2xl font-bold">
                  {duplicateRate}%
                </div>
              </div>

              <button
                disabled={confirming}
                className="
                  rounded-lg
                  bg-green-700
                  px-5
                  py-3
                  text-white
                  disabled:opacity-50
                  disabled:cursor-not-allowed
                "
                onClick={async () => {

                  if (!previewResult) return;

                  try {

                    setConfirming(true);

                    const result: any =
                      await confirmImportPreview(
                        workspaceId,
                        previewResult.preview_session_id
                      );

                    if (
                      result.rows_imported > 0 &&
                      result.rows_duplicates === 0 &&
                      result.rows_rejected === 0
                    ) {

                      setImportResultBanner({
                        type: "success",
                        message:
                          `Successfully imported ${result.rows_imported} trades`,
                      });

                    } else if (
                      result.rows_duplicates > 0 &&
                      result.rows_imported === 0
                    ) {

                      setImportResultBanner({
                        type: "warning",
                        message:
                          `${result.rows_duplicates} duplicate trades skipped`,
                      });

                    } else if (
                      result.rows_rejected > 0 &&
                      result.rows_imported === 0
                    ) {

                      setImportResultBanner({
                        type: "error",
                        message:
                          `${result.rows_rejected} trades rejected`,
                      });

                    } else {

                      setImportResultBanner({
                        type: "warning",
                        message:
                          `Imported ${result.rows_imported}, Rejected ${result.rows_rejected}, Duplicates ${result.rows_duplicates}`,
                      });

                    }

                    setTimeout(() => {
                      setImportResultBanner(null);
                    }, 6000);

                    setPreviewResult(null);

                    await load();

                  } catch (err: any) {

                    alert(
                      err?.message ??
                      "Import confirmation failed"
                    );

                  } finally {

                    setConfirming(false);

                  }

                }}
              >
                {confirming
                  ? "Confirming..."
                  : "Confirm Import"}
              </button>

            </div>

          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-4">

            <div className="rounded-xl border p-4">
              <div className="text-sm text-slate-500">
                Evidence Source
              </div>

              <div className="mt-2 font-semibold">
                {preview.source_type.toUpperCase()}
              </div>
            </div>

            <div className="rounded-xl border p-4">
              <div className="text-sm text-slate-500">
                Trust Tier
              </div>

              <div className="mt-2 font-semibold">
                Tier 2
              </div>
            </div>

            <div className="rounded-xl border p-4">
              <div className="text-sm text-slate-500">
                Verification State
              </div>

              <div className="mt-2 font-semibold">
                Preview Generated
              </div>
            </div>

            <div className="rounded-xl border p-4">
              <div className="text-sm text-slate-500">
                Evidence Status
              </div>

              <div className="mt-2 font-semibold">
                Pending Confirmation
              </div>
            </div>

          </div>

          <div className="overflow-hidden rounded-2xl border bg-white">

            <div className="border-b bg-slate-50 px-6 py-4">
              <h2 className="font-semibold">
                Normalized Trade Preview
              </h2>
            </div>

            <div className="overflow-auto">

              <table className="w-full">

                <thead>

                  <tr className="border-b">

                    <th className="p-4 text-left">
                      Symbol
                    </th>

                    <th className="p-4 text-left">
                      Side
                    </th>

                    <th className="p-4 text-left">
                      Qty
                    </th>

                    <th className="p-4 text-left">
                      Entry
                    </th>

                    <th className="p-4 text-left">
                      Exit
                    </th>

                    <th className="p-4 text-left">
                      Opened
                    </th>

                  </tr>

                </thead>

                <tbody>

                {preview.normalized_preview.map(
                  (
                    trade,
                    index
                  ) => (

                  <tr
                    key={index}
                    className="border-b"
                  >

                    <td className="p-4">
                      {trade.symbol}
                    </td>

                    <td className="p-4">
                      {trade.side}
                    </td>

                    <td className="p-4">
                      {trade.quantity}
                    </td>

                    <td className="p-4">
                      {trade.entry_price}
                    </td>

                    <td className="p-4">
                      {trade.exit_price}
                    </td>

                    <td className="p-4">
                      {trade.opened_at}
                    </td>

                  </tr>

                ))}

                </tbody>

              </table>

            </div>

          </div>

          {preview.rejected_preview.length > 0 && (

          <div className="overflow-hidden rounded-2xl border border-red-200 bg-white">

            <div className="border-b bg-red-50 px-6 py-4">
              <h2 className="font-semibold text-red-700">
                Rejected Records
              </h2>
            </div>

            <table className="w-full">

              <thead>

                <tr className="border-b">

                  <th className="p-4 text-left">
                    Symbol
                  </th>

                  <th className="p-4 text-left">
                    Side
                  </th>

                  <th className="p-4 text-left">
                    Quantity
                  </th>

                  <th className="p-4 text-left">
                    Reason
                  </th>

                </tr>

              </thead>

              <tbody>

                {preview.rejected_preview.map(
                  (item, index) => (

                  <tr
                    key={index}
                    className="border-b"
                  >

                    <td className="p-4">
                      {item.row?.symbol ||
                      item.row?.Symbol ||
                      "-"}
                    </td>

                    <td className="p-4">
                      {item.row?.side ||
                      item.row?.Side ||
                      item.row?.Action ||
                      "-"}
                    </td>

                    <td className="p-4">
                      {item.row?.quantity ||
                      item.row?.Quantity ||
                      "-"}
                    </td>

                    <td className="p-4 text-red-700">
                      {item.reason}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

          )}

          {preview.duplicate_preview.length > 0 && (

          <div className="overflow-hidden rounded-2xl border border-amber-200 bg-white">

            <div className="border-b bg-amber-50 px-6 py-4">
              <h2 className="font-semibold text-amber-700">
                Duplicate Records
              </h2>
            </div>

            <table className="w-full">

              <thead>

                <tr className="border-b">

                  <th className="p-4 text-left">
                    Symbol
                  </th>

                  <th className="p-4 text-left">
                    Side
                  </th>

                  <th className="p-4 text-left">
                    Fingerprint
                  </th>

                </tr>

              </thead>

              <tbody>

                {preview.duplicate_preview.map(
                  (item, index) => (

                  <tr
                    key={index}
                    className="border-b"
                  >

                    <td className="p-4">
                      {item.row?.symbol ||
                      item.row?.Symbol ||
                      "-"}
                    </td>

                    <td className="p-4">
                      {item.row?.side ||
                      item.row?.Side ||
                      "-"}
                    </td>

                    <td className="p-4 font-mono text-xs">
                      {item.fingerprint}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

          )}
        </div>

        )}

        <div className="overflow-hidden rounded-2xl border bg-white">

          <div className="border-b bg-slate-50 px-6 py-4">
            <h2 className="font-semibold">
              Evidence Import Ledger
            </h2>
          </div>

          {loading ? (
              <div className="p-8">
                Loading jobs...
              </div>
          ) : (

            <div className="max-h-[600px] overflow-auto">

              <table className="w-full min-w-[1000px]">
                <thead className="sticky top-0 bg-white z-10">
                  <tr className="border-b bg-slate-50">
                    <th className="p-4 text-left">
                      Adapter
                    </th>

                    <th className="p-4 text-left">
                      File
                    </th>

                    <th className="p-4 text-left">
                      Status
                    </th>

                    <th className="p-4 text-left">
                      Received
                    </th>

                    <th className="p-4 text-left">
                      Imported
                    </th>

                    <th className="p-4 text-left">
                      Rejected
                    </th>

                    <th className="p-4 text-left">
                      Duplicates
                    </th>

                    <th className="p-4 text-left">
                      Created
                    </th>
                  </tr>
                </thead>

              <tbody>

                {batches.map(
                  (batch) => (
                    <tr
                      key={batch.id}
                      className="border-b"
                    >
                      <td className="p-4">
                        {batch.source_type}
                      </td>

                      <td className="p-4">
                        {batch.filename}
                      </td>

                      <td className="p-4">
                        <span className="rounded-full bg-green-100 px-2 py-1 text-xs text-green-700">
                          completed
                        </span>
                      </td>

                      <td className="p-4">
                        {batch.rows_received}
                      </td>

                      <td className="p-4">
                        {batch.rows_imported}
                      </td>

                      <td className="p-4 text-red-700">
                        {batch.rows_rejected}
                      </td>

                      <td className="p-4 text-amber-600">
                        {batch.rows_skipped_duplicates}
                      </td>

                      <td className="p-4">
                        {batch.created_at
                          ? new Date(
                              batch.created_at
                            ).toLocaleString()
                          : "-"}
                      </td>
                    </tr>
                  )
                )}

                {!batches.length && (
                  <tr>
                    <td
                      colSpan={8}
                      className="p-10 text-center text-slate-500"
                    >
                      No import jobs yet.
                    </td>
                  </tr>
                )}

              </tbody>
            </table>

            </div>

            )}
        </div>

      </div>
    </div>
  );
}