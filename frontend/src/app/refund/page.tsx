export default function RefundPage() {
  return (
    <div style={{ padding: "40px", maxWidth: 900, margin: "auto" }}>
      <h1>Refund Policy</h1>

      <p>
        Trading Truth Layer is operated by <b>Aurum Hybrid</b> and uses Paddle as
        its Merchant of Record.
      </p>

      <h2>14-Day Refund Guarantee</h2>
      <p>
        Customers are entitled to request a full refund within <b>14 days</b> of
        purchase, without providing any reason.
      </p>

      {/* ✅ REQUIRED PADDLE ALIGNMENT LINE */}
      <p>
        Refunds are processed in accordance with Paddle’s Buyer Terms.
      </p>

      <h2>Refund Processing</h2>
      <p>
        Refunds will be processed via the original payment method through Paddle.
      </p>

      <h2>After 14 Days</h2>
      <p>
        After 14 days, refunds may not be granted unless required by law.
      </p>

      <h2>Contact</h2>
      <p>Email: tradingtruthlayer@gmail.com</p>
    </div>
  );
}