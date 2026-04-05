import type { Config } from "tailwindcss";

// In Tailwind v4, colors and dark mode are configured via CSS (@theme inline / @custom-variant).
// This file only needs to declare content paths.
const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
};

export default config;
