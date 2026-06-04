"use client";

import { useQuery } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { getScanStats } from "@/services/scan.service";
import type { ApiSuccessResponse, ScanStatsDto } from "@/types/api";

export function useScanStatsQuery() {
  const query = useQuery<ApiSuccessResponse<ScanStatsDto>, AppApiError>({
    queryKey: queryKeys.scan.stats,
    queryFn: getScanStats,
  });

  return {
    data: query.data,
    error: query.error,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
