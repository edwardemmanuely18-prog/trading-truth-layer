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
    </html>
  );
}