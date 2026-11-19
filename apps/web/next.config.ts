import type { NextConfig } from "next";

// The browser always calls same-origin /api/*; Next proxies to the API service so
// session cookies stay same-origin. Set API_PROXY_TARGET in the container.
const apiTarget = process.env.API_PROXY_TARGET ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  outputFileTracingRoot: process.cwd(),
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiTarget}/api/:path*` }];
  },
};

export default nextConfig;
