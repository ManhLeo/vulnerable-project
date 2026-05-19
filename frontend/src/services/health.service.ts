import { apiClient } from "@/lib/api/client";
import type { ApiSuccessResponse, HealthDataDto } from "@/types/api";

export async function getHealth(): Promise<ApiSuccessResponse<HealthDataDto>> {
  const response = await apiClient.get<ApiSuccessResponse<HealthDataDto>>("/api/v1/health");
  return response.data;
}
