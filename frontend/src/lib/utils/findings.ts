import type { ApiSuccessResponse, FindingDto, ScanCodeResultDto } from "@/types/api";
import type { SeverityLevel } from "@/types/severity";

export interface UiFinding extends FindingDto {
  id: string;
  line: number;
  severity: SeverityLevel;
  pattern: string;
  issue: string;
  code: string;
}

export function formatConfidence(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }

  const percentage = value <= 1 ? value * 100 : value;
  return `${Math.round(percentage)}%`;
}

export function normalizeFindings(findings: FindingDto[] | undefined): UiFinding[] {
  if (!findings || findings.length === 0) {
    return [];
  }

  return findings.map((finding, index) => ({
    ...finding,
    line: Math.max(1, Number.isFinite(finding.line ?? NaN) ? Number(finding.line) : 1),
    severity: finding.severity ?? "LOW",
    pattern: finding.pattern ?? finding.title ?? finding.name ?? "Security finding",
    issue: finding.issue ?? finding.description ?? "No description provided.",
    code: finding.code ?? "",
    id: `${finding.pattern ?? finding.title ?? "finding"}-${finding.line ?? "na"}-${index}`,
  }));
}

export function getLatestScanResult(
  codeResult?: ApiSuccessResponse<ScanCodeResultDto>,
  fileResult?: ApiSuccessResponse<ScanCodeResultDto>,
): ScanCodeResultDto | null {
  if (fileResult?.data) {
    return fileResult.data;
  }

  if (codeResult?.data) {
    return codeResult.data;
  }

  return null;
}

export function countBySeverity(findings: UiFinding[]): Record<SeverityLevel, number> {
  return findings.reduce<Record<SeverityLevel, number>>(
    (acc, finding) => {
      acc[finding.severity] += 1;
      return acc;
    },
    {
      LOW: 0,
      MEDIUM: 0,
      HIGH: 0,
      CRITICAL: 0,
    },
  );
}
