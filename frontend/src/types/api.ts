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
  version: string;
  environment: string;
  timestamp: string;
  uptime: number;
  uptime_seconds: number;
  database: {
    status: "connected" | "disconnected" | "skipped";
    mode: "mongodb" | "in_memory";
  };
  model: {
    status: "loaded" | "not_loaded";
    loaded: boolean;
    name: string;
    device: string;
    checkpoint: string | null;
  };
  degraded: boolean;
}

export interface ModelInfoDto {
  model_name: string;
  model_loaded: boolean;
  device: string;
  supports_gpu: boolean;
  active_checkpoint: string;
  available_checkpoints: string[];
  available_model_options?: Array<{
    checkpoint_name: string;
    label: string;
    description: string;
    loaded?: boolean;
  }>;
  supported_modes?: Array<"single" | "best_confidence">;
}

export interface FindingDto {
  pattern?: string;
  issue?: string;
  severity?: SeverityLevel;
  line?: number | null;
  code?: string | null;
  title?: string | null;
  name?: string | null;
  cwe?: string | null;
  confidence?: number | null;
  description?: string | null;
  recommendation?: string | null;
}

export interface ScanCodeRequestDto {
  source_code: string;
  language: "c" | "cpp";
  model_mode?: "single" | "best_confidence";
  checkpoint_name?: string;
  checkpoint_names?: string[];
}

export interface ScanResultMetadataDto {
  model_mode?: string;
  selected_checkpoint?: string | null;
  checkpoint?: string | null;
  model_name?: string | null;
  model_version?: string | null;
  inference_used?: boolean;
  analysis_mode?: string;
  findings_metrics?: FindingsMetricsDto;
  candidate_results?: Array<{
    checkpoint_name: string;
    confidence: number;
    risk_level?: string;
    is_vulnerable?: boolean;
  }>;
}

export interface FindingsMetricsDto {
  is_vulnerable_by_metrics?: boolean;
  findings_count: number;
  risk_score: number;
  risk_level: string;
  severity_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export interface ScanCodeResultDto {
  scan_id: string;
  is_demo?: boolean;
  source_type?: string;
  language?: string;
  source_code?: string;
  is_vulnerable: boolean;
  confidence: number;
  risk_level: SeverityLevel;
  findings: FindingDto[];
  findings_metrics?: FindingsMetricsDto;
  analysis_mode?: string;
  metadata?: ScanResultMetadataDto | null;
}

export interface DemoSampleDto {
  id: string;
  title: string;
  language: "c" | "cpp";
  source_code: string;
  description: string;
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

export interface ScanStatsDto {
  total_scans: number;
  vulnerable_scans: number;
  safe_scans: number;
  vulnerable_ratio: number;
  average_confidence: number;
  risk_distribution: Record<SeverityLevel, number>;
}

export interface AdminUserDto {
  id: string;
  email: string;
  role: "guest" | "user" | "admin";
  is_active: boolean;
  is_deleted: boolean;
  created_at: string;
  last_login_at: string | null;
  failed_login_attempts: number;
}

export interface AdminStatsDto {
  users: {
    total_active: number;
  };
  scans: ScanStatsDto;
}
