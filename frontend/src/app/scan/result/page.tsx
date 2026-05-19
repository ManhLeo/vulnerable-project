"use client";

import { useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useScanStore } from "@/lib/store/scan-store";
import { normalizeFindings } from "@/lib/utils/findings";
import { CodeEditorPanel } from "@/features/scan-workspace/components/code-editor-panel";
import { FindingsCountSummary } from "@/features/scan-workspace/components/findings-count-summary";
import { FindingsPanel } from "@/features/scan-workspace/components/findings-panel";
import { RiskSummaryPanel } from "@/features/scan-workspace/components/risk-summary-panel";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function ScanResultPage(): JSX.Element {
  const router = useRouter();
  const {
    code,
    language,
    latestResult: scanResult,
    selectedFindingIndex,
    setSelectedFindingIndex,
  } = useScanStore();

  const findings = useMemo(() => normalizeFindings(scanResult?.findings), [scanResult?.findings]);

  useEffect(() => {
    if (findings.length === 0) {
      setSelectedFindingIndex(null);
      return;
    }
    setSelectedFindingIndex(0);
  }, [findings, setSelectedFindingIndex]);

  if (!scanResult) {
    return (
      <div className="space-y-6">
        <section className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight">Scan Result</h1>
          <p className="text-sm text-muted-foreground">
            View detailed vulnerability scan insights and code-level explainability.
          </p>
        </section>

        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface-panel p-12 text-center">
          <h3 className="text-lg font-semibold text-text-primary">No results loaded</h3>
          <p className="mt-2 text-sm text-text-muted max-w-sm">
            Please run a new vulnerability scan from the workspace or select a historical record from the history page.
          </p>
          <div className="mt-6 flex gap-3">
            <Button onClick={() => router.push("/")} variant="primary">
              Go to Workspace
            </Button>
            <Button onClick={() => router.push("/scan/history")} variant="secondary">
              View Scan History
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Scan Analysis Report</h1>
          <p className="text-sm text-text-muted">
            Code-level security audit for language: <span className="font-semibold text-primary">{language.toUpperCase()}</span>
          </p>
        </div>
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={() => router.back()}
          className="self-start sm:self-auto"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      </section>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.9fr)_minmax(320px,1fr)]">
        <div className="space-y-4">
          <CodeEditorPanel
            language={language}
            code={code}
            onCodeChange={() => {}}
            readonly={true}
            findings={findings}
            selectedFindingIndex={selectedFindingIndex}
          />
        </div>

        <aside className="space-y-4">
          <div className="space-y-4">
            <RiskSummaryPanel result={scanResult} />
            <FindingsCountSummary findings={findings} />
            <FindingsPanel
              findings={findings}
              selectedFindingIndex={selectedFindingIndex}
              onSelectFinding={setSelectedFindingIndex}
              isVulnerable={scanResult.is_vulnerable}
            />
          </div>
        </aside>
      </div>
    </div>
  );
}
