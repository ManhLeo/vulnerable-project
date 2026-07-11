interface PublicEnv {
  NEXT_PUBLIC_API_URL: string;
  NEXT_PUBLIC_API_BASE_URL: string;
}

function getOptionalEnv(key: keyof PublicEnv): string | undefined {
  const value = process.env[key];
  if (!value || value.trim().length === 0) {
    return undefined;
  }
  return value;
}

function resolveApiBaseUrl(): string {
  const configured =
    getOptionalEnv("NEXT_PUBLIC_API_URL") ?? getOptionalEnv("NEXT_PUBLIC_API_BASE_URL");
  if (configured) {
    return configured;
  }

  if (process.env.NODE_ENV !== "production") {
    return "http://localhost:8001";
  }

  throw new Error("Missing required environment variable: NEXT_PUBLIC_API_URL");
}

const apiBaseUrl = resolveApiBaseUrl();

export const env: PublicEnv = {
  NEXT_PUBLIC_API_URL: apiBaseUrl,
  NEXT_PUBLIC_API_BASE_URL: apiBaseUrl,
};
