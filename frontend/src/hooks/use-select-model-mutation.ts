"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { selectModel } from "@/services/model.service";
import type { ApiSuccessResponse, ModelInfoDto } from "@/types/api";

export function useSelectModelMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<
    ApiSuccessResponse<ModelInfoDto>,
    AppApiError,
    string
  >({
    mutationFn: selectModel,
    onSuccess: (res) => {
      // Update cache instantly
      queryClient.setQueryData(queryKeys.model.info, res);
      // Invalidate query to trigger visual updates
      queryClient.invalidateQueries({
        queryKey: queryKeys.model.info,
      });
    },
  });

  return {
    data: mutation.data,
    error: mutation.error,
    isLoading: mutation.isPending,
    isError: mutation.isError,
    mutate: mutation.mutate,
    mutateAsync: mutation.mutateAsync,
  };
}
