import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type BadgeVariant = "neutral" | "critical" | "high" | "medium" | "low" | "safe";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  neutral: "bg-surface-subtle text-text-secondary",
  critical: "bg-severityBg-critical text-severity-critical",
  high: "bg-severityBg-high text-severity-high",
  medium: "bg-severityBg-medium text-severity-medium",
  low: "bg-severityBg-low text-severity-low",
  safe: "bg-severityBg-safe text-severity-safe",
};

export function Badge({ className, variant = "neutral", ...props }: BadgeProps): JSX.Element {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium tracking-wide",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}
