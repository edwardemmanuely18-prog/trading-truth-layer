const API_BASE = "/api";

export const API_BASE_URL = API_BASE;
const DEV_USER_ID: number | null = null;
const TOKEN_STORAGE_KEY = "ttl_access_token";

export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredAccessToken(token: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredAccessToken() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export type AuthUser = {
  id: number;
  email: string;
  name: string;
  role: string;
};

export type AuthWorkspace = {
  workspace_id: number;
  workspace_name: string;
  workspace_role: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
  workspaces: AuthWorkspace[];
};

export type MeResponse = {
  user: AuthUser;
  workspaces: AuthWorkspace[];
};

export type RegisterPayload = {
  email: string;
  name: string;
  password: string;
  workspace_name?: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type Trade = {
  id: number;
  workspace_id?: number;
  member_id: number;
  symbol: string;
  side: string;
  opened_at: string;
  closed_at?: string | null;
  entry_price: number;
  exit_price?: number | null;
  quantity: number;
  net_pnl?: number | null;
  currency: string;
  strategy_tag?: string | null;
  source_system?: string | null;
};

export type ImportBatch = {
  id: number;
  workspace_id: number;
  filename: string;
  source_type: string;
  rows_received: number;
  rows_imported: number;
  rows_rejected: number;
  rows_skipped_duplicates: number;
  created_at?: string | null;
};

export type ImportCsvResult = {
  workspace_id: number;
  filename: string;
  format_type?: string;
  rows_received: number;
  rows_imported: number;
  rows_rejected: number;
  rows_skipped_duplicates: number;
  errors?: string[];
};

export type DashboardResponse = {
  workspace_id: number;
  workspace_name: string;
  member_count: number;
  trade_count: number;
  claim_count: number;
};

export type PlanBilling = {
  monthly_price_usd?: number | null;
  annual_price_usd?: number | null;
  currency?: string | null;
  billing_interval?: string | null;
  stripe_price_lookup_key_monthly?: string | null;
  stripe_price_lookup_key_annual?: string | null;
};

export type PlanDetail = {
  code: string;
  name: string;
  description: string;
  recommended_for: string[];
  billing: PlanBilling;
};

export type WorkspacePlanDetail = PlanDetail;

export type WorkspaceSettings = {
  workspace_id: number;
  name: string;
  description?: string | null;
  billing_email?: string | null;
  plan_code: string;
  billing_status: string;
  billing_provider?: string | null;
  stripe_customer_id?: string | null;
  stripe_subscription_id?: string | null;
  paddle_customer_id?: string | null;
  paddle_subscription_id?: string | null;
  paddle_transaction_id?: string | null;
  paddle_price_id?: string | null;
  subscription_current_period_end?: string | null;
  limits: {
    claim_limit: number;
    trade_limit: number;
    member_limit: number;
    storage_limit_mb: number;
  };
  plan_detail?: WorkspacePlanDetail;
  effective_plan_code: string;
  effective_plan_detail?: PlanDetail;
  effective_limits?: {
    claim_limit: number;
    trade_limit: number;
    member_limit: number;
    storage_limit_mb: number;
  };
  plan_governance?: {
    configured_plan_code: string;
    effective_plan_code: string;
    billing_status: string;
    paid_access_active: boolean;
    plan_mismatch: boolean;
    reason: string;
    message: string;
  };
  created_at?: string | null;
  updated_at?: string | null;
};

export type WorkspaceSettingsUpdatePayload = {
  name: string;
  description?: string | null;
  billing_email?: string | null;
};

export type UsageDimension = {
  used: number;
  limit: number;
  ratio?: number | null;
  status?: "ok" | "near_limit" | "at_limit" | "over_limit" | "unlimited";
};

export type PlanCatalogItem = {
  code: string;
  name: string;
  description: string;
  limits: {
    claim_limit: number;
    trade_limit: number;
    member_limit: number;
    storage_limit_mb: number;
  };
  recommended_for: string[];
  public_price_hint?: string;
  billing?: PlanBilling;
};

export type UpgradeRecommendation = {
  current_plan_code: string;
  effective_plan_code?: string;
  recommendation_basis_plan_code?: string;
  recommended_plan_code: string;
  recommended_plan_name: string;
  recommended_plan_is_distinct?: boolean;
  upgrade_required_now: boolean;
  upgrade_recommended_soon: boolean;
  billing_activation_recommended?: boolean;
  already_at_highest_tier?: boolean;
  breached_dimensions: string[];
  near_limit_dimensions: string[];
};

export type WorkspaceGovernance = {
  has_any_over_limit: boolean;
  has_any_at_limit: boolean;
  has_any_near_limit: boolean;
  upgrade_required_now: boolean;
  upgrade_recommended_soon: boolean;
  billing_activation_recommended?: boolean;
  configured_plan_code?: string;
  effective_plan_code?: string;
  paid_access_active?: boolean;
  plan_mismatch?: boolean;
  plan_mismatch_reason?: string;
  plan_mismatch_message?: string;
};

export type WorkspaceStripeReadiness = {
  has_customer_id: boolean;
  has_subscription_id: boolean;
  integration_status: string;
};

export type WorkspaceUsageSummary = {
  workspace_id: number;
  plan_code: string;
  billing_status: string;
  effective_plan_code: string;
  usage: {
    members: UsageDimension;
    trades: UsageDimension;
    claims: UsageDimension;
    storage_mb: UsageDimension;
  };
  stripe_ready: WorkspaceStripeReadiness;
  governance?: WorkspaceGovernance;
  upgrade_recommendation?: UpgradeRecommendation;
  plan_catalog?: PlanCatalogItem[];
  configured_plan_detail?: PlanDetail;
  effective_plan_detail?: PlanDetail;
};

export type BillingDiagnostics = {
  stripe_package_installed?: boolean;
  stripe_billing_enabled?: boolean;
  billing_enabled?: boolean;
  secret_key_configured?: boolean;
  price_lookup_key?: string;
  paddle_enabled?: boolean;
  api_key_configured?: boolean;
  paddle_price_id?: string;
  manual_billing_enabled?: boolean;
};

export type ManualPaymentDetails = {
  enabled?: boolean;
  payment_method?: string | null;
  account_name?: string | null;
  account_number?: string | null;
  bank_name?: string | null;
  phone_number?: string | null;
  notes?: string | null;
};

export type BillingCheckoutResponse = {
  mode: string;
  workspace_id: number;
  url?: string | null;
  checkout_url?: string | null;
  session_id?: string | null;
  transaction_id?: string | null;
  current_plan_code?: string;
  target_plan_code?: string;
  billing_cycle?: string;
  checkout_intent?: string;
  message?: string | null;
  stripe_customer_id?: string | null;
  stripe_price_id?: string | null;
  stripe_price_lookup_key?: string | null;
  paddle_price_id?: string | null;
  manual_payment_details?: ManualPaymentDetails;
  diagnostics?: BillingDiagnostics;
};

export type BillingPortalResponse = {
  workspace_id: number;
  mode?: string;
  url?: string | null;
  portal_url?: string | null;
  message?: string | null;
  created_at?: string | null;
  manual_payment_details?: ManualPaymentDetails;
};

export type WorkspaceBillingFoundation = {
  workspace_id: number;
  plan_code: string;
  plan_name: string;
  effective_plan_code?: string;
  billing_status: string;
  billing_status_is_paid?: boolean;
  plan_mismatch?: boolean;
  billing_email?: string | null;
  billing_provider?: string | null;
  stripe_customer_id?: string | null;
  stripe_subscription_id?: string | null;
  paddle_customer_id?: string | null;
  paddle_subscription_id?: string | null;
  paddle_transaction_id?: string | null;
  paddle_price_id?: string | null;
  subscription_current_period_end?: string | null;
  prices: {
    monthly_price_usd?: number | null;
    annual_price_usd?: number | null;
  };
  stripe_ready: {
    has_customer_id: boolean;
    has_subscription_id: boolean;
    integration_status: string;
    billing_enabled?: boolean;
    secret_key_configured?: boolean;
    package_installed?: boolean;
  };
  paddle_ready?: {
    enabled: boolean;
    api_key_configured: boolean;
    webhook_secret_configured: boolean;
    has_customer_id: boolean;
    has_subscription_id: boolean;
    price_catalog_count: number;
  };
  manual_billing?: {
    enabled: boolean;
    ready: boolean;
    payment_method?: string | null;
  };
  manual_payment_details?: ManualPaymentDetails;
  checkout_state: {
    can_start_checkout: boolean;
    mode: string;
    portal_available: boolean;
  };
};

export type WorkspaceMemberRole = "owner" | "operator" | "member" | "auditor";

export type WorkspaceMember = {
  workspace_id: number;
  user_id: number;
  email: string;
  name: string;
  global_role: string;
  workspace_role: string;
};

export type WorkspaceInvite = {
  id: number;
  workspace_id: number;
  email: string;
  role: string;
  token: string;
  status: string;
  invited_by_user_id?: number | null;
  accepted_by_user_id?: number | null;
  created_at?: string | null;
  expires_at?: string | null;
  accepted_at?: string | null;
};

export type ClaimSchema = {
  id: number;
  workspace_id: number;
  name: string;
  period_start: string;
  period_end: string;
  included_member_ids_json: number[];
  included_symbols_json: string[];
  excluded_trade_ids_json: number[];
  methodology_notes: string;
  status: string;
  visibility: string;
  parent_claim_id?: number | null;
  root_claim_id?: number | null;
  version_number?: number;
  verified_at?: string | null;
  published_at?: string | null;
  locked_at?: string | null;
  locked_trade_set_hash?: string | null;
  claim_hash?: string;
};

export type ClaimSchemaCreatePayload = {
  workspace_id: number;
  name: string;
  period_start: string;
  period_end: string;
  included_member_ids_json: number[];
  included_symbols_json: string[];
  excluded_trade_ids_json: number[];
  methodology_notes: string;
  visibility: string;
};

export type ClaimSchemaUpdatePayload = {
  name: string;
  period_start: string;
  period_end: string;
  included_member_ids_json: number[];
  included_symbols_json: string[];
  excluded_trade_ids_json: number[];
  methodology_notes: string;
  visibility: string;
};

export type ClaimVersion = {
  id: number;
  name: string;
  status: string;
  visibility: string;
  version_number: number;
  parent_claim_id?: number | null;
  root_claim_id?: number | null;
  claim_hash?: string;
};

export type ClaimSchemaPreview = {
  claim_schema_id: number;
  claim_hash?: string;
  name: string;
  verification_status: string;
  trade_count: number;
  net_pnl: number;
  profit_factor: number;
  win_rate: number;
  leaderboard: {
    rank: number;
    member_id?: number;
    member: string;
    net_pnl: number;
    win_rate: number;
    profit_factor: number;
  }[];
  scope: {
    period_start: string;
    period_end: string;
    included_members: number[];
    included_symbols: string[];
    methodology_notes: string;
    visibility?: string;
  };
  lifecycle?: {
    status: string;
    verified_at?: string | null;
    published_at?: string | null;
    locked_at?: string | null;
    locked_trade_set_hash?: string | null;
  };
  lineage?: {
    parent_claim_id?: number | null;
    root_claim_id?: number | null;
    version_number?: number;
  };
};

export type EquityCurvePoint = {
  index: number;
  trade_id: number;
  member_id: number;
  symbol: string;
  opened_at: string;
  net_pnl: number;
  cumulative_pnl: number;
};

export type ClaimEquityCurve = {
  claim_schema_id: number;
  claim_hash: string;
  name: string;
  status: string;
  trade_count: number;
  point_count: number;
  starting_equity: number;
  ending_equity: number;
  curve: EquityCurvePoint[];
};

export type ClaimTradeEvidenceRow = {
  index: number;
  trade_id: number;
  workspace_id: number;
  member_id: number;
  symbol: string;
  side: string;
  opened_at: string;
  closed_at?: string | null;
  entry_price: number;
  exit_price?: number | null;
  quantity: number;
  net_pnl: number;
  currency: string;
  strategy_tag?: string | null;
  source_system?: string | null;
  cumulative_pnl: number | null;
};

export type ClaimTradeScopeReason =
  | "OUTSIDE_PERIOD"
  | "MEMBER_FILTER"
  | "SYMBOL_FILTER"
  | "MANUAL_EXCLUSION";

export type ClaimTradeScopeRow = {
  index: number;
  trade_id: number;
  workspace_id: number;
  member_id: number;
  symbol: string;
  side: string;
  opened_at: string;
  closed_at: string | null;
  entry_price: number;
  exit_price: number | null;
  quantity: number;
  net_pnl: number;
  currency: string;
  strategy_tag?: string | null;
  source_system?: string | null;
  cumulative_pnl: number | null;
  scope_status: "included" | "excluded";
  exclusion_reason?: ClaimTradeScopeReason | null;
  exclusion_reason_label?: string | null;
  exclusion_reason_detail?: string | null;
};

export type ClaimTradeScopeSummary = {
  workspace_trade_count: number;
  included_trade_count: number;
  excluded_trade_count: number;
  excluded_breakdown: Partial<Record<ClaimTradeScopeReason, number>>;
};

export type ClaimTradeEvidence = {
  claim_schema_id: number;
  claim_hash: string;
  name: string;
  status: string;
  trade_count: number;
  trades: ClaimTradeEvidenceRow[];
  included_trade_count?: number;
  excluded_trade_count?: number;
  included_trades?: ClaimTradeScopeRow[];
  excluded_trades?: ClaimTradeScopeRow[];
  summary?: ClaimTradeScopeSummary;
};

export type EvidencePack = {
  claim_schema_id: number;
  claim_hash?: string;
  exported_at?: string;
  export_version?: string;
  schema_snapshot: Record<string, unknown>;
  trade_set_hash: string;
  metrics_snapshot: Record<string, unknown>;
  equity_curve_snapshot?: Record<string, unknown>;
  methodology_notes: string;
  lifecycle?: {
    status: string;
    verified_at?: string | null;
    published_at?: string | null;
    locked_at?: string | null;
    locked_trade_set_hash?: string | null;
  };
};

export type EvidenceBundleManifest = {
  export_version: string;
  exported_at: string;
  claim_schema_id: number;
  claim_hash: string;
  included_files: string[];
};

export type AuditEvent = {
  id: number;
  event_type: string;
  entity_type: string;
  entity_id: string;
  actor_id?: string | null;
  workspace_id?: string | null;
  old_state?: string | null;
  new_state?: string | null;
  metadata_json?: string | null;
  created_at?: string | null;
};

export type EvidenceBundleAuditPayload = {
  claim_schema_id: number;
  claim_hash: string;
  exported_at: string;
  export_version: string;
  event_count: number;
  events: AuditEvent[];
};

export type EvidenceBundle = {
  claim_schema_id: number;
  claim_hash: string;
  exported_at: string;
  export_version: string;
  included_files: string[];
  manifest: EvidenceBundleManifest;
  evidence_pack: EvidencePack;
  audit_events: EvidenceBundleAuditPayload;
};

export type PublicClaim = {
  claim_schema_id: number;
  claim_hash: string;
  name: string;
  verification_status: string;
  trade_count: number;
  net_pnl: number;
  profit_factor: number;
  win_rate: number;
  leaderboard: {
    rank: number;
    member_id?: number;
    member: string;
    net_pnl: number;
    win_rate: number;
    profit_factor: number;
  }[];
  scope: {
    period_start: string;
    period_end: string;
    included_members: number[];
    included_symbols: string[];
    methodology_notes: string;
    visibility?: string;
  };
  lifecycle: {
    status: string;
    verified_at?: string | null;
    published_at?: string | null;
    locked_at?: string | null;
    locked_trade_set_hash?: string | null;
  };
  lineage?: {
    parent_claim_id?: number | null;
    root_claim_id?: number | null;
    version_number?: number;
  };
  trade_set_hash: string;
  is_publicly_accessible?: boolean;
};

export type PublicClaimDirectoryItem = PublicClaim;

export type PublicVerifyResult = {
  claim_schema_id: number;
  claim_hash: string;
  name: string;
  verification_status: string;
  integrity_status: "valid" | "compromised";
  trade_count: number;
  net_pnl: number;
  profit_factor: number;
  win_rate: number;
  leaderboard: {
    rank: number;
    member_id?: number;
    member: string;
    net_pnl: number;
    win_rate: number;
    profit_factor: number;
  }[];
  scope: {
    period_start: string;
    period_end: string;
    included_members: number[];
    included_symbols: string[];
    methodology_notes: string;
    visibility?: string;
  };
  lifecycle: {
    status: string;
    verified_at?: string | null;
    published_at?: string | null;
    locked_at?: string | null;
  };
  lineage?: {
    parent_claim_id?: number | null;
    root_claim_id?: number | null;
    version_number?: number;
  };
  trade_set_hash: string;
  trades?: ClaimTradeScopeRow[];
  included_trade_count?: number;
  excluded_trade_count?: number;
  included_trades?: ClaimTradeScopeRow[];
  excluded_trades?: ClaimTradeScopeRow[];
  summary?: ClaimTradeScopeSummary;
  equity_curve?: {
    point_count: number;
    starting_equity: number;
    ending_equity: number;
    curve: EquityCurvePoint[];
  };
};

export type ClaimIntegrityResult = {
  claim_schema_id: number;
  claim_hash?: string;
  name: string;
  status: string;
  integrity_status: "valid" | "compromised";
  trade_count: number;
  stored_hash: string;
  recomputed_hash: string;
  hash_match: boolean;
  verified_at: string;
};

export type ApiErrorPayload = {
  code?: string;
  message?: string;
  detail?: string;
  resource?: string;
  workspace_id?: number;
  used?: number;
  limit?: number;
  recommended_action?: string;
  upgrade_hint?: string;
};

export class ApiError extends Error {
  status: number;
  payload: ApiErrorPayload | null;
  rawBody: string;

  constructor(message: string, status: number, payload: ApiErrorPayload | null, rawBody: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
    this.rawBody = rawBody;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function getApiErrorCode(error: unknown): string | null {
  if (!isApiError(error)) return null;
  return error.payload?.code ?? null;
}

function getAuthHeaders(headers?: HeadersInit) {
  const merged = new Headers(headers || {});
  const token = getStoredAccessToken();

  if (token && !merged.has("Authorization")) {
    merged.set("Authorization", `Bearer ${token}`);
  }

  return merged;
}

function parseApiErrorPayload(rawText: string): ApiErrorPayload | null {
  if (!rawText) return null;

  try {
    const parsed = JSON.parse(rawText);

    if (typeof parsed === "string") {
      return { message: parsed };
    }

    if (parsed && typeof parsed === "object") {
      if ("detail" in parsed) {
        const detail = (parsed as { detail?: unknown }).detail;

        if (typeof detail === "string") {
          return { message: detail, detail };
        }

        if (detail && typeof detail === "object") {
          return detail as ApiErrorPayload;
        }
      }

      return parsed as ApiErrorPayload;
    }
  } catch {
    return { message: rawText, detail: rawText };
  }

  return null;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = getAuthHeaders(options?.headers);

  if (!(options?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const rawText = await res.text();
    const payload = parseApiErrorPayload(rawText);
    const message =
      payload?.message ||
      payload?.detail ||
      rawText ||
      `API request failed with status ${res.status}`;

    throw new ApiError(message, res.status, payload, rawText);
  }

  return res.json() as Promise<T>;
}

function withDevUser(path: string) {
  const token = typeof window !== "undefined" ? getStoredAccessToken() : null;
  if (token) return path;

  if (DEV_USER_ID === null) return path;

  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}user_id=${DEV_USER_ID}`;
}

function ensureLeaderboard<T extends { leaderboard?: unknown }>(row: T) {
  return {
    ...row,
    leaderboard: Array.isArray(row.leaderboard) ? row.leaderboard : [],
  };
}

function ensurePlanBilling(row?: Partial<PlanBilling> | null): PlanBilling {
  return {
    monthly_price_usd:
      typeof row?.monthly_price_usd === "number"
        ? row.monthly_price_usd
        : row?.monthly_price_usd ?? null,
    annual_price_usd:
      typeof row?.annual_price_usd === "number"
        ? row.annual_price_usd
        : row?.annual_price_usd ?? null,
    currency: row?.currency ?? "USD",
    billing_interval: row?.billing_interval ?? "monthly",
    stripe_price_lookup_key_monthly: row?.stripe_price_lookup_key_monthly ?? null,
    stripe_price_lookup_key_annual: row?.stripe_price_lookup_key_annual ?? null,
  };
}

function ensureWorkspacePlanDetail(
  row?: Partial<WorkspacePlanDetail> | null
): WorkspacePlanDetail | undefined {
  if (!row) return undefined;

  return {
    code: String(row.code ?? ""),
    name: String(row.name ?? ""),
    description: String(row.description ?? ""),
    recommended_for: Array.isArray(row.recommended_for) ? row.recommended_for.map(String) : [],
    billing: ensurePlanBilling(row.billing),
  };
}

function ensurePlanCatalogItem(row: Partial<PlanCatalogItem>): PlanCatalogItem {
  return {
    code: String(row.code ?? ""),
    name: String(row.name ?? ""),
    description: String(row.description ?? ""),
    limits: {
      claim_limit: Number(row.limits?.claim_limit ?? 0),
      trade_limit: Number(row.limits?.trade_limit ?? 0),
      member_limit: Number(row.limits?.member_limit ?? 0),
      storage_limit_mb: Number(row.limits?.storage_limit_mb ?? 0),
    },
    recommended_for: Array.isArray(row.recommended_for) ? row.recommended_for.map(String) : [],
    public_price_hint: row.public_price_hint ?? undefined,
    billing: ensurePlanBilling(row.billing),
  };
}

function ensureWorkspaceSettings(row: WorkspaceSettings): WorkspaceSettings {
  return {
    ...row,
    billing_provider: row?.billing_provider ?? null,
    stripe_customer_id: row?.stripe_customer_id ?? null,
    stripe_subscription_id: row?.stripe_subscription_id ?? null,
    paddle_customer_id: row?.paddle_customer_id ?? null,
    paddle_subscription_id: row?.paddle_subscription_id ?? null,
    paddle_transaction_id: row?.paddle_transaction_id ?? null,
    paddle_price_id: row?.paddle_price_id ?? null,
    limits: {
      claim_limit: Number(row?.limits?.claim_limit ?? 0),
      trade_limit: Number(row?.limits?.trade_limit ?? 0),
      member_limit: Number(row?.limits?.member_limit ?? 0),
      storage_limit_mb: Number(row?.limits?.storage_limit_mb ?? 0),
    },
    plan_detail: ensureWorkspacePlanDetail(row?.plan_detail),
    effective_plan_code: String(row?.effective_plan_code ?? row?.plan_code ?? "starter"),
    effective_plan_detail: ensureWorkspacePlanDetail(row?.effective_plan_detail),
    effective_limits: row?.effective_limits
      ? {
          claim_limit: Number(row.effective_limits.claim_limit ?? 0),
          trade_limit: Number(row.effective_limits.trade_limit ?? 0),
          member_limit: Number(row.effective_limits.member_limit ?? 0),
          storage_limit_mb: Number(row.effective_limits.storage_limit_mb ?? 0),
        }
      : undefined,
    plan_governance: row?.plan_governance
      ? {
          configured_plan_code: String(row.plan_governance.configured_plan_code ?? row.plan_code ?? "starter"),
          effective_plan_code: String(
            row.plan_governance.effective_plan_code ?? row.effective_plan_code ?? row.plan_code ?? "starter"
          ),
          billing_status: String(row.plan_governance.billing_status ?? row.billing_status ?? "inactive"),
          paid_access_active: Boolean(row.plan_governance.paid_access_active),
          plan_mismatch: Boolean(row.plan_governance.plan_mismatch),
          reason: String(row.plan_governance.reason ?? "ok"),
          message: String(row.plan_governance.message ?? ""),
        }
      : undefined,
  };
}

function ensurePublicClaim(row: PublicClaimDirectoryItem): PublicClaimDirectoryItem {
  return {
    ...row,
    leaderboard: Array.isArray(row.leaderboard) ? row.leaderboard : [],
    scope: row.scope ?? {
      period_start: "—",
      period_end: "—",
      included_members: [],
      included_symbols: [],
      methodology_notes: "",
      visibility: "—",
    },
    lifecycle: row.lifecycle ?? {
      status: row.verification_status || "unknown",
      verified_at: null,
      published_at: null,
      locked_at: null,
      locked_trade_set_hash: null,
    },
    trade_set_hash: row.trade_set_hash ?? "—",
  };
}

function ensureUsageDimension(row?: Partial<UsageDimension> | null): UsageDimension {
  return {
    used: Number(row?.used ?? 0),
    limit: Number(row?.limit ?? 0),
    ratio: typeof row?.ratio === "number" ? row.ratio : row?.ratio ?? null,
    status: row?.status ?? "ok",
  };
}

function ensureWorkspaceUsageSummary(row: WorkspaceUsageSummary): WorkspaceUsageSummary {
  return {
    ...row,
    effective_plan_code: String(row?.effective_plan_code ?? row?.plan_code ?? "starter"),
    usage: {
      members: ensureUsageDimension(row?.usage?.members),
      trades: ensureUsageDimension(row?.usage?.trades),
      claims: ensureUsageDimension(row?.usage?.claims),
      storage_mb: ensureUsageDimension(row?.usage?.storage_mb),
    },
    stripe_ready: {
      has_customer_id: Boolean(row?.stripe_ready?.has_customer_id),
      has_subscription_id: Boolean(row?.stripe_ready?.has_subscription_id),
      integration_status:
        row?.stripe_ready?.integration_status || "ready_for_stripe_foundation",
    },
    governance: row?.governance
      ? {
          has_any_over_limit: Boolean(row.governance.has_any_over_limit),
          has_any_at_limit: Boolean(row.governance.has_any_at_limit),
          has_any_near_limit: Boolean(row.governance.has_any_near_limit),
          upgrade_required_now: Boolean(row.governance.upgrade_required_now),
          upgrade_recommended_soon: Boolean(row.governance.upgrade_recommended_soon),
          billing_activation_recommended: Boolean(row.governance.billing_activation_recommended),
          configured_plan_code: row.governance.configured_plan_code ?? row.plan_code,
          effective_plan_code:
            row.governance.effective_plan_code ?? row.effective_plan_code ?? row.plan_code,
          paid_access_active: Boolean(row.governance.paid_access_active),
          plan_mismatch: Boolean(row.governance.plan_mismatch),
          plan_mismatch_reason: row.governance.plan_mismatch_reason ?? "",
          plan_mismatch_message: row.governance.plan_mismatch_message ?? "",
        }
      : undefined,
    upgrade_recommendation: row?.upgrade_recommendation
      ? {
          current_plan_code: row.upgrade_recommendation.current_plan_code,
          effective_plan_code: row.upgrade_recommendation.effective_plan_code,
          recommendation_basis_plan_code: row.upgrade_recommendation.recommendation_basis_plan_code,
          recommended_plan_code: row.upgrade_recommendation.recommended_plan_code,
          recommended_plan_name: row.upgrade_recommendation.recommended_plan_name,
          recommended_plan_is_distinct: Boolean(row.upgrade_recommendation.recommended_plan_is_distinct),
          upgrade_required_now: Boolean(row.upgrade_recommendation.upgrade_required_now),
          upgrade_recommended_soon: Boolean(row.upgrade_recommendation.upgrade_recommended_soon),
          billing_activation_recommended: Boolean(row.upgrade_recommendation.billing_activation_recommended),
          already_at_highest_tier: Boolean(row.upgrade_recommendation.already_at_highest_tier),
          breached_dimensions: Array.isArray(row.upgrade_recommendation.breached_dimensions)
            ? row.upgrade_recommendation.breached_dimensions
            : [],
          near_limit_dimensions: Array.isArray(row.upgrade_recommendation.near_limit_dimensions)
            ? row.upgrade_recommendation.near_limit_dimensions
            : [],
        }
      : undefined,
    plan_catalog: Array.isArray(row?.plan_catalog)
      ? row.plan_catalog.map((item) => ensurePlanCatalogItem(item))
      : [],
    configured_plan_detail: ensureWorkspacePlanDetail(row?.configured_plan_detail),
    effective_plan_detail: ensureWorkspacePlanDetail(row?.effective_plan_detail),
  };
}

function ensureManualPaymentDetails(
  row?: Partial<ManualPaymentDetails> | null
): ManualPaymentDetails | undefined {
  if (!row) return undefined;
  return {
    enabled: Boolean(row.enabled),
    payment_method: row.payment_method ?? null,
    account_name: row.account_name ?? null,
    account_number: row.account_number ?? null,
    bank_name: row.bank_name ?? null,
    phone_number: row.phone_number ?? null,
    notes: row.notes ?? null,
  };
}

function ensureWorkspaceBillingFoundation(
  row: WorkspaceBillingFoundation
): WorkspaceBillingFoundation {
  return {
    ...row,
    effective_plan_code: row?.effective_plan_code ?? row?.plan_code ?? "starter",
    billing_status_is_paid: Boolean(row?.billing_status_is_paid),
    plan_mismatch: Boolean(row?.plan_mismatch),
    billing_provider: row?.billing_provider ?? null,
    stripe_customer_id: row?.stripe_customer_id ?? null,
    stripe_subscription_id: row?.stripe_subscription_id ?? null,
    paddle_customer_id: row?.paddle_customer_id ?? null,
    paddle_subscription_id: row?.paddle_subscription_id ?? null,
    paddle_transaction_id: row?.paddle_transaction_id ?? null,
    paddle_price_id: row?.paddle_price_id ?? null,
    prices: {
      monthly_price_usd: row?.prices?.monthly_price_usd ?? null,
      annual_price_usd: row?.prices?.annual_price_usd ?? null,
    },
    stripe_ready: {
      has_customer_id: Boolean(row?.stripe_ready?.has_customer_id),
      has_subscription_id: Boolean(row?.stripe_ready?.has_subscription_id),
      integration_status:
        row?.stripe_ready?.integration_status || "ready_for_stripe_foundation",
      billing_enabled: Boolean(row?.stripe_ready?.billing_enabled),
      secret_key_configured: Boolean(row?.stripe_ready?.secret_key_configured),
      package_installed: Boolean(row?.stripe_ready?.package_installed),
    },
    paddle_ready: row?.paddle_ready
      ? {
          enabled: Boolean(row.paddle_ready.enabled),
          api_key_configured: Boolean(row.paddle_ready.api_key_configured),
          webhook_secret_configured: Boolean(row.paddle_ready.webhook_secret_configured),
          has_customer_id: Boolean(row.paddle_ready.has_customer_id),
          has_subscription_id: Boolean(row.paddle_ready.has_subscription_id),
          price_catalog_count: Number(row.paddle_ready.price_catalog_count ?? 0),
        }
      : undefined,
    manual_billing: row?.manual_billing
      ? {
          enabled: Boolean(row.manual_billing.enabled),
          ready: Boolean(row.manual_billing.ready),
          payment_method: row.manual_billing.payment_method ?? null,
        }
      : undefined,
    manual_payment_details: ensureManualPaymentDetails(row?.manual_payment_details),
    checkout_state: {
      can_start_checkout: Boolean(row?.checkout_state?.can_start_checkout),
      mode: row?.checkout_state?.mode || "placeholder_until_checkout",
      portal_available: Boolean(row?.checkout_state?.portal_available),
    },
  };
}

function ensureWorkspaceMember(row: WorkspaceMember): WorkspaceMember {
  return {
    workspace_id: Number(row.workspace_id ?? 0),
    user_id: Number(row.user_id ?? 0),
    email: String(row.email ?? ""),
    name: String(row.name ?? ""),
    global_role: String(row.global_role ?? "member"),
    workspace_role: String(row.workspace_role ?? "member"),
  };
}

function ensureWorkspaceInvite(row: WorkspaceInvite): WorkspaceInvite {
  return {
    id: Number(row.id ?? 0),
    workspace_id: Number(row.workspace_id ?? 0),
    email: String(row.email ?? ""),
    role: String(row.role ?? "member"),
    token: String(row.token ?? ""),
    status: String(row.status ?? "pending"),
    invited_by_user_id:
      typeof row.invited_by_user_id === "number"
        ? row.invited_by_user_id
        : row.invited_by_user_id ?? null,
    accepted_by_user_id:
      typeof row.accepted_by_user_id === "number"
        ? row.accepted_by_user_id
        : row.accepted_by_user_id ?? null,
    created_at: row.created_at ?? null,
    expires_at: row.expires_at ?? null,
    accepted_at: row.accepted_at ?? null,
  };
}

function ensureClaimTradeScopeRow(
  row: Partial<ClaimTradeScopeRow>,
  fallbackStatus: "included" | "excluded"
): ClaimTradeScopeRow {
  return {
    index: Number(row.index ?? 0),
    trade_id: Number(row.trade_id ?? 0),
    workspace_id: Number(row.workspace_id ?? 0),
    member_id: Number(row.member_id ?? 0),
    symbol: String(row.symbol ?? ""),
    side: String(row.side ?? ""),
    opened_at: String(row.opened_at ?? ""),
    closed_at: row.closed_at ?? null,
    entry_price: Number(row.entry_price ?? 0),
    exit_price: typeof row.exit_price === "number" ? row.exit_price : row.exit_price ?? null,
    quantity: Number(row.quantity ?? 0),
    net_pnl: Number(row.net_pnl ?? 0),
    currency: String(row.currency ?? ""),
    strategy_tag: row.strategy_tag ?? null,
    source_system: row.source_system ?? null,
    cumulative_pnl:
      typeof row.cumulative_pnl === "number" ? row.cumulative_pnl : row.cumulative_pnl ?? null,
    scope_status: row.scope_status ?? fallbackStatus,
    exclusion_reason: row.exclusion_reason ?? null,
    exclusion_reason_label: row.exclusion_reason_label ?? null,
    exclusion_reason_detail: row.exclusion_reason_detail ?? null,
  };
}

function ensureClaimTradeEvidence(row: ClaimTradeEvidence): ClaimTradeEvidence {
  const includedRows = Array.isArray(row?.included_trades)
    ? row.included_trades.map((item) => ensureClaimTradeScopeRow(item, "included"))
    : Array.isArray(row?.trades)
      ? row.trades.map((item) => ensureClaimTradeScopeRow(item as ClaimTradeScopeRow, "included"))
      : [];

  const excludedRows = Array.isArray(row?.excluded_trades)
    ? row.excluded_trades.map((item) => ensureClaimTradeScopeRow(item, "excluded"))
    : [];

  return {
    ...row,
    trade_count: Number(row?.trade_count ?? includedRows.length),
    trades: includedRows,
    included_trade_count: Number(row?.included_trade_count ?? includedRows.length),
    excluded_trade_count: Number(row?.excluded_trade_count ?? excludedRows.length),
    included_trades: includedRows,
    excluded_trades: excludedRows,
    summary: row?.summary
      ? {
          workspace_trade_count: Number(row.summary.workspace_trade_count ?? 0),
          included_trade_count: Number(row.summary.included_trade_count ?? includedRows.length),
          excluded_trade_count: Number(row.summary.excluded_trade_count ?? excludedRows.length),
          excluded_breakdown: row.summary.excluded_breakdown ?? {},
        }
      : {
          workspace_trade_count: includedRows.length + excludedRows.length,
          included_trade_count: includedRows.length,
          excluded_trade_count: excludedRows.length,
          excluded_breakdown: {},
        },
  };
}

export const api = {
  register: async (payload: RegisterPayload): Promise<AuthResponse> => {
    const result = await apiFetch<AuthResponse>(`/auth/register`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (result.access_token) {
      setStoredAccessToken(result.access_token);
    }

    return result;
  },

  login: async (payload: LoginPayload): Promise<AuthResponse> => {
    const result = await apiFetch<AuthResponse>(`/auth/login`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (result.access_token) {
      setStoredAccessToken(result.access_token);
    }

    return result;
  },

  logout: () => {
    clearStoredAccessToken();
  },

  getMe: async (): Promise<MeResponse> => {
    return apiFetch<MeResponse>(withDevUser(`/auth/me`), {
      cache: "no-store",
    });
  },

  getMyWorkspaces: async (): Promise<AuthWorkspace[]> => {
    return apiFetch<AuthWorkspace[]>(withDevUser(`/workspaces`), {
      cache: "no-store",
    });
  },

  getDashboard: async (workspaceId: number): Promise<DashboardResponse> => {
    return apiFetch<DashboardResponse>(withDevUser(`/workspaces/${workspaceId}/dashboard`), {
      cache: "no-store",
    });
  },

  getWorkspaceSettings: async (workspaceId: number): Promise<WorkspaceSettings> => {
    const row = await apiFetch<WorkspaceSettings>(withDevUser(`/workspaces/${workspaceId}/settings`), {
      cache: "no-store",
    });

    return ensureWorkspaceSettings(row);
  },

  updateWorkspaceSettings: async (
    workspaceId: number,
    payload: WorkspaceSettingsUpdatePayload
  ): Promise<WorkspaceSettings> => {
    const row = await apiFetch<WorkspaceSettings>(withDevUser(`/workspaces/${workspaceId}/settings`), {
      method: "PATCH",
      body: JSON.stringify(payload),
    });

    return ensureWorkspaceSettings(row);
  },

  getWorkspaceUsage: async (workspaceId: number): Promise<WorkspaceUsageSummary> => {
    const row = await apiFetch<WorkspaceUsageSummary>(withDevUser(`/workspaces/${workspaceId}/usage`), {
      cache: "no-store",
    });

    return ensureWorkspaceUsageSummary(row);
  },

  getWorkspaceBillingFoundation: async (
    workspaceId: number
  ): Promise<WorkspaceBillingFoundation> => {
    const row = await apiFetch<WorkspaceBillingFoundation>(
      withDevUser(`/workspaces/${workspaceId}/billing-foundation`),
      {
        cache: "no-store",
      }
    );

    return ensureWorkspaceBillingFoundation(row);
  },

  createBillingCheckoutSession: async (
    workspaceId: number,
    payload: { plan_code: string; billing_cycle: string }
  ): Promise<BillingCheckoutResponse> => {
    const row = await apiFetch<any>(withDevUser(`/workspaces/${workspaceId}/billing/checkout`), {
      method: "POST",
      body: JSON.stringify(payload),
    });

    return {
      ...row,
      url: row?.checkout_url ?? row?.url ?? null,
      checkout_url: row?.checkout_url ?? row?.url ?? null,
      checkout_intent: row?.checkout_intent ?? undefined,
      manual_payment_details: ensureManualPaymentDetails(row?.manual_payment_details),
    };
  },

  createBillingPortalSession: async (workspaceId: number): Promise<BillingPortalResponse> => {
    const row = await apiFetch<any>(withDevUser(`/workspaces/${workspaceId}/billing/portal`), {
      method: "POST",
      body: JSON.stringify({}),
    });

    return {
      ...row,
      url: row?.portal_url ?? row?.url ?? null,
      portal_url: row?.portal_url ?? row?.url ?? null,
      manual_payment_details: ensureManualPaymentDetails(row?.manual_payment_details),
    };
  },

  getTrades: async (workspaceId: number): Promise<Trade[]> => {
    return apiFetch<Trade[]>(withDevUser(`/workspaces/${workspaceId}/trades`), {
      cache: "no-store",
    });
  },

  getImports: async (workspaceId: number): Promise<ImportBatch[]> => {
    return apiFetch<ImportBatch[]>(withDevUser(`/workspaces/${workspaceId}/imports`), {
      cache: "no-store",
    });
  },

  getWorkspaceMembers: async (workspaceId: number): Promise<WorkspaceMember[]> => {
    const rows = await apiFetch<WorkspaceMember[]>(withDevUser(`/workspaces/${workspaceId}/members`), {
      cache: "no-store",
    });
    return Array.isArray(rows) ? rows.map(ensureWorkspaceMember) : [];
  },

  updateWorkspaceMemberRole: async (
    workspaceId: number,
    userId: number,
    payload: { role: WorkspaceMemberRole }
  ): Promise<WorkspaceMember> => {
    const row = await apiFetch<WorkspaceMember>(
      withDevUser(`/workspaces/${workspaceId}/members/${userId}`),
      {
        method: "PATCH",
        body: JSON.stringify(payload),
      }
    );
    return ensureWorkspaceMember(row);
  },

  removeWorkspaceMember: async (
    workspaceId: number,
    userId: number
  ): Promise<{ removed: boolean; workspace_id: number; user_id: number }> => {
    return apiFetch(withDevUser(`/workspaces/${workspaceId}/members/${userId}`), {
      method: "DELETE",
    });
  },

  getWorkspaceInvites: async (workspaceId: number): Promise<WorkspaceInvite[]> => {
    const rows = await apiFetch<WorkspaceInvite[]>(withDevUser(`/workspaces/${workspaceId}/invites`), {
      cache: "no-store",
    });
    return Array.isArray(rows) ? rows.map(ensureWorkspaceInvite) : [];
  },

  createWorkspaceInvite: async (
    workspaceId: number,
    payload: { email: string; role: WorkspaceMemberRole | "member" | "operator" | "auditor" }
  ): Promise<WorkspaceInvite> => {
    const row = await apiFetch<WorkspaceInvite>(withDevUser(`/workspaces/${workspaceId}/invites`), {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return ensureWorkspaceInvite(row);
  },

  revokeWorkspaceInvite: async (workspaceId: number, inviteId: number): Promise<WorkspaceInvite> => {
    const row = await apiFetch<WorkspaceInvite>(
      withDevUser(`/workspaces/${workspaceId}/invites/${inviteId}/revoke`),
      {
        method: "POST",
      }
    );
    return ensureWorkspaceInvite(row);
  },

  acceptWorkspaceInvite: async (token: string) => {
    return apiFetch(`/invites/accept`, {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  },

  getLatestClaimSchema: async (): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/latest`), {
      cache: "no-store",
    });
  },

  getWorkspaceClaims: async (workspaceId: number): Promise<PublicClaimDirectoryItem[]> => {
    const rows = await apiFetch<PublicClaimDirectoryItem[]>(
      withDevUser(`/workspaces/${workspaceId}/claim-schemas`),
      {
        cache: "no-store",
      }
    );

    return Array.isArray(rows) ? rows.map(ensurePublicClaim) : [];
  },

  getClaimSchema: async (claimSchemaId: number): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/${claimSchemaId}`), {
      cache: "no-store",
    });
  },

  updateClaimSchema: async (
    claimSchemaId: number,
    payload: ClaimSchemaUpdatePayload
  ): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/${claimSchemaId}`), {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

    createTrade: async (workspaceId: number, payload: unknown): Promise<Trade> => {
    return apiFetch<Trade>(withDevUser(`/workspaces/${workspaceId}/trades`), {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  updateTrade: async (
    workspaceId: number,
    tradeId: number,
    payload: unknown
  ): Promise<Trade> => {
    return apiFetch<Trade>(withDevUser(`/workspaces/${workspaceId}/trades/${tradeId}`), {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  deleteTrade: async (
    workspaceId: number,
    tradeId: number
  ): Promise<{ status: string; trade_id: number }> => {
    return apiFetch<{ status: string; trade_id: number }>(
      withDevUser(`/workspaces/${workspaceId}/trades/${tradeId}`),
      {
        method: "DELETE",
      }
    );
  },

  importTradesCsv: async (workspaceId: number, file: File): Promise<ImportCsvResult> => {
    const formData = new FormData();
    formData.append("file", file);

    const headers = getAuthHeaders();

    const res = await fetch(`${API_BASE}${withDevUser(`/workspaces/${workspaceId}/trades/import-csv`)}`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!res.ok) {
      const rawText = await res.text();
      const payload = parseApiErrorPayload(rawText);
      const message =
        payload?.message ||
        payload?.detail ||
        rawText ||
        `CSV import failed with status ${res.status}`;
      throw new ApiError(message, res.status, payload, rawText);
    }

    return res.json() as Promise<ImportCsvResult>;
  },

  createClaimSchema: async (payload: ClaimSchemaCreatePayload): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas`), {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  cloneClaimSchema: async (claimSchemaId: number): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/${claimSchemaId}/clone`), {
      method: "POST",
    });
  },

  getClaimVersions: async (claimSchemaId: number): Promise<ClaimVersion[]> => {
    return apiFetch<ClaimVersion[]>(withDevUser(`/claim-schemas/${claimSchemaId}/versions`), {
      cache: "no-store",
    });
  },

  verifyClaimSchema: async (claimSchemaId: number): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/${claimSchemaId}/verify`), {
      method: "POST",
    });
  },

  publishClaimSchema: async (claimSchemaId: number): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/${claimSchemaId}/publish`), {
      method: "POST",
    });
  },

  lockClaimSchema: async (claimSchemaId: number): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(withDevUser(`/claim-schemas/${claimSchemaId}/lock`), {
      method: "POST",
    });
  },

  getClaimPreview: async (claimSchemaId: number): Promise<ClaimSchemaPreview> => {
    const row = await apiFetch<ClaimSchemaPreview>(
      withDevUser(`/claim-schemas/${claimSchemaId}/preview`),
      {
        cache: "no-store",
      }
    );

    return ensureLeaderboard(row);
  },

  getClaimEquityCurve: async (claimSchemaId: number): Promise<ClaimEquityCurve> => {
    const row = await apiFetch<ClaimEquityCurve>(
      withDevUser(`/claim-schemas/${claimSchemaId}/equity-curve`),
      {
        cache: "no-store",
      }
    );

    return {
      ...row,
      curve: Array.isArray(row.curve) ? row.curve : [],
    };
  },

  getClaimTrades: async (claimSchemaId: number): Promise<ClaimTradeEvidence> => {
    const row = await apiFetch<ClaimTradeEvidence>(withDevUser(`/claim-schemas/${claimSchemaId}/trades`), {
      cache: "no-store",
    });

    return ensureClaimTradeEvidence(row);
  },

  getEvidencePack: async (claimSchemaId: number): Promise<EvidencePack> => {
    return apiFetch<EvidencePack>(withDevUser(`/claim-schemas/${claimSchemaId}/evidence-pack`), {
      cache: "no-store",
    });
  },

  getEvidenceBundle: async (claimSchemaId: number): Promise<EvidenceBundle> => {
    return apiFetch<EvidenceBundle>(withDevUser(`/claim-schemas/${claimSchemaId}/evidence-bundle`), {
      cache: "no-store",
    });
  },

  getPublicClaim: async (claimSchemaId: number): Promise<PublicClaim> => {
    const row = await apiFetch<PublicClaim>(`/public/claim-schemas/${claimSchemaId}`, {
      cache: "no-store",
    });

    return ensurePublicClaim(row);
  },

  getPublicClaims: async (): Promise<PublicClaimDirectoryItem[]> => {
    const rows = await apiFetch<PublicClaimDirectoryItem[]>(`/public/claims`, {
      cache: "no-store",
    });

    return Array.isArray(rows) ? rows.map(ensurePublicClaim) : [];
  },

  getPublicClaimByHash: async (claimHash: string): Promise<PublicVerifyResult> => {
    const row = await apiFetch<PublicVerifyResult>(`/public/verify/${claimHash}`, {
      cache: "no-store",
    });

    return {
      ...row,
      leaderboard: Array.isArray(row.leaderboard) ? row.leaderboard : [],
      scope: row.scope ?? {
        period_start: "—",
        period_end: "—",
        included_members: [],
        included_symbols: [],
        methodology_notes: "",
        visibility: "—",
      },
      lifecycle: row.lifecycle ?? {
        status: row.verification_status || "unknown",
        verified_at: null,
        published_at: null,
        locked_at: null,
      },
      trade_set_hash: row.trade_set_hash ?? "—",
      trades: Array.isArray(row.trades)
        ? row.trades.map((item) => ensureClaimTradeScopeRow(item, "included"))
        : [],
      included_trade_count: Number(row.included_trade_count ?? 0),
      excluded_trade_count: Number(row.excluded_trade_count ?? 0),
      included_trades: Array.isArray(row.included_trades)
        ? row.included_trades.map((item) => ensureClaimTradeScopeRow(item, "included"))
        : [],
      excluded_trades: Array.isArray(row.excluded_trades)
        ? row.excluded_trades.map((item) => ensureClaimTradeScopeRow(item, "excluded"))
        : [],
      summary: row.summary
        ? {
            workspace_trade_count: Number(row.summary.workspace_trade_count ?? 0),
            included_trade_count: Number(row.summary.included_trade_count ?? 0),
            excluded_trade_count: Number(row.summary.excluded_trade_count ?? 0),
            excluded_breakdown: row.summary.excluded_breakdown ?? {},
          }
        : undefined,
      equity_curve: row.equity_curve
        ? {
            point_count: Number(row.equity_curve.point_count ?? 0),
            starting_equity: Number(row.equity_curve.starting_equity ?? 0),
            ending_equity: Number(row.equity_curve.ending_equity ?? 0),
            curve: Array.isArray(row.equity_curve.curve) ? row.equity_curve.curve : [],
          }
        : undefined,
    };
  },

  getClaimIntegrity: async (claimSchemaId: number): Promise<ClaimIntegrityResult> => {
    return apiFetch<ClaimIntegrityResult>(
      withDevUser(`/claim-schemas/${claimSchemaId}/verify-integrity`),
      {
        cache: "no-store",
      }
    );
  },

  getLatestAuditEvents: async (limit = 20): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(withDevUser(`/audit-events/latest?limit=${limit}`), {
      cache: "no-store",
    });
  },

  getAuditEventsForEntity: async (
    entityType: string,
    entityId: string | number
  ): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(
      withDevUser(`/audit-events/entity/${entityType}/${entityId}`),
      {
        cache: "no-store",
      }
    );
  },

  getAuditEventsForWorkspace: async (
    workspaceId: string | number,
    limit = 50
  ): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(
      withDevUser(`/audit-events/workspace/${workspaceId}?limit=${limit}`),
      {
        cache: "no-store",
      }
    );
  },
};