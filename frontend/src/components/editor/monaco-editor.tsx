"use client";

import dynamic from "next/dynamic";
import type { ComponentProps } from "react";
import { useCallback, useEffect, useMemo, useRef } from "react";

import type { SeverityLevel } from "@/types/severity";

const MonacoEditorNoSSR = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[320px] w-full items-center justify-center rounded-md border border-border bg-surface-subtle text-sm text-text-muted">
      Loading editor...
    </div>
  ),
});

export interface MonacoFindingDecoration {
  line: number;
  severity: SeverityLevel;
  hoverMessage: string;
  isSelected?: boolean;
}

type MonacoEditorProps = Omit<ComponentProps<typeof MonacoEditorNoSSR>, "options"> & {
  height?: string | number;
  readonly?: boolean;
  decorations?: MonacoFindingDecoration[];
  revealLine?: number | null;
};

function severityClassName(severity: SeverityLevel): string {
  if (severity === "CRITICAL") return "finding-line-critical";
  if (severity === "HIGH") return "finding-line-high";
  if (severity === "MEDIUM") return "finding-line-medium";
  return "finding-line-low";
}

function severityGlyphClassName(severity: SeverityLevel): string {
  if (severity === "CRITICAL") return "finding-glyph-critical";
  if (severity === "HIGH") return "finding-glyph-high";
  if (severity === "MEDIUM") return "finding-glyph-medium";
  return "finding-glyph-low";
}

export function MonacoEditor({
  height = "320px",
  readonly = false,
  decorations = [],
  revealLine = null,
  onMount,
  ...props
}: MonacoEditorProps): JSX.Element {
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationIdsRef = useRef<string[]>([]);

  const handleBeforeMount = useCallback((monaco: any) => {
    monaco.editor.defineTheme("vulnerable-scanner-light", {
      base: "vs",
      inherit: true,
      rules: [
        { token: "", foreground: "111827", background: "FFFFFF" },
        { token: "comment", foreground: "64748B" },
        { token: "string", foreground: "047857" },
        { token: "keyword", foreground: "2563EB" },
        { token: "number", foreground: "B45309" },
      ],
      colors: {
        "editor.background": "#FFFFFF",
        "editor.foreground": "#111827",
        "editorLineNumber.foreground": "#94A3B8",
        "editorLineNumber.activeForeground": "#334155",
        "editor.selectionBackground": "#2563EB24",
        "editor.inactiveSelectionBackground": "#2563EB14",
        "editor.lineHighlightBackground": "#F8FAFC",
        "editorLineHighlightBackground": "#F8FAFC",
        "editorCursor.foreground": "#2563EB",
        "editorIndentGuide.background1": "#E5E7EB",
        "editorIndentGuide.activeBackground1": "#CBD5E1",
      },
    });
  }, []);

  const editorOptions = useMemo(
    () => ({
      minimap: { enabled: false },
      fontSize: 14,
      lineNumbers: "on" as const,
      scrollBeyondLastLine: false,
      automaticLayout: true,
      readOnly: readonly,
      glyphMargin: true,
      roundedSelection: true,
      renderLineHighlight: "all" as const,
      wordWrap: "on" as const,
      tabSize: 2,
      fontFamily: "JetBrains Mono, Geist Mono, Consolas, monospace",
      lineHeight: 22,
      padding: { top: 10, bottom: 10 },
      smoothScrolling: true,
    }),
    [readonly],
  );

  const decorationPayload = useMemo(
    () =>
      decorations.map((item) => ({
        range: {
          startLineNumber: item.line,
          startColumn: 1,
          endLineNumber: item.line,
          endColumn: 1,
        },
        options: {
          isWholeLine: true,
          className: `${severityClassName(item.severity)} ${item.isSelected ? "finding-line-selected" : ""}`.trim(),
          glyphMarginClassName: severityGlyphClassName(item.severity),
          glyphMarginHoverMessage: { value: item.hoverMessage },
          linesDecorationsClassName: severityClassName(item.severity),
        },
      })),
    [decorations],
  );

  const applyDecorations = useCallback(() => {
    if (!editorRef.current || !monacoRef.current) return;

    decorationIdsRef.current = editorRef.current.deltaDecorations(
      decorationIdsRef.current,
      decorationPayload.map((item: any) => ({
        range: new monacoRef.current.Range(
          item.range.startLineNumber,
          item.range.startColumn,
          item.range.endLineNumber,
          item.range.endColumn,
        ),
        options: item.options,
      })),
    );
  }, [decorationPayload]);

  useEffect(() => {
    applyDecorations();
  }, [applyDecorations]);

  useEffect(() => {
    if (!editorRef.current || !revealLine) return;
    editorRef.current.revealLineInCenter(revealLine);
    editorRef.current.setPosition({ lineNumber: revealLine, column: 1 });
    editorRef.current.focus();
  }, [revealLine]);

  const handleMount = useCallback(
    (editor: unknown, monaco: unknown) => {
      editorRef.current = editor;
      monacoRef.current = monaco;
      applyDecorations();
      onMount?.(editor as never, monaco as never);
    },
    [applyDecorations, onMount],
  );

  return (
    <div className="w-full overflow-hidden rounded-md border border-border bg-surface-panel transition-colors focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/15">
      <style jsx global>{`
        .finding-line-critical {
          background: rgba(239, 68, 68, 0.16) !important;
        }
        .finding-line-high {
          background: rgba(239, 68, 68, 0.12) !important;
        }
        .finding-line-medium {
          background: rgba(56, 189, 248, 0.1) !important;
        }
        .finding-line-low {
          background: rgba(56, 189, 248, 0.08) !important;
        }
        .finding-line-selected {
          background: rgba(56, 189, 248, 0.18) !important;
          box-shadow: inset 3px 0 0 0 #38bdf8 !important;
        }
        .finding-glyph-critical {
          background: #dc2626;
          width: 8px !important;
          height: 8px !important;
          margin-top: 6px;
          margin-left: 4px;
          border-radius: 999px;
        }
        .finding-glyph-high {
          background: #ea580c;
          width: 8px !important;
          height: 8px !important;
          margin-top: 6px;
          margin-left: 4px;
          border-radius: 999px;
        }
        .finding-glyph-medium {
          background: #d97706;
          width: 8px !important;
          height: 8px !important;
          margin-top: 6px;
          margin-left: 4px;
          border-radius: 999px;
        }
        .finding-glyph-low {
          background: #2563eb;
          width: 8px !important;
          height: 8px !important;
          margin-top: 6px;
          margin-left: 4px;
          border-radius: 999px;
        }
      `}</style>

      <MonacoEditorNoSSR
        height={height}
        beforeMount={handleBeforeMount}
        theme="vulnerable-scanner-light"
        options={editorOptions}
        onMount={handleMount}
        {...props}
      />
    </div>
  );
}
