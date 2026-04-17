import type { Metadata, Viewport } from "next";
import { Inter, Source_Serif_4, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const serif = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-serif",
  display: "swap",
});
const sans = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-sans",
  display: "swap",
});
const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "skywatch",
  description:
    "A small weather prototype. Open-Meteo forecast, no browser geolocation, optional computer-vision checks against public webcams.",
  keywords: [
    "weather",
    "forecast",
    "privacy",
    "open source",
    "computer vision",
    "ECMWF",
    "Open-Meteo",
  ],
  openGraph: {
    title: "skywatch",
    description: "A small weather prototype. No tracking, no browser geolocation.",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#fbfaf7",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${serif.variable} ${sans.variable} ${mono.variable}`}>
      <body className="min-h-screen">
        {/* Masthead */}
        <header className="border-b border-rule bg-paper">
          <div className="mx-auto flex max-w-6xl items-baseline justify-between gap-6 px-5 py-4">
            <a href="/" className="no-underline">
              <span className="font-serif text-lg font-bold tracking-tight text-ink">
                skywatch
              </span>
            </a>
            <nav className="flex items-center gap-5 font-sans text-sm text-ink-mute">
              <a
                href="https://github.com/ruddro-roy/skywatch"
                target="_blank"
                rel="noopener noreferrer"
                className="no-underline hover:text-ink"
              >
                GitHub
              </a>
              <a
                href="https://ruddro-roy.github.io/skywatch/"
                target="_blank"
                rel="noopener noreferrer"
                className="no-underline hover:text-ink"
              >
                Docs
              </a>
              <span className="live-pill">v0.1</span>
            </nav>
          </div>
        </header>

        <main>{children}</main>

        {/* Colophon */}
        <footer className="mt-16 border-t border-rule py-8">
          <div className="mx-auto max-w-6xl px-5 text-center font-sans text-xs text-ink-mute">
            <p className="mb-1">
              skywatch is open source (MIT). No tracking, no ads, no browser geolocation, no IP logging.
            </p>
            <p>
              Source on{" "}
              <a
                href="https://github.com/ruddro-roy/skywatch"
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub
              </a>
              . Forecast data from{" "}
              <a href="https://open-meteo.com" target="_blank" rel="noopener noreferrer">
                Open-Meteo
              </a>{" "}
              (ECMWF IFS).
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
