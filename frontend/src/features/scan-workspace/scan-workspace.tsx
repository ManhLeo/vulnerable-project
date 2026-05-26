"use client";

import { useEffect, useMemo, useState } from "react";

import type { AppApiError } from "@/lib/api/client";
import { normalizeFindings } from "@/lib/utils/findings";
import { useScanCodeMutation } from "@/hooks/use-scan-code-mutation";
import { useScanFileMutation } from "@/hooks/use-scan-file-mutation";
import { CodeEditorPanel } from "@/features/scan-workspace/components/code-editor-panel";
import { FindingsCountSummary } from "@/features/scan-workspace/components/findings-count-summary";
import { FindingsPanel } from "@/features/scan-workspace/components/findings-panel";
import { LanguageSelector } from "@/features/scan-workspace/components/language-selector";
import { ModelSelector } from "@/features/scan-workspace/components/model-selector";
import { RiskSummaryPanel } from "@/features/scan-workspace/components/risk-summary-panel";
import { ScanActions } from "@/features/scan-workspace/components/scan-actions";
import { ScanStatusPanel } from "@/features/scan-workspace/components/scan-status-panel";
import { UploadPanel } from "@/features/scan-workspace/components/upload-panel";
import { useScanStore } from "@/lib/store/scan-store";

export function ScanWorkspace(): JSX.Element {
  const {
    code,
    language,
    latestResult: scanResult,
    selectedFindingIndex,
    hasTriggeredScan,
    setCode,
    setLanguage,
    setLatestResult,
    setSelectedFindingIndex,
    setHasTriggeredScan,
  } = useScanStore();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const codeScanMutation = useScanCodeMutation();
  const fileScanMutation = useScanFileMutation();

  const isScanning = codeScanMutation.isLoading || fileScanMutation.isLoading;

  const mergedError: AppApiError | null = useMemo(() => {
    return codeScanMutation.error ?? fileScanMutation.error ?? null;
  }, [codeScanMutation.error, fileScanMutation.error]);

  const findings = useMemo(() => normalizeFindings(scanResult?.findings), [scanResult?.findings]);

  useEffect(() => {
    if (findings.length === 0) {
      setSelectedFindingIndex(null);
      return;
    }

    setSelectedFindingIndex(0);
  }, [findings, setSelectedFindingIndex]);

  const handleScanCode = (): void => {
    if (!code.trim() || isScanning) {
      return;
    }

    setHasTriggeredScan(true);
    codeScanMutation.mutate(
      {
        code,
        language,
      },
      {
        onSuccess: (res) => {
          setLatestResult(res.data);
        },
      }
    );
  };

  const handleScanFile = (): void => {
    if (!selectedFile || isScanning) {
      return;
    }

    setHasTriggeredScan(true);
    fileScanMutation.mutate(selectedFile, {
      onSuccess: (res) => {
        setLatestResult(res.data);
      },
    });
  };

  const disableCodeScan = isScanning || code.trim().length === 0;
  const disableFileScan = isScanning || !selectedFile;

  const showExplainability = Boolean(scanResult) && !isScanning;

  return (
    <div className="space-y-5">
      <section className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight text-text-primary md:text-2xl">Scan Workspace</h1>
        <p className="text-sm text-text-muted">
          Analyze pasted code or uploaded files in a focused Monaco-first security workflow.
        </p>
      </section>

      <section className="sticky top-14 z-20 rounded-lg border border-border bg-surface-panel/95 p-3 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-surface-panel/85">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)_minmax(0,1.2fr)_auto] md:items-end">
          <LanguageSelector value={language} onChange={setLanguage} disabled={isScanning} />
          <ModelSelector disabled={isScanning} />
          <UploadPanel
            onFileChange={(nextFile) => {
              setSelectedFile(nextFile);
              if (!nextFile) {
                return;
              }

              void (async () => {
                try {
                  const text = await nextFile.text();
                  setCode(text);
                  setLatestResult(null);
                  setHasTriggeredScan(false);
                  setSelectedFindingIndex(null);
                } catch {
                  // If we cannot read file content, keep current code.
                }
              })();
            }}
            disabled={isScanning}
            selectedFileName={selectedFile?.name}
          />
          <div className="md:w-[220px]">
            <ScanActions
              onScanCode={handleScanCode}
              onScanFile={handleScanFile}
              disableCodeScan={disableCodeScan}
              disableFileScan={disableFileScan}
              isScanning={isScanning}
            />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.9fr)_minmax(320px,1fr)]">
        <div className="space-y-4">
          <CodeEditorPanel
            language={language}
            code={code}
            onCodeChange={setCode}
            readonly={showExplainability}
            findings={findings}
            selectedFindingIndex={selectedFindingIndex}
          />
        </div>

        <aside className="space-y-4">
          <ScanStatusPanel
            isScanning={isScanning}
            hasTriggeredScan={hasTriggeredScan}
            error={mergedError}
          />

          {showExplainability && scanResult ? (
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
          ) : (
            <section className="rounded-lg border border-dashed border-border bg-surface-panel p-4">
              <h3 className="text-sm font-semibold text-text-primary">Findings overview</h3>
              <p className="mt-1 text-xs text-text-muted">
                Run a scan to populate risk summary and detailed findings for this workspace.
              </p>
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}
