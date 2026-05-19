import type { ApiSuccessResponse, FindingDto, ScanCodeResultDto } from "@/types/api";
import type { SeverityLevel } from "@/types/severity";

export interface UiFinding extends FindingDto {
  id: string;
  line: number;
  severity: SeverityLevel;
}

export function normalizeFindings(findings: FindingDto[] | undefined): UiFinding[] {
  if (!findings || findings.length === 0) {
    return [];
  }

  return findings.map((finding, index) => ({
    ...finding,
    line: Math.max(1, Number.isFinite(finding.line) ? finding.line : 1),
    id: `${finding.pattern}-${finding.line}-${index}`,
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
