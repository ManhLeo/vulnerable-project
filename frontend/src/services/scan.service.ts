import { apiClient } from "@/lib/api/client";
import type {
  ApiSuccessResponse,
  ScanCodeRequestDto,
  ScanCodeResultDto,
  ScanHistoryDataDto,
  ScanHistoryQueryDto,
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

export async function scanFile(file: File): Promise<ApiSuccessResponse<ScanCodeResultDto>> {
  const formData = new FormData();
  formData.append("file", file);

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
