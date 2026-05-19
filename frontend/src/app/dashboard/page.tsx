import { DashboardPageContent } from "@/features/scan-history/dashboard-page-content";

export default function DashboardPage(): JSX.Element {
  return (
    <div className="space-y-6">
      <section className="space-y-1">
        <h1 className="text-xl font-semibold tracking-tight text-text-primary md:text-2xl">Dashboard</h1>
        <p className="text-xs text-text-muted">
          Security posture overview with risk distribution and recent scan activity.
        </p>
      </section>

      <DashboardPageContent />
    </div>
  );
}
