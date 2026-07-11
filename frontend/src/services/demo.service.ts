import { apiClient } from "@/lib/api/client";
import type { ApiSuccessResponse, DemoSampleDto, ScanCodeResultDto } from "@/types/api";

export async function getDemoSamples(): Promise<ApiSuccessResponse<DemoSampleDto[]>> {
  const response = await apiClient.get<ApiSuccessResponse<DemoSampleDto[]>>(
    "/api/v1/demo/samples",
  );
  return response.data;
}

export async function runDemoScan(sampleId: string): Promise<ApiSuccessResponse<ScanCodeResultDto>> {
  const response = await apiClient.post<ApiSuccessResponse<ScanCodeResultDto>>(
    "/api/v1/demo/scan",
    { sample_id: sampleId },
  );
  return response.data;
}
