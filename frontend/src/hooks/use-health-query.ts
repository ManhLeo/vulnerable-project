"use client";

import { useQuery } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { getHealth } from "@/services/health.service";
import type { ApiSuccessResponse, HealthDataDto } from "@/types/api";

export function useHealthQuery() {
  const query = useQuery<ApiSuccessResponse<HealthDataDto>, AppApiError>({
    queryKey: queryKeys.health.all,
    queryFn: getHealth,
  });

  return {
    data: query.data,
    error: query.error,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
