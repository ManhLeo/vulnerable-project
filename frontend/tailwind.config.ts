import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/features/**/*.{ts,tsx}",
    "./src/hooks/**/*.{ts,tsx}",
    "./src/lib/**/*.{ts,tsx}",
    "./src/services/**/*.{ts,tsx}",
    "./src/styles/**/*.{ts,tsx}",
    "./src/types/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        borderStrong: "hsl(var(--border-strong))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",

        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",

        surface: {
          page: "hsl(var(--surface-page))",
          panel: "hsl(var(--surface-panel))",
          elevated: "hsl(var(--surface-elevated))",
          subtle: "hsl(var(--surface-subtle))"
        },

        text: {
          primary: "hsl(var(--text-primary))",
          secondary: "hsl(var(--text-secondary))",
          muted: "hsl(var(--text-muted))",
          placeholder: "hsl(var(--text-placeholder))"
        },

        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          hover: "hsl(var(--primary-hover))",
          subtle: "hsl(var(--primary-subtle))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))"
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))"
        },
        severity: {
          critical: "hsl(var(--severity-critical))",
          high: "hsl(var(--severity-high))",
          medium: "hsl(var(--severity-medium))",
          low: "hsl(var(--severity-low))",
          safe: "hsl(var(--severity-safe))"
        },
        severityBg: {
          critical: "hsl(var(--severity-critical-bg))",
          high: "hsl(var(--severity-high-bg))",
          medium: "hsl(var(--severity-medium-bg))",
          low: "hsl(var(--severity-low-bg))",
          safe: "hsl(var(--severity-safe-bg))"
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)"
      }
    }
  },
  plugins: []
};

export default config;
