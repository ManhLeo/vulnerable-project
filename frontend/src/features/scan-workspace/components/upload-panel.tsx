"use client";

import { useEffect, useRef } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface UploadPanelProps {
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
  selectedFileName?: string;
  resetSignal?: number;
}

export function UploadPanel({
  onFileChange,
  disabled = false,
  selectedFileName,
  resetSignal = 0,
}: UploadPanelProps): JSX.Element {
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }, [resetSignal]);

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const nextFile = event.target.files?.[0] ?? null;
    onFileChange(nextFile);
  };

  const openFilePicker = (): void => {
    inputRef.current?.click();
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
        ref={inputRef}
        id="code-file"
        type="file"
        disabled={disabled}
        accept=".c,.cpp,.h,.hpp,text/plain"
        onChange={handleFileInput}
        className="sr-only"
        tabIndex={-1}
      />
      <div className="flex min-h-10 items-center gap-2 rounded-md border border-border bg-surface-elevated px-2 py-1.5">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={openFilePicker}
          disabled={disabled}
          className="shrink-0"
        >
          Choose file
        </Button>
        <span className="min-w-0 truncate text-sm text-text-muted">
          {selectedFileName ?? "No file selected"}
        </span>
      </div>
    </div>
  );
}
