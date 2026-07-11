import { cn } from "@/lib/utils";
import { formatConfidence } from "@/lib/utils/findings";
import type { ScanCodeResultDto } from "@/types/api";
import { SeverityBadge } from "@/features/scan-workspace/components/severity-badge";

interface RiskSummaryPanelProps {
  result: ScanCodeResultDto;
}

export function RiskSummaryPanel({ result }: RiskSummaryPanelProps): JSX.Element {
  const confidenceValue = result.confidence <= 1 ? result.confidence * 100 : result.confidence;
  const confidencePercentage = Math.max(0, Math.min(100, Math.round(confidenceValue)));

  return (
    <section className="rounded-lg border border-border bg-surface-panel p-4 shadow-sm">
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
            {formatConfidence(result.confidence)}
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
        <div className="h-1.5 w-full rounded-full bg-surface-elevated">
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

      {result.metadata?.selected_checkpoint ? (
        <div className="mt-4 space-y-2 border-t border-border/40 pt-3">
          <div className="grid grid-cols-2 gap-3 text-[11px]">
            <div>
              <span className="block font-semibold uppercase tracking-wide text-text-muted">Mode</span>
              <span className="text-text-secondary">
                {result.metadata.model_mode === "best_confidence" ? "Best Confidence Ensemble" : "Single"}
              </span>
            </div>
            <div>
              <span className="block font-semibold uppercase tracking-wide text-text-muted">Model used</span>
              <span className="font-mono text-text-secondary">{result.metadata.selected_checkpoint}</span>
            </div>
          </div>
          {result.metadata.candidate_results && result.metadata.candidate_results.length > 0 ? (
            <div className="space-y-2">
              <span className="block text-[10px] font-semibold uppercase tracking-wide text-text-muted">Candidate results</span>
              <div className="space-y-2">
                {result.metadata.candidate_results.map((candidate) => (
                  <div
                    key={candidate.checkpoint_name}
                    className="rounded-md border border-border bg-surface-elevated px-3 py-2 text-[11px] text-text-secondary"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono">{candidate.checkpoint_name}</span>
                      <span>{formatConfidence(candidate.confidence)}</span>
                    </div>
                    <div className="mt-1 flex items-center justify-between gap-2 text-text-muted">
                      <span>{candidate.risk_level ?? "UNKNOWN"}</span>
                      <span>{candidate.is_vulnerable ? "Vulnerable" : "Safe"}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
