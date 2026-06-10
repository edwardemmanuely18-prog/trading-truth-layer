"use client";

import { useEffect, useState } from "react";
import AurumNav from "../../../components/AurumNav";

export default function WorkspacesPage() {
  const [rows, setRows] =
    useState<any[]>([]);

  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/aurum/workspaces`
    )
      .then(async (r) => {
        const data = await r.json();

        if (Array.isArray(data)) {
          setRows(data);
        } else {
          setRows([]);
        }
      })
      .catch(() => {
        setRows([]);
      });
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-7xl">

        <h1 className="text-5xl font-bold mb-4">
          Workspace Registry
        </h1>

        <AurumNav />

        <div className="mt-8 overflow-x-auto rounded-3xl border bg-white">

          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="p-4 text-left">ID</th>
                <th className="p-4 text-left">Name</th>
                <th className="p-4 text-left">Plan</th>
                <th className="p-4 text-left">Members</th>
                <th className="p-4 text-left">Trades</th>
                <th className="p-4 text-left">Claims</th>
              </tr>
            </thead>

            <tbody>
              {rows.map((w) => (
                <tr
                  key={w.workspace_id}
                  className="border-b"
                >
                  <td className="p-4">
                    {w.workspace_id}
                  </td>

                  <td className="p-4">
                    {w.name}
                  </td>

                  <td className="p-4">
                    {w.plan_code}
                  </td>

                  <td className="p-4">
                    {w.members}
                  </td>

                  <td className="p-4">
                    {w.trades}
                  </td>

                  <td className="p-4">
                    {w.claims}
                  </td>
                </tr>
              ))}
            </tbody>

          </table>

        </div>

      </div>
    </main>
  );
}