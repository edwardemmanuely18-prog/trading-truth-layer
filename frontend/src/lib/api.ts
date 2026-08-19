const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://trading-truth-layer.onrender.com";

export const API_BASE_URL = API_BASE;
const DEV_USER_ID: number | null = null;
const TOKEN_STORAGE_KEY = "ttl_access_token";
const ACTIVE_WORKSPACE_STORAGE_KEY = "ttl_active_workspace_id";

import type {
    WorkspaceEntitlements,
} from "./entitlements";

const inflightRequests = new Map<
  string,
  Promise<any>
>();

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

export function getStoredActiveWorkspaceId(): number | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(ACTIVE_WORKSPACE_STORAGE_KEY);
  if (!raw) return null;

  const parsed = Number(raw);
  return Number.isNaN(parsed) ? null : parsed;
}

export function setStoredActiveWorkspaceId(workspaceId: number | null) {
  if (typeof window === "undefined") return;

  if (workspaceId === null || workspaceId === undefined) {
    window.localStorage.removeItem(ACTIVE_WORKSPACE_STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(ACTIVE_WORKSPACE_STORAGE_KEY, String(workspaceId));
}

export function clearStoredActiveWorkspaceId() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACTIVE_WORKSPACE_STORAGE_KEY);
}

export type AuthUser = {
  id: number;
  email: string;
  name: string;
  role: string;
  email_verified: boolean;
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

export type ForgotPasswordPayload = {
  email: string;
};

export type ResendVerificationPayload = {
  email: string;
};

export type ResetPasswordPayload = {
  token: string;
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
  tags?: string[];
  strategy_tag?: string | null;
  source_system?: string | null;
};

export type VerifyClaimResult = {
  claim_id: number;
  workspace_id: number;
  name: string;
  status: string;
  visibility: string;
  claim_hash: string;
  stored_trade_set_hash?: string | null;
  recomputed_trade_set_hash?: string | null;
  integrity: "valid" | "compromised" | "unlocked";
  version_number?: number | null;
  root_claim_id?: number | null;
  parent_claim_id?: number | null;
  published_at?: string | null;
  verified_at?: string | null;
  locked_at?: string | null;
  period_start?: string | null;
  period_end?: string | null;
  public_view_path: string;
  verify_path: string;
};

export type VerifyPayloadV7 = {
  payload_version: string;

  issuer: {
    id?: number;
    name: string;
    type?: string;
    network: string;
    endpoint_kind?: string;
  };

  network_identity: {
    claim_hash: string;
    claim_id: number;
    workspace_id: number;
    verify_path: string;
    public_view_path: string;
    exposure_level: VerificationExposureLevel;
  };

  verification_record: {
    name: string;
    status: string;
    visibility: string;
    version_number?: number | null;
    root_claim_id?: number | null;
    parent_claim_id?: number | null;
  };

  scope: {
    period_start?: string | null;
    period_end?: string | null;
    included_trade_count: number;
    excluded_trade_count: number;
    included_member_ids: number[];
    included_symbols: string[];
  };

  integrity_record: {
    status: string;
    is_valid: boolean;
    stored_trade_set_hash?: string | null;
    recomputed_trade_set_hash?: string | null;
  };

  lifecycle: {
    verified_at?: string | null;
    published_at?: string | null;
    locked_at?: string | null;
  };

  proof_summary: {
    claim_hash: string;
    trade_set_hash?: string | null;
    integrity_status: string;
    integrity_valid: boolean;
    canonical: boolean;
    portable: boolean;
    api_addressable: boolean;
  };

  portable_capabilities?: {
    canonical?: boolean;
    portable?: boolean;
    api_addressable?: boolean;
  };

  // keep legacy fields (important!)
  claim_id: number;
  workspace_id: number;
  name: string;
  status: string;
  visibility: string;
  claim_hash: string;
  public_view_path: string;
  verify_path: string;
};

export interface BrokerConnection {
  id: number;

  provider: string;

  connection_name: string;

  connection_status: string;

  verification_status: string;

  account_environment: string;

  sync_status: string;

  trust_tier: string;

  account_id?: string;

  account_name?: string;

  last_sync_at?: string;

  verified_at?: string;
}

export interface BrokerAdapter {
  id: number;
  provider: string;
  display_name: string;
  adapter_type: string;
  trust_tier: string;
  supports_live_sync: boolean;
  supports_historical_import: boolean;
  status: string;
}

export interface VerifyBrokerConnectionPayload {
  connection_id: number;

  login?: string;
  password?: string;
  server?: string;

  api_key?: string;
  api_secret?: string;

  host?: string;
  port?: number;
  client_id?: number;

  flex_query_id?: string;
  flex_token?: string;
}


export interface ImportJob {
  id: number;

  adapter_provider: string;

  filename: string;

  file_type: string;

  status: string;

  records_detected: number;

  imported_records: number;

  created_at: string;
}

export interface SyncJob {
  id: number;
  provider: string;
  sync_type: string;
  status: string;
  records_processed: number;
  records_imported: number;
  error_message?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
}

export interface EvidenceRecord {
  trade_id: number;

  symbol: string;

  side: string;

  source_system?: string;

  import_source?: string;

  import_job_id?: number;

  broker_connection_id?: number;

  broker_account_id?: string;

  verification_state?: string;

  evidence_trust_tier?: string;

  raw_trade_hash?: string;

  ingestion_timestamp?: string;
}

export interface IntegrityRecord {
  trade_id: number;

  symbol: string;

  verification_state: string | null;

  evidence_trust_tier: string | null;

  integrity_type?: string;

  import_source: string | null;

  import_job_id: number | null;

  broker_connection_id: number | null;

  broker_account_id: string | null;

  broker_trade_id: string | null;

  raw_trade_hash: string | null;

  trade_fingerprint: string | null;

  ingestion_timestamp: string | null;
}

export interface WorkspaceSnapshot {

    health_score: number;

    health_state: string;

    trust_state: string;

    governance_state: string;

    active_alerts: number;

    services: {

        evidence_engine: string;

        verification_engine: string;

        report_engine: string;

        trust_layer: string;

        governance_engine: string;

    };

}

export async function getIntegrityRegistry(
  workspaceId: number
): Promise<IntegrityRecord[]> {

  return apiFetch(
    `/api/workspaces/${workspaceId}/evidence-registry`
  );

}

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

export type ImportSourceType =
  | "auto"
  | "csv"
  | "mt5"
  | "ibkr";

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

export type InstitutionalDashboardResponse = {
  workspace_id: number;

  workspace: {
    member_count: number;
    trade_count: number;
    claim_count: number;
  };

  claims: {
    draft: number;
    verified: number;
    published: number;
    locked: number;
  };

  workflow: {
    import_complete: boolean;
    claim_created: boolean;
    verification_started: boolean;
    published: boolean;
    locked: boolean;
  };

  governance: {
    utilization: number;
    status: string;
    effective_plan_code: string;
  };

  import_health: {
    rows_received: number;
    rows_imported: number;
    rows_rejected: number;
    rows_duplicates: number;

    duplicate_ratio: number;
    rejection_ratio: number;
  };

  strategy_analytics: {
    strategy_count: number;

    best_strategy?: {
      tag: string;
      trade_count: number;
      net_pnl: number;
      avg_pnl: number;
      win_rate: number;
      avg_win: number;
      avg_loss: number;
      expectancy: number;
    };

    strategies: any[];
  };

  trading_metrics: any;

  executive: {
    active_alerts: number;
    integrity_health: string;
    verification_coverage: number;
  };
};

export type PlanBilling = {
  monthly_price_usd?: number | null;
  annual_price_usd?: number | null;

  /*
    Backward compatibility layer.
    Legacy plan responses still expose these keys.
  */
  monthly?: number | null;
  annual?: number | null;

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
  preferences?: {

      timezone: string;

      language: string;

      currency: string;

      date_format: string;

      auto_refresh: boolean;

      auto_save: boolean;

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
  is_internal: boolean;
};

export type WorkspacePlanSimulation = {
    workspace_id: number;

    current_plan: string;

    available_plans: {
        code: string;
        name: string;
        entitled: boolean;
        limitations: string[];
        capabilities: string[];
    }[];

    simulated_plan?: string | null;

    simulation_enabled: boolean;

    internal_workspace: boolean;
};

export type WorkspaceSettingsUpdatePayload = {

    name: string;

    description?: string | null;

    billing_email?: string | null;

    timezone: string;

    language: string;

    currency: string;

    date_format: string;

    auto_refresh: boolean;

    auto_save: boolean;

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
    claim_limit?: number;
    trade_limit?: number;
    member_limit?: number;
    storage_limit_mb?: number;

    /*
      Legacy compact keys still supported by normalization layer.
    */
    claims?: number;
    trades?: number;
    members?: number;
    storage_mb?: number;
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
  billing_enabled?: boolean;
  secret_key_configured?: boolean;
  package_installed?: boolean;
};

export type WorkspaceUsageSummary = {
  workspace_id: number;

  plan_code: string;

  billing_status: string;

  effective_plan_code: string;

  limits?: {
    claims: number;
    trades: number;
    members: number;
    storage_mb: number;
  };

  usage?: {
    members: number;
    trades: number;
    active_trades?: number;
    claims: number;
    storage_mb: number;
  };

  metrics?: {
    used: number;
    consumed: number;
    ledger_count: number;
    limit: number;
    utilization: number;
  };

  diagnostics?: {
    resolved_plan_code?: string;

    raw_limit_columns?: {
      claim_limit?: number;
      trade_limit?: number;
      member_limit?: number;
      storage_limit_mb?: number;
    };

    defaults_for_resolved_plan?: {
      claims?: number;
      trades?: number;
      members?: number;
      storage_mb?: number;
    };
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

    paddle_enabled?: boolean;
    api_key_configured?: boolean;
    paddle_price_id?: string;

    manual_billing_enabled?: boolean;

    price_lookup_key?: string;

    provider_ready?: boolean;

    checkout_ready?: boolean;

    portal_ready?: boolean;

    webhookConfigured?: boolean;

    enabled_features?: Record<string, boolean>;

    available_plans?: {
        code: string;
        name: string;
        description: string;
        pricing: {
            monthly: number;
            annual: number;
        };
        recommended_for: string[];
        commercial_services: string[];
        features: Record<string, boolean>;
    }[];
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

  provider?: string;

  url?: string | null;

  portal_url?: string | null;

  support_email?: string;

  message?: string |null;

  created_at?: string | null;

  manual_payment_details?: ManualPaymentDetails;
};

export type BillingInvoiceResponse = {

    invoice_available: boolean;

    invoice_url: string | null;

    provider?: string;

    invoice_number?: string;

    issued_at?: string;

    message?: string;

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
  active_billing_provider?: string | null;
  billing_provider_label?: string | null;
  provider_customer_id?: string | null;
  provider_subscription_id?: string | null;
  provider_environment?: string | null;
  manual_billing_visible?: boolean;
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
    environment?: string | null;
  };
  manual_billing?: {
    enabled: boolean;
    ready: boolean;
    visible?: boolean;
    payment_method?: string | null;
  };
  manual_payment_details?: ManualPaymentDetails;
  public_plans?: Record<string, any>;
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

export interface WorkspaceGovernanceSnapshot {

  workspace: {
    id: number;
    name: string;
    plan: string;
  };

  capacity: {
    members: number;
    member_limit: number;
    utilization: number;
  };

  identity_summary: {
    owners: number;
    operators: number;
    auditors: number;
    members: number;
  };

  authority_distribution: {
    critical: number;
    high: number;
    medium: number;
    standard: number;
  };

  governance_health: {
    overall_score: number;

    owner: {
      score: number;
      healthy: boolean;
    };

    operator: {
      score: number;
      healthy: boolean;
    };

    auditor: {
      score: number;
      healthy: boolean;
    };

    invitation: {
      score: number;
      healthy: boolean;
      findings: {
        title: string;
        description: string;
        severity: string;
      }[];
    };
  };

  recommendations: {
    title: string;
    description: string;
    priority: string;
    action: string;
  }[];

  profiles: any[];

  governance_version?: string;

  generated_by?: string;

  snapshot_type?: string;
}

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
  verify_path?: string | null;
  public_view_path?: string | null;
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
  issuer?: ClaimIssuer;
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

export type ClaimTemplate = {
  id: number;

  workspace_id: number;

  name: string;

  description: string;

  template_type: string;

  included_member_ids_json: number[];

  included_symbols_json: string[];

  excluded_trade_ids_json: number[];

  methodology_notes: string;

  visibility: string;

  active: boolean;
};

export type ClaimTemplateCreatePayload = {
  workspace_id: number;
  name: string;
  description: string;
  template_type: string;
  included_member_ids_json: number[];
  included_symbols_json: string[];
  excluded_trade_ids_json: number[];
  methodology_notes: string;
  visibility: string;
  active: boolean;
};

export type ClaimTemplateUpdatePayload =
  ClaimTemplateCreatePayload;

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
  tags?: string[];
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
  tags?: string[];
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
  root_claim_id?: number | null;
  public_view_path?: string | null;
  verify_path?: string | null;
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
  issuer?: ClaimIssuer;
  profile?: PublicTrustProfile | null;
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
  issuer?: ClaimIssuer;
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
  public_view_path?: string;
  verify_path?: string;
};

export type ImportPreviewResponse = {
  preview_session_id: number;
  status: string;

  preview: {
    workspace_id: number;
    source_type: string;

    rows_received: number;
    rows_accepted: number;
    rows_rejected: number;
    rows_duplicates: number;

    normalized_preview: any[];
    rejected_preview: any[];
    duplicate_preview: any[];
  };

  message: string;
};

export type ConfirmImportPreviewResponse = {
  preview_session_id: number;
  status: string;

  rows_imported: number;
  rows_rejected: number;
  rows_duplicates: number;

  message: string;
};

export type IntegrationProviderType =
  | "manual"
  | "csv"
  | "mt4"
  | "mt5"
  | "broker_api"
  | "platform_api"
  | "webhook"
  | "unknown";

export type VerificationExposureLevel =
  | "internal_only"
  | "unlisted"
  | "public"
  | "external_distribution";

export type ClaimIssuer = {
  id: number;
  name: string;
  type: string;
  network: string;
};

export type ExternalVerificationIdentity = {
  claim_hash: string;
  verify_path: string;
  public_view_path?: string | null;
  trade_set_hash?: string | null;
  verification_status: string;
  integrity_status?: string | null;
  exposure_level: VerificationExposureLevel;
};

export type ExternalVerificationRecord = {
  claim_schema_id: number;
  workspace_id?: number | null;
  name: string;
  identity: ExternalVerificationIdentity;
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
  metrics: {
    trade_count: number;
    net_pnl: number;
    profit_factor: number;
    win_rate: number;
  };
  lineage?: {
    parent_claim_id?: number | null;
    root_claim_id?: number | null;
    version_number?: number | null;
  };
};

export type IntegrationSourceMetadata = {
  provider: IntegrationProviderType;
  provider_label?: string | null;
  source_system?: string | null;
  source_account_id?: string | null;
  source_workspace_ref?: string | null;
  sync_mode?: "manual" | "scheduled" | "webhook" | "api" | "unknown";
  last_synced_at?: string | null;
};

export type PlatformCapabilityFlags = {
  public_verification_enabled: boolean;
  public_distribution_enabled: boolean;
  external_verification_enabled: boolean;
  api_access_enabled: boolean;
  broker_import_enabled: boolean;
  webhook_ingestion_enabled: boolean;
};

export type PlatformReadiness = {
  workspace_id?: number | null;
  capabilities: PlatformCapabilityFlags;
  integration_sources: IntegrationSourceMetadata[];
  verification_exposure_level: VerificationExposureLevel;
  recommended_next_step?: string | null;
};

export type ExternalVerificationLookupResult = {
  record: ExternalVerificationRecord;
  platform_readiness?: PlatformReadiness;
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

export type ClaimDisputeStatus = "open" | "under_review" | "resolved" | "rejected";

export type ClaimDispute = {
  id: number;
  claim_schema_id: number;
  workspace_id: number;

  status: ClaimDisputeStatus;
  challenge_type: string;
  reason_code: string;

  summary: string;
  evidence_note?: string | null;

  reporter_user_id: number;
  reviewer_user_id?: number | null;

  resolution_note?: string | null;

  opened_at: string;
  updated_at: string;
  resolved_at?: string | null;
};

export type PublicTrustProfile = {
  profile_id: string;
  workspace_id: number;
  name: string;
  type: string;
  network: string;
  claims_count: number;
  locked_claims_count: number;
  contested_claims_count: number;
  average_trust_score: number;
  average_network_score: number;
  total_net_pnl: number;
  trust_profile_band: string;
};

/* ===========================================================
   TVS CANONICAL VERIFICATION CERTIFICATE
   =========================================================== */

export type VerificationTier =
    | "tier_1"
    | "tier_2"
    | "tier_3";

export type VerificationCertificateIdentity = {

    claim_id: number;

    workspace_id: number;

    claim_hash: string;

    verify_path: string;

    public_view_path: string;

    exposure_level: VerificationExposureLevel;

};

export type VerificationCertificateIssuer = {

    id?: number;

    name: string;

    type: string;

    network: string;

};

export type VerificationCertificateVerification = {

    status: string;

    visibility: string;

    canonical: boolean;

    portable: boolean;

    api_addressable: boolean;

};

export type VerificationCertificateLifecycle = {

    verified_at?: string | null;

    published_at?: string |null;

    locked_at?: string | null;

};

export type VerificationCertificateLineage = {

    version_number?: number | null;

    parent_claim_id?: number | null;

    root_claim_id?: number | null;

};

export type VerificationCertificateIntegrity = {

    status: string;

    valid: boolean;

    stored_trade_set_hash?: string | null;

    recomputed_trade_set_hash?: string | null;

};

export type VerificationCertificateScope = {

    period_start?: string | null;

    period_end?: string | null;

    included_trade_count: number;

    excluded_trade_count: number;

    included_member_ids: number[];

    included_symbols: string[];

};

export type VerificationCertificatePerformance = {

    trade_count: number;

    net_pnl: number;

    profit_factor: number;

    win_rate: number;

};

export type VerificationCertificateTrust = {

    score: number;

    band: string;

    tier: VerificationTier;

};

export type VerificationCertificateEvidence = {

    primary_tier: VerificationTier;

    primary_source: string;

    trade_set_hash?: string | null;

};

export type VerificationCertificate = {

    payload_version: string;

    identity: VerificationCertificateIdentity;

    issuer: VerificationCertificateIssuer;

    verification: VerificationCertificateVerification;

    lifecycle: VerificationCertificateLifecycle;

    lineage: VerificationCertificateLineage;

    integrity: VerificationCertificateIntegrity;

    scope: VerificationCertificateScope;

    performance: VerificationCertificatePerformance;

    trust: VerificationCertificateTrust;

    evidence: VerificationCertificateEvidence;

    leaderboard?: PublicClaim["leaderboard"];

    profile?: PublicTrustProfile | null;

    equity_curve?: ClaimEquityCurve;

};

export type PublicProfileResponse = {
  profile: PublicTrustProfile;
  claims: PublicClaimDirectoryItem[];
  claims_count: number;
};

export type ApiErrorPayload = {
  code?: string;
  message?: string;
  detail?: string;
  page?: string;
  plan?: string;
  resource?: string;
  workspace_id?: number;
  used?: number;
  limit?: number;
  recommended_action?: string;
  upgrade_hint?: string;
  upgrade_required?: boolean;
};

export type VerificationAnalytics = {

    executive: {

        workspace_trust_score: number;

        allocator_ready: boolean;

        network_health: string;

        verification_band: string;

    };

    coverage: {

        verification: number;

        publication: number;

        lock: number;

    };

    lifecycle: {

        draft: number;

        verified: number;

        published: number;

        locked: number;

    };

    visibility: {

        private?: number;

        unlisted?: number;

        public?: number;

    };

    broker_network: {

        total_accounts: number;

        verified: number;

        live: number;

        providers: string[];

    };

    integrity: {

        integrity_score: number;

        open_findings: number;

        resolved: number;

        claims_scanned: number;

        critical: number;

        high: number;

        warning: number;

        fatal: number;

        total_alerts: number;

        audit_events: number;

    };

    claims: {

        id: number;

        name: string;

        status: string;

        visibility: string;

        network_state: string;

        claim_hash?: string | null;

        verified_at?: string | null;

        published_at?: string | null;

        locked_at?: string | null;

    }[];

};

export type ExternalReview = {
  id: number;

  claim_schema_id: number;

  reviewer_name: string;

  reviewer_organization?: string | null;

  reviewer_role: string;

  observation_type: string;

  statement: string;

  rating?: number | null;

  review_direction: string;

  status: string;

  created_at?: string | null;
};

export type ExternalReviewResponse = {
  count: number;
  reviews: ExternalReview[];
};

export type ExternalReviewAnalytics = {
  total_reviews: number;

  roles: Record<string, number>;

  observation_types: Record<string, number>;
};

export type CreateReviewPayload = {
  claim_schema_id: number;

  reviewer_name: string;

  reviewer_organization?: string;

  reviewer_role: string;

  observation_type: string;

  statement: string;

  review_finding?: string;
};

export async function createExternalReview(
  workspaceId: number,
  payload: CreateReviewPayload
) {
  return apiFetch(
    `/external-reviews/workspace/${workspaceId}`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export type TrustScoresAnalytics = {
  average_trust_score: number;
  average_network_score: number;

  claims_count: number;
  locked_claims_count: number;
  contested_claims_count: number;

  total_net_pnl: number;

  trust_profile_band: string;

  workspace_id: number;
  profile_id: string;

  type: string;
  network: string;
};

export type TrustScore = {

  claim_id: number;

  claim_name: string;

  status: string;

  trust_score: number;

  review_count: number;

  average_rating: number;

  tier: string;

  verification_band: string;

  decision: string;

  confidence: number;

  verified_at?: string | null;

  published_at?: string | null;

  locked_at?: string | null;

};

export type TrustScoreResponse = {

  summary: {

    claims: number;

    average_score: number;

    institutional_grade: string;

    verified: number;

    network_score: number;

  };

  count: number;

  scores: TrustScore[];

};

/* ===========================================================
   INSTITUTIONAL INVESTIGATION SYSTEM (IIS)
=========================================================== */

export interface InvestigationNode {

    id: string;

    type: string;

    node_type: string;

    label: string;

    score: number;

    severity?: string;

    metadata?: Record<string, any>;

}

export interface InvestigationRelationship {

    source: string;

    target: string;

    relationship: string;

    weight: number;

    confidence: number;

    metadata: Record<string, any>;

}

export interface InvestigationTimelineEvent {

    timestamp: string;

    category: string;

    title: string;

    description: string;

    severity: string;

    evidence_reference?: string;

    metadata?: Record<string, any>;

}

export interface InvestigationFinding {

    id: string;

    title: string;

    description: string;

    severity: string;

    confidence: number;

    affected_claims: number[];

    affected_trades: number[];

    affected_members: number[];

    affected_accounts: number[];

    affected_sync_jobs: number[];

    evidence: string[];

    recommendation: string;

}

export interface InvestigationRecommendation {

    priority: number;

    title: string;

    rationale: string;

    action: string;

    automated?: boolean;

}

export interface InvestigationCriticalPathStep {
    order: number;
    title: string;
    category: string;
    severity: string;
    description: string;
    metadata: Record<string, unknown>;
}

export interface InvestigationCriticalPath {
    score: number;
    root_cause: string;
    steps: InvestigationCriticalPathStep[];
    recommendations: string[];
}

export interface InvestigationSummary {

    investigation_confidence: number;

    total_findings: number;

    critical_findings: number;

    high_findings: number;

    medium_findings: number;

    low_findings: number;

    informational_findings: number;

    evidence_nodes: number;

    relationships: number;

    timeline_events: number;

    affected_claims: number;

    affected_members: number;

    affected_accounts: number;

    affected_sync_jobs: number;

    overall_risk: string;

    executive_summary: string;

}

export interface InvestigationReport {

    workspace_id: number;

    scope: string;

    scope_id: number;

    status: string;

    generated_at: string;

    metadata?: Record<string, unknown>;

    summary: InvestigationSummary;

    findings: InvestigationFinding[];

    nodes: InvestigationNode[];

    relationships: InvestigationRelationship[];

    timeline: InvestigationTimelineEvent[];

    recommendations: InvestigationRecommendation[];

    critical_path?: InvestigationCriticalPath;

    execution?: InvestigationDomain;

    evidence?: InvestigationDomain;

    governance?: InvestigationDomain;

    broker?: InvestigationDomain;

    synchronization?: InvestigationDomain;

    review?: InvestigationDomain;

    behavior?: InvestigationDomain;

    verification?: InvestigationDomain;

    allocator?: InvestigationDecision;

}

export interface InvestigationDomain {

    name: string;

    confidence: number;

    findings: InvestigationFinding[];

    metadata: Record<string, any>;

}

export interface InvestigationDecision {

    decision: string;

    confidence: number;

    rationale: string;

    residual_risk: string;

    required_actions: string[];

    metadata: Record<string, unknown>;

}

export interface InvestigationDomains {

    execution: InvestigationDomain;

    evidence: InvestigationDomain;

    governance: InvestigationDomain;

    broker: InvestigationDomain;

    synchronization: InvestigationDomain;

    review: InvestigationDomain;

    behavior: InvestigationDomain;

    verification: InvestigationDomain;

    allocator: InvestigationDomain;

}

export type LeaderboardAnalytics = {
  summary: {
    claims: number;
    members: number;
  };

  claim_rankings: any[];

  member_rankings: any[];
};

export type RiskAnalytics = {
  overview: {
    trades: number;
    net_pnl: number;
    wins: number;
    losses: number;
    win_rate: number;
    profit_factor: number;
    max_drawdown: number;
  };

  recent_claims: {
    claim_schema_id: number;
    name: string;
    status: string;
    trade_count: number;
    net_pnl: number;
    profit_factor: number;
    max_drawdown: number;
  }[];
};

export async function getRiskAnalytics(
  workspaceId: number
): Promise<RiskAnalytics> {

  return apiFetch<RiskAnalytics>(
    `/workspace/${workspaceId}/risk-analytics`
  );
}

/* ===========================================================
   EVIDENCE ACQUISITION
=========================================================== */

export interface EvidenceAcquisitionOverview {

    summary: {

        connected_sources: number;

        registered_adapters: number;

        active_synchronizations: number;

        evidence_packages: number;

    };

    runtime: {

        state: string;

        registered_engines: number;

        running_engines: number;

        active_connections: number;

        synchronization_jobs: number;

    };

    providers: {

        total: number;

        certified: number;

        active: number;

        synchronizing: number;

        failed: number;

    };

    bridge: {

        registered_engines: number;

        desktop_registered: boolean;

        financial_registered: boolean;

        gateway_registered: boolean;

        healthy: boolean;

        desktop: boolean;

        financial: boolean;

        gateway: boolean;

    };

    engines: {

        gateway: {

            registered: boolean;

            healthy: boolean;

        };

        desktop: {

            registered: boolean;

            healthy: boolean;

        };

        financial: {

            registered: boolean;

            healthy: boolean;

        };

    };

}

export interface EvidenceAcquisitionSource {
    name: string;
    engine: string;
    provider_type: string;
    certified: boolean;
    active: boolean;
    connected: boolean;
    state: string;

    configured_connections?: number;
    connected_connections?: number;
    healthy_connections?: number;
    verified_connections?: number;
}

/* ===========================================================
   V2 EVIDENCE REGISTRY
   =========================================================== */

export interface V2EvidenceRegistryProvider {
  provider_name: string;
  provider_platform: string;
  broker_server: string | null;
  broker_account_id: string | null;
  broker_account_name: string | null;
  account_state: string | null;
  account_currency: string | null;
  original_ticket_id: string | null;
  original_deal_id: string | null;
  original_order_id: string | null;
  original_position_id: string | null;
  original_execution_id: string | null;
}

export interface V2EvidenceRegistryRecord {
  canonical_evidence_id: string;
  evidence_type: string;
  workspace_id: number | null;
  provider_id: string | null;
  evidence_hash: string;
  evidence_version: number;
  lifecycle: string;
  synchronization_batch: string | null;
  synchronization_session: string | null;
  registered_at: string | null;
  registered_at_utc: string | null;
  registered_at_timezone: string;

  provider: V2EvidenceRegistryProvider;

  metadata: Record<string, unknown>;
}

export interface V2EvidenceRegistryDetail
  extends V2EvidenceRegistryRecord {
  registered_at_utc: string | null;
  registered_at_timezone: string;

  canonical_payload: Record<string, unknown> | null;
  provenance_payload: Record<string, unknown> | null;

  payload_hash: string | null;
  evidence_payload_size: number | null;
}

export interface V2EvidenceRegistryPagination {
  page: number;
  page_size: number;
  total_records: number;
  total_pages: number;
  has_previous: boolean;
  has_next: boolean;
}

export interface V2EvidenceRegistryPage {
  workspace_id: number;
  evidence_type: string | null;
  evidence_types: string[] | null;
  records: V2EvidenceRegistryRecord[];
  pagination: V2EvidenceRegistryPagination;
}

export interface V2EvidencePackage {
  synchronization_batch: string;
  record_count: number;
  synchronization_session: string | null;
  provider_name: string | null;
  provider_platform: string | null;
  broker_account_id: string | null;
  first_registered_at: string | null;
  last_registered_at: string | null;
}

export interface V2EvidencePackagePage {
  workspace_id: number;
  packages: V2EvidencePackage[];
  pagination: {
    page: number;
    page_size: number;
    total_packages: number;
    total_pages: number;
    has_previous: boolean;
    has_next: boolean;
  };
}

export interface V2EvidenceRegistryResponse {
  workspace_id: number;
  records: V2EvidenceRegistryRecord[];
}

export interface V2EvidenceRegistrySummary {
  workspace_id: number;
  total_records: number;
  lifecycle_counts: Record<string, number>;
  provider_counts: Record<string, number>;
  evidence_type_counts: Record<string, number>;
}

export interface V2EvidenceRegistrySearchResponse {
  workspace_id: number;
  query: string;
  results: V2EvidenceRegistryRecord[];
}

export interface V2EvidencePackage {
    synchronization_batch: string;
    record_count: number;
    synchronization_session: string | null;
    provider_name: string | null;
    provider_platform: string | null;
    broker_account_id: string | null;
    first_registered_at: string | null;
    last_registered_at: string | null;
}

export interface V2EvidencePackagePage {
    workspace_id: number;
    packages: V2EvidencePackage[];
    pagination: {
        page: number;
        page_size: number;
        total_packages: number;
        total_pages: number;
        has_previous: boolean;
        has_next: boolean;
    };
}

export async function getV2EvidencePackagesPage(
    workspaceId: number,
    page = 1,
    pageSize = 25,
): Promise<V2EvidencePackagePage> {
    return apiFetch<V2EvidencePackagePage>(
        `/workspaces/${workspaceId}/evidence-registry/v2/packages?page=${page}&page_size=${pageSize}`,
    );
}

export interface EvidenceAcquisitionSynchronization {

    id: string;

    provider: string;

    status: string;

    progress: number;

    started_at?: string | null;

    completed_at?: string | null;

}

export interface EvidenceAcquisitionDiagnostics {

    runtime_state: string;

    runtime_health: string;

    registered_engines: number;

    registered_providers: number;

    active_connections: number;

    synchronization_jobs: number;

}

/* -----------------------------------------------------------
   Overview
------------------------------------------------------------ */

export async function getEvidenceAcquisitionOverview(
    workspaceId: number,
): Promise<EvidenceAcquisitionOverview> {

    return apiFetch<EvidenceAcquisitionOverview>(
        `/workspaces/${workspaceId}/evidence-acquisition/overview`,
    );

}

/* -----------------------------------------------------------
   Sources
------------------------------------------------------------ */

export async function getEvidenceAcquisitionSources(
    workspaceId: number,
): Promise<EvidenceAcquisitionSource[]> {

    return apiFetch<EvidenceAcquisitionSource[]>(
        `/workspaces/${workspaceId}/evidence-acquisition/sources`,
    );

}

/* -----------------------------------------------------------
   Synchronization Center
------------------------------------------------------------ */

export async function getEvidenceAcquisitionSynchronizations(
    workspaceId: number,
): Promise<EvidenceAcquisitionSynchronization[]> {

    return apiFetch<EvidenceAcquisitionSynchronization[]>(
        `/workspaces/${workspaceId}/evidence-acquisition/synchronizations`,
    );

}

/* -----------------------------------------------------------
   Diagnostics
------------------------------------------------------------ */

export async function getEvidenceAcquisitionDiagnostics(
    workspaceId: number,
): Promise<EvidenceAcquisitionDiagnostics> {

    return apiFetch<EvidenceAcquisitionDiagnostics>(
        `/workspaces/${workspaceId}/evidence-acquisition/diagnostics`,
    );

}

export async function testDesktopConnection(
    workspaceId: number,
    payload: DesktopConnectionTestRequest,
): Promise<DesktopConnectionTestResponse> {

    return apiFetch<DesktopConnectionTestResponse>(
        `/api/workspaces/${workspaceId}/provider-connections/desktop/test`,
        {
            method: "POST",
            body: JSON.stringify(payload),
        },
    );
}

export async function createDesktopConnection(
    workspaceId: number,
    payload: DesktopConnectionCreateRequest,
): Promise<DesktopConnectionCreateResponse> {

    return apiFetch<DesktopConnectionCreateResponse>(
        `/api/workspaces/${workspaceId}/provider-connections/desktop/create`,
        {
            method: "POST",
            body: JSON.stringify(payload),
        },
    );
}

/* ===========================================================
   PROVIDER CONNECTIONS
=========================================================== */

export interface ProviderConnectionsOverview {

    summary: {
        supported_providers: number;
        configured_connections: number;
        verified_connections: number;
        healthy_connections: number;
        synchronizing: number;
        evidence_packages: number;
    };

    engines: {

        desktop: {
            name: string;
            display_name?: string;
            supported_providers: number;
            configured_connections: number;
            active_connections: number;
            synchronizing_connections: number;
            healthy_connections: number;
            initialized: boolean;
            running: boolean;
            healthy: boolean;
        };

        gateway: {
            name: string;
            display_name?: string;
            supported_providers: number;
            configured_connections: number;
            active_connections: number;
            synchronizing_connections: number;
            healthy_connections: number;
            initialized: boolean;
            running: boolean;
            healthy: boolean;
        };

        financial: {
            name: string;
            display_name?: string;
            supported_providers: number;
            configured_connections: number;
            active_connections: number;
            synchronizing_connections: number;
            healthy_connections: number;
            initialized: boolean;
            running: boolean;
            healthy: boolean;
        };

    };

}

export interface ProviderConnectionEngine {

    id: string;

    name: string;

    supported_providers: number;

    configured_connections: number;

    healthy_connections: number;

    status: string;

}

export interface ProviderConnectionRecord {
    id: string;
    workspace_id: number;
    connection_name: string;
    provider: string;
    engine: string;
    environment: string;
    status: string;
    health: string;
    connected: boolean;
    verified: boolean;
}

export interface ProviderConnectionStatistics {
    synchronization_count: number;
    successful_synchronizations: number;
    failed_synchronizations: number;
    evidence_packages: number;
    last_synchronization: string | null;
}

export interface ProviderConnectionDetail {
    id: string;
    workspace_id: number;
    connection_name: string;
    provider: string;
    engine: string;
    environment: string;
    status: string;
    health: string;
    verified: boolean;
    connected: boolean;
    created_at: string;
    updated_at: string;
    statistics: ProviderConnectionStatistics;
}

export interface DesktopConnectionVerificationCheck {
    name: string;
    passed: boolean;
    message: string;
    observed: any;
    expected: any;
}

export interface DesktopConnectionVerificationResponse {
    provider: string;
    verified: boolean;
    checks: DesktopConnectionVerificationCheck[];
    error: string | null;
    snapshot: {
        provider: string;
        provider_version?: string | null;
        connected: boolean;
        account_id?: string | null;
        broker?: string | null;
        server?: string | null;
        terminal?: string | null;
        terminal_version?: string | null;
        metadata?: Record<string, any>;
    } | null;
}

export interface ProviderConnectionActivity {

    total: number;

    connected: number;

    disconnected: number;

    failed: number;

    synchronizing: number;

}

export async function getProviderConnectionsOverview(
    workspaceId: number,
): Promise<ProviderConnectionsOverview> {

    return apiFetch<ProviderConnectionsOverview>(
        `/api/workspaces/${workspaceId}/provider-connections/overview`,
    );

}

export async function getProviderConnectionEngines(
    workspaceId: number,
): Promise<ProviderConnectionEngine[]> {

    return apiFetch<ProviderConnectionEngine[]>(
        `/api/workspaces/${workspaceId}/provider-connections/engines`,
    );

}

export async function getProviderConnections(
    workspaceId: number,
): Promise<ProviderConnectionRecord[]> {

    return apiFetch<ProviderConnectionRecord[]>(
        `/api/workspaces/${workspaceId}/provider-connections/connections`,
    );

}

export async function getProviderConnectionActivity(
    workspaceId: number,
): Promise<ProviderConnectionActivity> {

    return apiFetch<ProviderConnectionActivity>(
        `/api/workspaces/${workspaceId}/provider-connections/activity`,
    );

}

export async function getProviderConnection(
    workspaceId: number,
    connectionId: string,
): Promise<ProviderConnectionDetail> {
    return apiFetch<ProviderConnectionDetail>(
        `/api/workspaces/${workspaceId}/provider-connections/${encodeURIComponent(connectionId)}`,
        {
            cache: "no-store",
        },
    );
}

// ============================================================================
// Provider Connections
// ============================================================================

export async function synchronizeProviderConnection(
    workspaceId: number,
    connectionId: string,
) {
    return apiFetch(

        `/api/workspaces/${workspaceId}/provider-connections/${connectionId}/synchronize`,

        {
            method: "POST",
        },

    );
}

export async function verifyProviderConnection(
    workspaceId: number,
    connectionId: string,
): Promise<DesktopConnectionVerificationResponse> {
    return apiFetch<DesktopConnectionVerificationResponse>(
        `/api/workspaces/${workspaceId}/provider-connections/${encodeURIComponent(connectionId)}/verify`,
        {
            method: "POST",
        },
    );
}

/* ===========================================================
   DESKTOP TRADING ENGINE
=========================================================== */

export interface DesktopConnectionTestRequest {
    provider: string;

    connection_name: string;

    environment: "live" | "demo";

    evidence_categories: string[];

    synchronization_profile: string;

    credentials: Record<string, any>;
}

export interface DesktopConnectionConnection {
    workspace_id: number;
    provider: string;
    connection_name: string;
    environment: string;
    synchronization_profile: string;
    verification_status: string;
    connection_status: string;
    evidence_categories: string[];
}

export interface DesktopConnectionDiscovery {
    provider: string;
    provider_registered: boolean;
    engine_version: string;
    engine_running: boolean;
    engine_initialized: boolean;

    provider_version?: string | null;

    broker_name?: string | null;

    terminal_company?: string | null;
    terminal_version?: string | null;
    terminal_build?: string | null;
    terminal_architecture?: string | null;
    terminal_path?: string | null;

    account_number?: string | null;
    server?: string | null;

    supported_evidence: string[];

    healthy: boolean;
}

export interface DesktopConnectionSynchronization {
    engine: string;
    initialized: boolean;
    running: boolean;
    healthy: boolean;
    synchronization_profile: string;
    synchronization_state: string;
    synchronized_categories: string[];
    evidence_packages: number;
    synchronized_at?: string | null;
}

export interface DesktopConnectionRuntime {
    initialized: boolean;
    running: boolean;
    healthy: boolean;
    statistics: Record<string, any>;
}

export interface DesktopConnectionResponse {
    success: boolean;
    message: string;

    connection: DesktopConnectionConnection;

    discovery: DesktopConnectionDiscovery;

    synchronization: DesktopConnectionSynchronization;

    runtime: DesktopConnectionRuntime;
}

export type DesktopConnectionTestResponse =
    DesktopConnectionResponse;

export interface DesktopConnectionCreateRequest {
    provider: string;

    connection_name: string;

    environment: "live" | "demo";

    synchronization_profile: string;

    evidence_categories: string[];

    credentials: Record<string, any>;
}

export interface DesktopConnectionCreateResponse {
    id: string;
    provider: string;
    connection_name: string;
    status: string;
    synchronization_profile: string;
    created_at: string;
}

export class ApiError extends Error {
  status: number;
  payload: ApiErrorPayload | null;
  rawBody: string;
  redirectTo?: string;

  constructor(
    message: string,
    status: number,
    payload: ApiErrorPayload | null,
    rawBody: string,
    options?: { redirectTo?: string }
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
    this.rawBody = rawBody;
    this.redirectTo = options?.redirectTo;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function resolveBillingProviderLabel(
  foundation?: WorkspaceBillingFoundation | null
): string {
  const provider = String(
    foundation?.billing_provider_label ||
      foundation?.active_billing_provider ||
      foundation?.billing_provider ||
      ""
  )
    .trim()
    .toLowerCase();

  if (provider === "paddle") return "Paddle";
  if (provider === "stripe") return "Stripe";
  if (provider === "manual" || provider === "manual billing") return "Manual Billing";
  if (provider === "none" || !provider) return "Unconfigured";
  return foundation?.billing_provider_label || provider;
}

export function isSandboxBillingFoundation(
  foundation?: WorkspaceBillingFoundation | null
): boolean {
  return isSandboxPlanCode(
    foundation?.effective_plan_code ?? foundation?.plan_code ?? null
  );
}

export function getApiErrorCode(error: unknown): string | null {
  if (!isApiError(error)) return null;
  return error.payload?.code ?? null;
}

function getAuthHeaders(headers?: HeadersInit) {
  const merged = new Headers(headers || {});
  const token = getStoredAccessToken();

  // ✅ FORCE TOKEN PRESENCE CHECK
  if (token) {
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

        if (Array.isArray(detail)) {
          const first = detail[0];

          if (
            first &&
            typeof first === "object" &&
            "msg" in first
          ) {
            return {
              message: String((first as any).msg),
              detail: String((first as any).msg),
            };
          }

          return {
            message: "Validation failed",
            detail: "Validation failed",
          };
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

function getApiBaseUrl() {
  return (
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://trading-truth-layer.onrender.com"
  );
}

export async function getBrokerConnections(
  workspaceId: number
): Promise<BrokerConnection[]> {
  return apiFetch<BrokerConnection[]>(
    withDevUser(
      `/workspaces/${workspaceId}/broker-connections`
    ),
    {
      cache: "no-store",
    }
  );
}

export async function getBrokerAdapters(
  workspaceId: number
): Promise<BrokerAdapter[]> {
  return apiFetch(
    `/workspaces/${workspaceId}/broker-adapters`
  );
}

export async function createBrokerConnection(
  workspaceId: number,
  payload: {
    provider: string;
    connection_name: string;
  }
) {
  return apiFetch(
    `/workspaces/${workspaceId}/broker-connections`,
    {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
}

export async function verifyBrokerConnection(
  workspaceId: number,
  payload: VerifyBrokerConnectionPayload
) {
  return apiFetch(
    `/api/workspaces/${workspaceId}/broker-connections/verify`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}

export async function getImportJobs(
  workspaceId: number
): Promise<ImportJob[]> {
  return apiFetch(
    `/workspaces/${workspaceId}/import-jobs`
  );
}

export async function uploadImportJob(
  workspaceId: number,
  adapterProvider: string,
  file: File
) {
  const formData = new FormData();

  formData.append(
    "adapter_provider",
    adapterProvider
  );

  formData.append(
    "file",
    file
  );

  const token =
    getStoredAccessToken();

  const res = await fetch(
    `${getApiBaseUrl()}/api/workspaces/${workspaceId}/import-jobs`,
    {
      method: "POST",

      headers: token
        ? {
            Authorization:
              `Bearer ${token}`,
          }
        : undefined,

      body: formData,
    }
  );

  if (!res.ok) {
    throw new Error(
      "Upload failed"
    );
  }

  return res.json();
}

export async function getSyncJobs(
  workspaceId: number
): Promise<SyncJob[]> {
  return apiFetch<SyncJob[]>(
    `/workspaces/${workspaceId}/sync-jobs`
  );
}

export async function createSyncJob(
  workspaceId: number,
  payload: {
    connection_id: number;
    sync_type: string;
  }
) {
  return apiFetch(
    `/workspaces/${workspaceId}/sync-jobs`,
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(payload),
    }
  );
}

export async function executeSyncJob(
  workspaceId: number,
  jobId: number
) {
  const response = await apiFetch(
    `/workspaces/${workspaceId}/sync-jobs/${jobId}/execute`,
    {
      method: "POST",
    }
  );

  return response;
}

export async function createImportPreview(
  workspaceId: number,
  sourceType: string,
  file: File
) {
  const formData = new FormData();

  formData.append(
    "source_type",
    sourceType
  );

  formData.append(
    "file",
    file
  );

  return apiFetch(
    `/workspaces/${workspaceId}/imports/preview`,
    {
      method: "POST",
      body: formData,
    }
  );
}

export async function confirmImportPreview(
  workspaceId: number,
  previewSessionId: number
) {
  return apiFetch(
    `/workspaces/${workspaceId}/imports/preview/${previewSessionId}/confirm`,
    {
      method: "POST",
    }
  );
}

export async function getImportBatches(
  workspaceId: number
): Promise<ImportBatch[]> {
  return apiFetch<ImportBatch[]>(
    `/workspaces/${workspaceId}/import-batches`
  );
}

export async function getEvidenceRegistry(
  workspaceId: number
): Promise<EvidenceRecord[]> {

  return apiFetch(
    `/workspaces/${workspaceId}/evidence-registry`
  );
}

export async function getVerificationAnalytics(
  workspaceId: number
): Promise<VerificationAnalytics> {

  return apiFetch<VerificationAnalytics>(
    `/workspaces/${workspaceId}/verification-analytics`
  );

}

export async function getExternalReviews(
  workspaceId: number
): Promise<ExternalReviewResponse> {

  return apiFetch<ExternalReviewResponse>(
    `/external-reviews/workspace/${workspaceId}`
  );

}

export async function getExternalReviewAnalytics(
  workspaceId: number
): Promise<ExternalReviewAnalytics> {

  return apiFetch<ExternalReviewAnalytics>(
    `/external-reviews/workspace/${workspaceId}/analytics`
  );

}

export async function getEvidenceRecords(
  workspaceId: number
): Promise<EvidenceRecord[]> {
  return apiFetch<EvidenceRecord[]>(
    `/workspaces/${workspaceId}/evidence-records`
  );
}

export async function getAuditEvents(
  workspaceId: number
): Promise<AuditEvent[]> {

  return apiFetch<AuditEvent[]>(
    `/workspaces/${workspaceId}/audit-events`
  );

}

export async function getTrustScores(
  workspaceId: number
): Promise<TrustScoreResponse> {

  return apiFetch<TrustScoreResponse>(
    `/trust-scores/workspace/${workspaceId}`
  );
}

// ============================================================
// COMMERCIAL ACCESS GATEWAY
// ============================================================

type AuthorizationFailurePayload = {

    code?: string;

    page?: string;

    feature?: string;

    plan?: string;

    upgrade_required?: boolean;

    message?: string;

};

function handleAuthorizationFailure(

    payload: AuthorizationFailurePayload | undefined,

): never {

    if (!payload) {

        throw new Error(
            "Authorization failed."
        );

    }

    const code =
        payload.code ?? "";

    const commercialFailure =

        code === "page_locked" ||

        code === "feature_locked" ||

        code === "billing_required" ||

        code === "plan_limit_reached" ||

        payload.upgrade_required === true;

    if (!commercialFailure) {

        throw new Error(
            payload.message ??
            "Authorization failed."
        );

    }

    const workspaceId =
        getStoredActiveWorkspaceId();

    const target =

        workspaceId

            ? `/workspace/${workspaceId}/billing?upgrade=true`

            : "/";

    if (typeof window !== "undefined") {

        window.location.replace(
            target,
        );

    }

    throw new Error(
        payload.message ??
        "Upgrade required.",
    );

}

import type {

    EvidenceGraphNode,

    EvidenceGraphEdge,

    EvidenceGraphResponse,

} from "./evidence-graph/types";

export async function getEvidenceGraph(
    workspaceId:number,
    claimId?:number,
): Promise<EvidenceGraphResponse> {

  if (claimId) {

      return apiFetch<EvidenceGraphResponse>(
          `/evidence-graph/claim/${claimId}`
      );

  }

  return apiFetch<EvidenceGraphResponse>(
      `/evidence-graph/workspace/${workspaceId}`
  );

}

/* ===========================================================
   IIS API
=========================================================== */

export async function getWorkspaceInvestigation(
    workspaceId: number,
): Promise<InvestigationReport> {

    const raw = await apiFetch<any>(
        `/investigations/workspaces/${workspaceId}`,
    );

    return adaptInvestigationReport(raw);
}

function adaptInvestigationReport(
    raw: any,
): InvestigationReport {

    const graph = raw.graph ?? {};

    const nodes = graph.nodes ?? [];

    const relationships = graph.relationships ?? [];

    const findings = raw.findings ?? [];

    const recommendations = raw.recommendations ?? [];

    return {

        workspace_id: raw.workspace_id,

        scope: raw.scope,

        scope_id: raw.scope_id,

        status: raw.status,

        generated_at: raw.generated_at,

        metadata: raw.metadata ?? {},

        execution: raw.execution,

        evidence: raw.evidence,

        governance: raw.governance,

        broker: raw.broker,

        synchronization: raw.synchronization,

        review: raw.review,

        behavior: raw.behavior,

        verification: raw.verification,

        allocator: raw.allocator,

        summary: raw.summary,

        findings,

        nodes,

        relationships,

        timeline:
            raw.timeline ??
            [],

        recommendations,

        critical_path:
            raw.critical_path,

    };

}

export async function getClaimInvestigation(
    workspaceId: number,
    claimId: number,
): Promise<InvestigationReport> {

    return apiFetch<InvestigationReport>(
        `/investigations/workspaces/${workspaceId}/claims/${claimId}`,
    );

}

export async function getMemberInvestigation(
    workspaceId: number,
    memberId: number,
): Promise<InvestigationReport> {

    return apiFetch<InvestigationReport>(
        `/investigations/workspaces/${workspaceId}/members/${memberId}`,
    );

}

export async function getAccountInvestigation(
    workspaceId: number,
    accountId: number,
): Promise<InvestigationReport> {

    return apiFetch<InvestigationReport>(
        `/investigations/workspaces/${workspaceId}/accounts/${accountId}`,
    );

}

export async function getBrokerInvestigation(
    workspaceId: number,
    brokerId: number,
): Promise<InvestigationReport> {

    return apiFetch<InvestigationReport>(
        `/investigations/workspaces/${workspaceId}/brokers/${brokerId}`,
    );

}

export async function getSyncJobInvestigation(
    workspaceId: number,
    syncJobId: number,
): Promise<InvestigationReport> {

    return apiFetch<InvestigationReport>(
        `/investigations/workspaces/${workspaceId}/sync-jobs/${syncJobId}`,
    );

}

export async function getStrategyInvestigation(
    workspaceId: number,
    strategy: string,
): Promise<InvestigationReport> {

    return apiFetch<InvestigationReport>(
        `/investigations/workspaces/${workspaceId}/strategies/${encodeURIComponent(strategy)}`,
    );

}

export interface InvestigationOverview {

    score: number;

    total_findings: number;

    critical_findings: number;

    relationships: number;

    timeline_events: number;

    generated_at: string;

}

export async function getInvestigationOverview(
    workspaceId: number,
): Promise<InvestigationOverview> {

    return apiFetch<InvestigationOverview>(
        `/investigations/workspaces/${workspaceId}/overview`,
    );

}

export async function getInvestigationDomains(
    workspaceId: number,
): Promise<InvestigationDomains> {

    return apiFetch<InvestigationDomains>(
        `/investigations/workspaces/${workspaceId}/domains`,
    );

}

export async function getAllocatorInvestigation(
    workspaceId: number,
): Promise<InvestigationDomain> {

    return apiFetch<InvestigationDomain>(
        `/investigations/workspaces/${workspaceId}/allocator`,
    );

}

export async function getVerificationInvestigation(
    workspaceId: number,
): Promise<InvestigationDomain> {

    return apiFetch<InvestigationDomain>(
        `/investigations/workspaces/${workspaceId}/verification`,
    );

}

export async function getInstitutionalInvestigation(
    workspaceId: number,
) {

    const [

        report,

        overview,

        domains,

    ] = await Promise.all([

        getWorkspaceInvestigation(
            workspaceId,
        ),

        getInvestigationOverview(
            workspaceId,
        ),

        getInvestigationDomains(
            workspaceId,
        ),

    ]);

    return {

        report,

        overview,

        domains,

    };

}

export async function getCriticalPath(

    claimId:number,

){

    return apiFetch(

        `/evidence-graph/claim/${claimId}/critical-path`

    );

}

export async function getRiskGraph(

    claimId:number,

){

    return apiFetch(

        `/evidence-graph/claim/${claimId}/risk`

    );

}

export async function getFullGraph(

    claimId:number,

){

    return apiFetch(

        `/evidence-graph/claim/${claimId}/full`

    );

}

export async function
getLeaderboardAnalytics(
  workspaceId: number
): Promise<LeaderboardAnalytics> {

  return apiFetch(
    `/workspace/${workspaceId}/leaderboard-analytics`
  );
}

export async function acknowledgeAlert(
  alertId: number
) {
  return apiFetch(
    `/api/integrity-alerts/${alertId}/acknowledge`,
    {
      method: "POST",
    }
  );
}

export async function investigateAlert(
  alertId: number
) {
  return apiFetch(
    `/api/integrity-alerts/${alertId}/investigate`,
    {
      method: "POST",
    }
  );
}

export async function resolveAlert(
  alertId: number
) {
  return apiFetch(
    `/api/integrity-alerts/${alertId}/resolve`,
    {
      method: "POST",
    }
  );
}

export const getInstitutionalDashboard =
  async (
    workspaceId: number
  ): Promise<InstitutionalDashboardResponse> => {

    return apiFetch<
      InstitutionalDashboardResponse
    >(
      withDevUser(
        `/workspaces/${workspaceId}/dashboard`
      ),
      {
        cache: "no-store",
      }
    );
  };

export type DashboardSummary = {
  trade_count: number;

  member_count: number;

  claim_count: number;

  draft_claims: number;

  verified_claims: number;

  published_claims: number;

  locked_claims: number;

  active_alerts: number;
};

export type IntegrityDashboardResponse = {
  integrity_score: number;

  claims_scanned: number;

  total_alerts: number;

  open_findings: number;

  resolved_findings: number;

  severity: {
    warning: number;
    high: number;
    critical: number;
    fatal: number;
  };

  scanner_status: Record<
    string,
    {
      status: string;
      findings: number;
    }
  >;

  alert_distribution: Record<
    string,
    number
  >;

  recent_findings: {
    id: number;
    severity: string;
    type: string;
    status: string;
    message: string;
    created_at: string;
  }[];
};

export type IntegrityDashboard = {
  integrity_score: number;

  claims_scanned: number;

  total_alerts: number;

  healthy: boolean;

  severity: {
    warning: number;
    high: number;
    critical: number;
    fatal: number;
  };
};

export type IntegrityAlertFeedItem = {
  id: number;

  severity: string;

  alert_type: string;

  status: string;

  message: string;

  created_at: string | null;

  acknowledged_at: string | null;

  resolved_at: string | null;

  acknowledged_by: string | null;

  resolved_by: string | null;
};

export async function getIntegrityDashboard(
  workspaceId: number
): Promise<IntegrityDashboardResponse> {

  return apiFetch(
    `/integrity/dashboard/${workspaceId}`
  );

}

export type DashboardExecutive = {
  workspace: {
    members: number;
    trades: number;
    claims: number;
  };

  integrity: {
    alerts: number;
  };
};

export async function getDashboardExecutive(
  workspaceId: number
): Promise<DashboardExecutive> {

  return apiFetch(
    `/dashboard-executive/${workspaceId}`
  );

}

export type IntegrityScanHistoryItem = {
  id: number;

  status: string;

  claims_scanned: number;

  alerts_found: number;

  started_at: string;

  completed_at: string;
};

export async function getIntegrityScanHistory(
  workspaceId: number
): Promise<
  IntegrityScanHistoryItem[]
> {
  return apiFetch(
    `/integrity/history/${workspaceId}`
  );
}

export interface EvidenceAnalyticsResponse {
  overview: {
    records: number;
    coverage: number;
    reliability: number;
    protection: number;
    quality_score: number;
    quality_band: string;
  };

  verification: {
    broker_verified: number;
    verified: number;
    self_reported: number;
  };

  tiers: {
    tier_1: number;
    tier_2: number;
    tier_3: number;
  };

  protection: {
    fingerprinted: number;
    hash_protected: number;
    unprotected: number;
  };

  feed: {
    trade_id: number;
    symbol: string;
    verification_state: string;
    trust_tier: string;
    integrity_type: string;
  }[];

  exceptions: {
    trade_id: number;
    symbol: string;
    issues: string[];
  }[];

  quality: {

    verification_quality: number;

    protection_quality: number;

    completeness_quality: number;

    import_quality: number;

    score: number;

    band: string;
  };
}

export interface DueDiligenceResponse {

  overview: {
    claims: number;
    published_claims: number;
    locked_claims: number;
    evidence_records: number;
  };

  trust: {
    trust_score: number;
    network_score: number;
    trust_band: string;
  };

  verification: {
    coverage: number;
    verified_claims: number;
    status: string;
  };

  scanner_health: {
    health_score: number;
    compromised_claims: number;
    open_findings: number;
    resolved_findings: number;
  }

  evidence: {
    quality_score: number;
    quality_band: string;
    coverage: number;
  };

  governance: {
    compliance: number;
  };

  risk: {
    risk_score: number;
    profit_factor: number;
    win_rate: number;
    max_drawdown: number;
  };

  assessment: {
    grade: string;
    status: string;
    confidence: number;
    recommendation: string;
  };
}

export async function getDueDiligence(
  workspaceId: number
): Promise<DueDiligenceResponse> {

  return apiFetch(
    `/workspace/${workspaceId}/due-diligence`
  );
}

export async function getDueDiligenceReport(
  workspaceId: number
) {
  return apiFetch(
    `/reports/workspace/${workspaceId}/due-diligence`
  );
}

export async function getVerificationReport(
  workspaceId: number
) {
  return apiFetch(
    `/reports/workspace/${workspaceId}/verification`
  );
}

export async function getAuditReport(
  workspaceId: number
) {
  return apiFetch(
    `/reports/workspace/${workspaceId}/audit`
  );
}

export async function getAllocatorReport(
  workspaceId: number
) {
  return apiFetch(
    `/reports/workspace/${workspaceId}/allocator`
  );
}

export async function downloadInstitutionalInvestigationReport(
    workspaceId: number,
): Promise<void> {

    return apiDownload(
        `/reports/workspace/${workspaceId}/investigation/download`,
        `institutional_investigation_report_${workspaceId}.pdf`,
    );

}

export async function downloadExecutiveReport(
    workspaceId: number,
): Promise<void> {

    return apiDownload(

        `/reports/workspace/${workspaceId}/executive/download`,

        `executive_report_${workspaceId}.pdf`,

    );

}

export async function getEvidenceAnalytics(
  workspaceId: number
): Promise<EvidenceAnalyticsResponse> {

  return apiFetch(
    `/evidence-analytics/${workspaceId}`
  );
}

export async function getDashboardSummary(
  workspaceId: number
): Promise<DashboardSummary> {

  return apiFetch(
    `/dashboard-summary/${workspaceId}`
  );

}

export async function getWorkspaceSnapshot(
    workspaceId: number
) {

    return apiFetch(
        `/workspaces/${workspaceId}/snapshot`
    );

}

export async function getIntegrityAlertFeed(
  workspaceId: number
): Promise<IntegrityAlertFeedItem[]> {

  return apiFetch(
    `/integrity-alert-feed/${workspaceId}`
  );

}

export async function runIntegrityScan(
  workspaceId: number
) {

  return apiFetch(
    `/integrity/scan/${workspaceId}`,
    {
      method: "POST",
    }
  );

}

export const getStrategyPerformance = async (
  workspaceId: number,
  strategy?: string
) => {
  const params = new URLSearchParams()

  if (strategy) params.append("strategy", strategy)

  return apiFetch<any>(
    withDevUser(
      `/workspaces/${workspaceId}/strategy-performance${
        params.toString() ? `?${params.toString()}` : ""
      }`
    ),
    { cache: "no-store" }
  )
}

/* ===========================================================
   BILLING API
=========================================================== */

export async function getWorkspaceBillingFoundation(
    workspaceId: number,
): Promise<WorkspaceBillingFoundation> {

    return ensureWorkspaceBillingFoundation(
        await apiFetch<WorkspaceBillingFoundation>(
            `/billing/foundation/${workspaceId}`
        )
    );

}

export async function getWorkspaceUsage(
    workspaceId: number,
): Promise<WorkspaceUsageSummary> {

    return ensureWorkspaceUsageSummary(
        await apiFetch<WorkspaceUsageSummary>(
            `/workspaces/${workspaceId}/usage`
        )
    );

}

export async function getWorkspaceGovernance(
    workspaceId: number,
): Promise<WorkspaceGovernance> {

    return apiFetch<WorkspaceGovernance>(
        `/workspaces/${workspaceId}/governance`
    );

}

export async function getWorkspaceSettings(
    workspaceId: number,
): Promise<WorkspaceSettings> {

    return ensureWorkspaceSettings(
        await apiFetch<WorkspaceSettings>(
            `/workspaces/${workspaceId}/settings`
        )
    );

}

export async function getBillingDiagnostics(
    workspaceId: number,
): Promise<BillingDiagnostics> {

    return apiFetch<BillingDiagnostics>(
        `/billing/workspaces/${workspaceId}/diagnostics`
    );

}

export async function createBillingCheckout(
    workspaceId: number,
    payload: {
        plan_code: string;
        billing_cycle: "monthly" | "annual";
    },
): Promise<BillingCheckoutResponse> {

    return apiFetch<BillingCheckoutResponse>(
        `/billing/workspaces/${workspaceId}/checkout`,
        {
            method: "POST",
            body: JSON.stringify(payload),
        }
    );

}

export async function openBillingPortal(
    workspaceId: number,
): Promise<BillingPortalResponse> {

    return apiFetch<BillingPortalResponse>(
        `/billing/workspaces/${workspaceId}/portal`
    );

}

export async function downloadLatestInvoice(
    workspaceId: number,
): Promise<BillingInvoiceResponse> {

    return apiFetch<BillingInvoiceResponse>(
        `/billing/workspaces/${workspaceId}/invoice/latest`
    );

}


function withApiPrefix(path: string) {
    // auth routes should NOT be prefixed
    if (path.startsWith("/auth")) return path;

    // everything else MUST go through /api
    return path.startsWith("/api") ? path : `/api${path}`;
  }

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = getAuthHeaders(options?.headers);

  const baseUrl = getApiBaseUrl();
  const finalPath = withApiPrefix(path);

  const requestKey =
    `${options?.method || "GET"}:${finalPath}`;

  if (
    !options?.method ||
    options.method === "GET"
  ) {
    const existing =
      inflightRequests.get(requestKey);

    if (existing) {
      return existing as Promise<T>;
    }
  }

  if (
    process.env.NODE_ENV ===
    "development"
  ) {
    console.log(
      "API CALL:",
      `${baseUrl}${finalPath}`
    );
  }

  if (!(options?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }


  const requestPromise = (async () => {

    const res = await fetch(`${baseUrl}${finalPath}`, {
      ...options,
      headers,
    });

    if (!res.ok) {

      if (res.status === 401) {

          clearStoredAccessToken();

          clearStoredActiveWorkspaceId();

      }

      const rawText = await res.text();
      const payload = parseApiErrorPayload(rawText);

      const message =
          payload?.message ||
          payload?.detail ||
          rawText ||
          `API request failed with status ${res.status}`;

      if (

          payload?.code === "page_locked" ||

          payload?.code === "feature_locked" ||

          payload?.code === "billing_required" ||

          payload?.code === "plan_limit_reached" ||

          payload?.code === "PLAN_LIMIT_REACHED" ||

          payload?.upgrade_required === true

      ) {

          handleAuthorizationFailure(
              payload,
          );

      }

      throw new ApiError(

          message,

          res.status,

          payload,

          rawText,

      );
    }

    const text = await res.text();

      try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError(
      "Invalid JSON response from server",
      res.status,
      null,
      text
    );
  }

})();

if (
  !options?.method ||
  options.method === "GET"
) {
  inflightRequests.set(
    requestKey,
    requestPromise
  );

  requestPromise.finally(() => {
    inflightRequests.delete(
      requestKey
    );
  });
}

return requestPromise;
}

export async function apiDownload(path: string, filename: string): Promise<void> {
  const headers = getAuthHeaders();
  const baseUrl = getApiBaseUrl();

  const finalPath = path.startsWith("/api") ? path : `/api${path}`;

  const res = await fetch(`${baseUrl}${finalPath}`, {
    method: "GET",
    headers,
  });

  if (!res.ok) {

      if (res.status === 401) {

          clearStoredAccessToken();

          clearStoredActiveWorkspaceId();

      }

      const rawText = await res.text();

      const payload = parseApiErrorPayload(rawText);

      if (

          payload?.code === "page_locked" ||

          payload?.code === "feature_locked" ||

          payload?.code === "billing_required" ||

          payload?.code === "plan_limit_reached" ||

          payload?.code === "PLAN_LIMIT_REACHED" ||

          payload?.upgrade_required === true

      ) {

          handleAuthorizationFailure(payload);

      }

      throw new ApiError(

          payload?.message || "Download failed",

          res.status,

          payload,

          rawText,

      );

  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();

  window.URL.revokeObjectURL(url);
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

function isSandboxPlanCode(value?: string | null): boolean {
  return String(value ?? "").toLowerCase().trim() === "sandbox";
}

function ensurePlanBilling(
  row?: Partial<PlanBilling> | null,
  planCode?: string | null
): PlanBilling {
  const sandbox = isSandboxPlanCode(planCode);

  return {
    monthly_price_usd:
      typeof row?.monthly_price_usd === "number"
        ? row.monthly_price_usd
        : row?.monthly_price_usd ?? (sandbox ? 0 : null),
    annual_price_usd:
      typeof row?.annual_price_usd === "number"
        ? row.annual_price_usd
        : row?.annual_price_usd ?? (sandbox ? 0 : null),
    currency: row?.currency ?? "USD",
    billing_interval: row?.billing_interval ?? "monthly",
    stripe_price_lookup_key_monthly: sandbox
      ? null
      : row?.stripe_price_lookup_key_monthly ?? null,
    stripe_price_lookup_key_annual: sandbox
      ? null
      : row?.stripe_price_lookup_key_annual ?? null,
  };
}

function ensureClaimLineage(row?: {
  parent_claim_id?: number | null;
  root_claim_id?: number | null;
  version_number?: number | null;
} | null):
  | {
      parent_claim_id?: number;
      root_claim_id?: number;
      version_number?: number;
    }
  | undefined {
  if (!row) return undefined;

  return {
    parent_claim_id:
      typeof row.parent_claim_id === "number" ? row.parent_claim_id : undefined,
    root_claim_id:
      typeof row.root_claim_id === "number" ? row.root_claim_id : undefined,
    version_number:
      typeof row.version_number === "number" ? row.version_number : undefined,
  };
}

function ensureVerificationCertificate(
    row: any,
): VerificationCertificate {

    return {

        payload_version:
            row?.payload_version ?? "v8",

        identity: {

            claim_id:
                Number(
                    row?.identity?.claim_id ??
                    row?.claim_id ??
                    0
                ),

            workspace_id:
                Number(
                    row?.identity?.workspace_id ??
                    row?.workspace_id ??
                    0
                ),

            claim_hash:
                row?.identity?.claim_hash ??
                row?.claim_hash ??
                "",

            verify_path:
                row?.identity?.verify_path ??
                row?.verify_path ??
                "",

            public_view_path:
                row?.identity?.public_view_path ??
                row?.public_view_path ??
                "",

            exposure_level:
                row?.identity?.exposure_level ??
                "public",

        },

        issuer:
            ensureClaimIssuer(row?.issuer)!,

        verification: {

            status:
                row?.verification?.status ??
                row?.status ??
                "",

            visibility:
                row?.verification?.visibility ??
                row?.visibility ??
                "",

            canonical:
                Boolean(
                    row?.verification?.canonical ?? true
                ),

            portable:
                Boolean(
                    row?.verification?.portable ?? true
                ),

            api_addressable:
                Boolean(
                    row?.verification?.api_addressable ?? true
                ),

        },

        lifecycle: {

            verified_at:
                row?.lifecycle?.verified_at ??
                row?.verified_at,

            published_at:
                row?.lifecycle?.published_at ??
                row?.published_at,

            locked_at:
                row?.lifecycle?.locked_at ??
                row?.locked_at,

        },

        lineage:
            ensureClaimLineage(row?.lineage) ?? {},

        integrity: {

            status:
                row?.integrity?.status ??
                row?.integrity_status ??
                "",

            valid:
                Boolean(
                    row?.integrity?.valid ??
                    row?.integrity_valid ??
                    true
                ),

            stored_trade_set_hash:
                row?.integrity?.stored_trade_set_hash,

            recomputed_trade_set_hash:
                row?.integrity?.recomputed_trade_set_hash,

        },

        scope: {

            period_start:
                row?.scope?.period_start,

            period_end:
                row?.scope?.period_end,

            included_trade_count:
                Number(
                    row?.scope?.included_trade_count ??
                    row?.trade_count ??
                    0
                ),

            excluded_trade_count:
                Number(
                    row?.scope?.excluded_trade_count ??
                    0
                ),

            included_member_ids:
                row?.scope?.included_member_ids ??
                row?.scope?.included_members ??
                [],

            included_symbols:
                row?.scope?.included_symbols ??
                [],

        },

        performance: {

            trade_count:
                Number(
                    row?.performance?.trade_count ??
                    row?.trade_count ??
                    0
                ),

            net_pnl:
                Number(
                    row?.performance?.net_pnl ??
                    row?.net_pnl ??
                    0
                ),

            profit_factor:
                Number(
                    row?.performance?.profit_factor ??
                    row?.profit_factor ??
                    0
                ),

            win_rate:
                Number(
                    row?.performance?.win_rate ??
                    row?.win_rate ??
                    0
                ),

        },

        trust: {

            score:
                Number(
                    row?.trust?.score ??
                    row?.trust_score ??
                    0
                ),

            band:
                row?.trust?.band ??
                row?.trust_band ??
                "",

            tier:
                row?.trust?.tier ??
                "tier_3",

        },

        evidence: {

            primary_tier:
                row?.evidence?.primary_tier ??
                "tier_3",

            primary_source:
                row?.evidence?.primary_source ??
                "Unknown",

            trade_set_hash:
                row?.evidence?.trade_set_hash ??
                row?.trade_set_hash,

        },

        leaderboard:
            Array.isArray(row?.leaderboard)
                ? row.leaderboard
                : [],

        profile:
            row?.profile
                ? ensurePublicTrustProfile(row.profile)
                : null,

        equity_curve:
            row?.equity_curve,

    };

}

function ensureClaimIssuer(
  row?: Partial<ClaimIssuer> | null
): ClaimIssuer | undefined {
  if (!row) return undefined;

  return {
    id: Number(row.id ?? 0),
    name: String(row.name ?? ""),
    type: String(row.type ?? "workspace"),
    network: String(row.network ?? "internal"),
  };
}

function ensureWorkspacePlanDetail(
  row?: Partial<WorkspacePlanDetail> | null
): WorkspacePlanDetail | undefined {
  if (!row) return undefined;

  const code = String(row.code ?? "");

  return {
    code,
    name: String(row.name ?? ""),
    description: String(row.description ?? ""),
    recommended_for: Array.isArray(row.recommended_for) ? row.recommended_for.map(String) : [],
    billing: ensurePlanBilling(row.billing, code),
  };
}

function ensurePlanCatalogItem(row: any): any {

    return {

        code: String(row.code ?? ""),

        name: String(row.name ?? ""),

        description: String(row.description ?? ""),

        recommended_for: Array.isArray(row.recommended_for)
            ? row.recommended_for.map(String)
            : [],

        pricing: {

            monthly:
                Number(
                    row.pricing?.monthly ??
                    row.monthly_price_usd ??
                    0
                ),

            annual:
                Number(
                    row.pricing?.annual ??
                    row.annual_price_usd ??
                    0
                ),

        },

        claims: Number(row.claims ?? 0),

        trades: Number(row.trades ?? 0),

        members: Number(row.members ?? 0),

        storage_mb: Number(row.storage_mb ?? 0),

        infrastructure: Array.isArray(row.infrastructure)
            ? row.infrastructure.map(String)
            : [],

        commercial_services: Array.isArray(row.commercial_services)
            ? row.commercial_services.map(String)
            : [],

        capacity_summary:
            row.capacity_summary ?? {},

        is_public:
            Boolean(row.is_public),

    };

}

function ensureWorkspaceSettings(row: WorkspaceSettings): WorkspaceSettings {
  return {
    ...row,
    preferences: {

        timezone:
            row.preferences?.timezone ??
            "UTC",

        language:
            row.preferences?.language ??
            "English",

        currency:
            row.preferences?.currency ??
            "USD",

        date_format:
            row.preferences?.date_format ??
            "YYYY-MM-DD",

        auto_refresh:
            row.preferences?.auto_refresh ??
            true,

        auto_save:
            row.preferences?.auto_save ??
            true,

    },
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
    root_claim_id:
      typeof row.root_claim_id === "number"
        ? row.root_claim_id
        : null,

    public_view_path:
      row.public_view_path ??
      `/claim/${row.claim_schema_id}/public`,

    verify_path:
      row.verify_path ??
      `/verify/${row.claim_hash}`,
      
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
    issuer: ensureClaimIssuer(row.issuer),
    profile: row?.profile ? ensurePublicTrustProfile(row.profile) : null,
    lineage: ensureClaimLineage(row.lineage),
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
      members: Number(row?.usage?.members ?? 0),

      trades: Number(row?.usage?.trades ?? 0),

      active_trades: Number(row?.usage?.active_trades ?? 0),

      claims: Number(row?.usage?.claims ?? 0),

      storage_mb: Number(row?.usage?.storage_mb ?? 0),
    },

    limits: {
      claims: Number(row?.limits?.claims ?? 0),

      trades: Number(row?.limits?.trades ?? 0),

      members: Number(row?.limits?.members ?? 0),

      storage_mb: Number(row?.limits?.storage_mb ?? 0),
    },

    // ✅ compatibility metrics layer
    metrics: {
      used: Number(
        row?.metrics?.used ??
        row?.usage?.trades ??
        0
      ),

      consumed: Number(
        row?.metrics?.consumed ??
        row?.usage?.trades ??
        0
      ),

      ledger_count: Number(
        row?.metrics?.ledger_count ??
        row?.usage?.active_trades ??
        0
      ),

      limit: Math.max(
        1,
        Number(
          row?.metrics?.limit ??
          row?.limits?.trades ??
          200
        )
      ),

      utilization: Number(
        row?.metrics?.utilization ??
        0
      ),
    },
     stripe_ready: {
      has_customer_id: Boolean(row?.stripe_ready?.has_customer_id),
      has_subscription_id: Boolean(row?.stripe_ready?.has_subscription_id),
      integration_status: row?.stripe_ready?.integration_status || "fallback_only",
      billing_enabled: Boolean(row?.stripe_ready?.billing_enabled),
      secret_key_configured: Boolean(row?.stripe_ready?.secret_key_configured),
      package_installed: Boolean(row?.stripe_ready?.package_installed),
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
    active_billing_provider: row?.active_billing_provider ?? row?.billing_provider ?? null,
    billing_provider_label: row?.billing_provider_label ?? null,
    provider_customer_id: row?.provider_customer_id ?? null,
    provider_subscription_id: row?.provider_subscription_id ?? null,
    provider_environment: row?.provider_environment ?? null,
    manual_billing_visible: Boolean(row?.manual_billing_visible),
    stripe_customer_id: row?.stripe_customer_id ?? null,
    stripe_subscription_id: row?.stripe_subscription_id ?? null,
    paddle_customer_id: row?.paddle_customer_id ?? null,
    paddle_subscription_id: row?.paddle_subscription_id ?? null,
    paddle_transaction_id: row?.paddle_transaction_id ?? null,
    paddle_price_id: row?.paddle_price_id ?? null,
    prices: {
      monthly_price_usd:
        row?.prices?.monthly_price_usd ??
        (isSandboxPlanCode(row?.plan_code) ? 0 : null),
      annual_price_usd:
        row?.prices?.annual_price_usd ??
        (isSandboxPlanCode(row?.plan_code) ? 0 : null),
    },
    stripe_ready: {
      has_customer_id: Boolean(row?.stripe_ready?.has_customer_id),
      has_subscription_id: Boolean(row?.stripe_ready?.has_subscription_id),
      integration_status: row?.stripe_ready?.integration_status || "fallback_only",
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
          environment: row.paddle_ready.environment ?? null,
        }
      : undefined,
    manual_billing: row?.manual_billing
      ? {
          enabled: Boolean(row.manual_billing.enabled),
          ready: Boolean(row.manual_billing.ready),
          visible: Boolean(row.manual_billing.visible),
          payment_method: row.manual_billing.payment_method ?? null,
        }
      : undefined,
    manual_payment_details:
      row?.manual_billing_visible || row?.manual_billing?.visible
        ? ensureManualPaymentDetails(row?.manual_payment_details)
        : undefined,

    public_plans: (() => {

      const rawPlans = (row as any)?.public_plans;

      if (!rawPlans) {
        return {};
      }

      // Backend returned an object (current implementation)
      if (
        typeof rawPlans === "object" &&
        !Array.isArray(rawPlans)
      ) {

        return Object.fromEntries(

          Object.entries(rawPlans).map(

            ([code, plan]: [string, any]) => [

              code,

              ensurePlanCatalogItem(plan),

            ]

          )

        );

      }

      // Backward compatibility if an array is ever returned
      if (Array.isArray(rawPlans)) {

        return Object.fromEntries(

          rawPlans.map((plan: any) => [

            plan.code,

            ensurePlanCatalogItem(plan),

          ])

        );

      }

      return {};

    })(),

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
    tags: row.tags ?? ((row as any).strategy_tag ? [(row as any).strategy_tag] : []),
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

function ensureClaimDispute(row: Partial<ClaimDispute>): ClaimDispute {
  return {
    id: Number(row.id ?? 0),
    claim_schema_id: Number(row.claim_schema_id ?? 0),
    workspace_id: Number(row.workspace_id ?? 0),

    status: (row.status ?? "open") as ClaimDisputeStatus,
    challenge_type: String(row.challenge_type ?? "general_review"),
    reason_code: String(row.reason_code ?? "other"),

    summary: String(row.summary ?? ""),
    evidence_note: row.evidence_note ?? null,

    reporter_user_id: Number(row.reporter_user_id ?? 0),
    reviewer_user_id:
      typeof row.reviewer_user_id === "number"
        ? row.reviewer_user_id
        : row.reviewer_user_id ?? null,

    resolution_note: row.resolution_note ?? null,

    opened_at: String(row.opened_at ?? ""),
    updated_at: String(row.updated_at ?? ""),
    resolved_at: row.resolved_at ?? null,
  };
}

function ensurePublicTrustProfile(
  row?: Partial<PublicTrustProfile> | null
): PublicTrustProfile {
  return {
    profile_id: String(row?.profile_id ?? ""),
    workspace_id: Number(row?.workspace_id ?? 0),
    name: String(row?.name ?? ""),
    type: String(row?.type ?? "workspace"),
    network: String(row?.network ?? "internal"),
    claims_count: Number(row?.claims_count ?? 0),
    locked_claims_count: Number(row?.locked_claims_count ?? 0),
    contested_claims_count: Number(row?.contested_claims_count ?? 0),
    average_trust_score: Number(row?.average_trust_score ?? 0),
    average_network_score: Number(row?.average_network_score ?? 0),
    total_net_pnl: Number(row?.total_net_pnl ?? 0),
    trust_profile_band: String(row?.trust_profile_band ?? "fragile"),
  };
}

function ensurePublicProfileResponse(row: PublicProfileResponse): PublicProfileResponse {
  return {
    profile: ensurePublicTrustProfile(row?.profile),
    claims: Array.isArray(row?.claims) ? row.claims.map(ensurePublicClaim) : [],
    claims_count: Number(row?.claims_count ?? 0),
  };
}

function ensureIntegrationSourceMetadata(
  row?: Partial<IntegrationSourceMetadata> | null
): IntegrationSourceMetadata {
  return {
    provider: (row?.provider ?? "unknown") as IntegrationProviderType,
    provider_label: row?.provider_label ?? null,
    source_system: row?.source_system ?? null,
    source_account_id: row?.source_account_id ?? null,
    source_workspace_ref: row?.source_workspace_ref ?? null,
    sync_mode: (row?.sync_mode ?? "unknown") as
      | "manual"
      | "scheduled"
      | "webhook"
      | "api"
      | "unknown",
    last_synced_at: row?.last_synced_at ?? null,
  };
}

function ensurePlatformReadiness(row?: Partial<PlatformReadiness> | null): PlatformReadiness | undefined {
  if (!row) return undefined;

  return {
    workspace_id:
      typeof row.workspace_id === "number" ? row.workspace_id : row.workspace_id ?? null,
    capabilities: {
      public_verification_enabled: Boolean(row.capabilities?.public_verification_enabled),
      public_distribution_enabled: Boolean(row.capabilities?.public_distribution_enabled),
      external_verification_enabled: Boolean(row.capabilities?.external_verification_enabled),
      api_access_enabled: Boolean(row.capabilities?.api_access_enabled),
      broker_import_enabled: Boolean(row.capabilities?.broker_import_enabled),
      webhook_ingestion_enabled: Boolean(row.capabilities?.webhook_ingestion_enabled),
    },
    integration_sources: Array.isArray(row.integration_sources)
      ? row.integration_sources.map((item) => ensureIntegrationSourceMetadata(item))
      : [],
    verification_exposure_level:
      (row.verification_exposure_level ?? "internal_only") as VerificationExposureLevel,
    recommended_next_step: row.recommended_next_step ?? null,
  };
}

function ensureExternalVerificationRecord(
  row: ExternalVerificationRecord | PublicVerifyResult
): ExternalVerificationRecord {
  const scope = "scope" in row && row.scope
    ? row.scope
    : {
        period_start: "—",
        period_end: "—",
        included_members: [],
        included_symbols: [],
        methodology_notes: "",
        visibility: "—",
      };

  const lifecycle = "lifecycle" in row && row.lifecycle
    ? row.lifecycle
    : {
        status: (row as any)?.verification_status ?? "unknown",
        verified_at: null,
        published_at: null,
        locked_at: null,
      };
  const issuer = "issuer" in row ? ensureClaimIssuer((row as any).issuer) : undefined;

  return {
    claim_schema_id: Number((row as any)?.claim_schema_id ?? 0),
    workspace_id:
      typeof (row as any)?.workspace_id === "number"
        ? (row as any).workspace_id
        : (row as any)?.workspace_id ?? null,
    name: String((row as any)?.name ?? issuer?.name ?? ""),
    identity: {
      claim_hash: String((row as any)?.claim_hash ?? ""),
      verify_path: String(
        (row as any)?.verify_path ??
          ((row as any)?.claim_hash ? `/verify/${(row as any).claim_hash}` : "")
      ),
      public_view_path:
        (row as any)?.public_view_path ??
        ((row as any)?.claim_schema_id
          ? `/claim/${(row as any).claim_schema_id}/public`
          : null),
      trade_set_hash: (row as any)?.trade_set_hash ?? null,
      verification_status: String((row as any)?.verification_status ?? "unknown"),
      integrity_status: (row as any)?.integrity_status ?? null,
      exposure_level:
        ((scope as any)?.visibility === "public"
          ? "public"
          : (scope as any)?.visibility === "unlisted"
            ? "unlisted"
            : "internal_only") as VerificationExposureLevel,
    },
    scope: {
      period_start: String(scope.period_start ?? "—"),
      period_end: String(scope.period_end ?? "—"),
      included_members: Array.isArray(scope.included_members) ? scope.included_members : [],
      included_symbols: Array.isArray(scope.included_symbols) ? scope.included_symbols : [],
      methodology_notes: String(scope.methodology_notes ?? ""),
      visibility: scope.visibility ?? "—",
    },
    lifecycle: {
      status: String(lifecycle.status ?? "unknown"),
      verified_at: lifecycle.verified_at ?? null,
      published_at: lifecycle.published_at ?? null,
      locked_at: lifecycle.locked_at ?? null,
    },
    metrics: {
      trade_count: Number((row as any)?.trade_count ?? 0),
      net_pnl: Number((row as any)?.net_pnl ?? 0),
      profit_factor: Number((row as any)?.profit_factor ?? 0),
      win_rate: Number((row as any)?.win_rate ?? 0),
    },
    lineage:
      "lineage" in row && row.lineage
        ? {
            parent_claim_id: row.lineage.parent_claim_id ?? null,
            root_claim_id: row.lineage.root_claim_id ?? null,
            version_number: row.lineage.version_number ?? null,
          }
        : undefined,
  };
}

function ensureExternalVerificationLookupResult(
  row: ExternalVerificationLookupResult | PublicVerifyResult
): ExternalVerificationLookupResult {
  if ("record" in row && row.record) {
    return {
      record: ensureExternalVerificationRecord(row.record),
      platform_readiness: ensurePlatformReadiness(row.platform_readiness),
    };
  }

  const publicRow = row as PublicVerifyResult;

  return {
    record: ensureExternalVerificationRecord(publicRow),
    platform_readiness: undefined,
  };
}

function normalizeVerifyPayload(
  row: VerifyPayloadV7 | VerifyClaimResult
): VerifyClaimResult {
  // Phase 7 payload detected
  if ((row as VerifyPayloadV7)?.payload_version) {
    const v7 = row as VerifyPayloadV7;

    return {
      claim_id: v7.claim_id,
      workspace_id: v7.workspace_id,
      name: v7.verification_record?.name || v7.name,
      status: v7.verification_record?.status || v7.status,
      visibility: v7.verification_record?.visibility || v7.visibility,
      claim_hash: v7.network_identity?.claim_hash || v7.claim_hash,
      stored_trade_set_hash: v7.integrity_record?.stored_trade_set_hash,
      recomputed_trade_set_hash: v7.integrity_record?.recomputed_trade_set_hash,
      integrity: v7.integrity_record?.status as any,
      version_number: v7.verification_record?.version_number,
      root_claim_id: v7.verification_record?.root_claim_id,
      parent_claim_id: v7.verification_record?.parent_claim_id,
      published_at: v7.lifecycle?.published_at,
      verified_at: v7.lifecycle?.verified_at,
      locked_at: v7.lifecycle?.locked_at,
      period_start: v7.scope?.period_start,
      period_end: v7.scope?.period_end,
      public_view_path: v7.network_identity?.public_view_path || v7.public_view_path,
      verify_path: v7.network_identity?.verify_path || v7.verify_path,
    };
  }

  // fallback (Phase 5)
  return row as VerifyClaimResult;
}

export const api = {
    register: async (payload: RegisterPayload): Promise<AuthResponse> => {
    clearStoredAccessToken();
    clearStoredActiveWorkspaceId();

    const result = await apiFetch<AuthResponse>(`/auth/register`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (result.access_token) {
      setStoredAccessToken(result.access_token);
    }

    const firstWorkspace = Array.isArray(result.workspaces) ? result.workspaces[0] : null;
    if (firstWorkspace?.workspace_id) {
      setStoredActiveWorkspaceId(firstWorkspace.workspace_id);
    }

    return result;
  },

    login: async (payload: LoginPayload): Promise<AuthResponse> => {
    clearStoredAccessToken();
    clearStoredActiveWorkspaceId();

    const result = await apiFetch<AuthResponse>(`/auth/login`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (result.access_token) {
      setStoredAccessToken(result.access_token);
    }

    const firstWorkspace = Array.isArray(result.workspaces) ? result.workspaces[0] : null;
    if (firstWorkspace?.workspace_id) {
      setStoredActiveWorkspaceId(firstWorkspace.workspace_id);
    }

    return result;
  },

  verifyEmail: async (token: string) => {
    return apiFetch<{
      status: string;
    }>(
      `/auth/verify-email?token=${encodeURIComponent(token)}`,
      {
        method: "GET",
      }
    );
  },

  forgotPassword: async (
    payload: ForgotPasswordPayload
  ) => {
    return apiFetch<{
      message: string;
    }>(
      `/auth/forgot-password`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  resetPassword: async (
    payload: ResetPasswordPayload
  ) => {
    return apiFetch<{
      status: string;
    }>(
      `/auth/reset-password`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  async resendVerification(
    payload: ResendVerificationPayload
  ) {
    return apiFetch<{
      message: string;
    }>(
      "/auth/resend-verification",
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  logout: () => {
    clearStoredAccessToken();
    clearStoredActiveWorkspaceId();
  },

  getInstitutionalDashboard: async (
    workspaceId: number
  ): Promise<InstitutionalDashboardResponse> => {

    return apiFetch<
      InstitutionalDashboardResponse
    >(
      withDevUser(
        `/workspaces/${workspaceId}/dashboard`
      ),
      {
        cache: "no-store",
      }
    );
  },

    /* ===========================================================
     V2 EVIDENCE REGISTRY
     =========================================================== */

  getV2EvidenceRegistry: async (
    workspaceId: number
  ): Promise<V2EvidenceRegistryResponse> => {
    return apiFetch<V2EvidenceRegistryResponse>(
      `/workspaces/${workspaceId}/evidence-registry/v2`,
      {
        cache: "no-store",
      }
    );
  },

  getV2EvidenceRegistryPage: async (
    workspaceId: number,
    page = 1,
    pageSize = 50,
    evidenceType?: string,
    evidenceTypes?: string[],
  ): Promise<V2EvidenceRegistryPage> => {
    const params = new URLSearchParams();

    params.set("page", String(page));
    params.set("page_size", String(pageSize));

    if (evidenceType) {
      params.set(
        "evidence_type",
        evidenceType,
      );
    }

    if (evidenceTypes?.length) {
      params.set(
        "evidence_types",
        evidenceTypes.join(","),
      );
    }

    return apiFetch<V2EvidenceRegistryPage>(
      `/workspaces/${workspaceId}/evidence-registry/v2?${params.toString()}`,
    );
  },

  getV2EvidencePackagesPage: async (
    workspaceId: number,
    page = 1,
    pageSize = 25,
  ): Promise<V2EvidencePackagePage> => {
    const params = new URLSearchParams();

    params.set(
      "page",
      String(page),
    );

    params.set(
      "page_size",
      String(pageSize),
    );

    return apiFetch<V2EvidencePackagePage>(
      `/workspaces/${workspaceId}/evidence-registry/v2/packages?${params.toString()}`,
      {
        cache: "no-store",
      },
    );
  },

  getV2EvidenceRegistrySummary: async (
    workspaceId: number
  ): Promise<V2EvidenceRegistrySummary> => {
    return apiFetch<V2EvidenceRegistrySummary>(
      `/workspaces/${workspaceId}/evidence-registry/v2/summary`,
      {
        cache: "no-store",
      }
    );
  },

  searchV2EvidenceRegistry: async (
    workspaceId: number,
    query: string
  ): Promise<V2EvidenceRegistrySearchResponse> => {
    return apiFetch<V2EvidenceRegistrySearchResponse>(
      `/workspaces/${workspaceId}/evidence-registry/v2/search?query=${encodeURIComponent(
        query
      )}`,
      {
        cache: "no-store",
      }
    );
  },

  getV2EvidenceRecord: async (
    workspaceId: number,
    canonicalEvidenceId: string
  ): Promise<V2EvidenceRegistryDetail> => {
    return apiFetch<V2EvidenceRegistryDetail>(
      `/workspaces/${workspaceId}/evidence-registry/v2/${encodeURIComponent(
        canonicalEvidenceId
      )}`,
      {
        cache: "no-store",
      }
    );
  },

  async getDashboardSummary(
    workspaceId: number
  ): Promise<DashboardSummary> {
    return apiFetch<DashboardSummary>(
      `/dashboard-summary/${workspaceId}`
    );
  },

  getWorkspaceSnapshot(
      workspaceId: number
  ): Promise<WorkspaceSnapshot> {

      return apiFetch<WorkspaceSnapshot>(
          `/workspaces/${workspaceId}/snapshot`
      );

  },

  getWorkspaceGovernanceSnapshot: async (
      workspaceId: number
  ): Promise<WorkspaceGovernanceSnapshot> => {

      return apiFetch<WorkspaceGovernanceSnapshot>(
          withDevUser(
              `/workspaces/${workspaceId}/governance`
          ),
          {
              cache: "no-store",
          }
      );

  },

  async getIntegrityDashboard(
    workspaceId: number
  ): Promise<
    IntegrityDashboardResponse
  > {
    return apiFetch(
      `/integrity/dashboard/${workspaceId}`
    );
  },

  async getIntegrityAlerts(
    workspaceId: number
  ): Promise<
    IntegrityAlertFeedItem[]
  > {
    return apiFetch(
      `/integrity-alert-feed/${workspaceId}`
    );
  },

  async getClaimTemplates(
    workspaceId: number
  ): Promise<ClaimTemplate[]> {
    return apiFetch(
      `/workspaces/${workspaceId}/claim-templates`
    );
  },

  async getClaimTemplate(
    templateId: number
  ): Promise<ClaimTemplate> {
    return apiFetch(
      `/claim-templates/${templateId}`
    );
  },

  async createClaimTemplate(
    payload: any
  ): Promise<ClaimTemplate> {
    return apiFetch(
      `/claim-templates`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  async updateClaimTemplate(
    templateId: number,
    payload: any
  ): Promise<ClaimTemplate> {
    return apiFetch(
      `/claim-templates/${templateId}`,
      {
        method: "PUT",
        body: JSON.stringify(payload),
      }
    );
  },

  async deleteClaimTemplate(
    templateId: number
  ): Promise<void> {
    return apiFetch(
      `/claim-templates/${templateId}`,
      {
        method: "DELETE",
      }
    );
  },

  async getClaimPresets(
    workspaceId: number
  ): Promise<any[]> {
    return apiFetch<any[]>(
      `/workspaces/${workspaceId}/claim-presets`
    );
  },

  getStrategyPerformance,

  getMe: async (): Promise<MeResponse> => {
    try {
      return await apiFetch<MeResponse>(withDevUser(`/auth/me`), {
        cache: "no-store",
      });
    } catch (error) {
      if (isApiError(error) && error.status === 401) {
        clearStoredAccessToken();
        clearStoredActiveWorkspaceId();
      }
      throw error;
    }
  },

  getMyWorkspaces: async (): Promise<AuthWorkspace[]> => {
    return apiFetch<AuthWorkspace[]>(withDevUser(`/workspaces`), {
      cache: "no-store",
    });
  },

  getWorkspaceTradeMetrics: async (
    workspaceId: number
  ): Promise<WorkspaceUsageSummary> => {

    const row = await apiFetch<WorkspaceUsageSummary>(
      withDevUser(`/workspaces/${workspaceId}/usage`),
      {
        cache: "no-store",
      }
    );

    return ensureWorkspaceUsageSummary(row);
  },

  getDashboard: async (workspaceId: number): Promise<DashboardResponse> => {
    return await apiFetch<DashboardResponse>(
      withDevUser(`/workspaces/${workspaceId}/dashboard`),
      { cache: "no-store" }
    );
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

  getWorkspaceUsage: async (
    workspaceId: number
  ): Promise<WorkspaceUsageSummary> => {
    const row = await apiFetch<WorkspaceUsageSummary>(
      withDevUser(`/workspaces/${workspaceId}/usage`),
      { cache: "no-store" }
    );

    return ensureWorkspaceUsageSummary(row);
  },

  getWorkspaceBillingFoundation: async (workspaceId: number) => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("ttl_access_token")
        : null;

    const response = await fetch(
      `${API_BASE_URL}/api/billing/workspaces/${workspaceId}/billing-foundation`,
      {
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {}),
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to load billing foundation");
    }

    return response.json();
  },

  createBillingCheckoutSession: async (
    workspaceId: number,
    payload: { plan_code: string; billing_cycle: string }
  ): Promise<BillingCheckoutResponse> => {
    const row = await apiFetch<any>(withDevUser(`/billing/workspaces/${workspaceId}/checkout`), {
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
    const row = await apiFetch<any>(withDevUser(`/billing/workspaces/${workspaceId}/portal`), {
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

  getWorkspacePlanSimulation,

  setWorkspacePlanSimulation,

  clearWorkspacePlanSimulation,

  async previewImportFile(
    workspaceId: number,
    file: File,
    sourceType: ImportSourceType
  ): Promise<ImportPreviewResponse> {

    const formData = new FormData();

    formData.append("file", file);
    formData.append("source_type", sourceType);

    return apiFetch<ImportPreviewResponse>(
      withDevUser(
        `/workspaces/${workspaceId}/imports/preview`
      ),
      {
        method: "POST",
        body: formData,
      }
    );
  },

  async confirmImportPreview(
    workspaceId: number,
    previewSessionId: number
  ): Promise<ConfirmImportPreviewResponse> {

    return apiFetch<ConfirmImportPreviewResponse>(
      withDevUser(
        `/workspaces/${workspaceId}/imports/preview/${previewSessionId}/confirm`
      ),
      {
        method: "POST",
      }
    );
  },

  async getTrades(
    workspaceId: number,
    params?: {
      tag?: string;
      strategy?: string
      symbol?: string;
      side?: string;
      limit?: number;
      offset?: number;
    }
  ) {
    const query = new URLSearchParams();

    if (params?.tag) query.append("tag", params.tag);
    if (params?.strategy)
        query.set("strategy", params.strategy)
    if (params?.symbol) query.append("symbol", params.symbol);
    if (params?.side) query.append("side", params.side);
    if (params?.limit) query.append("limit", String(params.limit));
    if (params?.offset) query.append("offset", String(params.offset));

    const qs = query.toString();

    return apiFetch<Trade[]>(
      withDevUser(
        `/workspaces/${workspaceId}/trades${qs ? `?${qs}` : ""}`
      ),
      { cache: "no-store" }
    );
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

  acceptWorkspaceInvite: async (
    token: string
  ): Promise<{
    message: string;
    workspace_id: number;
    role: string;
  }> => {
    const normalizedToken = String(token)
      .trim()
      .replace(/\s+/g, "_");

    console.log(
      "NORMALIZED INVITE TOKEN:",
      normalizedToken
    );

    return apiFetch(
      `/invites/${encodeURIComponent(normalizedToken)}/accept`,
      {
        method: "POST",
      }
    );
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

    createTrade: async (workspaceId: number, payload: any): Promise<Trade> => {
      return apiFetch<Trade>(
        withDevUser(`/workspaces/${workspaceId}/trades`),
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );
    },

  updateTrade: async (
    workspaceId: number,
    tradeId: number,
    payload: any
  ): Promise<Trade> => {
    return apiFetch<Trade>(
      withDevUser(`/workspaces/${workspaceId}/trades/${tradeId}`),
      {
        method: "PATCH",   // ✅ CORRECT
        body: JSON.stringify(payload),
      }
    );
  },

  deleteTrade: async (
    workspaceId: number,
    tradeId: number
  ): Promise<{ status: string; trade_id: number }> => {
    return apiFetch<{ status: string; trade_id: number }>(
      withDevUser(`/workspaces/${workspaceId}/trades/${tradeId}`), // ✅ FIXED
      {
        method: "DELETE",
      }
    );
  },

  importTradesCsv: async (workspaceId: number, file: File): Promise<ImportCsvResult> => {
    const formData = new FormData();
    formData.append("file", file);

    const headers = getAuthHeaders();

    const baseUrl = getApiBaseUrl();

    const res = await fetch(
      `${getApiBaseUrl()}/api${withDevUser(`/workspaces/${workspaceId}/trades/import-csv`)}`,
      {
        method: "POST",
        headers,
        body: formData,
      }
    );

  if (!res.ok) {
    const rawText = await res.text();
    const payload = parseApiErrorPayload(rawText);
    const message =
      payload?.message ||
      payload?.detail ||
      rawText ||
      `API request failed with status ${res.status}`;

    if (res.status === 401) {
      clearStoredAccessToken();
      clearStoredActiveWorkspaceId();
    }

    throw new ApiError(message, res.status, payload, rawText);
  }

    return res.json() as Promise<ImportCsvResult>;
  },

  // =========================================
  // PHASE 16 — BROKER IMPORT LAYER
  // =========================================

  uploadImportFile: async (
    workspaceId: number,
    file: File,
    sourceType?: ImportSourceType
  ): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append(
      "source_type",
      sourceType ?? "auto"
    );
    formData.append("mode", "manual");

    const headers = getAuthHeaders();

    const res = await fetch(
      `${getApiBaseUrl()}/api${withDevUser(`/workspaces/${workspaceId}/imports/upload`)}`,
      {
        method: "POST",
        headers,
        body: formData,
      }
    );

    if (!res.ok) {
      const rawText = await res.text();
      const payload = parseApiErrorPayload(rawText);

      throw new ApiError(
        payload?.message || "Import upload failed",
        res.status,
        payload,
        rawText
      );
    }

    return res.json();
  },

  // -----------------------------
  // AUTO IMPORT CONFIG
  // -----------------------------
  configureAutoImport: async (
    workspaceId: number,
    payload: {
      source_type: ImportSourceType;
      enabled: boolean;
      cadence: "hourly" | "daily";
    }
  ) => {
    return apiFetch(
      withDevUser(`/workspaces/${workspaceId}/imports/auto`),
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  // -----------------------------
  // REAL-TIME STREAM (IBKR FUTURE)
  // -----------------------------
  sendStreamEvent: async (
    workspaceId: number,
    payload: {
      source_type: ImportSourceType;
      trade: Record<string, any>;
    }
  ) => {
    return apiFetch(
      withDevUser(`/workspaces/${workspaceId}/imports/stream-event`),
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  createClaimSchema: async (payload: ClaimSchemaCreatePayload): Promise<ClaimSchema> => {
    const usage = await apiFetch<WorkspaceUsageSummary>(
      withDevUser(`/workspaces/${payload.workspace_id}/usage`),
      { cache: "no-store" }
    );

    const usedClaims = Number(usage?.usage?.claims ?? 0);

    const limitClaims = Number(usage?.limits?.claims ?? 0);

    if (usedClaims >= limitClaims && limitClaims > 0) {
      throw new Error("Claim limit reached. Upgrade required.");
    }

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

    return {
      ...ensureLeaderboard(row),
      issuer: ensureClaimIssuer(row.issuer),
      lineage: ensureClaimLineage(row.lineage),
    };
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

  // =========================================
  // DOWNLOADS (FIXED AUTH)
  // =========================================

  downloadEvidenceBundle: async (claimSchemaId: number): Promise<void> => {
    return apiDownload(
      `/claim-schemas/${claimSchemaId}/evidence-bundle/download`,
      `evidence_bundle_${claimSchemaId}.zip`
    );
  },

  downloadClaimReport: async (claimSchemaId: number): Promise<void> => {
    return apiDownload(
      `/claim-schemas/${claimSchemaId}/report/download`,
      `claim_report_${claimSchemaId}.pdf`
    );
  },

  getPublicProfile: async (
    workspaceId: number
  ): Promise<PublicProfileResponse> => {

    const row = await apiFetch<any>(
      `/profiles/${workspaceId}`,
      {
        cache: "no-store",
      }
    );

    return ensurePublicProfileResponse({
      profile: {
        profile_id: `workspace:${workspaceId}`,

        workspace_id: Number(
          row?.profile?.workspace_id ??
          row?.workspace_id ??
          workspaceId
        ),

        name:
          row?.profile?.name ??
          row?.name ??
          `Workspace #${workspaceId}`,

        type:
          row?.profile?.type ??
          "workspace",

        network:
          row?.profile?.network ??
          "internal",

        claims_count: Number(
          row?.profile?.claims_count ??
          row?.stats?.claim_count ??
          0
        ),

        locked_claims_count: Number(
          row?.profile?.locked_claims_count ??
          row?.stats?.claim_count ??
          0
        ),

        contested_claims_count: Number(
          row?.profile?.contested_claims_count ??
          0
        ),

        average_trust_score: Number(
          row?.profile?.average_trust_score ??
          row?.stats?.avg_trust ??
          0
        ),

        average_network_score: Number(
          row?.profile?.average_network_score ??
          0
        ),

        total_net_pnl: Number(
          row?.profile?.total_net_pnl ??
          row?.stats?.total_pnl ??
          0
        ),

        trust_profile_band:
          row?.profile?.trust_profile_band ??
          "developing",
      },

      claims: Array.isArray(row?.claims)
        ? row.claims
        : [],

      claims_count: Number(
        row?.claims_count ??
        row?.stats?.claim_count ??
        0
      ),
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
      issuer: ensureClaimIssuer(row.issuer),
      lineage: ensureClaimLineage(row.lineage),
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

    getExternalVerificationRecord: async (
    claimHash: string
  ): Promise<ExternalVerificationLookupResult> => {
    const row = await apiFetch<ExternalVerificationLookupResult | PublicVerifyResult>(
      `/public/verify/${claimHash}`,
      {
        cache: "no-store",
      }
    );

    return ensureExternalVerificationLookupResult(row);
  },

  getWorkspacePlatformReadiness: async (
    workspaceId: number
  ): Promise<PlatformReadiness> => {
    const row = await apiFetch<PlatformReadiness>(
      withDevUser(`/workspaces/${workspaceId}/platform-readiness`),
      {
        cache: "no-store",
      }
    );

    return (
      ensurePlatformReadiness(row) ?? {
        workspace_id: workspaceId,
        capabilities: {
          public_verification_enabled: false,
          public_distribution_enabled: false,
          external_verification_enabled: false,
          api_access_enabled: false,
          broker_import_enabled: false,
          webhook_ingestion_enabled: false,
        },
        integration_sources: [],
        verification_exposure_level: "internal_only",
        recommended_next_step: null,
      }
    );
  },

  getVerifyClaimByHash: async (
      claimHash: string,
  ): Promise<VerificationCertificate> => {

      const row = await apiFetch<any>(
          `/verify/${claimHash}`,
          {
              cache: "no-store",
          }
      );

      return ensureVerificationCertificate(row);

  },

    // =========================
    // Phase 9 — Claim Disputes
    // =========================

    getClaimDisputes: async (claimSchemaId: number): Promise<ClaimDispute[]> => {
      const rows = await apiFetch<ClaimDispute[]>(
        withDevUser(`/claim-schemas/${claimSchemaId}/disputes`),
        { cache: "no-store" }
      );

      return Array.isArray(rows) ? rows.map(ensureClaimDispute) : [];
    },

    createClaimDispute: async (
      claimSchemaId: number,
      payload: {
        summary: string;
        evidence_note?: string;
        challenge_type?: string;
        reason_code?: string;
      }
    ): Promise<ClaimDispute> => {
      const row = await apiFetch<ClaimDispute>(
        withDevUser(`/claim-schemas/${claimSchemaId}/disputes`),
        {
          method: "POST",
          body: JSON.stringify(payload),
        }
      );

      return ensureClaimDispute(row);
    },

    updateClaimDisputeStatus: async (
      disputeId: number,
      payload: {
        status: ClaimDisputeStatus;
        resolution_note?: string;
      }
    ): Promise<ClaimDispute> => {
      const row = await apiFetch<ClaimDispute>(
        withDevUser(`/claim-disputes/${disputeId}`),
        {
          method: "PATCH",
          body: JSON.stringify(payload),
        }
      );

      return ensureClaimDispute(row);
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
      { cache: "no-store" }
    );
  },

  getAuditEventsForWorkspace: async (
    workspaceId: number,
    limit = 50
  ): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(
      withDevUser(`/workspaces/${workspaceId}/audit-events?limit=${limit}`),
      { cache: "no-store" }
    );
  },

  getWorkspacePublicClaims: async (
    workspaceId: number
  ): Promise<any[]> => {
    return apiFetch<any[]>(
      withDevUser(`/workspaces/${workspaceId}/public-claims`),
      { cache: "no-store" }
    );
  },

  getGlobalPublicClaims: async (
    minTrust = 0,
    minTrades = 0,
    sortBy: "trust" | "pnl" | "trades" = "trust"
  ): Promise<any[]> => {
    return apiFetch<any[]>(
      `/public/claims?min_trust=${minTrust}&min_trades=${minTrades}&sort_by=${sortBy}`,
      { cache: "no-store" }
    );
  },
  };

export function computeTrustScore(claim: any): number {
  if (!claim) return 0;

  let score = 0;

  if (claim.integrity_status === "valid") score += 40;

  if (claim.verification_status === "locked") score += 20;

  const trades = Number(claim.trade_count || 0);
  if (trades >= 50) score += 20;
  else if (trades >= 20) score += 15;
  else if (trades >= 10) score += 10;
  else if (trades > 0) score += 5;

  if (claim.verified_at || claim.lifecycle?.verified_at) score += 10;

  if (claim.scope?.visibility === "public") score += 10;

  return Math.min(score, 100);
}

export function computeTrustWeightedPnl(claim: any): number {
  const trustScore = computeTrustScore(claim);
  const netPnl = Number(claim?.net_pnl ?? 0);

  if (!Number.isFinite(netPnl)) return 0;
  return (netPnl * trustScore) / 100;
}

export function resolveVerificationExposureLevel(claim: any): VerificationExposureLevel {
  const visibility = String(claim?.scope?.visibility ?? claim?.visibility ?? "")
    .toLowerCase()
    .trim();

  if (visibility === "public") return "public";
  if (visibility === "unlisted") return "unlisted";

  const hasClaimHash = Boolean(String(claim?.claim_hash ?? "").trim());
  const status = String(claim?.verification_status ?? claim?.status ?? "")
    .toLowerCase()
    .trim();

  if ((status === "locked" || status === "published") && hasClaimHash) {
    return "external_distribution";
  }

  return "internal_only";
}

export async function downloadEvidenceJson(
  claimId: number
) {
  return apiDownload(
    `/claim-schemas/${claimId}/evidence-pack/download`,
    `evidence_pack_${claimId}.json`
  );
}

export async function downloadEvidenceZip(claimId: number) {
  return apiDownload(
    `/claim-schemas/${claimId}/evidence-bundle/download`,
    `evidence_bundle_${claimId}.zip`
  );
}

export async function downloadClaimReportPdf(claimId: number) {
  return apiDownload(
    `/claim-schemas/${claimId}/claim-report/download`,
    `claim_report_${claimId}.pdf`
  );
}

export async function getWorkspaceEntitlements(
    workspaceId: number,
): Promise<WorkspaceEntitlements> {

    return apiFetch<WorkspaceEntitlements>(
        `/workspaces/${workspaceId}/entitlements`,
    );

}

export async function getWorkspacePlanSimulation(
    workspaceId:number,
){

    return apiFetch(

        `/workspaces/${workspaceId}/plan-simulation`

    );

}

export async function setWorkspacePlanSimulation(

    workspaceId:number,

    plan:string,

){

    return apiFetch(

        `/workspaces/${workspaceId}/plan-simulation`,

        {

            method:"PUT",

            body:JSON.stringify({

                plan,

            }),

        },

    );

}

export async function clearWorkspacePlanSimulation(

    workspaceId:number,

){

    return apiFetch(

        `/workspaces/${workspaceId}/plan-simulation`,

        {

            method:"DELETE",

        },

    );

}