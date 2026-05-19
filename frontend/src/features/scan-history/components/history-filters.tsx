import type { SeverityLevel } from "@/types/severity";

interface HistoryFiltersProps {
  search: string;
  risk: "ALL" | SeverityLevel;
  vulnerable: "ALL" | "YES" | "NO";
  onSearchChange: (value: string) => void;
  onRiskChange: (value: "ALL" | SeverityLevel) => void;
  onVulnerableChange: (value: "ALL" | "YES" | "NO") => void;
}

export function HistoryFilters({
  search,
  risk,
  vulnerable,
  onSearchChange,
  onRiskChange,
  onVulnerableChange,
}: HistoryFiltersProps): JSX.Element {
  const inputBase =
    "h-9 rounded-[6px] border border-gray-300 bg-white px-3 text-xs text-text-primary placeholder:text-text-muted outline-none transition-shadow focus:border-primary focus:ring-2 focus:ring-primary/10";

  return (
    <div
      className="flex flex-wrap items-center gap-2"
      aria-label="History filters"
    >
      {/* Search */}
      <div className="relative flex-1 min-w-[180px] max-w-xs">
        <svg
          className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-muted"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search filename or language…"
          aria-label="Search scan history"
          className={`${inputBase} pl-8 w-full`}
        />
      </div>

      {/* Risk level */}
      <select
        value={risk}
        onChange={(event) =>
          onRiskChange(event.target.value as "ALL" | SeverityLevel)
        }
        aria-label="Filter by risk level"
        className={`${inputBase} pr-8 cursor-pointer`}
      >
        <option value="ALL">All risk levels</option>
        <option value="CRITICAL">Critical</option>
        <option value="HIGH">High</option>
        <option value="MEDIUM">Medium</option>
        <option value="LOW">Low</option>
      </select>

      {/* Vulnerable status */}
      <select
        value={vulnerable}
        onChange={(event) =>
          onVulnerableChange(event.target.value as "ALL" | "YES" | "NO")
        }
        aria-label="Filter by vulnerability status"
        className={`${inputBase} pr-8 cursor-pointer`}
      >
        <option value="ALL">All statuses</option>
        <option value="YES">Vulnerable</option>
        <option value="NO">Safe</option>
      </select>

      {/* Active filter indicator */}
      {(search || risk !== "ALL" || vulnerable !== "ALL") && (
        <button
          type="button"
          onClick={() => {
            onSearchChange("");
            onRiskChange("ALL");
            onVulnerableChange("ALL");
          }}
          className="h-9 rounded-[6px] border border-gray-300 bg-white px-3 text-xs font-medium text-text-secondary hover:bg-gray-50 hover:text-text-primary transition-colors"
          aria-label="Clear all filters"
        >
          Clear
        </button>
      )}
    </div>
  );
}
