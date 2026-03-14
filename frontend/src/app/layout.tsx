import "./globals.css";
import type { Metadata } from "next";

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
      <body>{children}</body>
    </html>
  );
}