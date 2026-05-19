import { cn } from "@/lib/utils";
import type { ScanCodeResultDto } from "@/types/api";
import { SeverityBadge } from "@/features/scan-workspace/components/severity-badge";

interface RiskSummaryPanelProps {
  result: ScanCodeResultDto;
}

export function RiskSummaryPanel({ result }: RiskSummaryPanelProps): JSX.Element {
  const confidencePercentage = Math.round(result.confidence * 100);

  return (
    <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Security Profile</h3>
        <span className={cn(
          "inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide border",
          result.is_vulnerable
            ? "bg-severityBg-critical text-severity-critical border-severity-critical/20"
            : "bg-severityBg-safe text-severity-safe border-severity-safe/20"
        )}>
          {result.is_vulnerable ? "Vulnerable" : "Safe"}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider block">AI Confidence</span>
          <p className="font-mono text-lg font-bold text-text-primary">
            {confidencePercentage}%
          </p>
        </div>

        <div className="space-y-1">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider block">Overall Risk</span>
          <div className="flex items-center pt-0.5">
            <SeverityBadge severity={result.risk_level} />
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-border/40">
        <div className="mb-1.5 flex items-center justify-between text-xs">
          <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider">Confidence Gauge</span>
        </div>
        <div className="h-1.5 w-full rounded-full bg-gray-100">
          <div
            className={cn(
              "h-1.5 rounded-full transition-all duration-300",
              result.is_vulnerable ? "bg-severity-critical" : "bg-severity-safe"
            )}
            style={{ width: `${confidencePercentage}%` }}
            aria-label={`Confidence ${confidencePercentage}%`}
          />
        </div>
      </div>
    </section>
  );
}
