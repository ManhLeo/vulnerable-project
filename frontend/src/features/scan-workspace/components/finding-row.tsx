import { cn } from "@/lib/utils";
import type { UiFinding } from "@/lib/utils/findings";
import { SeverityBadge } from "@/features/scan-workspace/components/severity-badge";

interface FindingRowProps {
  finding: UiFinding;
  isSelected: boolean;
  onSelect: () => void;
}

export function FindingRow({ finding, isSelected, onSelect }: FindingRowProps): JSX.Element {
  const severityColors: Record<string, string> = {
    CRITICAL: "border-l-severity-critical",
    HIGH: "border-l-severity-high",
    MEDIUM: "border-l-severity-medium",
    LOW: "border-l-severity-low",
  };

  const leftBorderColor = severityColors[finding.severity] || "border-l-border";

  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        className={cn(
          "w-full rounded-[6px] border border-border bg-white text-left transition-all duration-150 relative",
          "border-l-[3px]",
          isSelected 
            ? "bg-severityBg-low border-l-primary border-primary/40 shadow-sm" 
            : cn(leftBorderColor, "hover:bg-gray-50/80"),
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20",
          "p-3"
        )}
        aria-label={`Finding ${finding.pattern} at line ${finding.line}`}
        aria-current={isSelected}
      >
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-semibold text-text-primary uppercase tracking-wide truncate max-w-[70%]">
            {finding.pattern}
          </span>
          <SeverityBadge severity={finding.severity} />
        </div>

        <p className="mt-1.5 text-xs text-text-secondary line-clamp-2 leading-relaxed">
          {finding.issue}
        </p>

        <div className="mt-2.5 flex items-center justify-between gap-2 text-[11px] text-text-muted">
          <span className="font-mono bg-gray-100/70 px-1.5 py-0.5 rounded text-[10px]">
            L{finding.line}
          </span>
          {finding.code && (
            <code className="max-w-[70%] truncate font-mono bg-gray-100/70 px-1.5 py-0.5 rounded text-[10px] text-text-secondary border border-border/30">
              {finding.code.trim()}
            </code>
          )}
        </div>
      </button>
    </li>
  );
}
