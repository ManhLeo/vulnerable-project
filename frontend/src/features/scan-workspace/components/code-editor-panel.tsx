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
  isScanning?: boolean;
  onEditorMount?: (editor: unknown) => void;
}

export function CodeEditorPanel({
  language,
  code,
  onCodeChange,
  readonly = false,
  findings = [],
  selectedFindingIndex = null,
  isScanning = false,
  onEditorMount,
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
    <section className="min-w-0 rounded-xl border border-border bg-surface-panel p-3 shadow-sm md:p-4">
      <div className="mb-3 flex items-center justify-between gap-3 rounded-lg border border-border bg-surface-subtle px-3 py-2.5">
        <div className="min-w-0">
          <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-text-secondary">Source Code</h2>
          <p className="mt-1 text-[11px] text-text-muted">
            {isScanning ? "Scanning..." : readonly ? "Read-only while reviewing findings" : "Ready"}
          </p>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-text-muted">
          <span className="rounded-full border border-border bg-white px-2 py-0.5 font-medium uppercase text-text-primary">
            {language === "cpp" ? "C++" : "C"}
          </span>
          <span className="hidden sm:inline">{code.split("\n").length} lines</span>
          <span className="hidden md:inline">{code.length} chars</span>
        </div>
      </div>
      <MonacoEditor
        language={language}
        value={code}
        onChange={(value) => onCodeChange(value ?? "")}
        height="min(72vh, 760px)"
        readonly={readonly}
        decorations={decorations}
        revealLine={revealLine}
        onMount={(editor) => onEditorMount?.(editor)}
      />
    </section>
  );
}
