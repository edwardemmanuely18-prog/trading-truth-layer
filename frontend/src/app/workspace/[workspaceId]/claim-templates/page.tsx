"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "../../../../lib/api";

import Navbar from "../../../../components/Navbar";

export default function ClaimTemplatesPage() {

  const params = useParams();

  const workspaceId =
    Number(params.workspaceId);

  useEffect(() => {

    async function load() {

      try {

        const data =
          await api.getClaimPresets(
            workspaceId
          ) as any[];

        setTemplates(data);

      } catch (err) {

        console.error(err);

      } finally {

        setLoading(false);

      }

    }

    load();

  }, [workspaceId]);

  const [templates, setTemplates] =
    useState<any[]>([]);

  const [loading, setLoading] =
    useState(true);

  const totalTemplates =
    templates.length;

  const systemTemplates =
    templates.filter(
      (t) => t.is_system
    ).length;

  const workspaceTemplates =
    templates.filter(
      (t) => !t.is_system
    ).length;

  const activeTemplates =
    templates.length;

  return (
    <div className="min-h-screen bg-slate-50">

      <Navbar workspaceId={workspaceId} />

      <div className="mx-auto max-w-7xl px-6 py-10">

        <div className="mb-8">

          <div className="text-xs uppercase tracking-widest text-slate-500">
            Claim Operations
          </div>

          <h1 className="mt-2 text-4xl font-bold">
            Template Registry
          </h1>

          <p className="mt-3 max-w-4xl text-slate-600">
            Reusable institutional claim blueprints used
            to standardize verification workflows,
            methodology definitions, reporting periods,
            symbol universes, governance requirements,
            and recurring claim creation.
          </p>

        </div>

        <div className="mb-8 grid gap-4 md:grid-cols-4">

          <div className="rounded-2xl border bg-white p-6">

            <div className="text-sm text-slate-500">
              Total Templates
            </div>

            <div className="mt-2 text-4xl font-bold">
              {totalTemplates}
            </div>

          </div>

          <div className="rounded-2xl border bg-white p-6">

            <div className="text-sm text-slate-500">
              System Templates
            </div>

            <div className="mt-2 text-4xl font-bold">
              {systemTemplates}
            </div>

          </div>

          <div className="rounded-2xl border bg-white p-6">

            <div className="text-sm text-slate-500">
              Workspace Templates
            </div>

            <div className="mt-2 text-4xl font-bold">
              {workspaceTemplates}
            </div>

          </div>

          <div className="rounded-2xl border bg-white p-6">

            <div className="text-sm text-slate-500">
              Active Templates
            </div>

            <div className="mt-2 text-4xl font-bold">
              {activeTemplates}
            </div>

          </div>

        </div>

        <div className="mb-8 flex gap-3">

          <Link
            href={`/workspace/${workspaceId}/claim-templates/create`}
            className="rounded-xl bg-slate-900 px-5 py-3 text-white"
          >
            Create Template
          </Link>

          <Link
            href="/schema"
            className="rounded-xl border px-5 py-3"
          >
            Open Claim Builder
          </Link>

        </div>

        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">

          <table className="w-full">

            <thead className="border-b bg-slate-50">

              <tr>

                <th className="px-6 py-4 text-left">
                  Template
                </th>

                <th className="px-6 py-4 text-left">
                  Type
                </th>

                <th className="px-6 py-4 text-left">
                  Description
                </th>

                <th className="px-6 py-4 text-left">
                  Scope
                </th>

                <th className="px-6 py-4 text-left">
                  Status
                </th>

                <th className="px-6 py-4 text-left">
                  Actions
                </th>

              </tr>

            </thead>

            <tbody>

              {loading && (

                <tr>

                  <td
                    colSpan={6}
                    className="px-6 py-6"
                  >
                    Loading templates...
                  </td>

                </tr>

              )}

              {!loading &&
                templates.map(
                  (template) => (

                    <tr
                      key={template.id}
                      className="border-b"
                    >

                      <td className="px-6 py-4 font-medium">
                        {template.name}
                      </td>

                      <td className="px-6 py-4">
                        {template.preset_type}
                      </td>

                      <td className="px-6 py-4">
                        {template.description}
                      </td>

                      <td className="px-6 py-4">
                        {template.is_system
                          ? "System"
                          : "Workspace"}
                      </td>

                      <td className="px-6 py-4">
                        Active
                      </td>

                      <td className="px-6 py-4">

                        <Link
                          href={`/schema?presetId=${template.id}`}
                          className="rounded bg-slate-900 px-3 py-2 text-white"
                        >
                          Use Template
                        </Link>

                      </td>

                    </tr>

                  )
                )}

            </tbody>

          </table>

        </div>

        <div className="mt-8 rounded-2xl border bg-white p-8">

          <h2 className="text-2xl font-semibold">
            Institutional Template Lifecycle
          </h2>

          <div className="mt-6 grid gap-6 md:grid-cols-5">

            <div>
              <div className="font-semibold">
                1. Create Template
              </div>

              <div className="mt-2 text-sm text-slate-600">
                Define reusable claim blueprint.
              </div>
            </div>

            <div>
              <div className="font-semibold">
                2. Governance Review
              </div>

              <div className="mt-2 text-sm text-slate-600">
                Validate methodology and standards.
              </div>
            </div>

            <div>
              <div className="font-semibold">
                3. Save Registry
              </div>

              <div className="mt-2 text-sm text-slate-600">
                Store inside workspace template registry.
              </div>
            </div>

            <div>
              <div className="font-semibold">
                4. Apply Template
              </div>

              <div className="mt-2 text-sm text-slate-600">
                Auto-populate Claim Builder.
              </div>
            </div>

            <div>
              <div className="font-semibold">
                5. Verification Lifecycle
              </div>

              <div className="mt-2 text-sm text-slate-600">
                Draft → Verify → Publish → Lock.
              </div>
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}