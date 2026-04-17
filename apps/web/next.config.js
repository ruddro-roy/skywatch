/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow images from webcam thumbnail sources
  images: {
    remotePatterns: [
      // Windy webcam thumbnails
      { protocol: "https", hostname: "**.windy.com" },
      { protocol: "https", hostname: "**.windytv.com" },
      // UDOT / US DOT camera thumbnails
      { protocol: "https", hostname: "**.udottraffic.utah.gov" },
      { protocol: "http", hostname: "**.udottraffic.utah.gov" },
      // Generic HTTPS thumbnails (tighten in production)
      { protocol: "https", hostname: "**" },
    ],
  },

  // Rewrites: proxy API calls in development to avoid CORS
  async rewrites() {
    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiBase}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
