export default function PricingPage() {
  return (
    <div
      style={{
        padding: "48px 24px",
        maxWidth: 1100,
        margin: "0 auto",
        lineHeight: 1.8,
        fontSize: 16,
      }}
    >
      <h1 style={{ fontSize: 36, marginBottom: 32 }}>
        Pricing
      </h1>

      <p style={{ marginBottom: 18 }}>
        Choose a plan that fits your operational verification workflow,
        governance scale, and workspace requirements.
      </p>

      {/* Sandbox */}
      <div style={card}>
        <h2
          style={{
            fontSize: 24,
            fontWeight: 700,
            marginBottom: 14,
          }}
        >
          Sandbox
        </h2>

        <p style={{ marginBottom: 18 }}>
          Controlled evaluation environment for testing platform workflows and
          product capabilities.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$0/month</strong>
        </p>

        <ul style={{ paddingLeft: 24, marginBottom: 24 }}>
          <li style={{ marginBottom: 10 }}>Claims: 2</li>
          <li style={{ marginBottom: 10 }}>Trades: 200</li>
          <li style={{ marginBottom: 10 }}>Members: 2</li>
          <li style={{ marginBottom: 10 }}>Storage: 100 MB</li>
        </ul>
      </div>

      {/* Starter */}
      <div style={card}>
        <h2
          style={{
            fontSize: 24,
            fontWeight: 700,
            marginBottom: 14,
          }}
        >
          Starter
        </h2>

        <p style={{ marginBottom: 18 }}>
          Entry commercial tier for small verification workflows and operational
          teams.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$19/month</strong> or $190/year
        </p>

        <ul style={{ paddingLeft: 24, marginBottom: 24 }}>
          <li style={{ marginBottom: 10 }}>Claims: 5</li>
          <li style={{ marginBottom: 10 }}>Trades: 1,000</li>
          <li style={{ marginBottom: 10 }}>Members: 3</li>
          <li style={{ marginBottom: 10 }}>Storage: 500 MB</li>
        </ul>
      </div>

      {/* Pro */}
      <div style={card}>
        <h2
          style={{
            fontSize: 24,
            fontWeight: 700,
            marginBottom: 14,
          }}
        >
          Pro
        </h2>

        <p style={{ marginBottom: 18 }}>
          Designed for active operators requiring larger canonical record
          capacity and collaboration controls.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$79/month</strong> or $790/year
        </p>

        <ul style={{ paddingLeft: 24, marginBottom: 24 }}>
          <li style={{ marginBottom: 10 }}>Claims: 25</li>
          <li style={{ marginBottom: 10 }}>Trades: 10,000</li>
          <li style={{ marginBottom: 10 }}>Members: 10</li>
          <li style={{ marginBottom: 10 }}>Storage: 5 GB</li>
        </ul>
      </div>

      {/* Growth */}
      <div style={card}>
        <h2
          style={{
            fontSize: 24,
            fontWeight: 700,
            marginBottom: 14,
          }}
        >
          Growth
        </h2>

        <p style={{ marginBottom: 18 }}>
          Operational scale tier for growing teams, governance workflows, and
          verification infrastructure expansion.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$249/month</strong> or $2,490/year
        </p>

        <ul style={{ paddingLeft: 24, marginBottom: 24 }}>
          <li style={{ marginBottom: 10 }}>Claims: 100</li>
          <li style={{ marginBottom: 10 }}>Trades: 100,000</li>
          <li style={{ marginBottom: 10 }}>Members: 50</li>
          <li style={{ marginBottom: 10 }}>Storage: 25 GB</li>
        </ul>
      </div>

      {/* Business */}
      <div style={card}>
        <h2
          style={{
            fontSize: 24,
            fontWeight: 700,
            marginBottom: 14,
          }}
        >
          Business
        </h2>

        <p style={{ marginBottom: 18 }}>
          Enterprise-grade operational capacity for institutional workspace
          environments.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$999/month</strong> or $9,990/year
        </p>

        <ul style={{ paddingLeft: 24, marginBottom: 24 }}>
          <li style={{ marginBottom: 10 }}>Claims: 500</li>
          <li style={{ marginBottom: 10 }}>Trades: 1,000,000</li>
          <li style={{ marginBottom: 10 }}>Members: 250</li>
          <li style={{ marginBottom: 10 }}>Storage: 100 GB</li>
        </ul>
      </div>
    </div>
  );
}

const card: React.CSSProperties = {
  border: "1px solid #d4d4d8",
  borderRadius: 18,
  padding: 28,
  marginTop: 28,
  background: "#ffffff",
  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
};