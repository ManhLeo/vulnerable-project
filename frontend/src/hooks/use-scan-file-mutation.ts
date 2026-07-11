"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { AppApiError } from "@/lib/api/client";
import { queryKeys } from "@/lib/query/query-keys";
import { scanFile } from "@/services/scan.service";
import type { ApiSuccessResponse, ScanCodeResultDto } from "@/types/api";

interface ScanFilePayload {
  file: File;
  language?: "c" | "cpp";
  model_mode?: "single" | "best_confidence";
  checkpoint_name?: string;
  checkpoint_names?: string[];
}

export function useScanFileMutation() {
  const queryClient = useQueryClient();

  const mutation = useMutation<ApiSuccessResponse<ScanCodeResultDto>, AppApiError, ScanFilePayload>({
    mutationFn: scanFile,
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
    reset: mutation.reset,
  };
}
