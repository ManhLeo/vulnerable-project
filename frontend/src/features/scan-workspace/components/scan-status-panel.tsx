"use client";

import type { AppApiError } from "@/lib/api/client";

interface ScanStatusPanelProps {
  isScanning: boolean;
  hasTriggeredScan: boolean;
  error: AppApiError | null;
}

export function ScanStatusPanel({
  isScanning,
  hasTriggeredScan,
  error,
}: ScanStatusPanelProps): JSX.Element {
  if (isScanning) {
    return (
      <div
        className="flex items-center gap-3 rounded-lg border border-border bg-white p-4 shadow-sm"
        role="status"
        aria-live="polite"
        aria-label="AI scan in progress"
      >
        {/* Spinner */}
        <svg
          className="h-4 w-4 shrink-0 animate-spin text-primary"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="3"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-text-primary">Scanning…</p>
          <p className="mt-0.5 text-[11px] text-text-muted">
            AI model is analyzing code for vulnerabilities.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="rounded-lg border border-severity-critical/25 bg-severityBg-critical p-4"
        role="alert"
        aria-live="assertive"
      >
        <div className="flex items-start gap-2">
          <svg
            className="mt-0.5 h-3.5 w-3.5 shrink-0 text-severity-critical"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
          <div className="min-w-0">
            <p className="text-xs font-semibold text-severity-critical">Scan request failed</p>
            <p className="mt-1 text-[11px] text-text-secondary leading-relaxed">{error.message}</p>
            {error.error_code && (
              <p className="mt-1 font-mono text-[10px] text-text-muted">
                Code: {error.error_code}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (!hasTriggeredScan) {
    return (
      <div
        className="rounded-lg border border-dashed border-border bg-white p-4"
        aria-label="Scan status: awaiting input"
      >
        <p className="text-xs font-semibold text-text-primary">Awaiting scan</p>
        <p className="mt-1 text-[11px] text-text-muted leading-relaxed">
          Paste code or upload a file, then press <span className="font-semibold text-text-secondary">Scan Code</span> to start analysis.
        </p>
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-2 rounded-lg border border-severity-safe/25 bg-severityBg-safe p-4"
      role="status"
    >
      <svg
        className="h-3.5 w-3.5 shrink-0 text-severity-safe"
        viewBox="0 0 24 24"
        fill="currentColor"
        aria-hidden="true"
      >
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
      </svg>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-severity-safe">Scan complete</p>
        <p className="mt-0.5 text-[11px] text-text-muted">
          Results are shown in the explainability panel.
        </p>
      </div>
    </div>
  );
}
