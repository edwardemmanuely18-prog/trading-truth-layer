"use client";

import { useEffect, useState } from "react";

export default function ClaimsPage() {
  const [claims, setClaims] =
    useState<any[]>([]);

  useEffect(() => {
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/aurum/claims`
    )
      .then(r => r.json())
      .then(setClaims);
  }, []);

  return (
    <main className="p-8">
      <h1 className="text-4xl font-bold mb-8">
        Claim Registry
      </h1>

      <table className="w-full border">
        <thead>
          <tr>
            <th>ID</th>
            <th>Workspace</th>
            <th>Name</th>
            <th>Status</th>
            <th>Visibility</th>
          </tr>
        </thead>

        <tbody>
          {claims.map((c) => (
            <tr key={c.id}>
              <td>{c.id}</td>
              <td>{c.workspace_id}</td>
              <td>{c.name}</td>
              <td>{c.status}</td>
              <td>{c.visibility}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}