"use client";

import { useMemo, useState } from "react";

import { ErrorState } from "@/components/common/error-state";
import { useScanHistoryQuery } from "@/hooks/use-scan-history-query";
import { matchesHistoryFilters, type HistoryFilters } from "@/lib/utils/scan-history";

import { HistoryFilters as HistoryFiltersPanel } from "./components/history-filters";
import { PaginationControls } from "./components/pagination-controls";
import { ScanHistoryTable } from "./components/scan-history-table";

export function HistoryPageContent(): JSX.Element {
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<HistoryFilters>({
    search: "",
    risk: "ALL",
    vulnerable: "ALL",
  });

  const { data, isLoading, isError, error } = useScanHistoryQuery({ page, limit: 10 });

  const filteredItems = useMemo(() => {
    const items = data?.data.items ?? [];
    return items.filter((item) => matchesHistoryFilters(item, filters));
  }, [data?.data.items, filters]);

  if (isError) {
    return (
      <ErrorState
        title="Unable to load history"
        message={error?.message ?? "Request failed. Please retry."}
      />
    );
  }

  const totalRecords = data?.data.total ?? 0;

  return (
    <div className="space-y-4">
      {/* Toolbar row: filters + record count */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <HistoryFiltersPanel
          search={filters.search}
          risk={filters.risk}
          vulnerable={filters.vulnerable}
          onSearchChange={(value) => setFilters((prev) => ({ ...prev, search: value }))}
          onRiskChange={(value) => setFilters((prev) => ({ ...prev, risk: value }))}
          onVulnerableChange={(value) => setFilters((prev) => ({ ...prev, vulnerable: value }))}
        />
        {!isLoading && (
          <span className="font-mono text-[11px] text-text-muted shrink-0">
            {filteredItems.length} / {totalRecords} records
          </span>
        )}
      </div>

      {/* Table */}
      <ScanHistoryTable items={filteredItems} isLoading={isLoading} />

      {/* Pagination */}
      {!isLoading && (
        <PaginationControls
          page={data?.data.page ?? 1}
          limit={data?.data.limit ?? 10}
          total={data?.data.total ?? 0}
          onPageChange={(nextPage) => setPage(nextPage)}
        />
      )}
    </div>
  );
}
