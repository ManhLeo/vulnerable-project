export const queryKeys = {
  health: {
    all: ["health"] as const,
  },
  model: {
    all: ["model"] as const,
    info: ["model", "info"] as const,
  },
  scan: {
    all: ["scan"] as const,
    code: ["scan", "code"] as const,
    file: ["scan", "file"] as const,
  },
  history: {
    all: ["history"] as const,
    list: (page: number, limit: number) => ["history", "list", page, limit] as const,
  },
} as const;
