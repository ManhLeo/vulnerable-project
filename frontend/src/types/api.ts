import type { SeverityLevel } from "@/types/severity";

export type ApiStatus = "success" | "error";

export interface ApiSuccessResponse<TData> {
  status: "success";
  data: TData;
  message: string;
}

export interface ApiErrorResponse {
  status: "error";
  message: string;
  error_code: string;
}

export type ApiResponse<TData> = ApiSuccessResponse<TData> | ApiErrorResponse;

export interface HealthDataDto {
  service: string;
  status: string;
  timestamp: string;
}

export interface ModelInfoDto {
  model_name: string;
  model_version: string;
  device: string;
  labels: string[];
}

export interface FindingDto {
  pattern: string;
  issue: string;
  severity: SeverityLevel;
  line: number;
  code: string;
}

export interface ScanCodeRequestDto {
  code: string;
  language: string;
}

export interface ScanCodeResultDto {
  scan_id: string;
  is_vulnerable: boolean;
  confidence: number;
  risk_level: SeverityLevel;
  findings: FindingDto[];
}

export interface ScanHistoryItemDto {
  id: string;
  filename: string | null;
  language: string;
  is_vulnerable: boolean;
  confidence: number;
  risk_level: SeverityLevel;
  created_at: string;
}

export interface ScanHistoryQueryDto {
  page?: number;
  limit?: number;
}

export interface ScanHistoryDataDto {
  items: ScanHistoryItemDto[];
  total: number;
  page: number;
  limit: number;
}
