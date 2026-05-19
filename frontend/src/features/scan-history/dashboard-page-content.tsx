"use client";

import { useMemo } from "react";
import { useRouter } from "next/navigation";
import { ErrorState } from "@/components/common/error-state";
import { useScanHistoryQuery } from "@/hooks/use-scan-history-query";
import { Button } from "@/components/ui/button";
import {
  buildDashboardSummary,
  buildRiskDistribution,
  getRecentScans,
} from "@/lib/utils/scan-history";

import { RecentScansList } from "./components/recent-scans-list";
import { RiskDistributionSummary } from "./components/risk-distribution-summary";
import { StatCard } from "./components/stat-card";
import { ActivityFeed } from "./components/activity-feed";

export function DashboardPageContent(): JSX.Element {
  const router = useRouter();
  const { data, isLoading, isError, error } = useScanHistoryQuery({ page: 1, limit: 50 });

  const summary = useMemo(() => {
    const items = data?.data.items ?? [];
    return buildDashboardSummary(items);
  }, [data?.data.items]);

  const distribution = useMemo(() => {
    const items = data?.data.items ?? [];
    return buildRiskDistribution(items);
  }, [data?.data.items]);

  const recent = useMemo(() => {
    const items = data?.data.items ?? [];
    return getRecentScans(items, 6);
  }, [data?.data.items]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        {/* Shimmer Stat Cards */}
        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse rounded-lg border border-border bg-white p-5 shadow-sm space-y-3">
              <div className="h-2 w-20 rounded bg-gray-100" />
              <div className="h-8 w-24 rounded bg-gray-100" />
            </div>
          ))}
        </section>

        {/* Shimmer Main Grid */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <div className="animate-pulse rounded-lg border border-border bg-white shadow-sm overflow-hidden">
              <div className="h-12 border-b border-border/60 bg-gray-50/50 p-4" />
              <div className="p-4 space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="h-3 w-40 rounded bg-gray-100" />
                    <div className="h-3 w-16 rounded bg-gray-100" />
                    <div className="h-3 w-12 rounded bg-gray-100" />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="space-y-6">
            <div className="animate-pulse rounded-lg border border-border bg-white p-5 shadow-sm space-y-4">
              <div className="h-3 w-28 rounded bg-gray-100" />
              <div className="h-3 w-full rounded-full bg-gray-100" />
              <div className="grid grid-cols-4 gap-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-10 rounded bg-gray-100" />
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        title="Unable to load dashboard"
        message={error?.message ?? "Dashboard data request failed."}
      />
    );
  }

  if ((data?.data.items ?? []).length === 0) {
    return (
      <section className="rounded-lg border border-border bg-white p-12 text-center shadow-sm max-w-xl mx-auto mt-8">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary-subtle text-primary border border-primary/10">
          <span className="font-mono font-bold text-lg">AI</span>
        </div>
        <h2 className="mt-4 text-base font-semibold text-text-primary">No scans detected</h2>
        <p className="mt-2 text-xs text-text-muted max-w-xs mx-auto leading-relaxed">
          Run your first automated vulnerability check or upload source code in the workspace to populate this dashboard.
        </p>
        <div className="mt-6">
          <Button onClick={() => router.push("/")} variant="primary" size="sm">
            Go to Workspace
          </Button>
        </div>
      </section>
    );
  }

  return (
    <div className="space-y-6">
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Total scans" value={summary.total} />
        <StatCard title="Vulnerable scans" value={summary.vulnerable} />
        <StatCard title="Safe scans" value={summary.safe} />
        <StatCard
          title="Avg confidence"
          value={`${(summary.averageConfidence * 100).toFixed(1)}%`}
        />
      </section>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Left 2 columns: Recent Scans Data Table */}
        <div className="lg:col-span-2 space-y-4">
          <RecentScansList items={recent} />
        </div>

        {/* Right 1 column: Risk Distribution horizontal bar chart & Activity Feed */}
        <div className="space-y-6">
          <RiskDistributionSummary distribution={distribution} />
          <ActivityFeed items={recent} />
        </div>
      </section>
    </div>
  );
}
