import { apiClient } from "@/lib/api/client";
import type {
  ApiSuccessResponse,
  ScanCodeRequestDto,
  ScanCodeResultDto,
  ScanHistoryDataDto,
  ScanHistoryQueryDto,
  ScanStatsDto,
} from "@/types/api";

export async function scanCode(
  payload: ScanCodeRequestDto,
): Promise<ApiSuccessResponse<ScanCodeResultDto>> {
  const response = await apiClient.post<ApiSuccessResponse<ScanCodeResultDto>>(
    "/api/v1/scan/code",
    payload,
  );
  return response.data;
}

interface ScanFilePayload {
  file: File;
  language?: "c" | "cpp";
  model_mode?: "single" | "best_confidence";
  checkpoint_name?: string;
  checkpoint_names?: string[];
}

export async function scanFile({
  file,
  language,
  model_mode,
  checkpoint_name,
  checkpoint_names,
}: ScanFilePayload): Promise<ApiSuccessResponse<ScanCodeResultDto>> {
  const formData = new FormData();
  formData.append("file", file);
  if (language) {
    formData.append("language", language);
  }
  if (model_mode) {
    formData.append("model_mode", model_mode);
  }
  if (checkpoint_name) {
    formData.append("checkpoint_name", checkpoint_name);
  }
  if (checkpoint_names && checkpoint_names.length > 0) {
    formData.append("checkpoint_names", JSON.stringify(checkpoint_names));
  }

  const response = await apiClient.post<ApiSuccessResponse<ScanCodeResultDto>>(
    "/api/v1/scan/file",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );

  return response.data;
}

export async function getScanHistory(
  query: ScanHistoryQueryDto = {},
): Promise<ApiSuccessResponse<ScanHistoryDataDto>> {
  const response = await apiClient.get<ApiSuccessResponse<ScanHistoryDataDto>>(
    "/api/v1/scan/history",
    {
      params: {
        page: query.page ?? 1,
        limit: query.limit ?? 10,
      },
    },
  );

  return response.data;
}

export async function getScanRecord(
  id: string,
): Promise<ApiSuccessResponse<ScanCodeResultDto & { source_code: string; language: string; filename: string | null }>> {
  const response = await apiClient.get<ApiSuccessResponse<ScanCodeResultDto & { source_code: string; language: string; filename: string | null }>>(
    `/api/v1/scan/${id}`,
  );
  return response.data;
}

export async function getScanStats(): Promise<ApiSuccessResponse<ScanStatsDto>> {
  const response = await apiClient.get<ApiSuccessResponse<ScanStatsDto>>(
    "/api/v1/scan/stats",
  );
  return response.data;
}
