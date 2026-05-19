import type { ScanHistoryItemDto } from "@/types/api";
import { SEVERITY_LEVELS, type SeverityLevel } from "@/types/severity";

export interface HistoryFilters {
  search: string;
  risk: "ALL" | SeverityLevel;
  vulnerable: "ALL" | "YES" | "NO";
}

export interface DashboardSummary {
  total: number;
  vulnerable: number;
  safe: number;
  averageConfidence: number;
}

export function normalizeSearchTerm(value: string): string {
  return value.trim().toLowerCase();
}

export function matchesHistoryFilters(
  item: ScanHistoryItemDto,
  filters: HistoryFilters,
): boolean {
  const search = normalizeSearchTerm(filters.search);
  const filename = (item.filename ?? "").toLowerCase();
  const language = item.language.toLowerCase();

  const searchMatch =
    search.length === 0 || filename.includes(search) || language.includes(search);

  const riskMatch = filters.risk === "ALL" ? true : item.risk_level === filters.risk;

  const vulnerableMatch =
    filters.vulnerable === "ALL"
      ? true
      : filters.vulnerable === "YES"
        ? item.is_vulnerable
        : !item.is_vulnerable;

  return searchMatch && riskMatch && vulnerableMatch;
}

export function buildDashboardSummary(items: ScanHistoryItemDto[]): DashboardSummary {
  const total = items.length;
  const vulnerable = items.filter((item) => item.is_vulnerable).length;
  const safe = total - vulnerable;
  const averageConfidence =
    total === 0
      ? 0
      : Number((items.reduce((sum, item) => sum + item.confidence, 0) / total).toFixed(2));

  return { total, vulnerable, safe, averageConfidence };
}

export function buildRiskDistribution(items: ScanHistoryItemDto[]): Record<SeverityLevel, number> {
  return SEVERITY_LEVELS.reduce(
    (acc, severity) => {
      acc[severity] = items.filter((item) => item.risk_level === severity).length;
      return acc;
    },
    {
      LOW: 0,
      MEDIUM: 0,
      HIGH: 0,
      CRITICAL: 0,
    } as Record<SeverityLevel, number>,
  );
}

export function getRecentScans(items: ScanHistoryItemDto[], limit = 5): ScanHistoryItemDto[] {
  return [...items]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, limit);
}
