import { useEffect } from "react";
import type { UiFinding } from "@/lib/utils/findings";
import { FindingRow } from "@/features/scan-workspace/components/finding-row";

interface FindingsPanelProps {
  findings: UiFinding[];
  selectedFindingIndex: number | null;
  onSelectFinding: (index: number) => void;
  isVulnerable?: boolean;
}

export function FindingsPanel({
  findings,
  selectedFindingIndex,
  onSelectFinding,
  isVulnerable = false,
}: FindingsPanelProps): JSX.Element {
  // Arrow key navigation through findings
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (findings.length === 0 || selectedFindingIndex === null) return;

      const activeEl = document.activeElement;
      // Skip if user is actively writing inside an input, textarea or Monaco editor
      if (
        activeEl &&
        (activeEl.tagName === "INPUT" ||
          activeEl.tagName === "TEXTAREA" ||
          activeEl.closest(".monaco-editor"))
      ) {
        return;
      }

      if (e.key === "ArrowDown") {
        e.preventDefault();
        const nextIndex = (selectedFindingIndex + 1) % findings.length;
        onSelectFinding(nextIndex);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        const prevIndex = (selectedFindingIndex - 1 + findings.length) % findings.length;
        onSelectFinding(prevIndex);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [findings, selectedFindingIndex, onSelectFinding]);

  if (findings.length === 0) {
    return (
      <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Findings</h3>
        {isVulnerable ? (
          <p className="mt-3 rounded-[6px] border border-severity-high/20 bg-severityBg-high p-3 text-xs text-severity-high/90 leading-relaxed font-medium">
            Model flagged this scan as vulnerable, but no specific pattern-based matches were found.
          </p>
        ) : (
          <p className="mt-3 rounded-[6px] border border-severity-safe/20 bg-severityBg-safe p-3 text-xs text-severity-safe/90 leading-relaxed font-medium">
            No vulnerabilities detected. Your code looks secure.
          </p>
        )}
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-border bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between border-b border-border/60 pb-3">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Findings List</h3>
        <span className="text-[10px] font-mono font-medium text-text-muted">
          Use ↑ ↓ to navigate findings
        </span>
      </div>
      <ul className="mt-3 space-y-2 max-h-[420px] overflow-y-auto pr-1 scrollbar-thin">
        {findings.map((finding, index) => (
          <FindingRow
            key={finding.id}
            finding={finding}
            isSelected={selectedFindingIndex === index}
            onSelect={() => onSelectFinding(index)}
          />
        ))}
      </ul>
    </section>
  );
}
