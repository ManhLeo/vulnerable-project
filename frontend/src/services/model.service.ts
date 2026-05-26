import { apiClient } from "@/lib/api/client";
import type { ApiSuccessResponse, ModelInfoDto } from "@/types/api";

export async function getModelInfo(): Promise<ApiSuccessResponse<ModelInfoDto>> {
  const response = await apiClient.get<ApiSuccessResponse<ModelInfoDto>>("/api/v1/model/info");
  return response.data;
}

export async function selectModel(checkpointName: string): Promise<ApiSuccessResponse<ModelInfoDto>> {
  const response = await apiClient.post<ApiSuccessResponse<ModelInfoDto>>("/api/v1/model/select", {
    checkpoint_name: checkpointName,
  });
  return response.data;
}
