import * as React from "react";

import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={cn(
        "h-9 w-full rounded-md border border-input bg-surface-panel px-3 text-sm text-text-primary",
        "placeholder:text-text-placeholder focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/15",
        "focus-visible:border-primary disabled:cursor-not-allowed disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
});

Input.displayName = "Input";
