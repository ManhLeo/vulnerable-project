import { DashboardPageContent } from "@/features/scan-history/dashboard-page-content";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function DashboardPage(): JSX.Element {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <div className="space-y-6">
        <section className="space-y-1">
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-primary">Security Analytics</p>
          <h1 className="text-xl font-semibold tracking-tight text-text-primary md:text-2xl">Analytics</h1>
          <p className="text-xs text-text-muted">
            Scan analytics dashboard with volume, confidence, risk distribution, and recent activity.
          </p>
        </section>

        <DashboardPageContent />
      </div>
    </ProtectedRoute>
  );
}
