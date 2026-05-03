const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "https://trading-truth-layer.onrender.com/api";

export const API_BASE_URL = API_BASE;
const DEV_USER_ID: number | null = null;
const TOKEN_STORAGE_KEY = "ttl_access_token";
const ACTIVE_WORKSPACE_STORAGE_KEY = "ttl_active_workspace_id";

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
  billing_enabled?: boolean;
  secret_key_configured?: boolean;
  package_installed?: boolean;
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

export type PublicProfileResponse = {
  profile: PublicTrustProfile;
  claims: PublicClaimDirectoryItem[];
  claims_count: number;
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
  upgrade_required?: boolean;
};

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

export async function getStrategyPerformance(workspaceId: number) {
  return apiFetch(`/workspaces/${workspaceId}/strategy-performance`);
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = getAuthHeaders(options?.headers);

  const baseUrl = getApiBaseUrl();
  const finalPath = withApiPrefix(path);

  console.log("API CALL:", `${baseUrl}${finalPath}`, {
    token: getStoredAccessToken(),
  });

  if (!(options?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }


  function withApiPrefix(path: string) {
    // auth routes should NOT be prefixed
    if (path.startsWith("/auth")) return path;

    // everything else MUST go through /api
    return path.startsWith("/api") ? path : `/api${path}`;
  }

  const res = await fetch(`${baseUrl}${finalPath}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const rawText = await res.text();
    const payload = parseApiErrorPayload(rawText);

    const isLimitError =
      payload?.code === "LIMIT_EXCEEDED" ||
      payload?.code === "PLAN_LIMIT_REACHED" ||
      payload?.upgrade_required === true ||
      payload?.recommended_action === "upgrade";

    if (isLimitError) {
      const workspaceId = payload?.workspace_id;

      if (typeof window !== "undefined" && workspaceId) {
        throw new ApiError(
          payload?.message || "Workspace limit reached",
          res.status,
          payload,
          rawText,
          {
            redirectTo: workspaceId
              ? `/workspace/${workspaceId}/settings?upgrade=true`
              : undefined,
          }
        );
      }

      throw new ApiError(
        payload?.message || "Workspace limit reached",
        res.status,
        payload,
        rawText
      );
    }

    const message =
      payload?.message ||
      payload?.detail ||
      rawText ||
      `API request failed with status ${res.status}`;

    throw new ApiError(message, res.status, payload, rawText);
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
}

async function apiDownload(path: string, filename: string): Promise<void> {
  const headers = getAuthHeaders();
  const baseUrl = getApiBaseUrl();

  const finalPath = path.startsWith("/api") ? path : `/api${path}`;

  const res = await fetch(`${baseUrl}${finalPath}`, {
    method: "GET",
    headers,
  });

  if (!res.ok) {
    const rawText = await res.text();
    const payload = parseApiErrorPayload(rawText);

    throw new ApiError(
      payload?.message || "Download failed",
      res.status,
      payload,
      rawText
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

function ensurePlanCatalogItem(row: Partial<PlanCatalogItem>): PlanCatalogItem {
  const code = String(row.code ?? "");

  return {
    code,
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
    billing: ensurePlanBilling(row.billing, code),
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
      members: ensureUsageDimension(row?.usage?.members),
      trades: ensureUsageDimension(row?.usage?.trades),
      claims: ensureUsageDimension(row?.usage?.claims),
      storage_mb: ensureUsageDimension(row?.usage?.storage_mb),
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

  logout: () => {
    clearStoredAccessToken();
    clearStoredActiveWorkspaceId();
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

  getWorkspaceBillingFoundation: async (
    workspaceId: number
  ): Promise<WorkspaceBillingFoundation> => {
    const row = await apiFetch<WorkspaceBillingFoundation>(
      withDevUser(`/billing/workspaces/${workspaceId}/billing-foundation`),
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

  async getTrades(
    workspaceId: number,
    params?: {
      tag?: string;
      symbol?: string;
      side?: string;
      limit?: number;
      offset?: number;
    }
  ) {
    const query = new URLSearchParams();

    if (params?.tag) query.append("tag", params.tag);
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
    sourceType: "csv" | "mt5" | "ibkr" = "csv"
  ): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("source_type", sourceType);
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
      source_type: "csv" | "mt5" | "ibkr";
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
      source_type: "ibkr" | "mt5";
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

    if (usage.usage.claims.status === "at_limit" || usage.usage.claims.status === "over_limit") {
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

  getPublicProfile: async (workspaceId: number): Promise<PublicProfileResponse> => {
    const row = await apiFetch<PublicProfileResponse>(`/profiles/${workspaceId}`, {
      cache: "no-store",
    });

    return ensurePublicProfileResponse(row);
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

  getVerifyClaimByHash: async (claimHash: string): Promise<VerifyClaimResult> => {
    const row = await apiFetch<VerifyPayloadV7 | VerifyClaimResult>(
      `/verify/${claimHash}`,
      {
        cache: "no-store",
      }
    );

    return normalizeVerifyPayload(row);
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