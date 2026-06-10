"use client";

import { useEffect, useState } from "react";
import AurumNav from "../../../components/AurumNav";

export default function AurumUsersPage() {
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/aurum/users`
    )
        .then(async (r) => {
        const data = await r.json();

        if (Array.isArray(data)) {
            setUsers(data);
        } else {
            setUsers([]);
        }
        })
        .catch(() => {
        setUsers([]);
        });
    }, []);

  return (
    <main className="p-8">
      <h1 className="text-4xl font-bold mb-4">
        Platform Users
      </h1>

      <AurumNav />

      <table className="w-full border mt-8">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Verified</th>
          </tr>
        </thead>

        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>
                {u.email_verified
                  ? "Verified"
                  : "Pending"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}