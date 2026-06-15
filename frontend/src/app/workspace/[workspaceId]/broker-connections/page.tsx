"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import Navbar from "../../../../components/Navbar";

import {
  getBrokerConnections,
  createBrokerConnection,
  verifyBrokerConnection,
  type BrokerConnection,
} from "../../../../lib/api";

export default function BrokerConnectionsPage() {
  const params = useParams();

  const workspaceId = Number(params.workspaceId);

  const [loading, setLoading] = useState(true);
  const [connections, setConnections] = useState<
    BrokerConnection[]
  >([]);

  const [error, setError] = useState("");

  const [provider, setProvider] =
    useState("interactive_brokers");

  const [connectionName, setConnectionName] =
    useState("");

  const [creating, setCreating] =
    useState(false);

  const [selectedConnectionId, setSelectedConnectionId] =
    useState<number | null>(null);

  const [login, setLogin] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [server, setServer] =
    useState("");

  const [verifying, setVerifying] =
    useState(false);

  async function load() {
      try {
        setLoading(true);

        const result =
          await getBrokerConnections(
            workspaceId
          );

        setConnections(result);
      } catch (err: any) {
        setError(
          err?.message ||
            "Failed to load broker connections"
        );
      } finally {
        setLoading(false);
      }
    }

  useEffect(() => {
    if (workspaceId) {
      void load();
    }
  }, [workspaceId]);

  async function handleCreateConnection() {
    try {
      if (!connectionName.trim()) {
        alert("Connection name required");
        return;
      }

      setCreating(true);

      await createBrokerConnection(
        workspaceId,
        {
          provider,
          connection_name:
            connectionName,
        }
      );

      setConnectionName("");

      await load();

    } catch (err: any) {
      alert(
        err?.message ??
        "Failed creating connection"
      );
    } finally {
      setCreating(false);
    }
  }

  async function handleVerifyConnection() {
    if (!selectedConnectionId) {
      return;
    }

    try {
      setVerifying(true);

      await verifyBrokerConnection(
        workspaceId,
        {
          connection_id:
            selectedConnectionId,

          login,
          password,
          server,
        }
      );

      setSelectedConnectionId(null);

      setLogin("");
      setPassword("");
      setServer("");

      await load();

      alert(
        "Broker connection verified successfully"
      );
    } catch (err: any) {
      alert(
        err?.message ??
        "Verification failed"
      );
    } finally {
      setVerifying(false);
    }
  }
  

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">
            Broker Connections
          </h1>

          <p className="mt-3 text-slate-600">
            Direct broker integrations used for
            institutional-grade evidence ingestion
            and verification.
          </p>
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-6">
          <h2 className="mb-4 text-xl font-semibold">
            Create Broker Connection
          </h2>

          <div className="grid gap-4 md:grid-cols-3">

            <select
              value={provider}
              onChange={(e) =>
                setProvider(e.target.value)
              }
              className="rounded-lg border p-3"
            >
              <option value="interactive_brokers">
                Interactive Brokers
              </option>

              <option value="mt4">
                MetaTrader 4
              </option>

              <option value="mt5">
                MetaTrader 5
              </option>

              <option value="dxtrade">
                DXtrade
              </option>

              <option value="matchtrader">
                MatchTrader
              </option>

              <option value="tradestation">
                TradeStation
              </option>

              <option value="tradovate">
                Tradovate
              </option>

              <option value="ninjatrader">
                NinjaTrader
              </option>

              <option value="ctrader">
                cTrader
              </option>
            </select>

            <input
              type="text"
              value={connectionName}
              onChange={(e) =>
                setConnectionName(
                  e.target.value
                )
              }
              placeholder="Connection Name"
              className="rounded-lg border p-3"
            />

            <button
              onClick={
                handleCreateConnection
              }
              disabled={creating}
              className="rounded-lg bg-slate-900 px-4 py-3 text-white"
            >
              {creating
                ? "Creating..."
                : "Create Connection"}
            </button>

          </div>
        </div>

        {loading && (
          <div className="rounded-xl border bg-white p-6">
            Loading broker registry...
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
            <table className="w-full">
              <thead className="border-b bg-slate-50">
                <tr>
                    <th className="px-6 py-4 text-left">
                    Provider
                    </th>

                    <th className="px-6 py-4 text-left">
                    Connection
                    </th>

                    <th className="px-6 py-4 text-left">
                    Account
                    </th>

                    <th className="px-6 py-4 text-left">
                    Environment
                    </th>

                    <th className="px-6 py-4 text-left">
                    Status
                    </th>

                    <th className="px-6 py-4 text-left">
                    Verification
                    </th>

                    <th className="px-6 py-4 text-left">
                    Sync
                    </th>

                    <th className="px-6 py-4 text-left">
                    Trust
                    </th>

                    <th className="px-6 py-4 text-left">
                    Actions
                    </th>
                </tr>
              </thead>

              <tbody>
                {connections.map((row) => (
                  <tr
                    key={row.id}
                    className="border-b"
                  >
                    <td className="px-6 py-4">
                      {row.provider}
                    </td>

                    <td className="px-6 py-4">
                      {row.connection_name}
                    </td>

                    <td className="px-6 py-4">
                      {row.account_id ?? "-"}
                    </td>

                    <td className="px-6 py-4">
                      {row.account_environment}
                    </td>

                    <td className="px-6 py-4">
                      {row.connection_status}
                    </td>

                    <td className="px-6 py-4">
                      {row.verification_status}
                    </td>

                    <td className="px-6 py-4">
                      {row.sync_status}
                    </td>

                    <td className="px-6 py-4">
                      {row.trust_tier}
                    </td>

                    <td className="px-6 py-4">
                      {row.verification_status !==
                      "verified" ? (
                        <button
                          onClick={() =>
                            setSelectedConnectionId(
                              row.id
                            )
                          }
                          className="rounded bg-blue-600 px-3 py-1 text-white"
                        >
                          Verify
                        </button>
                      ) : (
                        "Verified"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {selectedConnectionId && (
          <div className="mb-8 rounded-2xl border bg-white p-6">
            <h2 className="mb-4 text-xl font-semibold">
              Verify Broker Connection
            </h2>

            <div className="grid gap-4 md:grid-cols-4">

              <input
                value={login}
                onChange={(e) =>
                  setLogin(e.target.value)
                }
                placeholder="Login"
                className="rounded border p-3"
              />

              <input
                type="password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                placeholder="Password"
                className="rounded border p-3"
              />

              <input
                value={server}
                onChange={(e) =>
                  setServer(e.target.value)
                }
                placeholder="Server"
                className="rounded border p-3"
              />

              <button
                onClick={
                  handleVerifyConnection
                }
                disabled={verifying}
                className="rounded bg-green-600 p-3 text-white"
              >
                {verifying
                  ? "Verifying..."
                  : "Verify"}
              </button>

            </div>
          </div>
        )}

        <div className="mt-8 rounded-2xl border bg-white p-6">
          <h2 className="text-xl font-semibold">
            TTL Evidence Trust Hierarchy
          </h2>

          <div className="mt-4 space-y-3">
            <div>
              Tier 1 — Direct Broker Ingestion
            </div>

            <div>
              Tier 2 — Broker Export Upload
            </div>

            <div>
              Tier 3 — Manual Trade Entry
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}