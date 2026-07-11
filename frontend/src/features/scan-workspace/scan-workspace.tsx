"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { FileCode, Radar, RotateCcw, ShieldAlert } from "lucide-react";

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
import { useAuth } from "@/hooks/useAuth";
import type { ScanCodeRequestDto } from "@/types/api";

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
    prepareForNewScan,
    resetWorkspace,
  } = useScanStore();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedModelValue, setSelectedModelValue] = useState<string>("");
  const [uploadResetSignal, setUploadResetSignal] = useState(0);
  const editorRef = useRef<any>(null);

  const codeScanMutation = useScanCodeMutation();
  const fileScanMutation = useScanFileMutation();
  const { user, isLoading: isAuthLoading } = useAuth();

  const isGuest = !isAuthLoading && !user;
  const isScanning = codeScanMutation.isLoading || fileScanMutation.isLoading;
  const canSelectRequestModel = Boolean(user) && !isAuthLoading;
  const resultUsesAi = scanResult?.metadata?.inference_used !== false;
  const previousRoleRef = useRef<string | null>(null);

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

  useEffect(() => {
    if (isAuthLoading) {
      return;
    }

    const currentRole = user?.role ?? "guest";
    if (previousRoleRef.current === null) {
      previousRoleRef.current = currentRole;
      return;
    }

    if (previousRoleRef.current !== currentRole) {
      codeScanMutation.reset();
      fileScanMutation.reset();
      setSelectedFile(null);
      setSelectedModelValue("");
      setUploadResetSignal((value) => value + 1);
      resetWorkspace();
      previousRoleRef.current = currentRole;
    }
  }, [codeScanMutation, fileScanMutation, isAuthLoading, resetWorkspace, user?.role]);

  const handleScanCode = (): void => {
    if (!code.trim() || isScanning) {
      return;
    }

    setHasTriggeredScan(true);
    const modelPayload =
      canSelectRequestModel && selectedModelValue === "__ensemble_best_confidence__"
        ? {
            model_mode: "best_confidence" as ScanCodeRequestDto["model_mode"],
            checkpoint_names: ["best_codebert_linevul.pt", "best_graphcodebert_linevul.pt"],
          }
        : canSelectRequestModel && selectedModelValue
          ? {
              checkpoint_name: selectedModelValue,
            }
          : {};

    codeScanMutation.mutate(
      {
        source_code: code,
        language,
        ...modelPayload,
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
    const modelPayload =
      canSelectRequestModel && selectedModelValue === "__ensemble_best_confidence__"
        ? {
            model_mode: "best_confidence" as const,
            checkpoint_names: ["best_codebert_linevul.pt", "best_graphcodebert_linevul.pt"],
          }
        : canSelectRequestModel && selectedModelValue
          ? {
              checkpoint_name: selectedModelValue,
            }
          : {};

    fileScanMutation.mutate({
      file: selectedFile,
      language,
      ...modelPayload,
    }, {
      onSuccess: (res) => {
        setLatestResult(res.data);
      },
    });
  };

  const disableCodeScan = isScanning || code.trim().length === 0;
  const disableFileScan = isScanning || !selectedFile;
  const showNewScan = !isScanning && (Boolean(scanResult) || Boolean(mergedError) || hasTriggeredScan);

  const showExplainability = Boolean(scanResult) && !isScanning;

  const handleNewScan = (): void => {
    codeScanMutation.reset();
    fileScanMutation.reset();
    setSelectedFile(null);
    setUploadResetSignal((value) => value + 1);
    prepareForNewScan(true);
    window.requestAnimationFrame(() => {
      editorRef.current?.focus?.();
    });
  };

  return (
    <div className="space-y-4">
      <section className="flex flex-col gap-2 border-b border-border pb-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-primary">Vulnerable Scanner</p>
          <h1 className="mt-1 text-2xl font-semibold text-text-primary">Security Analysis Workspace</h1>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <Radar className="h-4 w-4 text-primary" />
          <span>{isScanning ? "Analysis pipeline running" : "Ready for code inspection"}</span>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[300px_minmax(0,1fr)_360px]">
        <aside className="space-y-4 rounded-lg border border-border bg-surface-panel p-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <ShieldAlert className="h-4 w-4 text-primary" />
            <h2 className="text-sm font-semibold text-text-primary">Scan Control</h2>
          </div>
          <LanguageSelector value={language} onChange={setLanguage} disabled={isScanning} />
          {isGuest ? (
            <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-text-muted">
              <p className="font-semibold text-primary">Findings Metrics Only</p>
              <p className="mt-1 leading-relaxed">
              Guest use the Findings Metrics mode. Log in to perform combined AI model analysis.
              </p>
            </div>
          ) : null}
          {canSelectRequestModel ? (
            <ModelSelector
              mode="request"
              disabled={isScanning}
              value={selectedModelValue}
              onChange={setSelectedModelValue}
            />
          ) : null}
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
                  // Keep the current editor content if local file reading fails.
                }
              })();
            }}
            disabled={isScanning}
            selectedFileName={selectedFile?.name}
            resetSignal={uploadResetSignal}
          />
          <ScanActions
            onScanCode={handleScanCode}
            onScanFile={handleScanFile}
            onNewScan={handleNewScan}
            disableCodeScan={disableCodeScan}
            disableFileScan={disableFileScan}
            isScanning={isScanning}
            showNewScan={showNewScan}
          />
          <div className="rounded-lg border border-border bg-surface-subtle p-3 text-xs text-text-muted">
            <div className="flex items-center gap-2 text-text-secondary">
              <FileCode className="h-4 w-4" />
              <span className="font-semibold">Accepted files</span>
            </div>
            <p className="mt-2 font-mono text-[11px]">.c .cpp .h .hpp</p>
          </div>
        </aside>

        <CodeEditorPanel
          language={language}
          code={code}
          onCodeChange={setCode}
          readonly={showExplainability}
          findings={findings}
          selectedFindingIndex={selectedFindingIndex}
          isScanning={isScanning}
          onEditorMount={(editor) => {
            editorRef.current = editor;
          }}
        />

        <aside className="space-y-4">
          <ScanStatusPanel
            isScanning={isScanning}
            hasTriggeredScan={hasTriggeredScan}
            error={mergedError}
            usesAiInference={!isGuest}
          />

          {showExplainability && scanResult ? (
            <>
              {resultUsesAi ? (
                <section className="rounded-lg border border-primary/20 bg-primary/5 p-4 shadow-sm">
                  <h3 className="text-sm font-semibold text-primary">Metrics + AI Model</h3>
                  <p className="mt-1 text-xs text-text-muted">
                    This result combines Findings Metrics with AI model inference.
                  </p>
                </section>
              ) : (
                <section className="rounded-lg border border-primary/20 bg-primary/5 p-4 shadow-sm">
                  <h3 className="text-sm font-semibold text-primary">Findings Metrics Only</h3>
                  <p className="mt-1 text-xs text-text-muted">
                  This result was generated from available static indicators/detections, without using an AI model.
                  </p>
                </section>
              )}
              <section className="rounded-lg border border-border bg-surface-panel p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-semibold text-text-primary">Scan complete</h3>
                    <p className="mt-1 text-xs text-text-muted">Review findings below or reset the workspace for another sample.</p>
                  </div>
                  <button
                    type="button"
                    onClick={handleNewScan}
                    className="inline-flex items-center gap-2 rounded-md border border-border bg-surface-elevated px-3 py-2 text-xs font-semibold text-text-secondary transition hover:bg-surface-subtle hover:text-text-primary"
                  >
                    <RotateCcw className="h-4 w-4" />
                    New Scan
                  </button>
                </div>
              </section>
              <RiskSummaryPanel result={scanResult} />
              <FindingsCountSummary findings={findings} />
              <FindingsPanel
                findings={findings}
                selectedFindingIndex={selectedFindingIndex}
                onSelectFinding={setSelectedFindingIndex}
                isVulnerable={scanResult.is_vulnerable}
              />
            </>
          ) : (
            <section className="rounded-lg border border-dashed border-border bg-surface-panel p-5">
              <h3 className="text-sm font-semibold text-text-primary">No scan result yet</h3>
              <p className="mt-2 text-xs leading-relaxed text-text-muted">
                {isGuest
                  ? "Paste C/C++ source code or upload a file to start Findings Metrics analysis."
                  : "Paste C/C++ source code or upload a file to start vulnerability analysis."}
              </p>
              {mergedError ? (
                <button
                  type="button"
                  onClick={handleNewScan}
                  className="mt-4 inline-flex items-center gap-2 rounded-md border border-border bg-surface-elevated px-3 py-2 text-xs font-semibold text-text-secondary transition hover:bg-surface-subtle hover:text-text-primary"
                >
                  <RotateCcw className="h-4 w-4" />
                  New Scan
                </button>
              ) : null}
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}
