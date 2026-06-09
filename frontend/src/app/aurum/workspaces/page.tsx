"use client";

import { useEffect, useState } from "react";

export default function WorkspacesPage() {
  const [rows, setRows] =
    useState<any[]>([]);

  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/aurum/workspaces`
    )
      .then(r => r.json())
      .then(setRows);
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-4xl font-bold mb-8">
        Workspace Registry
      </h1>

      <table className="w-full border">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Plan</th>
            <th>Members</th>
            <th>Trades</th>
            <th>Claims</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((w) => (
            <tr key={w.workspace_id}>
              <td>{w.workspace_id}</td>
              <td>{w.name}</td>
              <td>{w.plan_code}</td>
              <td>{w.members}</td>
              <td>{w.trades}</td>
              <td>{w.claims}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}