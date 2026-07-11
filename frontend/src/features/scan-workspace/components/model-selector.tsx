"use client";

import { useModelInfoQuery } from "@/hooks/use-model-info-query";
import { useSelectModelMutation } from "@/hooks/use-select-model-mutation";
import { useAuth } from "@/hooks/useAuth";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

interface ModelSelectorProps {
  disabled?: boolean;
  mode?: "request" | "global";
  value: string;
  onChange: (value: string) => void;
}

const ENSEMBLE_VALUE = "__ensemble_best_confidence__";

export function ModelSelector({
  disabled = false,
  mode = "request",
  value,
  onChange,
}: ModelSelectorProps): JSX.Element {
  const { data, isLoading: isQueryLoading } = useModelInfoQuery();
  const selectModelMutation = useSelectModelMutation();
  const { user, isLoading: isAuthLoading } = useAuth();

  const info = data?.data;
  const isPending = isQueryLoading || selectModelMutation.isLoading;
  const canManageGlobalModel = mode === "global" && user?.role === "admin" && !isAuthLoading;
  const canUseRequestModel = mode === "request" && Boolean(user) && !isAuthLoading;

  const handleSelect = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const nextValue = event.target.value;
    onChange(nextValue);
    if (
      canManageGlobalModel &&
      nextValue &&
      nextValue !== ENSEMBLE_VALUE &&
      nextValue !== info?.active_checkpoint
    ) {
      selectModelMutation.mutate(nextValue);
    }
  };

  const rawCheckpointOptions =
    info?.available_model_options?.length
      ? info.available_model_options
      : (info?.available_checkpoints ?? []).map((checkpoint) => ({
          checkpoint_name: checkpoint,
          label: checkpoint,
          description: "Available model checkpoint",
        }));
  const checkpointOptions =
    mode === "global"
      ? rawCheckpointOptions.filter((option) => option.checkpoint_name !== ENSEMBLE_VALUE)
      : rawCheckpointOptions;
  const activeCheckpoint = mode === "global" ? value || info?.active_checkpoint || "" : value;
  const device = info?.device ?? "cpu";
  const supportsGpu = info?.supports_gpu ?? false;
  const isDisabled =
    disabled ||
    isPending ||
    checkpointOptions.length === 0 ||
    (!canManageGlobalModel && !canUseRequestModel);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <label htmlFor="model-checkpoint" className="text-xs font-semibold uppercase tracking-wide text-text-secondary">
          Model Mode
        </label>
        <div className="flex items-center gap-1.5">
          {selectModelMutation.isLoading && (
            <Loader2 className="h-3 w-3 animate-spin text-text-muted" />
          )}
          <Badge variant={supportsGpu ? "safe" : "neutral"} className="px-2 py-0.5 text-[10px] font-semibold">
            {device.toUpperCase()}
          </Badge>
          {mode === "global" ? (
            <Badge variant="neutral" className="px-2 py-0.5 text-[10px] font-semibold">
              Admin global
            </Badge>
          ) : (
            <Badge variant="neutral" className="px-2 py-0.5 text-[10px] font-semibold">
              Per scan
            </Badge>
          )}
        </div>
      </div>
      <select
        id="model-checkpoint"
        value={activeCheckpoint}
        disabled={isDisabled}
        onChange={handleSelect}
        className="h-10 w-full rounded-md border border-border bg-surface-elevated px-3 text-sm text-text-primary outline-none transition placeholder:text-text-muted focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isPending && checkpointOptions.length === 0 ? (
          <option>Loading checkpoints...</option>
        ) : (
          <>
            {mode === "request" ? (
              <option value="">Default active model</option>
            ) : null}
            {checkpointOptions.map((option) => (
              <option key={option.checkpoint_name} value={option.checkpoint_name}>
                {option.label}
              </option>
            ))}
          </>
        )}
      </select>
      <p className="text-[11px] leading-relaxed text-text-muted">
        {activeCheckpoint
          ? checkpointOptions.find((option) => option.checkpoint_name === activeCheckpoint)?.description ??
            "Selected model configuration"
          : mode === "request"
            ? "No per-scan override selected. The backend will use the active server checkpoint."
            : "Global checkpoint selection is restricted to administrators."}
      </p>
    </div>
  );
}
