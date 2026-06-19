"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

import Navbar from "../../../../../components/Navbar";
import { api } from "../../../../../lib/api";

export default function CreateClaimTemplatePage() {
  const params = useParams();

  const workspaceId = Number(
    params.workspaceId
  );

  const [loading, setLoading] =
    useState(false);

  const [name, setName] =
    useState("");

  const [description, setDescription] =
    useState("");

  const [templateType, setTemplateType] =
    useState("general");

  const [includedMembers, setIncludedMembers] =
    useState("");

  const [includedSymbols, setIncludedSymbols] =
    useState("");

  const [excludedTrades, setExcludedTrades] =
    useState("");

  const [methodologyNotes, setMethodologyNotes] =
    useState("");

  const [visibility] =
    useState("private");

  async function handleSave() {
    try {
      setLoading(true);

      await api.createClaimTemplate({
        workspace_id: workspaceId,

        name,

        description,

        template_type:
          templateType,

        included_member_ids_json:
          includedMembers
            .split(",")
            .map((x) =>
              Number(x.trim())
            )
            .filter(Boolean),

        included_symbols_json:
          includedSymbols
            .split(",")
            .map((x) =>
              x.trim()
            )
            .filter(Boolean),

        excluded_trade_ids_json:
          excludedTrades
            .split(",")
            .map((x) =>
              Number(x.trim())
            )
            .filter(Boolean),

        methodology_notes:
          methodologyNotes,

        visibility,

        active: true,
      });

      alert(
        "Template saved successfully"
      );

      window.location.href =
        `/workspace/${workspaceId}/claim-templates`;

    } catch (err) {
      console.error(err);

      alert(
        "Failed to save template"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar workspaceId={workspaceId} />

      <div className="mx-auto max-w-5xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Claim Operations
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Create Claim Template
          </h1>

          <p className="mt-3 text-slate-600">
            Define a reusable institutional
            claim blueprint that can later
            be applied directly inside the
            Claim Builder.
          </p>

        </div>

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

          <div className="grid gap-6">

            <div>

              <label className="mb-2 block text-sm font-medium">
                Template Name
              </label>

              <input
                value={name}
                onChange={(e) =>
                  setName(
                    e.target.value
                  )
                }
                className="w-full rounded-xl border px-4 py-3"
                placeholder="Monthly Verification Template"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">
                Description
              </label>

              <textarea
                value={description}
                onChange={(e) =>
                  setDescription(
                    e.target.value
                  )
                }
                rows={4}
                className="w-full rounded-xl border px-4 py-3"
                placeholder="Template description"
              />

            </div>

            <div className="grid gap-6 md:grid-cols-2">

              <div>

                <label className="mb-2 block text-sm font-medium">
                  Template Type
                </label>

                <input
                  value={templateType}
                  onChange={(e) =>
                    setTemplateType(
                      e.target.value
                    )
                  }
                  className="w-full rounded-xl border px-4 py-3"
                  placeholder="general"
                />

              </div>

              <div>
                <label className="mb-2 block text-sm font-medium">
                    Visibility
                </label>

                <input
                    value="Private"
                    disabled
                    className="w-full rounded-xl border bg-slate-100 px-4 py-3"
                />

                <p className="mt-2 text-sm text-slate-500">
                    Templates always create private draft claims.
                    Visibility is governed by the claim lifecycle.
                </p>
              </div>

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">
                Included Member IDs
              </label>

              <input
                value={includedMembers}
                onChange={(e) =>
                  setIncludedMembers(
                    e.target.value
                  )
                }
                className="w-full rounded-xl border px-4 py-3"
                placeholder="1,2,3"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">
                Included Symbols
              </label>

              <input
                value={includedSymbols}
                onChange={(e) =>
                  setIncludedSymbols(
                    e.target.value
                  )
                }
                className="w-full rounded-xl border px-4 py-3"
                placeholder="XAUUSD,EURUSD,GBPUSD"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">
                Excluded Trade IDs
              </label>

              <input
                value={excludedTrades}
                onChange={(e) =>
                  setExcludedTrades(
                    e.target.value
                  )
                }
                className="w-full rounded-xl border px-4 py-3"
                placeholder="12,45,88"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">
                Methodology Notes
              </label>

              <textarea
                value={methodologyNotes}
                onChange={(e) =>
                  setMethodologyNotes(
                    e.target.value
                  )
                }
                rows={6}
                className="w-full rounded-xl border px-4 py-3"
                placeholder="Verification methodology..."
              />

            </div>

            <div className="flex gap-3">

              <button
                onClick={handleSave}
                disabled={loading}
                className="rounded-xl bg-slate-900 px-6 py-3 text-white"
              >
                {loading
                  ? "Saving..."
                  : "Save Template"}
              </button>

              <Link
                href={`/workspace/${workspaceId}/claim-templates`}
                className="rounded-xl border px-6 py-3"
              >
                Cancel
              </Link>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

