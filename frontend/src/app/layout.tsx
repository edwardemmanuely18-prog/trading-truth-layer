import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../components/AuthProvider";

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
      <body>
        <AuthProvider>
          {children}

          {/* ✅ FOOTER MUST BE INSIDE BODY */}
          <footer
            style={{
              borderTop: "1px solid #e5e7eb",
              padding: "20px",
              marginTop: "40px",
              textAlign: "center",
              fontSize: "14px",
            }}
          >
            <a href="/terms" style={{ marginRight: 12 }}>
              Terms
            </a>
            <a href="/privacy" style={{ marginRight: 12 }}>
              Privacy
            </a>
            <a href="/refund">Refund</a>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}