export default function PricingPage() {
  return (
    <div style={{ padding: "40px", maxWidth: 900, margin: "auto" }}>
      <h1>Pricing</h1>

      <div style={{ border: "1px solid #ccc", padding: 20, marginTop: 20 }}>
        <h2>Starter Plan</h2>
        <h3>$10/month</h3>

        <ul>
          <li>Up to 5 claims</li>
          <li>Up to 3 workspace members</li>
          <li>Basic verification tools</li>
        </ul>
      </div>
    </div>
  );
}