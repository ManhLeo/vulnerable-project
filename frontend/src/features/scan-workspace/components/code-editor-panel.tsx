"use client";

import { MonacoEditor, type MonacoFindingDecoration } from "@/components/editor/monaco-editor";
import type { UiFinding } from "@/lib/utils/findings";

interface CodeEditorPanelProps {
  language: string;
  code: string;
  onCodeChange: (value: string) => void;
  readonly?: boolean;
  findings?: UiFinding[];
  selectedFindingIndex?: number | null;
}

export function CodeEditorPanel({
  language,
  code,
  onCodeChange,
  readonly = false,
  findings = [],
  selectedFindingIndex = null,
}: CodeEditorPanelProps): JSX.Element {
  const decorations: MonacoFindingDecoration[] = findings.map((finding, index) => ({
    line: finding.line,
    severity: finding.severity,
    hoverMessage: `${finding.severity}: ${finding.issue}`,
    isSelected: selectedFindingIndex === index,
  }));

  const revealLine =
    selectedFindingIndex !== null && findings[selectedFindingIndex]
      ? findings[selectedFindingIndex].line
      : null;

  return (
    <section className="rounded-lg border border-border bg-surface-panel p-3 shadow-sm md:p-4">
      <div className="mb-2 flex items-center justify-between gap-2">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-text-secondary">Code workspace</h2>
        <span className="text-[11px] text-text-muted">
          {readonly ? "Read-only while reviewing findings" : "Editable"}
        </span>
      </div>
      <MonacoEditor
        language={language}
        value={code}
        onChange={(value) => onCodeChange(value ?? "")}
        height="min(68vh, 640px)"
        readonly={readonly}
        decorations={decorations}
        revealLine={revealLine}
      />
    </section>
  );
}
