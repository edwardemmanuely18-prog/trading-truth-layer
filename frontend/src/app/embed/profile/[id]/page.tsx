const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://trading-truth-layer.onrender.com"; // ✅ FIXED backend URL
  
type PublicClaim = {
  id: string | number;
  trust_score: number;
  net_pnl: number;
};

async function getPublicProfile(id: number) {
  const res = await fetch(`${API_BASE}/api/public/profile/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }

  return res.json();
}

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function EmbedProfilePage({ params }: PageProps) {
  const { id } = await params;

  const workspaceId = Number(id);

  // ✅ HARD VALIDATION (prevents false invalid states)
  if (!Number.isFinite(workspaceId) || workspaceId <= 0) {
    return <div style={styles.center}>Invalid profile id</div>;
  }

  let data: any = null;
  let error: string | null = null;

  try {
    data = await getPublicProfile(workspaceId);
  } catch (err: any) {
    error = err?.message || "Failed to load profile";
  }

  if (error) {
    return <div style={styles.center}>{error}</div>;
  }

  // ✅ SAFE NORMALIZATION LAYER
  const profile = {
    id: data?.workspace_id ?? workspaceId,
    name: data?.name ?? `Workspace #${workspaceId}`,
    trust_score: Number(data?.stats?.avg_trust ?? 0),
    network_score: 0, // future-proof
    locked_claims: Number(data?.stats?.claim_count ?? 0),
    net_pnl: Number(data?.stats?.total_pnl ?? 0),
  };

  // ✅ SAFE CLAIMS NORMALIZATION
  const claims: PublicClaim[] = Array.isArray(data?.claims)
    ? data.claims.map((c: any, i: number) => ({
        id: c.id ?? i,
        trust_score: Number(c.trust_score ?? 0),
        net_pnl: Number(c.net_pnl ?? 0),
        }))
    : [];

  return (
    <div style={styles.container}>
      
      {/* HEADER */}
      <div style={styles.header}>
        <div style={styles.title}>{profile.name}</div>
        <div style={styles.subtitle}>Public Trust Profile</div>
      </div>

      {/* METRICS */}
      <div style={styles.metrics}>
        <Metric label="Trust" value={profile.trust_score} />
        <Metric label="Network" value={profile.network_score} />
        <Metric label="Locked Claims" value={profile.locked_claims} />
        <Metric label="PnL" value={profile.net_pnl} />
      </div>

      {/* CLAIMS */}
      <div style={styles.section}>
        <div style={styles.sectionTitle}>Claims</div>

        {claims.length > 0 ? (
          claims.map((c: PublicClaim) => (
            <div key={c.id} style={styles.claim}>
              <div style={styles.claimRow}>
                <span>Trust:</span> {c.trust_score}
              </div>
              <div style={styles.claimRow}>
                <span>PnL:</span> {c.net_pnl}
              </div>
            </div>
          ))
        ) : (
          <div style={styles.empty}>No public claims</div>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div style={styles.metric}>
      <div style={styles.metricValue}>{formatNumber(value)}</div>
      <div style={styles.metricLabel}>{label}</div>
    </div>
  );
}

// ✅ ADDED: formatting helper (prevents ugly NaN / undefined)
function formatNumber(value: number) {
  if (!Number.isFinite(value)) return "0";
  return value.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}

const styles: any = {
  container: {
    fontFamily: "sans-serif",
    padding: 16,
    background: "#ffffff",
    color: "#0f172a",
    width: "100%",
    height: "100%",
    boxSizing: "border-box"
  },
  header: {
    marginBottom: 16
  },
  title: {
    fontSize: 20,
    fontWeight: 600
  },
  subtitle: {
    fontSize: 12,
    color: "#64748b"
  },
  metrics: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: 12,
    marginBottom: 16
  },
  metric: {
    border: "1px solid #e2e8f0",
    borderRadius: 8,
    padding: 10,
    textAlign: "center"
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 600
  },
  metricLabel: {
    fontSize: 12,
    color: "#64748b"
  },
  section: {
    marginTop: 10
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 600,
    marginBottom: 8
  },
  claim: {
    border: "1px solid #e2e8f0",
    borderRadius: 6,
    padding: 8,
    marginBottom: 6
  },
  claimRow: {
    fontSize: 12
  },
  empty: {
    fontSize: 12,
    color: "#94a3b8"
  },
  center: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
    fontFamily: "sans-serif"
  }
};