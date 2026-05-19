"use client";

import { useQuery } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { getScanHistory } from "@/services/scan.service";
import type {
  ApiSuccessResponse,
  ScanHistoryDataDto,
  ScanHistoryQueryDto,
} from "@/types/api";

export function useScanHistoryQuery(query: ScanHistoryQueryDto = {}) {
  const page = query.page ?? 1;
  const limit = query.limit ?? 10;

  const queryResult = useQuery<ApiSuccessResponse<ScanHistoryDataDto>, AppApiError>({
    queryKey: queryKeys.history.list(page, limit),
    queryFn: () => getScanHistory({ page, limit }),
  });

  return {
    data: queryResult.data,
    error: queryResult.error,
    isLoading: queryResult.isLoading,
    isError: queryResult.isError,
  };
}
