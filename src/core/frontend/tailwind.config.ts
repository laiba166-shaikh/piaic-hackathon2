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
        paper: {
          cream: "#F5F1E8",      // Paper Cream (background)
          white: "#FEFEFE",      // Bright White
        },
        ink: {
          black: "#2C3E50",      // Ink Black (text)
          dark: "#1A252F",       // Darker shade
          light: "#546E7A",      // Lighter shade
        },
        vintage: {
          blue: "#4A7C99",       // Vintage Blue (accent)
          dark: "#3A5F7D",       // Darker blue
          light: "#6B9FB8",      // Lighter blue
        },
        sepia: {
          brown: "#8B7355",      // Sepia Brown (borders)
          dark: "#6B5742",       // Darker brown
          light: "#A89077",      // Lighter brown
        },
        accent: {
          gold: "#D4AF37",       // Gold accent
          red: "#C85A54",        // Muted red
          green: "#5A8A6F",      // Muted green
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Patrick Hand", "cursive"],
        mono: ["Courier Prime", "monospace"],
      },
      spacing: {
        "18": "4.5rem",
        "88": "22rem",
        "128": "32rem",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      boxShadow: {
        journal: "0 4px 6px -1px rgba(139, 115, 85, 0.1), 0 2px 4px -1px rgba(139, 115, 85, 0.06)",
        "journal-lg": "0 10px 15px -3px rgba(139, 115, 85, 0.1), 0 4px 6px -2px rgba(139, 115, 85, 0.05)",
      },
    },
  },
  plugins: [],
};

export default config;
