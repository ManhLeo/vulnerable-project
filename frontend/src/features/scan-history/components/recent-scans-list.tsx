import { useState } from "react";
import { useRouter } from "next/navigation";
import { SeverityBadge } from "@/features/scan-workspace/components/severity-badge";
import type { ScanHistoryItemDto } from "@/types/api";
import { getScanRecord } from "@/services/scan.service";
import { useScanStore } from "@/lib/store/scan-store";
import type { AppApiError } from "@/lib/api/client";

interface RecentScansListProps {
  items: ScanHistoryItemDto[];
}

export function RecentScansList({ items }: RecentScansListProps): JSX.Element {
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
        });
        setCode(res.data.source_code);
        setLanguage(res.data.language);
        router.push("/scan/result");
      }
    } catch (err) {
      setDetailError(err as AppApiError);
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <section className="rounded-lg border border-border bg-white shadow-sm overflow-hidden" aria-label="Recent scans">
      <div className="flex items-center justify-between border-b border-border/60 p-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-text-secondary">Recent Scans</h2>
        <span className="text-[10px] font-mono text-text-muted">
          Latest {items.length} runs
        </span>
      </div>

      {detailError ? (
        <div className="border-b border-severity-critical/20 bg-severityBg-critical px-4 py-3" role="alert">
          <p className="text-xs font-semibold text-severity-critical">Unable to open scan detail</p>
          <p className="mt-1 text-[11px] text-text-secondary">{detailError.message}</p>
          <p className="mt-1 font-mono text-[10px] text-text-muted">Code: {detailError.error_code}</p>
        </div>
      ) : null}

      {items.length === 0 ? (
        <div className="p-8 text-center">
          <p className="text-xs text-text-muted">No recent scans available.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs">
            <thead className="bg-gray-50 border-b border-border/60">
              <tr>
                <th className="px-4 py-2.5 text-left text-[10px] font-bold text-text-muted uppercase tracking-wider">Filename</th>
                <th className="px-4 py-2.5 text-left text-[10px] font-bold text-text-muted uppercase tracking-wider">Language</th>
                <th className="px-4 py-2.5 text-left text-[10px] font-bold text-text-muted uppercase tracking-wider">Risk</th>
                <th className="px-4 py-2.5 text-left text-[10px] font-bold text-text-muted uppercase tracking-wider">Confidence</th>
                <th className="px-4 py-2.5 text-right text-[10px] font-bold text-text-muted uppercase tracking-wider">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {items.map((item) => (
                <tr
                  key={item.id}
                  className="hover:bg-gray-50/50 cursor-pointer transition-colors group"
                  onClick={() => handleRowClick(item.id)}
                >
                  <td className="px-4 py-3 font-medium text-text-primary group-hover:text-primary transition-colors max-w-[140px] truncate">
                    {item.filename ?? "Untitled source"}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center rounded bg-gray-100 px-1.5 py-0.5 text-[10px] font-semibold text-text-secondary tracking-wide uppercase">
                      {item.language}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <SeverityBadge severity={item.risk_level} />
                  </td>
                  <td className="px-4 py-3 font-mono font-semibold text-text-secondary">
                    {(item.confidence * 100).toFixed(0)}%
                  </td>
                  <td className="px-4 py-3 text-right text-text-muted font-mono text-[10px]">
                    {loadingId === item.id ? (
                      <span className="text-primary font-semibold">Loading...</span>
                    ) : (
                      new Date(item.created_at).toLocaleDateString(undefined, {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
