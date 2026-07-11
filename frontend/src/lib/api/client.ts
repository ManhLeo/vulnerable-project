import axios, { type AxiosError, type AxiosInstance } from "axios";

import { env } from "@/lib/env";
import type { ApiErrorResponse } from "@/types/api";

export interface AppApiError {
  status: "error";
  message: string;
  error_code: string;
  statusCode?: number;
}

const DEFAULT_API_ERROR: Omit<AppApiError, "status"> = {
  message: "Internal server error",
  error_code: "INTERNAL_SERVER_ERROR",
};

export function normalizeApiError(error: unknown): AppApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;
    const payload = axiosError.response?.data;

    if (
      payload &&
      payload.status === "error" &&
      typeof payload.message === "string" &&
      typeof payload.error_code === "string"
    ) {
      return {
        status: "error",
        message: payload.message,
        error_code: payload.error_code,
        statusCode: axiosError.response?.status,
      };
    }

    if (axiosError.code === "ECONNABORTED") {
      return {
        status: "error",
        message: "Request timeout",
        error_code: "REQUEST_TIMEOUT",
        statusCode: axiosError.response?.status,
      };
    }

    return {
      status: "error",
      message: axiosError.message || "Network request failed",
      error_code: "NETWORK_ERROR",
      statusCode: axiosError.response?.status,
    };
  }

  return {
    status: "error",
    message: DEFAULT_API_ERROR.message,
    error_code: DEFAULT_API_ERROR.error_code,
  };
}

function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: env.NEXT_PUBLIC_API_URL,
    timeout: 15000,
    withCredentials: true,
    headers: {
      "Content-Type": "application/json",
    },
  });

  client.interceptors.response.use(
    (response) => response,
    (error: unknown) => Promise.reject(normalizeApiError(error)),
  );

  return client;
}

export const apiClient = createApiClient();
