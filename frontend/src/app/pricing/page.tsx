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
        Choose a plan that fits your operational verification
        workflows, governance scale, auditability requirements,
        and canonical record infrastructure needs.
      </p>

      <p style={{ marginBottom: 18 }}>
        Trading Truth Layer is infrastructure software for
        operational verification workflows, canonical ledger
        systems, evidence generation, governance operations,
        and auditability infrastructure.
      </p>

      <p style={{ marginBottom: 32 }}>
        All subscriptions are digital software service plans
        delivered electronically through the Trading Truth Layer
        platform.
      </p>

      {/* Sandbox */}
      <div style={card}>
        <h2 style={title}>
          Sandbox
        </h2>

        <p style={{ marginBottom: 18 }}>
          Controlled evaluation environment for testing platform
          workflows and infrastructure capabilities.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$0/month</strong>
        </p>

        <ul style={list}>
          <li style={item}>Claims: 2</li>
          <li style={item}>Trades: 200</li>
          <li style={item}>Members: 2</li>
          <li style={item}>Storage: 100 MB</li>
        </ul>
      </div>

      {/* Starter */}
      <div style={card}>
        <h2 style={title}>
          Starter
        </h2>

        <p style={{ marginBottom: 18 }}>
          Entry commercial tier for smaller operational workflows
          and verification infrastructure usage.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$19/month</strong> or $190/year
        </p>

        <ul style={list}>
          <li style={item}>Claims: 5</li>
          <li style={item}>Trades: 1,000</li>
          <li style={item}>Members: 3</li>
          <li style={item}>Storage: 500 MB</li>
        </ul>
      </div>

      {/* Pro */}
      <div style={card}>
        <h2 style={title}>
          Pro
        </h2>

        <p style={{ marginBottom: 18 }}>
          Designed for active operators requiring larger canonical
          record capacity and collaboration controls.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$79/month</strong> or $790/year
        </p>

        <ul style={list}>
          <li style={item}>Claims: 25</li>
          <li style={item}>Trades: 10,000</li>
          <li style={item}>Members: 10</li>
          <li style={item}>Storage: 5 GB</li>
        </ul>
      </div>

      {/* Growth */}
      <div style={card}>
        <h2 style={title}>
          Growth
        </h2>

        <p style={{ marginBottom: 18 }}>
          Operational scale tier for expanding governance workflows
          and evidence infrastructure operations.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$249/month</strong> or $2,490/year
        </p>

        <ul style={list}>
          <li style={item}>Claims: 100</li>
          <li style={item}>Trades: 100,000</li>
          <li style={item}>Members: 50</li>
          <li style={item}>Storage: 25 GB</li>
        </ul>
      </div>

      {/* Business */}
      <div style={card}>
        <h2 style={title}>
          Business
        </h2>

        <p style={{ marginBottom: 18 }}>
          Enterprise-grade operational infrastructure for larger
          institutional verification environments.
        </p>

        <p style={{ marginBottom: 18 }}>
          <strong>$999/month</strong> or $9,990/year
        </p>

        <ul style={list}>
          <li style={item}>Claims: 500</li>
          <li style={item}>Trades: 1,000,000</li>
          <li style={item}>Members: 250</li>
          <li style={item}>Storage: 100 GB</li>
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

const title: React.CSSProperties = {
  fontSize: 24,
  fontWeight: 700,
  marginBottom: 14,
};

const list: React.CSSProperties = {
  paddingLeft: 24,
  marginBottom: 24,
};

const item: React.CSSProperties = {
  marginBottom: 10,
};