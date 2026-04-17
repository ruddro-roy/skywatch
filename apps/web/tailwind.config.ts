import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm, classic, print-inspired palette.
        paper: {
          DEFAULT: "#fbfaf7",   // page background
          raised: "#ffffff",    // cards
          panel: "#f5f2ea",     // sub-panels
        },
        ink: {
          DEFAULT: "#1a1a1a",
          soft:    "#2a2a2a",
          mute:    "#5a5a5a",
          faint:   "#8a8a8a",
        },
        rule: "#e5ddc9",          // dividers, borders
        accent: "#5a3e1b",        // links, emphasis
        accentSoft: "#8a6a3e",
        positive: "#3f6b3c",      // "live", agreement
        warn:     "#9b6a1f",
        negative: "#8a3b2f",
      },
      fontFamily: {
        serif: ['"Source Serif 4"', "Charter", '"Iowan Old Style"', "Georgia", "serif"],
        sans:  ['"Inter"', "system-ui", "sans-serif"],
        mono:  ['"JetBrains Mono"', "ui-monospace", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
