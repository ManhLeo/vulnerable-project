"use client";

import { useQuery } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { getModelInfo } from "@/services/model.service";
import type { ApiSuccessResponse, ModelInfoDto } from "@/types/api";

export function useModelInfoQuery() {
  const query = useQuery<ApiSuccessResponse<ModelInfoDto>, AppApiError>({
    queryKey: queryKeys.model.info,
    queryFn: getModelInfo,
  });

  return {
    data: query.data,
    error: query.error,
    isLoading: query.isLoading,
    isError: query.isError,
  };
}
