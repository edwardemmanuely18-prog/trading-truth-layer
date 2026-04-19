export default function PricingPage() {
  return (
    <div style={{ padding: "40px", maxWidth: 1100, margin: "auto" }}>
      <h1>Pricing</h1>
      <p>
        Choose a plan that fits your verification workflow, scale, and team size.
      </p>

      {/* Sandbox */}
      <div style={card}>
        <h2>Sandbox</h2>
        <p>Controlled evaluation environment for product proof.</p>

        <p><strong>$0/month</strong></p>

        <ul>
          <li>Claims: 2</li>
          <li>Trades: 200</li>
          <li>Members: 2</li>
          <li>Storage: 100 MB</li>
        </ul>
      </div>

      {/* Starter */}
      <div style={card}>
        <h2>Starter</h2>
        <p>Entry plan for early verification workflows.</p>

        <p><strong>$19/month</strong> or $190/year</p>

        <ul>
          <li>Claims: 5</li>
          <li>Trades: 1,000</li>
          <li>Members: 3</li>
          <li>Storage: 500 MB</li>
        </ul>
      </div>

      {/* Pro */}
      <div style={card}>
        <h2>Pro</h2>
        <p>For serious traders and small commercial operators.</p>

        <p><strong>$79/month</strong> or $790/year</p>

        <ul>
          <li>Claims: 25</li>
          <li>Trades: 10,000</li>
          <li>Members: 10</li>
          <li>Storage: 5 GB</li>
        </ul>
      </div>

      {/* Growth */}
      <div style={card}>
        <h2>Growth</h2>
        <p>Operational tier for scaling teams.</p>

        <p><strong>$249/month</strong> or $2,490/year</p>

        <ul>
          <li>Claims: 100</li>
          <li>Trades: 100,000</li>
          <li>Members: 50</li>
          <li>Storage: 25 GB</li>
        </ul>
      </div>

      {/* Business */}
      <div style={card}>
        <h2>Business</h2>
        <p>High-capacity tier for institutional use.</p>

        <p><strong>$999/month</strong> or $9,990/year</p>

        <ul>
          <li>Claims: 500</li>
          <li>Trades: 1,000,000</li>
          <li>Members: 250</li>
          <li>Storage: 100 GB</li>
        </ul>
      </div>
    </div>
  );
}

const card: React.CSSProperties = {
  border: "1px solid #ddd",
  borderRadius: 12,
  padding: 20,
  marginTop: 20,
};