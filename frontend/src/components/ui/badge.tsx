import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeVariant = "neutral" | "critical" | "high" | "medium" | "low" | "safe";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  neutral: "border-border bg-surface-subtle text-text-secondary",
  critical: "border-severity-critical/30 bg-severityBg-critical text-severity-critical",
  high: "border-severity-high/30 bg-severityBg-high text-severity-high",
  medium: "border-severity-medium/30 bg-severityBg-medium text-severity-medium",
  low: "border-severity-low/30 bg-severityBg-low text-severity-low",
  safe: "border-severity-safe/30 bg-severityBg-safe text-severity-safe",
};

export function Badge({ className, variant = "neutral", ...props }: BadgeProps): JSX.Element {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium tracking-wide",
        "border",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}
