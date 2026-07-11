import { apiClient } from "@/lib/api/client";
import type { AdminStatsDto, AdminUserDto } from "@/types/api";

export async function getAdminStats(): Promise<AdminStatsDto> {
  const response = await apiClient.get<AdminStatsDto>("/api/v1/admin/stats");
  return response.data;
}

export async function getAdminUsers(): Promise<AdminUserDto[]> {
  const response = await apiClient.get<AdminUserDto[]>("/api/v1/admin/users");
  return response.data;
}

export async function deleteAdminUser(userId: string): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(`/api/v1/admin/users/${userId}`);
  return response.data;
}

export async function exportScanSourcesCsv(): Promise<Blob> {
  const response = await apiClient.get<Blob>("/api/v1/admin/scan-sources/export.csv", {
    responseType: "blob",
  });
  return response.data;
}
