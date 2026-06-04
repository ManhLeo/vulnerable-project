import { HistoryPageContent } from "@/features/scan-history/history-page-content";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function ScanHistoryPage(): JSX.Element {
  return (
    <ProtectedRoute allowedRoles={["user", "admin"]}>
      <div className="space-y-6">
        <section className="space-y-1">
          <h1 className="text-xl font-semibold tracking-tight text-text-primary md:text-2xl">Scan History</h1>
          <p className="text-xs text-text-muted">
            Review prior scans with filters, severity signals, and paginated records.
          </p>
        </section>

        <HistoryPageContent />
      </div>
    </ProtectedRoute>
  );
}
