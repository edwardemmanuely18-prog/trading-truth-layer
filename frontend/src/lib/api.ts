const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export const API_BASE_URL = API_BASE;
const DEV_USER_ID = 1;

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
  cumulative_pnl: number;
};

export type ClaimTradeEvidence = {
  claim_schema_id: number;
  claim_hash: string;
  name: string;
  status: string;
  trade_count: number;
  trades: ClaimTradeEvidenceRow[];
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

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers || {});

  if (!(options?.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

function withDevUser(path: string) {
  const separator = path.includes("?") ? "&" : "?";
  return `${path}${separator}user_id=${DEV_USER_ID}`;
}

function ensureLeaderboard<T extends { leaderboard?: unknown }>(row: T) {
  return {
    ...row,
    leaderboard: Array.isArray(row.leaderboard) ? row.leaderboard : [],
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

export const api = {
  getDashboard: async (workspaceId: number): Promise<DashboardResponse> => {
  return apiFetch<DashboardResponse>(withDevUser(`/workspaces/${workspaceId}/dashboard`), {
    cache: "no-store",
  });
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
    return apiFetch<WorkspaceMember[]>(withDevUser(`/workspaces/${workspaceId}/members`), {
      cache: "no-store",
    });
  },

  getWorkspaceInvites: async (workspaceId: number): Promise<WorkspaceInvite[]> => {
    return apiFetch<WorkspaceInvite[]>(withDevUser(`/workspaces/${workspaceId}/invites`), {
      cache: "no-store",
    });
  },

  createWorkspaceInvite: async (
    workspaceId: number,
    payload: { email: string; role: string }
  ): Promise<WorkspaceInvite> => {
    return apiFetch<WorkspaceInvite>(withDevUser(`/workspaces/${workspaceId}/invites`), {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  acceptWorkspaceInvite: async (token: string) => {
    return apiFetch(`/invites/accept`, {
      method: "POST",
      body: JSON.stringify({ token }),
    });
  },

  getLatestClaimSchema: async (): Promise<ClaimSchema> => {
    return apiFetch<ClaimSchema>(`/claim-schemas/latest`, {
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
    return apiFetch<ClaimSchema>(`/claim-schemas/${claimSchemaId}`, {
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
    return apiFetch<Trade>(`/workspaces/${workspaceId}/trades`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  importTradesCsv: async (workspaceId: number, file: File): Promise<ImportCsvResult> => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/workspaces/${workspaceId}/trades/import-csv`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `CSV import failed with status ${res.status}`);
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
    return apiFetch<ClaimVersion[]>(`/claim-schemas/${claimSchemaId}/versions`, {
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
    const row = await apiFetch<ClaimSchemaPreview>(`/claim-schemas/${claimSchemaId}/preview`, {
      cache: "no-store",
    });

    return ensureLeaderboard(row);
  },

  getClaimEquityCurve: async (claimSchemaId: number): Promise<ClaimEquityCurve> => {
    const row = await apiFetch<ClaimEquityCurve>(`/claim-schemas/${claimSchemaId}/equity-curve`, {
      cache: "no-store",
    });

    return {
      ...row,
      curve: Array.isArray(row.curve) ? row.curve : [],
    };
  },

  getClaimTrades: async (claimSchemaId: number): Promise<ClaimTradeEvidence> => {
    const row = await apiFetch<ClaimTradeEvidence>(`/claim-schemas/${claimSchemaId}/trades`, {
      cache: "no-store",
    });

    return {
      ...row,
      trades: Array.isArray(row.trades) ? row.trades : [],
    };
  },

  getEvidencePack: async (claimSchemaId: number): Promise<EvidencePack> => {
    return apiFetch<EvidencePack>(`/claim-schemas/${claimSchemaId}/evidence-pack`, {
      cache: "no-store",
    });
  },

  getEvidenceBundle: async (claimSchemaId: number): Promise<EvidenceBundle> => {
    return apiFetch<EvidenceBundle>(`/claim-schemas/${claimSchemaId}/evidence-bundle`, {
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
    };
  },

  getClaimIntegrity: async (claimSchemaId: number): Promise<ClaimIntegrityResult> => {
    return apiFetch<ClaimIntegrityResult>(`/claim-schemas/${claimSchemaId}/verify-integrity`, {
      cache: "no-store",
    });
  },

  getLatestAuditEvents: async (limit = 20): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(`/audit-events/latest?limit=${limit}`, {
      cache: "no-store",
    });
  },

  getAuditEventsForEntity: async (
    entityType: string,
    entityId: string | number
  ): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(`/audit-events/entity/${entityType}/${entityId}`, {
      cache: "no-store",
    });
  },

  getAuditEventsForWorkspace: async (
    workspaceId: string | number,
    limit = 50
  ): Promise<AuditEvent[]> => {
    return apiFetch<AuditEvent[]>(`/audit-events/workspace/${workspaceId}?limit=${limit}`, {
      cache: "no-store",
    });
  },
};