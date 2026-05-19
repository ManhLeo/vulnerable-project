import { apiClient } from "@/lib/api/client";
import type { ApiSuccessResponse, ModelInfoDto } from "@/types/api";

export async function getModelInfo(): Promise<ApiSuccessResponse<ModelInfoDto>> {
  const response = await apiClient.get<ApiSuccessResponse<ModelInfoDto>>("/api/v1/model/info");
  return response.data;
}
