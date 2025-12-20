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
        // Primary colors
        primary: {
          DEFAULT: "#00D9FF",
          dark: "#00A8CC",
          light: "#33E0FF",
        },
        // Background colors
        bg: {
          primary: "#0A0E27",
          secondary: "#141B3D",
          tertiary: "#1E2749",
        },
        // Text colors
        text: {
          primary: "#FFFFFF",
          secondary: "#B8C1EC",
          muted: "#6B7AA1",
        },
        // Status colors
        success: "#00FF88",
        warning: "#FFB800",
        error: "#FF3366",
        info: "#00D9FF",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 8px 32px rgba(0, 0, 0, 0.37)",
        glow: "0 4px 20px rgba(0, 217, 255, 0.3)",
        "glow-lg": "0 8px 40px rgba(0, 217, 255, 0.5)",
      },
      backdropBlur: {
        glass: "10px",
      },
      borderRadius: {
        card: "16px",
        button: "12px",
      },
    },
  },
  plugins: [],
};

export default config;
