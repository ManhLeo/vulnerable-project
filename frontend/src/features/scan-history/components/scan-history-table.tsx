import { useState } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { SeverityBadge } from "@/features/scan-workspace/components/severity-badge";
import type { ScanHistoryItemDto } from "@/types/api";
import { getScanRecord } from "@/services/scan.service";
import { useScanStore } from "@/lib/store/scan-store";
import type { AppApiError } from "@/lib/api/client";

interface ScanHistoryTableProps {
  items: ScanHistoryItemDto[];
  isLoading?: boolean;
}

const SKELETON_ROWS = 8;

function toScanLanguage(value: string): "c" | "cpp" {
  return value === "c" ? "c" : "cpp";
}

function SkeletonRows(): JSX.Element {
  return (
    <>
      {Array.from({ length: SKELETON_ROWS }).map((_, i) => (
        <tr key={i} className="border-t border-border animate-pulse">
          <td className="px-4 py-3">
            <div className="h-3 w-36 rounded bg-surface-elevated" />
          </td>
          <td className="px-4 py-3">
            <div className="h-5 w-12 rounded bg-surface-elevated" />
          </td>
          <td className="px-4 py-3">
            <div className="h-5 w-16 rounded-full bg-surface-elevated" />
          </td>
          <td className="px-4 py-3">
            <div className="h-5 w-14 rounded-full bg-surface-elevated" />
          </td>
          <td className="px-4 py-3">
            <div className="h-3 w-10 rounded bg-surface-elevated" />
          </td>
          <td className="px-4 py-3">
            <div className="h-3 w-28 rounded bg-surface-elevated" />
          </td>
          <td className="px-4 py-3 text-right">
            <div className="ml-auto h-3 w-12 rounded bg-surface-elevated" />
          </td>
        </tr>
      ))}
    </>
  );
}

export function ScanHistoryTable({
  items,
  isLoading = false,
}: ScanHistoryTableProps): JSX.Element {
  const router = useRouter();
  const { setLatestResult, setCode, setLanguage } = useScanStore();
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<AppApiError | null>(null);

  const handleRowClick = async (id: string) => {
    if (loadingId) return;
    setLoadingId(id);
    setDetailError(null);
    try {
      const res = await getScanRecord(id);
      if (res.status === "success") {
        setLatestResult({
          scan_id: res.data.scan_id,
          is_vulnerable: res.data.is_vulnerable,
          confidence: res.data.confidence,
          risk_level: res.data.risk_level,
          findings: res.data.findings,
          metadata: res.data.metadata,
        });
        setCode(res.data.source_code);
        setLanguage(toScanLanguage(res.data.language));
        router.push("/scan/result");
      }
    } catch (err) {
      const appError = err as AppApiError;
      setDetailError(appError);
    } finally {
      setLoadingId(null);
    }
  };

  const thClass =
    "sticky top-0 z-10 bg-surface-elevated px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider text-text-muted border-b border-border whitespace-nowrap";

  return (
    <section
      className="rounded-lg border border-border bg-surface-panel shadow-sm overflow-hidden"
      aria-label="Scan history results"
    >
      {detailError ? (
        <div className="border-b border-severity-critical/20 bg-severityBg-critical px-4 py-3" role="alert">
          <p className="text-xs font-semibold text-severity-critical">Unable to open scan detail</p>
          <p className="mt-1 text-[11px] text-text-secondary">{detailError.message}</p>
          <p className="mt-1 font-mono text-[10px] text-text-muted">Code: {detailError.error_code}</p>
        </div>
      ) : null}
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr>
              <th scope="col" className={thClass}>Filename</th>
              <th scope="col" className={thClass}>Language</th>
              <th scope="col" className={thClass}>Risk</th>
              <th scope="col" className={thClass}>Status</th>
              <th scope="col" className={thClass}>Confidence</th>
              <th scope="col" className={thClass}>Created</th>
              <th scope="col" className={cn(thClass, "text-right")}>Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {isLoading ? (
              <SkeletonRows />
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={7}>
                  <div
                    className="flex flex-col items-center justify-center py-16 text-center"
                    aria-live="polite"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-surface-elevated text-text-muted">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={1.5}
                        className="h-5 w-5"
                      >
                        <circle cx="11" cy="11" r="8" />
                        <path d="m21 21-4.35-4.35" />
                      </svg>
                    </div>
                    <p className="mt-3 text-xs font-semibold text-text-primary">
                      No scan records found
                    </p>
                    <p className="mt-1 text-[11px] text-text-muted max-w-xs leading-relaxed">
                      Try adjusting your search or filters, or run a new scan in the workspace.
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              items.map((item) => (
                <tr
                  key={item.id}
                  className={cn(
                    "cursor-pointer transition-colors group",
                    loadingId === item.id
                      ? "bg-primary/5"
                      : "hover:bg-surface-subtle",
                  )}
                  onClick={() => handleRowClick(item.id)}
                  tabIndex={0}
                  role="button"
                  aria-label={`View scan details for ${item.filename ?? "Untitled source"}`}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") handleRowClick(item.id);
                  }}
                >
                  {/* Filename */}
                  <td className="px-4 py-2.5 font-semibold text-text-primary group-hover:text-primary transition-colors max-w-[200px]">
                    <span className="block truncate">
                      {item.filename ?? "Untitled source"}
                    </span>
                  </td>

                  {/* Language tag */}
                  <td className="px-4 py-2.5">
                    <span className="inline-flex items-center rounded bg-surface-elevated px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-text-secondary">
                      {item.language}
                    </span>
                  </td>

                  {/* Risk badge */}
                  <td className="px-4 py-2.5">
                    <SeverityBadge severity={item.risk_level} />
                  </td>

                  {/* Vulnerable status pill */}
                  <td className="px-4 py-2.5">
                    {item.is_vulnerable ? (
                      <span className="inline-flex items-center rounded-full border border-severity-critical/20 bg-severityBg-critical px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-severity-critical">
                        Vulnerable
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full border border-severity-safe/20 bg-severityBg-safe px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-severity-safe">
                        Safe
                      </span>
                    )}
                  </td>

                  {/* Confidence mono */}
                  <td className="px-4 py-2.5 font-mono font-semibold text-text-secondary">
                    {(item.confidence * 100).toFixed(0)}%
                  </td>

                  {/* Timestamp mono */}
                  <td className="px-4 py-2.5 font-mono text-[10px] text-text-muted whitespace-nowrap">
                    {new Date(item.created_at).toLocaleDateString(undefined, {
                      year: "2-digit",
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </td>

                  {/* Action */}
                  <td className="px-4 py-2.5 text-right">
                    <button
                      type="button"
                      className="text-[11px] font-semibold text-primary hover:underline disabled:cursor-not-allowed disabled:opacity-40 transition-colors"
                      disabled={loadingId !== null}
                      tabIndex={-1}
                      aria-hidden="true"
                    >
                      {loadingId === item.id ? "Loading..." : "View"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
