"use client";

import { Badge } from "@/components/ui/badge";

interface UploadPanelProps {
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
  selectedFileName?: string;
}

export function UploadPanel({
  onFileChange,
  disabled = false,
  selectedFileName,
}: UploadPanelProps): JSX.Element {
  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const nextFile = event.target.files?.[0] ?? null;
    onFileChange(nextFile);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <label htmlFor="code-file" className="text-xs font-semibold uppercase tracking-wide text-text-secondary">
          Source file
        </label>
        <Badge variant="neutral" className="px-2 py-0.5 text-[10px] font-semibold">
          Max 5MB
        </Badge>
      </div>
      <input
        id="code-file"
        type="file"
        disabled={disabled}
        accept=".py,.java,.c,.cpp,text/plain"
        onChange={handleFileInput}
        className="block h-9 w-full rounded-md border border-border bg-surface-panel px-3 text-sm file:mr-3 file:rounded-md file:border-0 file:bg-surface-subtle file:px-2.5 file:py-1 file:text-xs file:font-semibold disabled:cursor-not-allowed disabled:opacity-60"
      />
      {selectedFileName ? (
        <p className="text-xs text-text-primary">Selected: {selectedFileName}</p>
      ) : (
        <p className="text-xs text-text-muted">No file selected (.py, .java, .c, .cpp)</p>
      )}
    </div>
  );
}
