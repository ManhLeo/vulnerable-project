"use client";

import {
  QueryCache,
  QueryClient,
  QueryClientProvider,
  MutationCache,
} from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

import type { AppApiError } from "@/lib/api/client";

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: (failureCount: number, error: unknown) => {
              const appError = error as AppApiError;
              const statusCode = appError?.statusCode;

              if (typeof statusCode === "number" && statusCode >= 400 && statusCode < 500) {
                return false;
              }

              return failureCount < 2;
            },
            staleTime: 30_000,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 0,
          },
        },
        queryCache: new QueryCache({
          onError: () => {
            // Centralized query error boundary point for future toast integration.
          },
        }),
        mutationCache: new MutationCache({
          onError: () => {
            // Centralized mutation error boundary point for future toast integration.
          },
        }),
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
