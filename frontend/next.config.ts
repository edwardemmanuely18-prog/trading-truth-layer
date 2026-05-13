import type { NextConfig } from "next";

const backendBase =
  process.env.NEXT_PUBLIC_API_BASE ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

const normalizedBackendBase = backendBase.replace(/\/+$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${normalizedBackendBase}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;