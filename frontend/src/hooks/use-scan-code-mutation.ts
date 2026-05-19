"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { scanCode } from "@/services/scan.service";
import type {
  ApiSuccessResponse,
  ScanCodeRequestDto,
  ScanCodeResultDto,
} from "@/types/api";

export function useScanCodeMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<
    ApiSuccessResponse<ScanCodeResultDto>,
    AppApiError,
    ScanCodeRequestDto
  >({
    mutationFn: scanCode,
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.history.all,
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
