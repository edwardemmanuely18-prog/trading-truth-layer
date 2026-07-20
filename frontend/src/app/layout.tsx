import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../components/AuthProvider";
import PaddleLoader from "../components/PaddleLoader";


export const metadata: Metadata = {
  title: {
    default: "Trading Truth Layer",
    template: "%s | Trading Truth Layer",
  },

  description:
    "Institutional Trading Trust Infrastructure for verification, investigations, governance, due diligence, capital allocation readiness, public trust systems, and independently verifiable trading performance.",

  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/icon.png",
  },

  openGraph: {
    title: "Trading Truth Layer",

    description:
      "Institutional Trading Trust Infrastructure for verification, investigations, governance, due diligence, capital allocation readiness, public trust systems, and independently verifiable trading performance.",

    url: "https://www.tradingtruthlayer.com",

    siteName: "Trading Truth Layer",

    images: [
      {
        url: "/logo.png",
        width: 1200,
        height: 630,
        alt: "Trading Truth Layer Logo",
      },
    ],

    locale: "en_US",

    type: "website",
  },

  twitter: {
    card: "summary_large_image",
    title: "Trading Truth Layer",

    description:
      "Institutional Trading Trust Infrastructure for verification, investigations, governance, due diligence, capital allocation readiness, public trust systems, and independently verifiable trading performance.",

    images: ["/logo.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",

              "@type": "Organization",

              name: "Trading Truth Layer",

              url: "https://www.tradingtruthlayer.com",

              logo:
                "https://www.tradingtruthlayer.com/logo.png",

              description:
                "Institutional Trading Trust Infrastructure providing verification, governance, due diligence, allocator reports, investigation systems and independently verifiable trading performance.",

              email:
                "support@tradingtruthlayer.com",
            }),
          }}
        />
      </head>
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
                      maxWidth: 950,
                    }}
                  >
                    Institutional Trading Trust Infrastructure
                    for verification, investigations,
                    governance, due diligence, capital
                    allocation readiness, public trust
                    systems, and independently verifiable
                    trading performance.
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
                    href="/"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Home
                  </a>

                  <a
                    href="/guidebooks"
                    style={{
                      textDecoration: "none",
                      color: "#0f172a",
                      fontWeight: 500,
                    }}
                  >
                    Guidebooks
                  </a>

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
                  Trading Truth Layer is Institutional Trading
                  Trust Infrastructure designed for global
                  capital markets. The platform provides
                  institutional infrastructure for trading
                  verification, evidence intelligence,
                  investigations, governance workflows,
                  due diligence systems, allocator readiness,
                  public trust infrastructure, and canonical
                  trading records.

                  <br />
                  <br />

                  Trading Truth Layer operates as
                  infrastructure software and does not provide
                  brokerage services, investment advisory,
                  portfolio management, asset custody,
                  financial advice, or trade execution
                  services.

                  <br />
                  <br />

                  The Trading Truth Layer Guidebook Series
                  publishes institutional frameworks and
                  infrastructure doctrines governing the
                  Trading Truth Layer ecosystem.

                  <br />
                  <br />

                  Copyright © 2026 Trading Truth Layer.
                  All rights reserved.

                  <br />
                  <br />

                  Contact:
                  support@tradingtruthlayer.com

                  <br />

                  Website:
                  https://www.tradingtruthlayer.com
                </div>
              </div>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}