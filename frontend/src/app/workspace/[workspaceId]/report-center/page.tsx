"use client";

import {
  api,
  apiFetch,
  apiDownload,
  type PublicClaimDirectoryItem,
  downloadClaimReportPdf,
  downloadEvidenceZip,
  downloadEvidenceJson,
} from "../../../../lib/api";

import {
    use,
    useEffect,
    useState,
} from "react";

import {
    useRouter,
} from "next/navigation";

import Navbar from "../../../../components/Navbar";

type Props = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default function Page(
  { params }: Props
) {
  const resolved = use(params);

  const workspaceId =
    Number(
      resolved.workspaceId
    );

  const router =
    useRouter();

  const [
    claims,
    setClaims,
  ] = useState<
    PublicClaimDirectoryItem[]
  >([]);

  const [
    selectedClaimId,
    setSelectedClaimId,
  ] = useState<number | null>(
    null
  );

  const [
    loadingAction,
    setLoadingAction,
  ] = useState<string | null>(
    null
  );

  const [
    successAction,
    setSuccessAction,
  ] = useState<string | null>(
    null
  );

  useEffect(() => {

    const loadClaims =
      async () => {

        try {

          const rows =
            await api.getWorkspaceClaims(
              workspaceId
            );

          setClaims(rows);

          if (
            rows.length > 0
          ) {

            const latest =
              [...rows].sort(
                (
                  a,
                  b
                ) =>
                  b.claim_schema_id -
                  a.claim_schema_id
              )[0];

            setSelectedClaimId(
              latest.claim_schema_id
            );
          }

        } catch (
          error: any
        ) {

          console.error(
            error
          );

          if (

            error?.payload?.code === "page_locked" ||

            error?.payload?.upgrade_required === true

          ) {

            router.replace(
              `/workspace/${workspaceId}/billing?upgrade=true`
            );

            return;

          }

          throw error;

        }
      };

    void loadClaims();

  }, [workspaceId]);

  const downloadJson = async (
      url: string,
      filename: string,
  ) => {

      const data = await apiFetch<any>(url);

      const blob = new Blob(
          [
              JSON.stringify(
                  data,
                  null,
                  2,
              ),
          ],
          {
              type: "application/json",
          },
      );

      const objectUrl =
          URL.createObjectURL(blob);

      const link =
          document.createElement("a");

      link.href = objectUrl;

      link.download = filename;

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      URL.revokeObjectURL(objectUrl);

  };

  const runDownload = async (
    actionId: string,
    action: () => Promise<void>,
  ) => {

    try {

      setLoadingAction(
        actionId
      );

      setSuccessAction(
        null
      );

      await action();

      setSuccessAction(
        actionId
      );

      setTimeout(
        () =>
          setSuccessAction(
            null
          ),
        3000
      );

    } catch (
      error: any
    ) {

      console.error(
        error
      );

      if (

        error?.payload?.code === "page_locked" ||

        error?.payload?.upgrade_required === true

      ) {

        router.replace(
          `/workspace/${workspaceId}/billing?upgrade=true`
        );

        return;

      }

      throw error;

    } finally {

      setLoadingAction(
        null
      );

    }
  };

  const selectedClaim =
    claims.find(
      claim =>
        claim.claim_schema_id ===
        selectedClaimId
    );

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-10">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Trust Intelligence
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Report Center
          </h1>

          <p className="mt-3 text-slate-600">
            Institutional export hub
            for allocator due diligence,
            claim verification,
            evidence exports and
            audit-ready reporting.
          </p>

        </div>

        {/* Allocator Report */}

        <div className="rounded-xl border bg-white p-6">

          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

            <div>

              <h2 className="text-xl font-semibold">
                Allocator Due Diligence Report
              </h2>

              <p className="mt-2 text-slate-600">
                Comprehensive institutional
                assessment covering
                performance,
                verification,
                evidence,
                trust,
                integrity,
                governance and allocator
                readiness.
              </p>

            </div>

            <div className="flex flex-row gap-3 shrink-0">

              <button
                onClick={() =>
                  runDownload(
                    "allocator-pdf",
                    async () => {

                      await apiDownload(
                          `/reports/workspace/${workspaceId}/allocator/download`,
                          `allocator_report_${workspaceId}.pdf`,
                      );

                    }
                  )
                }
                disabled={
                  loadingAction ===
                  "allocator-pdf"
                }
                className="rounded-lg border px-4 py-2"
              >

                {loadingAction ===
                "allocator-pdf"
                  ? "Downloading..."
                  : successAction ===
                    "allocator-pdf"
                    ? "Downloaded ✓"
                    : "Download PDF"}

              </button>

              <button
                onClick={() =>
                  runDownload(
                    "allocator-json",
                    async () =>
                      downloadJson(
                        `/api/reports/workspace/${workspaceId}/allocator`,
                        "allocator-report.json"
                      )
                  )
                }
                disabled={
                  loadingAction ===
                  "allocator-json"
                }
                className="rounded-lg border px-4 py-2"
              >

                {loadingAction ===
                "allocator-json"
                  ? "Downloading..."
                  : successAction ===
                    "allocator-json"
                    ? "Downloaded ✓"
                    : "Download JSON"}

              </button>

            </div>

          </div>

        </div>

        {/* Claim Exports */}

        <div className="mt-10 rounded-xl border bg-white p-6">

          <h2 className="text-xl font-semibold">
            Claim Exports
          </h2>

          <p className="mt-2 text-slate-600">
            Select a specific claim and
            export its verification
            artifacts, evidence package
            and PDF report.
          </p>

          <div className="mt-6">

            <label className="mb-2 block text-sm font-medium">

              Select Claim

            </label>

            <select
              value={
                selectedClaimId ??
                ""
              }
              onChange={
                event =>
                  setSelectedClaimId(
                    Number(
                      event.target
                        .value
                    )
                  )
              }
              className="w-full rounded-lg border p-3"
            >

              {claims.map(
                claim => (

                  <option
                    key={
                      claim.claim_schema_id
                    }
                    value={
                      claim.claim_schema_id
                    }
                  >
                    #{claim.claim_schema_id}
                    {" - "}
                    {claim.name}
                    {" - "}
                    {
                      claim.verification_status
                    }
                  </option>

                )
              )}

            </select>

          </div>

          {selectedClaim ? (

            <div className="mt-8">

              <div className="overflow-x-auto">

                <table className="min-w-full border">

                  <thead>

                    <tr className="bg-slate-100">

                      <th className="border px-4 py-2 text-left">
                        Claim ID
                      </th>

                      <th className="border px-4 py-2 text-left">
                        Name
                      </th>

                      <th className="border px-4 py-2 text-left">
                        Status
                      </th>

                      <th className="border px-4 py-2 text-left">
                        Net PnL
                      </th>

                      <th className="border px-4 py-2 text-left">
                        Win Rate
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    <tr>

                      <td className="border px-4 py-2">
                        {
                          selectedClaim.claim_schema_id
                        }
                      </td>

                      <td className="border px-4 py-2">
                        {
                          selectedClaim.name
                        }
                      </td>

                      <td className="border px-4 py-2">
                        {
                          selectedClaim.verification_status
                        }
                      </td>

                      <td className="border px-4 py-2">
                        {
                          selectedClaim.net_pnl
                        }
                      </td>

                      <td className="border px-4 py-2">
                        {(
                          selectedClaim.win_rate <= 1
                            ? selectedClaim.win_rate * 100
                            : selectedClaim.win_rate
                        ).toFixed(2)}%
                      </td>

                    </tr>

                  </tbody>

                </table>

              </div>

              <div className="mt-6 flex flex-wrap gap-3">

                <button
                  onClick={() =>
                    runDownload(
                      "claim-pdf",
                      async () =>
                        downloadClaimReportPdf(
                          selectedClaim.claim_schema_id
                        )
                    )
                  }
                  disabled={
                    loadingAction ===
                    "claim-pdf"
                  }
                  className="rounded-lg border px-4 py-2"
                >

                  {loadingAction ===
                  "claim-pdf"
                    ? "Downloading..."
                    : successAction ===
                      "claim-pdf"
                      ? "Downloaded ✓"
                      : "Download Claim Report PDF"}

                </button>

                <button
                  onClick={() =>
                    runDownload(
                      "evidence-json",
                      async () =>
                        downloadEvidenceJson(
                          selectedClaim.claim_schema_id
                        )
                    )
                  }
                  disabled={
                    loadingAction ===
                    "evidence-json"
                  }
                  className="rounded-lg border px-4 py-2"
                >

                  {loadingAction ===
                  "evidence-json"
                    ? "Downloading..."
                    : successAction ===
                      "evidence-json"
                      ? "Downloaded ✓"
                      : "Download Evidence JSON"}

                </button>

                <button
                  onClick={() =>
                    runDownload(
                      "evidence-zip",
                      async () =>
                        downloadEvidenceZip(
                          selectedClaim.claim_schema_id
                        )
                    )
                  }
                  disabled={
                    loadingAction ===
                    "evidence-zip"
                  }
                  className="rounded-lg border px-4 py-2"
                >

                  {loadingAction ===
                  "evidence-zip"
                    ? "Downloading..."
                    : successAction ===
                      "evidence-zip"
                      ? "Downloaded ✓"
                      : "Download Evidence ZIP"}

                </button>

                <a
                  href={`/workspace/${workspaceId}/evidence`}
                  className="rounded-lg border px-4 py-2"
                >
                  Evidence Registry
                </a>

              </div>

            </div>

          ) : (

            <div className="mt-6 text-sm text-slate-500">
              No claims available.
            </div>

          )}

        </div>

        {loadingAction && (

          <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-700">

            Preparing export package...

          </div>

        )}

        {successAction && (

          <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-700">

            Export downloaded successfully.

          </div>

        )}

      </div>

    </div>
  );
}