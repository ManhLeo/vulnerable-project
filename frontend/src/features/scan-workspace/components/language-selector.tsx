"use client";

import { Badge } from "@/components/ui/badge";

const LANGUAGE_OPTIONS = [
  { value: "c_cpp", label: "C/C++" },
] as const;

interface LanguageSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function LanguageSelector({
  value,
  onChange,
  disabled = false,
}: LanguageSelectorProps): JSX.Element {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <label htmlFor="language" className="text-xs font-semibold uppercase tracking-wide text-text-secondary">
          Language
        </label>
        <Badge variant="neutral" className="px-2 py-0.5 text-[10px] font-semibold">
          Runtime-safe
        </Badge>
      </div>
      <select
        id="language"
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="h-9 w-full rounded-md border border-border bg-surface-panel px-3 text-sm outline-none ring-offset-background transition placeholder:text-text-muted focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
      >
        {LANGUAGE_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
