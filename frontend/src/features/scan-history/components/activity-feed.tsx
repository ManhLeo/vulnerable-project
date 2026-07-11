import type { ScanHistoryItemDto } from "@/types/api";
import { cn } from "@/lib/utils";

interface ActivityFeedProps {
  items: ScanHistoryItemDto[];
}

export function ActivityFeed({ items }: ActivityFeedProps): JSX.Element {
  const severityDotColors: Record<string, string> = {
    CRITICAL: "bg-severity-critical ring-severity-critical/20",
    HIGH: "bg-severity-high ring-severity-high/20",
    MEDIUM: "bg-severity-medium ring-severity-medium/20",
    LOW: "bg-severity-low ring-severity-low/20",
    SAFE: "bg-severity-safe ring-severity-safe/20",
  };

  return (
    <section className="rounded-lg border border-border bg-surface-panel p-4 shadow-sm" aria-label="Activity feed">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Security Activity Feed</h2>
        <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
      </div>

      {items.length === 0 ? (
        <p className="mt-4 text-xs text-text-muted text-center py-4">No recent activity.</p>
      ) : (
        <div className="mt-4 relative pl-4 border-l border-border space-y-4">
          {items.map((item) => {
            const dotColor = severityDotColors[item.risk_level] || "bg-gray-400";
            return (
              <div key={item.id} className="relative group">
                {/* Timeline Connector Bullet */}
                <div
                  className={cn(
                    "absolute -left-[21px] top-1.5 h-2.5 w-2.5 rounded-full ring-4 transition-all duration-300",
                    dotColor,
                  )}
                />

                <div className="flex flex-col gap-1">
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <span className="font-semibold text-text-primary group-hover:text-primary transition-colors truncate max-w-[150px]">
                      {item.filename ?? "Untitled source"}
                    </span>
                    <span className="font-mono text-[10px] text-text-muted">
                      {new Date(item.created_at).toLocaleTimeString(undefined, {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                      })}
                    </span>
                  </div>
                  <p className="text-[11px] text-text-secondary leading-relaxed">
                    AI Scan completed on <span className="font-semibold text-text-primary uppercase">{item.language}</span> code. Risk evaluated as <span className="font-medium text-text-primary">{item.risk_level}</span> (confidence {(item.confidence * 100).toFixed(0)}%).
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
