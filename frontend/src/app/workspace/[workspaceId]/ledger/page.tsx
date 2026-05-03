"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import Navbar from "../../../../components/Navbar";
import TradeTable from "../../../../components/TradeTable";
import { useAuth } from "../../../../components/AuthProvider";
import {
  api,
  type AuditEvent,
  type Trade,
  type WorkspaceUsageSummary,
} from "../../../../lib/api";

function formatDateTime(value?: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

function formatPercent(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function summarizeJson(value?: string | null) {
  if (!value) return "—";

  try {
    const parsed = JSON.parse(value);

    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      const entries = Object.entries(parsed).slice(0, 3);
      if (entries.length === 0) return "{}";
      return entries
        .map(([k, v]) => `${k}: ${typeof v === "object" ? "[...]" : String(v)}`)
        .join(" | ");
    }

    return JSON.stringify(parsed);
  } catch {
    return value;
  }
}

const EMPTY_TRADE_FORM = {
  member_id: "",
  symbol: "",
  side: "BUY",
  opened_at: "",
  closed_at: "",
  entry_price: "",
  exit_price: "",
  quantity: "",
  currency: "USD",
  net_pnl: "",
  strategy_tag: "",
  source_system: "MANUAL",
};

type TradeFormState = typeof EMPTY_TRADE_FORM;

function tradeToFormState(trade: Trade): TradeFormState {
  const toLocalDateTime = (value?: string | null) => {
    if (!value) return "";
    try {
      const date = new Date(value);
      const offset = date.getTimezoneOffset();
      const local = new Date(date.getTime() - offset * 60 * 1000);
      return local.toISOString().slice(0, 16);
    } catch {
      return "";
    }
  };

  return {
    member_id: String(trade.member_id ?? ""),
    symbol: trade.symbol ?? "",
    side: trade.side ?? "BUY",
    opened_at: toLocalDateTime(trade.opened_at),
    closed_at: toLocalDateTime(trade.closed_at),
    entry_price:
      trade.entry_price === null || trade.entry_price === undefined ? "" : String(trade.entry_price),
    exit_price:
      trade.exit_price === null || trade.exit_price === undefined ? "" : String(trade.exit_price),
    quantity: trade.quantity === null || trade.quantity === undefined ? "" : String(trade.quantity),
    currency: trade.currency ?? "USD",
    net_pnl: trade.net_pnl === null || trade.net_pnl === undefined ? "" : String(trade.net_pnl),
    strategy_tag: (trade as any).tags?.join(", ") || "",
    source_system: trade.source_system ?? "MANUAL",
  };
}

export default function WorkspaceLedgerPage() {
  const params = useParams();
  const { user, workspaces, loading: authLoading } = useAuth();

  const workspaceId = useMemo(() => {
    const raw = Array.isArray(params?.workspaceId) ? params.workspaceId[0] : params?.workspaceId;
    const parsed = Number(raw);
    return Number.isNaN(parsed) ? null : parsed;
  }, [params]);

  const workspaceMembership = useMemo(() => {
    if (!workspaceId) return null;
    return workspaces.find((w) => w.workspace_id === workspaceId) ?? null;
  }, [workspaceId, workspaces]);

  const workspaceRole = workspaceMembership?.workspace_role ?? null;
  const canWriteTrades = workspaceRole === "owner" || workspaceRole === "operator";

  const [trades, setTrades] = useState<Trade[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [latestAuditEvents, setLatestAuditEvents] = useState<AuditEvent[]>([]);
  const [workspaceAuditEvents, setWorkspaceAuditEvents] = useState<AuditEvent[]>([]);
  const [usage, setUsage] = useState<WorkspaceUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;

  // 🔥 Ledger filters
  const [search, setSearch] = useState("");
  const [symbolFilter, setSymbolFilter] = useState("");
  const [sideFilter, setSideFilter] = useState("");
  // 🔥 NEW — Tag system
  const [tags, setTags] = useState<string[]>([]);
  const [selectedTag, setSelectedTag] = useState("");
  const tradeUsage = usage?.usage?.trades;

  const displayTrades = useMemo(() => {
    if (!search) return trades;

    const s = search.toLowerCase();

    return trades.filter(t =>
      String(t.member_id).includes(s) ||
      (t.symbol || "").toLowerCase().includes(s)
    );
  }, [trades, search]);

  const [usageLoading, setUsageLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [strategyStats, setStrategyStats] = useState<any[]>([]);

  const [showManualTradeForm, setShowManualTradeForm] = useState(false);
  const [manualTradeSubmitting, setManualTradeSubmitting] = useState(false);
  const [manualTradeError, setManualTradeError] = useState<string | null>(null);
  const [manualTradeSuccess, setManualTradeSuccess] = useState<string | null>(null);
  const [manualTradeForm, setManualTradeForm] = useState<TradeFormState>(EMPTY_TRADE_FORM);

  const [editingTrade, setEditingTrade] = useState<Trade | null>(null);
  const [editTradeForm, setEditTradeForm] = useState<TradeFormState>(EMPTY_TRADE_FORM);
  const [editTradeSubmitting, setEditTradeSubmitting] = useState(false);
  const [editTradeError, setEditTradeError] = useState<string | null>(null);
  const [editTradeSuccess, setEditTradeSuccess] = useState<string | null>(null);

  const [deletingTradeId, setDeletingTradeId] = useState<number | null>(null);

  const tradeUsed = tradeUsage?.used ?? 0;        // consumed (billing)
  const tradeLimit = tradeUsage?.limit ?? 0;
  const ledgerCount = metrics?.ledger_count ?? 0; // actual trades
  
  const tradeLimitReached =
    (tradeUsage?.limit ?? 0) > 0 && (tradeUsage?.used ?? 0) >= (tradeUsage?.limit ?? 0);
  
  async function reloadLedgerData(resolvedWorkspaceId: number) {
    const [tradesRes, latestAuditRes, workspaceAuditRes, usageRes, strategyRes] = await Promise.all([
      api.getTrades(resolvedWorkspaceId, {
        tag: selectedTag || undefined,
        symbol: symbolFilter || undefined,
        side: sideFilter || undefined,
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,

      }),
      api.getLatestAuditEvents(20),
      api.getAuditEventsForWorkspace(resolvedWorkspaceId, 50),
      api.getWorkspaceUsage(resolvedWorkspaceId),
      api.getStrategyPerformance(resolvedWorkspaceId),
    ]);

    setStrategyStats(Array.isArray(strategyRes) ? strategyRes : []);
    setTrades(Array.isArray(tradesRes) ? tradesRes : []);
    setLatestAuditEvents(Array.isArray(latestAuditRes) ? latestAuditRes : []);
    setWorkspaceAuditEvents(Array.isArray(workspaceAuditRes) ? workspaceAuditRes : []);
    setUsage(usageRes);
  }

  function updateManualTradeField(field: keyof TradeFormState, value: string) {
    setManualTradeForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function updateEditTradeField(field: keyof TradeFormState, value: string) {
    setEditTradeForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function buildTradePayload(form: TradeFormState) {
    const payload = {
      member_id: Number(form.member_id),
      symbol: form.symbol.trim().toUpperCase(),
      side: form.side.trim().toUpperCase(),
      opened_at: new Date(form.opened_at).toISOString(),
      closed_at: form.closed_at.trim() === "" ? null : new Date(form.closed_at).toISOString(),
      entry_price: Number(form.entry_price),
      exit_price: form.exit_price.trim() === "" ? null : Number(form.exit_price),
      quantity: Number(form.quantity),
      currency: form.currency.trim().toUpperCase(),
      net_pnl: form.net_pnl.trim() === "" ? null : Number(form.net_pnl),
      tags: form.strategy_tag
        ? form.strategy_tag.split(",").map(t => t.trim()).filter(Boolean)
        : [],
      source_system: form.source_system.trim() || "MANUAL",
    };

    if (
      !Number.isFinite(payload.member_id) ||
      !payload.symbol ||
      !payload.side ||
      !form.opened_at ||
      !Number.isFinite(payload.entry_price) ||
      !Number.isFinite(payload.quantity) ||
      !payload.currency
    ) {
      throw new Error("Please fill all required trade fields correctly.");
    }

    if (Number.isNaN(new Date(payload.opened_at).getTime())) {
      throw new Error("Opened At is invalid.");
    }

    if (payload.closed_at && Number.isNaN(new Date(payload.closed_at).getTime())) {
      throw new Error("Closed At is invalid.");
    }

    if (form.exit_price.trim() !== "" && !Number.isFinite(Number(form.exit_price))) {
      throw new Error("Exit Price must be a valid number.");
    }

    if (form.net_pnl.trim() !== "" && !Number.isFinite(Number(form.net_pnl))) {
      throw new Error("Net PnL must be a valid number.");
    }

    return payload;
  }

  async function handleCreateManualTrade() {
    if (!workspaceId) return;

    try {
      setManualTradeSubmitting(true);
      setManualTradeError(null);
      setManualTradeSuccess(null);

      const payload = buildTradePayload(manualTradeForm);

      await api.createTrade(workspaceId, payload);
      await reloadLedgerData(workspaceId);

      setManualTradeSuccess("Manual trade created successfully.");
      setManualTradeForm(EMPTY_TRADE_FORM);
      setShowManualTradeForm(false);
    } catch (err) {
      setManualTradeError(
        err instanceof Error ? err.message : "Failed to create manual trade."
      );
    } finally {
      setManualTradeSubmitting(false);
    }
  }

  function handleEditTrade(trade: Trade) {
    setEditingTrade(trade);
    setEditTradeForm(tradeToFormState(trade));
    setEditTradeError(null);
    setEditTradeSuccess(null);
    setManualTradeError(null);
    setManualTradeSuccess(null);
    setShowManualTradeForm(false);
  }

  function handleCancelEditTrade() {
    setEditingTrade(null);
    setEditTradeForm(EMPTY_TRADE_FORM);
    setEditTradeError(null);
    setEditTradeSuccess(null);
  }

  async function handleSaveEditedTrade() {
    if (!workspaceId || !editingTrade) return;

    try {
      setEditTradeSubmitting(true);
      setEditTradeError(null);
      setEditTradeSuccess(null);

      const payload = buildTradePayload(editTradeForm);
      await api.updateTrade(workspaceId, editingTrade.id, payload);
      await reloadLedgerData(workspaceId);

      setEditTradeSuccess("Trade updated successfully.");
      setEditingTrade(null);
      setEditTradeForm(EMPTY_TRADE_FORM);
    } catch (err) {
      setEditTradeError(err instanceof Error ? err.message : "Failed to update trade.");
    } finally {
      setEditTradeSubmitting(false);
    }
  }

  async function handleDeleteTrade(trade: Trade) {
    if (!workspaceId) return;

    const confirmed = window.confirm(
      `Delete trade #${trade.id}? This action should remain governed and may be blocked if the trade is part of locked evidence.`
    );

    if (!confirmed) return;

    try {
      setDeletingTradeId(trade.id);
      setError(null);
      setManualTradeError(null);
      setEditTradeError(null);

      await api.deleteTrade(workspaceId, trade.id);
      await reloadLedgerData(workspaceId);

      if (editingTrade?.id === trade.id) {
        handleCancelEditTrade();
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to delete trade.";
      setError(message);
    } finally {
      setDeletingTradeId(null);
    }
  }

  useEffect(() => {
    if (!workspaceId || !workspaceMembership) {
      return;
    }

    let active = true;
    const resolvedWorkspaceId = workspaceId;

    async function load() {
      try {
        setLoading(true);
        setError(null);

        const [tradesRes, latestAuditRes, workspaceAuditRes, strategyRes] = await Promise.all([
          api.getTrades(resolvedWorkspaceId, {
            tag: selectedTag || undefined,
            symbol: symbolFilter || undefined,
            side: sideFilter || undefined,
            limit: PAGE_SIZE,
            offset: page * PAGE_SIZE,
          }),
          api.getLatestAuditEvents(20),
          api.getAuditEventsForWorkspace(resolvedWorkspaceId, 50),
          api.getStrategyPerformance(resolvedWorkspaceId),
        ]);

        useEffect(() => {
          setPage(0);
        }, [selectedTag, symbolFilter, sideFilter]);

        if (!active) return;

        setTrades(Array.isArray(tradesRes) ? tradesRes : []);
        setLatestAuditEvents(Array.isArray(latestAuditRes) ? latestAuditRes : []);
        setWorkspaceAuditEvents(Array.isArray(workspaceAuditRes) ? workspaceAuditRes : []);
        setStrategyStats(Array.isArray(strategyRes) ? strategyRes : []);

      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load ledger");
      } finally {
        if (!active) return;
        setLoading(false);
      }
    }

    load();

    return () => {
      active = false;
    };

  }, [workspaceId, workspaceMembership, selectedTag, symbolFilter, sideFilter]);

  useEffect(() => {
    if (!workspaceId || !workspaceMembership) {
      setUsage(null);
      setUsageLoading(false);
      return;
    }

    const resolvedWorkspaceId = workspaceId;
    let active = true;

    async function loadUsage() {
      try {
        setUsageLoading(true);
        const result = await api.getWorkspaceUsage(resolvedWorkspaceId);
        if (!active) return;
        setUsage(result);
      } catch {
        if (!active) return;
        setUsage(null);
      } finally {
        if (!active) return;
        setUsageLoading(false);
      }
    }

    void loadUsage();

    return () => {
      active = false;
    };
  }, [workspaceId, workspaceMembership]);

  if (!workspaceId) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading ledger...</div>
      </div>
    );
  }

  if (!user || !workspaceMembership) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <main className="mx-auto max-w-[1400px] px-6 py-10">
          <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-700">
            You do not have access to this workspace ledger.
          </div>
        </main>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Navbar workspaceId={workspaceId} />
        <div className="p-6">Loading ledger...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-[1400px] px-6 py-10">
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">
              Trading Truth Layer · Canonical Record Surface
            </div>
            <h1 className="mt-2 text-3xl font-bold">Canonical Ledger</h1>
            <p className="mt-2 text-slate-600">
              Normalized trade records, audit history, and governance events for workspace{" "}
              {workspaceId}.
            </p>
          </div>

          <div className="rounded-xl border bg-white px-4 py-3 text-sm shadow-sm">
            <div className="text-slate-500">Workspace Role</div>
            <div className="mt-1 font-semibold">{workspaceRole}</div>
          </div>
        </div>

        {error ? (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        ) : null}

        {!canWriteTrades ? (
          <div className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-amber-900 shadow-sm">
            <h2 className="text-xl font-semibold">Read-only ledger access</h2>
            <p className="mt-2 text-sm">
              Your current workspace role is <span className="font-semibold">{workspaceRole}</span>.
              You can review ledger records and audit history, but trade import remains restricted
              to owner/operator roles.
            </p>

            <div className="mt-4 flex flex-wrap gap-3">
              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
              >
                Open Claims Registry
              </Link>
              <Link
                href={`/workspace/${workspaceId}/evidence`}
                className="rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium hover:bg-amber-100"
              >
                Open Evidence Center
              </Link>
            </div>
          </div>
        ) : null}

        {usageLoading ? (
          <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
            Loading workspace usage...
          </div>
        ) : tradeUsage ? (
          <div
            className={`mb-8 rounded-2xl border p-5 shadow-sm ${
              tradeLimitReached ? "border-amber-200 bg-amber-50" : "bg-white"
            }`}
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">Trade Capacity</h2>
                <div className="mt-2 text-sm text-slate-600">
                  Current workspace trade usage against plan allowance.
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                {canWriteTrades && !tradeLimitReached ? (
                  <>
                    <button
                      type="button"
                      onClick={() => {
                        setManualTradeError(null);
                        setManualTradeSuccess(null);
                        setShowManualTradeForm((current) => !current);
                        handleCancelEditTrade();
                      }}
                      className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                    >
                      {showManualTradeForm ? "Close Manual Trade" : "Add Manual Trade"}
                    </button>

                    <Link
                      href={`/workspace/${workspaceId}/import`}
                      className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                    >
                      Import Trades
                    </Link>
                  </>
                ) : null}

                {tradeLimitReached ? (
                  <Link
                    href={`/workspace/${workspaceId}/settings`}
                    className="rounded-xl border border-amber-300 px-4 py-2 text-sm font-medium hover:bg-amber-100"
                  >
                    Review Plan & Billing
                  </Link>
                ) : null}
              </div>
            </div>

            <div className="mt-5 grid gap-4 md:grid-cols-3">
              <div className="rounded-xl bg-white/70 p-4">
                <div className="text-sm text-slate-500">Used</div>
                <div className="mt-1 text-2xl font-semibold">{tradeUsage.used}</div>
              </div>
              <div className="rounded-xl bg-white/70 p-4">
                <div className="text-sm text-slate-500">Limit</div>
                <div className="mt-1 text-2xl font-semibold">{tradeUsage.limit}</div>
              </div>
              <div className="rounded-xl bg-white/70 p-4">
                <div className="text-sm text-slate-500">Utilization</div>
                <div className="mt-1 text-2xl font-semibold">{formatPercent(tradeUsage.ratio)}</div>
              </div>
            </div>

            {tradeLimitReached ? (
              <div className="mt-4 rounded-xl border border-amber-200 bg-amber-100 px-4 py-3 text-sm text-amber-900">
                Trade limit reached. Additional trade intake should be blocked until the workspace
                is upgraded or usage is reduced.
              </div>
            ) : null}
          </div>
        ) : null}

        <div className="mb-8 grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Workspace</div>
            <div className="mt-2 text-2xl font-semibold">{workspaceId}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trades in Ledger</div>
            <div className="mt-2 text-2xl font-semibold">
            {trades?.length ?? 0}
          </div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Workspace Audit Events</div>
            <div className="mt-2 text-2xl font-semibold">{workspaceAuditEvents.length}</div>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-sm">
            <div className="text-sm text-slate-500">Trade Write Access</div>
            <div className="mt-2 text-2xl font-semibold">
              {canWriteTrades ? "enabled" : "read-only"}
            </div>
          </div>
        </div>

        {/* 🔥 Strategy Performance */}
        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Strategy Performance</h2>

          {strategyStats.length === 0 ? (
            <div className="text-sm text-slate-500">No strategy data.</div>
          ) : (
            strategyStats.map((s) => (
              <div key={s.tag} className="flex justify-between border-b py-2 text-sm">
                <span className="font-medium">{s.tag}</span>
                <span>
                  {s.winrate}% WR • ${Number(s.pnl).toFixed(2)}
                </span>
              </div>
            ))
          )}
        </div>

        <div className="mb-8 rounded-2xl border bg-white p-5 shadow-sm">

        {/* 🔥 Ledger Controls */}
        <div className="mb-6 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">Ledger Controls</h2>

          <div className="grid gap-4 md:grid-cols-4">
            <input
              placeholder="Search symbol or member..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="rounded-xl border px-3 py-2 text-sm"
            />

            <input
              placeholder="Filter symbol (EURUSD)"
              value={symbolFilter}
              onChange={(e) => setSymbolFilter(e.target.value.toUpperCase())}
              className="rounded-xl border px-3 py-2 text-sm"
            />

            <select
              value={sideFilter}
              onChange={(e) => setSideFilter(e.target.value)}
              className="rounded-xl border px-3 py-2 text-sm"
            >
              <option value="">All Sides</option>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>

            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="rounded-xl border px-3 py-2 text-sm"
            >
              <option value="">All Tags</option>
              {[
                ...new Set(
                  trades
                    .flatMap(t => t.tags || [])
                    .filter((tag: string) => tag.length > 0)
                )
              ].map((tag) => (
                <option key={tag} value={tag}>
                  {tag}
                </option>
              ))}
            </select>

            <button
              onClick={() => {
                setSearch("");
                setSymbolFilter("");
                setSideFilter("");
                setSelectedTag(""); 
              }}
              className="rounded-xl border px-3 py-2 text-sm"
            >
              Reset Filters
            </button>
          </div>
        </div>  
          
        <div className="rounded-2xl border bg-white p-5 shadow-sm">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-semibold">Trade Ledger</h2>

            <div className="flex flex-wrap gap-2">
              <Link
                href={`/workspace/${workspaceId}/claims`}
                className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Open Claims
              </Link>

              {canWriteTrades ? (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      setManualTradeError(null);
                      setManualTradeSuccess(null);
                      setShowManualTradeForm((current) => !current);
                      handleCancelEditTrade();
                    }}
                    className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                  >
                    {showManualTradeForm ? "Close Manual Trade" : "Add Manual Trade"}
                  </button>

                  <Link
                    href={`/workspace/${workspaceId}/import`}
                    className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                  >
                    Import Trades
                  </Link>
                </>
              ) : null}
            </div>
          </div>

          {showManualTradeForm && canWriteTrades ? (
            <div className="mb-5 rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <div className="text-lg font-semibold text-slate-900">Add Manual Trade</div>
              <div className="mt-1 text-sm text-slate-500">
                Create a canonical trade record directly in the ledger.
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Member ID</label>
                  <input
                    value={manualTradeForm.member_id}
                    onChange={(e) => updateManualTradeField("member_id", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="3001"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Symbol</label>
                  <input
                    value={manualTradeForm.symbol}
                    onChange={(e) => updateManualTradeField("symbol", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="EURUSD"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Side</label>
                  <select
                    value={manualTradeForm.side}
                    onChange={(e) => updateManualTradeField("side", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="BUY">BUY</option>
                    <option value="SELL">SELL</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Opened At</label>
                  <input
                    type="datetime-local"
                    value={manualTradeForm.opened_at}
                    onChange={(e) => updateManualTradeField("opened_at", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Closed At</label>
                  <input
                    type="datetime-local"
                    value={manualTradeForm.closed_at}
                    onChange={(e) => updateManualTradeField("closed_at", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Entry Price</label>
                  <input
                    value={manualTradeForm.entry_price}
                    onChange={(e) => updateManualTradeField("entry_price", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="1.0840"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Exit Price</label>
                  <input
                    value={manualTradeForm.exit_price}
                    onChange={(e) => updateManualTradeField("exit_price", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="Optional"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Quantity</label>
                  <input
                    value={manualTradeForm.quantity}
                    onChange={(e) => updateManualTradeField("quantity", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="1.0"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Currency</label>
                  <input
                    value={manualTradeForm.currency}
                    onChange={(e) => updateManualTradeField("currency", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="USD"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Net PnL</label>
                  <input
                    value={manualTradeForm.net_pnl}
                    onChange={(e) => updateManualTradeField("net_pnl", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="Optional"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Strategy Tag</label>
                  <input
                    value={manualTradeForm.strategy_tag}
                    onChange={(e) => updateManualTradeField("strategy_tag", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="manual_entry"
                  />
                </div>

                <div className="md:col-span-2 xl:col-span-3">
                  <label className="mb-1 block text-sm font-medium text-slate-700">Source System</label>
                  <input
                    value={manualTradeForm.source_system}
                    onChange={(e) => updateManualTradeField("source_system", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                    placeholder="MANUAL"
                  />
                </div>
              </div>

              {manualTradeError ? (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {manualTradeError}
                </div>
              ) : null}

              {manualTradeSuccess ? (
                <div className="mt-4 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                  {manualTradeSuccess}
                </div>
              ) : null}

              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() => void handleCreateManualTrade()}
                  disabled={manualTradeSubmitting}
                  className="rounded-xl border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {manualTradeSubmitting ? "Creating..." : "Create Manual Trade"}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setShowManualTradeForm(false);
                    setManualTradeError(null);
                    setManualTradeSuccess(null);
                  }}
                  className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : null}

          {editingTrade ? (
            <div className="mb-5 rounded-2xl border border-blue-200 bg-blue-50 p-5">
              <div className="text-lg font-semibold text-slate-900">
                Edit Trade #{editingTrade.id}
              </div>
              <div className="mt-1 text-sm text-slate-500">
                Update the canonical trade record. Governed delete remains separate.
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Member ID</label>
                  <input
                    value={editTradeForm.member_id}
                    onChange={(e) => updateEditTradeField("member_id", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Symbol</label>
                  <input
                    value={editTradeForm.symbol}
                    onChange={(e) => updateEditTradeField("symbol", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Side</label>
                  <select
                    value={editTradeForm.side}
                    onChange={(e) => updateEditTradeField("side", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  >
                    <option value="BUY">BUY</option>
                    <option value="SELL">SELL</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Opened At</label>
                  <input
                    type="datetime-local"
                    value={editTradeForm.opened_at}
                    onChange={(e) => updateEditTradeField("opened_at", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Closed At</label>
                  <input
                    type="datetime-local"
                    value={editTradeForm.closed_at}
                    onChange={(e) => updateEditTradeField("closed_at", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Entry Price</label>
                  <input
                    value={editTradeForm.entry_price}
                    onChange={(e) => updateEditTradeField("entry_price", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Exit Price</label>
                  <input
                    value={editTradeForm.exit_price}
                    onChange={(e) => updateEditTradeField("exit_price", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Quantity</label>
                  <input
                    value={editTradeForm.quantity}
                    onChange={(e) => updateEditTradeField("quantity", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Currency</label>
                  <input
                    value={editTradeForm.currency}
                    onChange={(e) => updateEditTradeField("currency", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Net PnL</label>
                  <input
                    value={editTradeForm.net_pnl}
                    onChange={(e) => updateEditTradeField("net_pnl", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium text-slate-700">Strategy Tag</label>
                  <input
                    value={editTradeForm.strategy_tag}
                    onChange={(e) => updateEditTradeField("strategy_tag", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>

                <div className="md:col-span-2 xl:col-span-3">
                  <label className="mb-1 block text-sm font-medium text-slate-700">Source System</label>
                  <input
                    value={editTradeForm.source_system}
                    onChange={(e) => updateEditTradeField("source_system", e.target.value)}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                  />
                </div>
              </div>

              {editTradeError ? (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {editTradeError}
                </div>
              ) : null}

              {editTradeSuccess ? (
                <div className="mt-4 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                  {editTradeSuccess}
                </div>
              ) : null}

              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() => void handleSaveEditedTrade()}
                  disabled={editTradeSubmitting}
                  className="rounded-xl border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {editTradeSubmitting ? "Saving..." : "Save Trade"}
                </button>

                <button
                  type="button"
                  onClick={handleCancelEditTrade}
                  className="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
                >
                  Cancel Edit
                </button>
              </div>
            </div>
          ) : null}

          <TradeTable
            trades={displayTrades}
            canWriteTrades={canWriteTrades}
            onEditTrade={handleEditTrade}
            onDeleteTrade={handleDeleteTrade}
            deletingTradeId={deletingTradeId}
          />
        </div>

        <div className="mt-10 rounded-2xl border bg-white p-5 shadow-sm">
          <h2 className="text-xl font-semibold">Audit Timeline</h2>

          {workspaceAuditEvents.length === 0 ? (
            <div className="mt-4 text-sm text-slate-500">No audit events found.</div>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="px-3 py-2">Event</th>
                    <th className="px-3 py-2">Entity</th>
                    <th className="px-3 py-2">Summary</th>
                    <th className="px-3 py-2">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {workspaceAuditEvents.map((event) => (
                    <tr key={event.id} className="border-b">
                      <td className="px-3 py-2">{event.event_type}</td>
                      <td className="px-3 py-2">{event.entity_type}</td>
                      <td className="px-3 py-2 text-xs">{summarizeJson(event.metadata_json)}</td>
                      <td className="px-3 py-2">{formatDateTime(event.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}