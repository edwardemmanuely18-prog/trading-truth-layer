import type { NextConfig } from "next";

const backendBase =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const normalizedBackendBase = backendBase.replace(/\/+$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${normalizedBackendBase}/:path*`,
      },
    ];
  },
};

export default nextConfig;