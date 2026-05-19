import type { ReactNode } from "react";

interface ErrorStateProps {
  title?: string;
  message: string;
  errorCode?: string;
  actionSlot?: ReactNode;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  errorCode,
  actionSlot,
}: ErrorStateProps): JSX.Element {
  return (
    <section
      className="w-full rounded-lg border border-severity-critical/25 bg-severityBg-critical p-5 shadow-sm"
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        {/* Error icon */}
        <svg
          className="mt-0.5 h-4 w-4 shrink-0 text-severity-critical"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
        </svg>

        <div className="min-w-0 flex-1 space-y-1">
          <h2 className="text-sm font-semibold text-severity-critical leading-snug">{title}</h2>
          <p className="text-xs text-text-secondary leading-relaxed">{message}</p>
          {errorCode ? (
            <p className="font-mono text-[10px] text-text-muted">
              Error code: {errorCode}
            </p>
          ) : null}
        </div>

        {actionSlot ? (
          <div className="shrink-0">{actionSlot}</div>
        ) : null}
      </div>
    </section>
  );
}
