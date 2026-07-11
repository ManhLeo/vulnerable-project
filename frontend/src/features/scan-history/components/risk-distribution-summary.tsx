import { SeverityBadge } from "@/features/scan-workspace/components/severity-badge";
import type { SeverityLevel } from "@/types/severity";
import { cn } from "@/lib/utils";

interface RiskDistributionSummaryProps {
  distribution: Record<SeverityLevel, number>;
}

export function RiskDistributionSummary({
  distribution,
}: RiskDistributionSummaryProps): JSX.Element {
  const total = Object.values(distribution).reduce((sum, val) => sum + val, 0);

  const severityColors: Record<SeverityLevel, string> = {
    CRITICAL: "bg-severity-critical",
    HIGH: "bg-severity-high",
    MEDIUM: "bg-severity-medium",
    LOW: "bg-severity-low",
  };

  return (
    <section className="rounded-lg border border-border bg-surface-panel p-4 shadow-sm" aria-label="Risk distribution">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Risk Distribution</h2>
        <span className="text-[10px] font-mono text-text-muted">
          {total} issues classified
        </span>
      </div>

      <div className="mt-4">
        {/* Horizontal Stacked Bar */}
        <div className="flex h-3 w-full rounded-full overflow-hidden bg-surface-elevated" role="img" aria-label="Stacked severity bar">
          {total === 0 ? (
            <div className="h-full w-full bg-surface-elevated" />
          ) : (
            (["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((severity) => {
              const count = distribution[severity] || 0;
              const percentage = total > 0 ? (count / total) * 100 : 0;
              if (count === 0) return null;

              return (
                <div
                  key={severity}
                  className={cn("h-full transition-all duration-300", severityColors[severity])}
                  style={{ width: `${percentage}%` }}
                  title={`${severity}: ${count} (${percentage.toFixed(0)}%)`}
                />
              );
            })
          )}
        </div>

        {/* Legend Grid */}
        <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((severity) => {
            const count = distribution[severity] || 0;
            const severityBorders: Record<SeverityLevel, string> = {
              CRITICAL: "border-l-severity-critical",
              HIGH: "border-l-severity-high",
              MEDIUM: "border-l-severity-medium",
              LOW: "border-l-severity-low",
            };
            return (
              <div
                key={severity}
                className={cn(
                  "flex items-center justify-between rounded-[4px] border border-border bg-surface-elevated p-2 border-l-[3px]",
                  severityBorders[severity],
                )}
              >
                <span className="text-[10px] font-semibold text-text-muted tracking-wide uppercase">
                  {severity}
                </span>
                <span className="font-mono text-xs font-bold text-text-primary">
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
