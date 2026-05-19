export const SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;

export type SeverityLevel = (typeof SEVERITY_LEVELS)[number];

export interface SeverityToken {
  label: SeverityLevel;
  cssVar: string;
  className: string;
}

export const severityTokens: Record<SeverityLevel, SeverityToken> = {
  LOW: {
    label: "LOW",
    cssVar: "--severity-low",
    className: "text-severity-low border-severity-low",
  },
  MEDIUM: {
    label: "MEDIUM",
    cssVar: "--severity-medium",
    className: "text-severity-medium border-severity-medium",
  },
  HIGH: {
    label: "HIGH",
    cssVar: "--severity-high",
    className: "text-severity-high border-severity-high",
  },
  CRITICAL: {
    label: "CRITICAL",
    cssVar: "--severity-critical",
    className: "text-severity-critical border-severity-critical",
  },
};
