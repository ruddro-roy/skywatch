import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "skywatch — Privacy-First AI Weather",
  description:
    "Hybrid AI weather prototype fusing multiple forecast models with computer-vision verification from public webcams. No tracking. No location sharing. Works anywhere on Earth.",
  keywords: [
    "weather",
    "AI forecast",
    "privacy",
    "open source",
    "computer vision",
    "ECMWF",
    "Open-Meteo",
  ],
  openGraph: {
    title: "skywatch",
    description: "Privacy-first hybrid AI weather prototype",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0c4a6e",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-[#0c1a2e] text-slate-100 antialiased">
        {/* Nav */}
        <nav className="sticky top-0 z-50 border-b border-slate-800 bg-[#0c1a2e]/90 backdrop-blur-sm">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
            {/* Logo */}
            <a href="/" className="flex items-center gap-2 hover:opacity-90 transition-opacity">
              <svg
                aria-label="skywatch"
                viewBox="0 0 32 32"
                fill="none"
                className="h-8 w-8"
              >
                {/* Outer ring — radar sweep */}
                <circle cx="16" cy="16" r="14" stroke="#0ea5e9" strokeWidth="1.5" />
                {/* Inner rings */}
                <circle cx="16" cy="16" r="8" stroke="#0ea5e9" strokeWidth="1" strokeDasharray="4 3" opacity="0.6" />
                <circle cx="16" cy="16" r="3" fill="#0ea5e9" />
                {/* Sweep line */}
                <line x1="16" y1="16" x2="27" y2="8" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round" />
                {/* Cloud arc */}
                <path
                  d="M8 14 Q10 10 14 11 Q15 8 19 9 Q23 10 22 14"
                  stroke="#7dd3fc"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  fill="none"
                  opacity="0.8"
                />
              </svg>
              <span className="text-lg font-semibold tracking-tight text-sky-300">
                sky<span className="text-white">watch</span>
              </span>
            </a>

            {/* Nav links */}
            <div className="flex items-center gap-4 text-sm text-slate-400">
              <a
                href="https://github.com/your-org/skywatch"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-sky-400 transition-colors"
              >
                GitHub
              </a>
              <a href="/docs" className="hover:text-sky-400 transition-colors">
                Docs
              </a>
              <span className="rounded-full bg-sky-900/50 border border-sky-700/50 px-2.5 py-0.5 text-xs text-sky-400">
                v0.1
              </span>
            </div>
          </div>
        </nav>

        {/* Page content */}
        <main>{children}</main>

        {/* Footer */}
        <footer className="mt-16 border-t border-slate-800 py-8 text-center text-xs text-slate-500">
          <p>
            skywatch is open source (MIT) — no tracking, no ads, no geolocation API.{" "}
            <a
              href="https://github.com/your-org/skywatch"
              className="text-sky-500 hover:text-sky-400"
              target="_blank"
              rel="noopener noreferrer"
            >
              Source code
            </a>
            {" · "}
            <a href="/privacy" className="hover:text-slate-400">
              Privacy
            </a>
            {" · "}
            Forecast data from{" "}
            <a
              href="https://open-meteo.com"
              className="hover:text-slate-400"
              target="_blank"
              rel="noopener noreferrer"
            >
              Open-Meteo
            </a>{" "}
            (ECMWF IFS)
          </p>
        </footer>
      </body>
    </html>
  );
}
