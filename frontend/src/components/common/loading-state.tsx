import type { ReactNode } from "react";

interface LoadingStateProps {
  title?: string;
  description?: string;
  actionSlot?: ReactNode;
}

export function LoadingState({
  title = "Loading…",
  description = "Please wait while data is being prepared.",
  actionSlot,
}: LoadingStateProps): JSX.Element {
  return (
    <section
      className="w-full rounded-lg border border-border bg-white p-5 shadow-sm"
      aria-live="polite"
      aria-busy="true"
      aria-label={title}
    >
      <div className="flex items-start gap-3">
        {/* Inline spinner */}
        <svg
          className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-primary"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <circle
            className="opacity-20"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="3"
          />
          <path
            className="opacity-80"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>

        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold text-text-primary">{title}</p>
          <p className="mt-0.5 text-[11px] text-text-muted leading-relaxed">{description}</p>

          {/* Shimmer skeleton rows */}
          <div className="mt-4 space-y-2" aria-hidden="true">
            <div className="h-2.5 w-2/3 rounded animate-pulse bg-gray-100" />
            <div className="h-2.5 w-1/2 rounded animate-pulse bg-gray-100" />
            <div className="h-2.5 w-5/6 rounded animate-pulse bg-gray-100" />
          </div>
        </div>

        {actionSlot ? (
          <div className="shrink-0">{actionSlot}</div>
        ) : null}
      </div>
    </section>
  );
}
