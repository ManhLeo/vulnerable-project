import { cn } from "@/lib/utils";
import { countBySeverity, type UiFinding } from "@/lib/utils/findings";

interface FindingsCountSummaryProps {
  findings: UiFinding[];
}

export function FindingsCountSummary({ findings }: FindingsCountSummaryProps): JSX.Element {
  const counts = countBySeverity(findings);

  const severityColors: Record<string, string> = {
    CRITICAL: "border-l-severity-critical",
    HIGH: "border-l-severity-high",
    MEDIUM: "border-l-severity-medium",
    LOW: "border-l-severity-low",
  };

  return (
    <section className="rounded-lg border border-border bg-surface-panel p-4 shadow-sm">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Findings Metrics</h3>
        <span className="font-mono text-xs font-semibold bg-surface-elevated px-2 py-0.5 rounded text-text-secondary">
          {findings.length} Total
        </span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((severity) => (
          <div
            key={severity}
            className={cn(
              "flex items-center justify-between rounded-[4px] border border-border bg-surface-elevated p-2 border-l-[3px]",
              severityColors[severity],
            )}
          >
            <span className="text-[10px] font-semibold text-text-muted tracking-wide uppercase">
              {severity}
            </span>
            <span className="font-mono text-xs font-bold text-text-primary">
              {counts[severity]}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
