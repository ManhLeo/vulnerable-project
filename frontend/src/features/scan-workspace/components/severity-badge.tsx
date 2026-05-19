import { cn } from "@/lib/utils";
import type { SeverityLevel } from "@/types/severity";

interface SeverityBadgeProps {
  severity: SeverityLevel;
  className?: string;
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps): JSX.Element {
  const severityStyles: Record<SeverityLevel, string> = {
    LOW: "text-severity-low bg-severityBg-low border-severity-low/20",
    MEDIUM: "text-severity-medium bg-severityBg-medium border-severity-medium/20",
    HIGH: "text-severity-high bg-severityBg-high border-severity-high/20",
    CRITICAL: "text-severity-critical bg-severityBg-critical border-severity-critical/20",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide uppercase",
        severityStyles[severity],
        className,
      )}
      aria-label={`Severity ${severity}`}
    >
      {severity}
    </span>
  );
}
