import { Badge } from "@/components/ui/badge";

export function TopbarStatus(): JSX.Element {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-border bg-surface-panel px-4 md:px-6">
      <div className="flex items-center gap-3">
        <p className="text-sm font-semibold text-text-primary">AI Security Platform</p>
        <span className="hidden text-xs text-text-muted sm:inline">Operational overview</span>
      </div>

      <div className="flex items-center gap-2">
        <Badge variant="neutral">Project: Active</Badge>
        <Badge variant="safe">Model: Online</Badge>
        <Badge variant="low">Scan Queue: 0</Badge>
      </div>
    </header>
  );
}
