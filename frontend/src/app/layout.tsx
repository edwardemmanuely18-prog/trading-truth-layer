import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "../components/AuthProvider";

export const metadata: Metadata = {
  title: "Trading Truth Layer",
  description: "Verified Trading Claims OS",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>

      <footer style={{ marginTop: 40, padding: 20, textAlign: "center" }}>
        <a href="/terms">Terms</a> |{" "}
        <a href="/privacy">Privacy</a> |{" "}
        <a href="/refund">Refund</a> |{" "}
        <a href="/pricing">Pricing</a>
      </footer>
    </html>
  );
}