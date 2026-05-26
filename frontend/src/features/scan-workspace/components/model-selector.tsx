"use client";

import { useModelInfoQuery } from "@/hooks/use-model-info-query";
import { useSelectModelMutation } from "@/hooks/use-select-model-mutation";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

interface ModelSelectorProps {
  disabled?: boolean;
}

export function ModelSelector({ disabled = false }: ModelSelectorProps): JSX.Element {
  const { data, isLoading: isQueryLoading } = useModelInfoQuery();
  const selectModelMutation = useSelectModelMutation();

  const info = data?.data;
  const isPending = isQueryLoading || selectModelMutation.isLoading;

  const handleSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    if (value && value !== info?.active_checkpoint) {
      selectModelMutation.mutate(value);
    }
  };

  const checkpointOptions = info?.available_checkpoints ?? [];
  const activeCheckpoint = info?.active_checkpoint ?? "";
  const device = info?.device ?? "cpu";
  const supportsGpu = info?.supports_gpu ?? false;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <label htmlFor="model-checkpoint" className="text-xs font-semibold uppercase tracking-wide text-text-secondary">
          Model Checkpoint
        </label>
        <div className="flex items-center gap-1.5">
          {selectModelMutation.isLoading && (
            <Loader2 className="h-3 w-3 animate-spin text-text-muted" />
          )}
          <Badge variant={supportsGpu ? "safe" : "neutral"} className="px-2 py-0.5 text-[10px] font-semibold">
            {device.toUpperCase()}
          </Badge>
        </div>
      </div>
      <select
        id="model-checkpoint"
        value={activeCheckpoint}
        disabled={disabled || isPending || checkpointOptions.length === 0}
        onChange={handleSelect}
        className="h-9 w-full rounded-md border border-border bg-surface-panel px-3 text-sm outline-none ring-offset-background transition placeholder:text-text-muted focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isPending && checkpointOptions.length === 0 ? (
          <option>Loading checkpoints...</option>
        ) : (
          checkpointOptions.map((checkpoint) => (
            <option key={checkpoint} value={checkpoint}>
              {checkpoint === "best_codebert_v3.pt"
                ? "CodeBERT (Default)"
                : checkpoint === "best_graphcodebert_stable.pt"
                ? "GraphCodeBERT"
                : checkpoint}
            </option>
          ))
        )}
      </select>
    </div>
  );
}
