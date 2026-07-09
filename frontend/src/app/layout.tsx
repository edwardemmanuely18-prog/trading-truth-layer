import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../components/AuthProvider";
import PaddleLoader from "../components/PaddleLoader";


export const metadata: Metadata = {
  title: "Trading Truth Layer",
  description: "Verified Trading Claims OS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          background: "#f8fafc",
          color: "#0f172a",
          fontFamily:
            "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        }}
      >
        <AuthProvider>
          <PaddleLoader />
          
          <div
            style={{
              minHeight: "100vh",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <div style={{ flex: 1 }}>
              {children}
            </div>

            {/* FOOTER */}
            <footer
              style={{
                borderTop: "1px solid #e5e7eb",
                background: "#ffffff",
                marginTop: 60,
                padding: "32px 24px",
              }}
            >
              <div
                style={{
                  maxWidth: 1200,
                  margin: "0 auto",
                  display: "flex",
                  flexDirection: "column",
                  gap: 18,
                }}
              >
                {/* Brand */}
                <div>
                  <div
                    style={{
                      fontSize: 18,
                      fontWeight: 700,
                      marginBottom: 6,
                    }}
                  >
                    Trading Truth Layer
                  </div>

                  <div
                    style={{
                      fontSize: 14,
                      color: "#475569",
                      lineHeight: 1.7,
                      maxWidth: 900,
                    }}
                  >
                    Verification infrastructure for trading records, canonical ledgers, auditability, governance workflows, and dispute-ready proof systems.
                  </div>
                </div>

                {/* Links */}
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 18,
                    fontSize: 14,
                  }}
                >
                  <a
                    href="/pricing"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Pricing
                  </a>

                  <a
                    href="/terms"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Terms
                  </a>

                  <a
                    href="/privacy"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Privacy
                  </a>

                  <a
                    href="/refund"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Refund
                  </a>

                  <a
                    href="/risk"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Risk Disclosure
                  </a>
                </div>

                {/* Compliance */}
                <div
                  style={{
                    fontSize: 13,
                    color: "#64748b",
                    lineHeight: 1.8,
                    borderTop: "1px solid #e5e7eb",
                    paddingTop: 18,
                  }}
                >
                  Trading Truth Layer is operated by Aurum Hybrid,
                  Tanzania. The platform provides infrastructure
                  software for operational verification, canonical
                  ledger systems, governance workflows, evidence
                  generation, and auditability infrastructure.

                  <br />
                  <br />

                  Trading Truth Layer does not provide brokerage,
                  investment advisory, portfolio management,
                  custody, financial advice, or trade execution
                  services.

                  <br />
                  <br />

                  Contact: support@tradingtruthlayer.com

                  <br />
                  Website: https://www.tradingtruthlayer.com
                </div>
              </div>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}